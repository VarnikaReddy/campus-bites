from database import setup_database, get_menu
from menu import create_menu_item

# Nutrition figures are approximate estimates per serving, not lab-tested values.
# Format: name, price, category, calories, protein_g, carbs_g, diet_type, description
FOOD_ITEMS = [
    # Chinese rice and noodles
    ("Veg Schezwan Fried Rice", 110, "Chinese Rice & Noodles", 460, 10, 72, "Vegan", "Spicy vegetable fried rice"),
    ("Egg Fried Rice", 120, "Chinese Rice & Noodles", 480, 16, 70, "Egg", "Fried rice with egg"),
    ("Chicken Fried Rice", 150, "Chinese Rice & Noodles", 520, 28, 68, "Non-vegetarian", "Chicken and vegetable fried rice"),
    ("Paneer Fried Rice", 140, "Chinese Rice & Noodles", 540, 19, 70, "Vegetarian", "Fried rice with paneer"),
    ("Mushroom Fried Rice", 130, "Chinese Rice & Noodles", 430, 10, 67, "Vegan", "Mushroom and vegetable rice"),
    ("Chilli Garlic Veg Noodles", 110, "Chinese Rice & Noodles", 440, 10, 68, "Vegan", "Garlic noodles with vegetables"),
    ("Hakka Veg Noodles", 100, "Chinese Rice & Noodles", 420, 9, 65, "Vegan", "Classic vegetable Hakka noodles"),
    ("Schezwan Noodles", 120, "Chinese Rice & Noodles", 460, 10, 70, "Vegan", "Hot Schezwan noodles"),
    ("Egg Hakka Noodles", 125, "Chinese Rice & Noodles", 480, 16, 67, "Egg", "Hakka noodles with egg"),
    ("Chicken Hakka Noodles", 155, "Chinese Rice & Noodles", 520, 27, 66, "Non-vegetarian", "Noodles with chicken"),
    ("Mushroom Garlic Noodles", 130, "Chinese Rice & Noodles", 430, 11, 65, "Vegan", "Garlic noodles with mushrooms"),

    # Indian rice and biryani
    ("Veg Biryani", 120, "Indian Rice & Biryani", 470, 10, 76, "Vegetarian", "Vegetable biryani with spices"),
    ("Paneer Biryani", 150, "Indian Rice & Biryani", 560, 19, 78, "Vegetarian", "Paneer and basmati rice"),
    ("Egg Biryani", 140, "Indian Rice & Biryani", 520, 19, 75, "Egg", "Biryani with boiled egg"),
    ("Chicken Biryani", 180, "Indian Rice & Biryani", 600, 32, 78, "Non-vegetarian", "Chicken dum biryani"),
    ("Ghee Rice", 100, "Indian Rice & Biryani", 390, 6, 62, "Vegetarian", "Fragrant rice cooked with ghee"),
    ("Jeera Rice", 90, "Indian Rice & Biryani", 330, 6, 58, "Vegetarian", "Cumin tempered rice"),
    ("Lemon Rice", 80, "Indian Rice & Biryani", 320, 6, 54, "Vegan", "South Indian lemon rice"),
    ("Tomato Rice", 85, "Indian Rice & Biryani", 340, 7, 59, "Vegan", "Tangy tomato rice"),
    ("Curd Rice", 75, "Indian Rice & Biryani", 300, 9, 48, "Vegetarian", "Cooling yogurt rice"),
    ("Peas Pulao", 100, "Indian Rice & Biryani", 360, 9, 62, "Vegan", "Basmati rice with peas"),

    # Rolls and wraps
    ("Veg Kathi Roll", 90, "Rolls & Wraps", 360, 10, 52, "Vegetarian", "Vegetable filling in a wrap"),
    ("Paneer Tikka Roll", 130, "Rolls & Wraps", 440, 20, 48, "Vegetarian", "Paneer tikka wrap"),
    ("Mushroom Roll", 110, "Rolls & Wraps", 350, 11, 49, "Vegan", "Spiced mushroom wrap"),
    ("Tofu Roll", 120, "Rolls & Wraps", 380, 19, 48, "Vegan", "Tofu and salad wrap"),
    ("Egg Roll", 90, "Rolls & Wraps", 340, 14, 42, "Egg", "Egg wrapped in a flatbread"),
    ("Double Egg Roll", 110, "Rolls & Wraps", 410, 20, 43, "Egg", "Double egg flatbread roll"),
    ("Chicken Roll", 140, "Rolls & Wraps", 430, 28, 46, "Non-vegetarian", "Chicken wrap with vegetables"),
    ("Spicy Chicken Roll", 150, "Rolls & Wraps", 460, 29, 48, "Non-vegetarian", "Spiced chicken wrap"),

    # Cafe and drinks
    ("Hot Chocolate", 90, "Café & Drinks", 280, 9, 42, "Vegetarian", "Warm chocolate milk"),
    ("Cold Mocha", 110, "Café & Drinks", 260, 7, 38, "Vegetarian", "Iced coffee and chocolate"),
    ("Iced Latte", 100, "Café & Drinks", 150, 8, 15, "Vegetarian", "Chilled espresso with milk"),
    ("Classic Hot Coffee", 45, "Café & Drinks", 80, 4, 8, "Vegetarian", "Hot coffee with milk"),
    ("Iced Chocolate", 100, "Café & Drinks", 250, 7, 39, "Vegetarian", "Cold chocolate drink"),
    ("Cold Brew Coffee", 90, "Café & Drinks", 10, 0, 2, "Vegan", "Chilled brewed coffee"),
    ("Banana Smoothie", 90, "Café & Drinks", 210, 8, 34, "Vegetarian", "Banana blended with milk"),
    ("Mango Smoothie", 100, "Café & Drinks", 230, 7, 39, "Vegetarian", "Mango and yogurt smoothie"),

    # Acai and yogurt bowls
    ("Berry Acai Bowl", 180, "Acai & Yogurt Bowls", 320, 8, 52, "Vegan", "Acai, berries and granola"),
    ("Banana Peanut Butter Yogurt Bowl", 150, "Acai & Yogurt Bowls", 390, 18, 44, "Vegetarian", "Yogurt, banana and peanut butter"),
    ("Mango Coconut Yogurt Bowl", 150, "Acai & Yogurt Bowls", 330, 11, 48, "Vegetarian", "Mango, yogurt and coconut"),
    ("Chocolate Banana Yogurt Bowl", 160, "Acai & Yogurt Bowls", 380, 13, 53, "Vegetarian", "Yogurt, banana and cocoa"),
    ("Strawberry Granola Yogurt Bowl", 150, "Acai & Yogurt Bowls", 310, 12, 45, "Vegetarian", "Strawberries, yogurt and granola"),

    # Tofu starters
    ("Chilli Tofu", 140, "Tofu Starters", 290, 20, 24, "Vegan", "Tofu tossed with chilli and peppers"),
    ("Crispy Tofu Bites", 130, "Tofu Starters", 340, 18, 30, "Vegan", "Crispy tofu bites"),
    ("Sesame Tofu", 145, "Tofu Starters", 310, 21, 25, "Vegan", "Tofu with sesame sauce"),
    ("Pepper Garlic Tofu", 135, "Tofu Starters", 260, 21, 16, "Vegan", "Tofu with pepper and garlic"),
    ("Tofu Satay", 150, "Tofu Starters", 320, 22, 22, "Vegan", "Grilled tofu with peanut dip"),

    # Quinoa, dosa, healthy bowls
    ("Vegetable Quinoa Bowl", 160, "Quinoa & Dosa", 380, 13, 58, "Vegan", "Quinoa with roasted vegetables"),
    ("Chickpea Quinoa Salad", 150, "Quinoa & Dosa", 360, 15, 52, "Vegan", "Quinoa, chickpeas and fresh vegetables"),
    ("Grilled Chicken Quinoa Bowl", 210, "Quinoa & Dosa", 450, 38, 42, "Non-vegetarian", "Quinoa bowl with grilled chicken"),
    ("Quinoa Upma", 120, "Quinoa & Dosa", 300, 10, 45, "Vegan", "Quinoa cooked with vegetables"),
    ("Amaranth Dosa", 90, "Dosa & South Indian", 280, 9, 44, "Vegan", "Dosa made with amaranth flour"),
    ("Ragi Dosa", 80, "Dosa & South Indian", 260, 7, 43, "Vegan", "Finger millet dosa"),
    ("Paneer Protein Bowl", 170, "Healthy Picks", 420, 27, 38, "Vegetarian", "Paneer, grains and vegetables"),
    ("Grilled Chicken Salad", 190, "Healthy Picks", 330, 35, 18, "Non-vegetarian", "Grilled chicken and fresh salad"),
    ("Tofu Power Bowl", 160, "Healthy Picks", 390, 24, 42, "Vegan", "Tofu, vegetables and brown rice"),
    ("Sprouts Chaat Bowl", 80, "Healthy Picks", 220, 13, 34, "Vegan", "Mixed sprouts with lemon and spices"),
    ("Moong Dal Chilla", 90, "Healthy Picks", 240, 15, 32, "Vegan", "Protein-rich lentil pancakes"),

    # Fresh fruit and eggs
    ("Boiled Egg (1 piece)", 15, "Fresh Fruits & Eggs", 78, 6, 1, "Egg", "One boiled egg"),
    ("Boiled Egg Whites (2)", 20, "Fresh Fruits & Eggs", 34, 7, 0, "Egg", "Two boiled egg whites"),
    ("Seasonal Fruit Cup", 70, "Fresh Fruits & Eggs", 120, 2, 30, "Vegan", "Fresh seasonal fruit pieces"),
    ("Mixed Fruit Bowl", 100, "Fresh Fruits & Eggs", 180, 3, 42, "Vegan", "Mixed fresh fruit bowl"),
    ("Banana and Apple Bowl", 80, "Fresh Fruits & Eggs", 160, 2, 41, "Vegan", "Fresh banana and apple"),
]


def main():
    setup_database()
    existing_names = {
        item["name"].strip().casefold()
        for item in get_menu(available_only=False)
    }

    added = 0
    skipped = 0
    for item in FOOD_ITEMS:
        name = item[0]
        if name.strip().casefold() in existing_names:
            print(f"Skipped existing item: {name}")
            skipped += 1
            continue
        try:
            create_menu_item(*item[:3], calories=item[3], protein=item[4],
                             carbs=item[5], diet_type=item[6], description=item[7])
            existing_names.add(name.strip().casefold())
            print(f"Added: {name} - Rs. {item[1]}")
            added += 1
        except Exception as error:
            print(f"Could not add {name}: {error}")

    print(f"\nFinished. Added {added}; skipped {skipped} existing items.")
    print("Nutrition values are approximate estimates per serving.")


if __name__ == "__main__":
    main()
