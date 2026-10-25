import html
import streamlit as st

from database import setup_database
from menu import show_menu, show_all_menu_items, create_menu_item, edit_menu_item
from orders import (
    place_order, get_all_orders, update_order_status,
    get_order_count, get_total_sales,
)
from ai_recommendation import recommend_healthy_food

st.set_page_config(page_title="Campus Bites | Canteen", page_icon="🍔", layout="wide")

# Student prototype only. For public deployment, use st.secrets and real authentication.
ADMIN_PASSWORD = "Canteen@123"
setup_database()

for key, default in {
    "admin_logged_in": False,
    "cart": {},
    "student_name": "",
    "student_id": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def add_to_cart(food, quantity):
    name = food["name"]
    if name in st.session_state.cart:
        st.session_state.cart[name]["quantity"] += quantity
    else:
        st.session_state.cart[name] = {
            "name": name, "price": food["price"], "quantity": quantity,
        }


def cart_total():
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart.values())


def nutrition_line(food):
    return (
        f"**{int(food.get('calories') or 0)} kcal** · "
        f"Protein **{float(food.get('protein') or 0):g} g** · "
        f"Carbs **{float(food.get('carbs') or 0):g} g**"
    )


st.sidebar.title("🍔 Campus Bites")
st.sidebar.caption("Your campus food, made easy.")
pages = ["🏠 Home", "🍽️ Order Food", "🤖 Healthy Recommendations", "🛒 My Cart"]
pages.append("🧑‍🍳 Admin Dashboard" if st.session_state.admin_logged_in else "🔐 Admin Login")
page = st.sidebar.radio("Navigate", pages, key="navigation")

if st.session_state.admin_logged_in:
    if st.sidebar.button("🔒 Admin Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("Fresh food. Less waiting.")

if page == "🔐 Admin Login":
    st.title("🔐 Admin Login")
    with st.form("admin_login_form"):
        password = st.text_input("Admin Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
    if submitted:
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

elif page == "🏠 Home":
    st.markdown("""
    <div style="text-align:center;padding:18px 0 12px">
      <div style="font-size:12px;letter-spacing:4px">FRESH FOOD · MADE FOR CAMPUS</div>
      <h1 style="letter-spacing:5px;margin-bottom:0">CAMPUS BITES</h1>
      <p style="letter-spacing:2px;color:gray">CANTEEN MENU</p>
      <hr>
    </div>
    """, unsafe_allow_html=True)

    foods = show_menu()
    if not foods:
        st.info("No food items are currently available. Ask the admin to add menu items.")
    else:
        grouped = {}
        for food in foods:
            grouped.setdefault(food["category"], []).append(food)

        category_names = list(grouped)
        for start in range(0, len(category_names), 2):
            cols = st.columns(2, gap="large")
            for offset, col in enumerate(cols):
                index = start + offset
                if index >= len(category_names):
                    continue
                category = category_names[index]
                with col:
                    st.markdown(f"### {html.escape(category).upper()}")
                    st.divider()
                    for food in grouped[category]:
                        st.markdown(
                            f"**{html.escape(food['name'])}**  "
                            f"<span style='float:right'>₹{float(food['price']):.0f}</span>",
                            unsafe_allow_html=True,
                        )
                        if food.get("description"):
                            st.caption(food["description"])
                        st.caption(
                            f"{int(food.get('calories') or 0)} kcal · "
                            f"Protein {float(food.get('protein') or 0):g} g · "
                            f"Carbs {float(food.get('carbs') or 0):g} g"
                        )
                        st.write("")
    st.caption("Nutrition values are estimates per serving and depend on the recipe and portion size.")
    st.info("To order, open Order Food. The Home page is menu-only; it has no cart buttons.")

elif page == "🍽️ Order Food":
    st.title("🍽️ Order Your Food")
    foods = show_menu()
    if not foods:
        st.warning("The menu is currently empty.")
    else:
        selected_name = st.selectbox("Select a food item", [food["name"] for food in foods])
        food = next(item for item in foods if item["name"] == selected_name)
        st.subheader(food["name"])
        if food.get("description"):
            st.write(food["description"])
        st.write(f"Category: {food['category']} · Price: ₹{float(food['price']):.0f}")
        st.caption(nutrition_line(food))
        quantity = st.number_input("Quantity", min_value=1, max_value=20, value=1, step=1)
        st.subheader(f"Item total: ₹{float(food['price']) * int(quantity):.0f}")
        if st.button("➕ Add to Cart", use_container_width=True):
            add_to_cart(food, int(quantity))
            st.success(f"{food['name']} added to your cart!")

    st.divider()
    item_count = sum(item["quantity"] for item in st.session_state.cart.values())
    st.subheader("🛒 Your Cart")
    st.write(f"Items in cart: {item_count} · Total: ₹{cart_total():.0f}")
    if st.button("🛒 Go to My Cart", type="primary", use_container_width=True):
        st.session_state.navigation = "🛒 My Cart"
        st.rerun()

elif page == "🤖 Healthy Recommendations":
    st.title("🥗 Healthy Food Recommendations")
    st.write("Choose a budget and nutrition goal to find matching menu items.")
    foods = show_menu()
    c1, c2 = st.columns(2)
    with c1:
        budget = st.slider("Maximum budget (₹)", 20, 500, 200, 10)
        diet = st.selectbox("Diet preference", ["Any", "Vegetarian", "Vegan", "Egg", "Non-vegetarian"])
        goal = st.selectbox("Goal", ["Balanced", "High protein", "Lower calorie"])
    with c2:
        max_calories = st.slider("Maximum calories per serving", 100, 1000, 700, 50)
        min_protein = st.slider("Minimum protein (g)", 0, 50, 5, 1)
    if st.button("✨ Recommend Healthy Foods", type="primary", use_container_width=True):
        picks = recommend_healthy_food(
            foods, budget=budget, diet=diet, goal=goal,
            max_calories=max_calories, min_protein=min_protein,
        )
        if not picks:
            st.warning("No dishes match all these filters. Try increasing your budget/calorie limit or lowering protein.")
        else:
            st.subheader("Your suggested dishes")
            for food in picks:
                with st.container(border=True):
                    left, right = st.columns([4, 1])
                    with left:
                        st.markdown(f"**{food['name']}** · ₹{float(food['price']):.0f}")
                        st.caption(f"{food['category']} · {food.get('diet_type', 'Vegetarian')}")
                        st.caption(nutrition_line(food))
                        if food.get("description"):
                            st.write(food["description"])
                    with right:
                        if st.button("Add", key=f"healthy_add_{food['id']}"):
                            add_to_cart(food, 1)
                            st.success("Added to cart.")
    st.caption("This is a transparent, rule-based recommendation feature built in Python, not a live external AI model.")
    st.caption("Nutrition figures are approximate estimates per serving, not medical or lab-verified data.")

elif page == "🛒 My Cart":
    st.title("🛒 Your Shopping Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty. Visit Order Food to get started.")
    else:
        for name, item in list(st.session_state.cart.items()):
            with st.container(border=True):
                left, middle, right = st.columns([3, 2, 1])
                with left:
                    st.write(f"**{item['name']}**")
                    st.caption(f"₹{item['price']:.0f} per item")
                with middle:
                    st.write(f"Quantity: {item['quantity']}")
                    st.write(f"Subtotal: ₹{item['price'] * item['quantity']:.0f}")
                with right:
                    if st.button("Remove", key=f"remove_{name}"):
                        del st.session_state.cart[name]
                        st.rerun()
        st.divider()
        st.subheader(f"Total: ₹{cart_total():.0f}")
        with st.form("checkout_form"):
            student_name = st.text_input("Full name", value=st.session_state.student_name)
            student_id = st.text_input("Student ID", value=st.session_state.student_id)
            pickup_time = st.selectbox("Pickup time", [
                "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
                "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
            ])
            submitted = st.form_submit_button("✅ Place Order", use_container_width=True)
        if submitted:
            try:
                order_id = place_order(
                    student_name, student_id,
                    list(st.session_state.cart.values()), pickup_time,
                )
                st.session_state.student_name = student_name.strip()
                st.session_state.student_id = student_id.strip()
                st.session_state.cart = {}
                st.success("Order placed successfully!")
                st.markdown(f"## Order number: #{order_id}")
                st.write(f"Pickup time: {pickup_time}")
                st.write("Order status: Received")
            except ValueError as error:
                st.error(str(error))

elif page == "🧑‍🍳 Admin Dashboard":
    if not st.session_state.admin_logged_in:
        st.error("Please log in as an admin.")
        st.stop()
    st.title("🧑‍🍳 Canteen Admin Dashboard")
    col1, col2 = st.columns(2)
    col1.metric("Total Orders", get_order_count())
    col2.metric("Total Order Value", f"₹{get_total_sales():.0f}")
    st.divider()
    st.subheader("Add a new food item")
    categories = [
        "Chinese Rice & Noodles", "Indian Rice & Biryani", "Rolls & Wraps",
        "Café & Drinks", "Acai & Yogurt Bowls", "Tofu Starters",
        "Quinoa & Dosa", "Dosa & South Indian", "Fresh Fruits & Eggs",
        "Healthy Picks", "Snacks", "Meals", "Drinks", "Other",
    ]
    with st.form("add_food_form"):
        new_name = st.text_input("Food name")
        new_price = st.number_input("Price (₹)", min_value=1, max_value=10000, value=100)
        new_category = st.selectbox("Category", categories)
        new_description = st.text_input("Short description")
        new_calories = st.number_input("Calories per serving (kcal)", min_value=0, max_value=3000, value=350)
        new_protein = st.number_input("Protein (g)", min_value=0.0, max_value=200.0, value=10.0, step=1.0)
        new_carbs = st.number_input("Carbohydrates (g)", min_value=0.0, max_value=300.0, value=45.0, step=1.0)
        new_diet = st.selectbox("Diet type", ["Vegetarian", "Vegan", "Egg", "Non-vegetarian"])
        add_submitted = st.form_submit_button("Add Food Item")
    if add_submitted:
        try:
            create_menu_item(
                new_name, float(new_price), new_category,
                calories=int(new_calories), protein=float(new_protein),
                carbs=float(new_carbs), diet_type=new_diet,
                description=new_description,
            )
            st.success("Food item added.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            if "UNIQUE constraint failed" in str(error):
                st.error("A food item with that name already exists.")
            else:
                st.error(f"Could not add item: {error}")

    st.subheader("Edit Existing Items")
    for food in show_all_menu_items():
        with st.expander(food["name"]):
            with st.form(f"edit_food_{food['id']}"):
                edit_name = st.text_input("Name", value=food["name"])
                edit_price = st.number_input("Price (₹)", min_value=1, max_value=10000,
                                             value=max(1, int(food["price"])), key=f"price_{food['id']}")
                edit_category = st.selectbox("Category", categories,
                    index=categories.index(food["category"]) if food["category"] in categories else categories.index("Other"),
                    key=f"category_{food['id']}")
                edit_available = st.checkbox("Available for ordering", value=bool(food["available"]),
                                             key=f"available_{food['id']}")
                edit_calories = st.number_input("Calories", min_value=0, max_value=3000,
                    value=int(food.get("calories") or 0), key=f"calories_{food['id']}")
                edit_protein = st.number_input("Protein (g)", min_value=0.0, max_value=200.0,
                    value=float(food.get("protein") or 0), key=f"protein_{food['id']}")
                edit_carbs = st.number_input("Carbs (g)", min_value=0.0, max_value=300.0,
                    value=float(food.get("carbs") or 0), key=f"carbs_{food['id']}")
                edit_diet = st.selectbox("Diet type", ["Vegetarian", "Vegan", "Egg", "Non-vegetarian"],
                    index=(["Vegetarian", "Vegan", "Egg", "Non-vegetarian"].index(food["diet_type"])
                           if food.get("diet_type") in ["Vegetarian", "Vegan", "Egg", "Non-vegetarian"] else 0),
                    key=f"diet_{food['id']}")
                edit_description = st.text_input("Description", value=food.get("description", ""),
                                                 key=f"description_{food['id']}")
                save_item = st.form_submit_button("Save Changes")
            if save_item:
                try:
                    edit_menu_item(food["id"], edit_name, float(edit_price), edit_category,
                                   edit_available, int(edit_calories), float(edit_protein),
                                   float(edit_carbs), edit_diet, edit_description)
                    st.success("Menu item updated.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not update item: {error}")

    st.divider()
    st.subheader("Incoming Orders")
    all_orders = get_all_orders()
    if not all_orders:
        st.info("No orders have been placed yet.")
    else:
        statuses = ["Received", "Preparing", "Ready", "Completed", "Cancelled"]
        for order in all_orders:
            with st.container(border=True):
                st.markdown(f"### Order #{order['id']}")
                st.write(f"**Student:** {order['student_name']} · **Student ID:** {order['student_id']}")
                st.write(f"**Items:** {order['items']}")
                st.write(f"**Total:** ₹{order['total']:.0f}")
                st.write(f"**Pickup:** {order['pickup_time']} · **Placed:** {order['created_at']}")
                current = order["status"] if order["status"] in statuses else "Received"
                new_status = st.selectbox("Order status", statuses, index=statuses.index(current),
                                          key=f"status_{order['id']}")
                if st.button("Update Status", key=f"update_{order['id']}"):
                    update_order_status(order["id"], new_status)
                    st.success("Order status updated.")
                    st.rerun()

st.divider()
st.caption("Campus Bites | Student Creative Coding Project")
