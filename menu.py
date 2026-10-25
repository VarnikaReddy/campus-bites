from database import get_menu, add_menu_item, update_menu_item


def show_menu():
    return get_menu(available_only=True)


def show_all_menu_items():
    return get_menu(available_only=False)


def create_menu_item(name, price, category, calories=0, protein=0, carbs=0,
                     diet_type="Vegetarian", description=""):
    if not name or not name.strip():
        raise ValueError("Food name cannot be empty.")
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    if min(float(calories), float(protein), float(carbs)) < 0:
        raise ValueError("Nutrition values cannot be negative.")
    add_menu_item(name, price, category, int(calories), float(protein),
                  float(carbs), diet_type, description)


def edit_menu_item(item_id, name, price, category, available,
                   calories=None, protein=None, carbs=None,
                   diet_type=None, description=None):
    if not name or not name.strip():
        raise ValueError("Food name cannot be empty.")
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    update_menu_item(item_id, name, price, category, available,
                     calories, protein, carbs, diet_type, description)
