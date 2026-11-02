import sqlite3
from pathlib import Path

DATA_FOLDER = Path(__file__).parent / "data"
DATA_FOLDER.mkdir(exist_ok=True)
DATABASE_PATH = DATA_FOLDER / "canteen.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():
    """Create tables and safely add nutrition columns to older databases."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                available INTEGER DEFAULT 1
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                items TEXT NOT NULL,
                total REAL NOT NULL,
                pickup_time TEXT NOT NULL,
                status TEXT DEFAULT 'Received',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(menu)").fetchall()
        }
        nutrition_columns = {
            "calories": "INTEGER NOT NULL DEFAULT 0",
            "protein": "REAL NOT NULL DEFAULT 0",
            "carbs": "REAL NOT NULL DEFAULT 0",
            "diet_type": "TEXT NOT NULL DEFAULT 'Vegetarian'",
            "description": "TEXT NOT NULL DEFAULT ''",
        }
        for column, definition in nutrition_columns.items():
            if column not in columns:
                connection.execute(
                    f"ALTER TABLE menu ADD COLUMN {column} {definition}"
                )

        existing = connection.execute("SELECT COUNT(*) FROM menu").fetchone()[0]
        if existing == 0:
            initial_menu = [
    # Keep your existing 8 menu items here

    ("Veg Schezwan Fried Rice", 110, "Chinese Rice & Noodles", 1, 460, 10, 72, "Vegan", "Spicy vegetable fried rice"),
    ("Egg Fried Rice", 120, "Chinese Rice & Noodles", 1, 480, 16, 70, "Egg", "Fried rice with egg"),
    ("Chicken Fried Rice", 150, "Chinese Rice & Noodles", 1, 520, 28, 68, "Non-vegetarian", "Chicken and vegetable fried rice"),
    ("Paneer Fried Rice", 140, "Chinese Rice & Noodles", 1, 540, 19, 70, "Vegetarian", "Fried rice with paneer"),
    ("Mushroom Fried Rice", 130, "Chinese Rice & Noodles", 1, 430, 10, 67, "Vegan", "Mushroom and vegetable rice"),

    ("Chicken Biryani", 180, "Indian Rice & Biryani", 1, 600, 32, 78, "Non-vegetarian", "Chicken dum biryani"),
    ("Veg Biryani", 120, "Indian Rice & Biryani", 1, 470, 10, 76, "Vegetarian", "Vegetable biryani"),
    ("Paneer Biryani", 150, "Indian Rice & Biryani", 1, 560, 19, 78, "Vegetarian", "Paneer and basmati rice"),
    ("Egg Biryani", 140, "Indian Rice & Biryani", 1, 520, 19, 75, "Egg", "Biryani with boiled egg"),

    ("Paneer Tikka Roll", 130, "Rolls & Wraps", 1, 440, 20, 48, "Vegetarian", "Paneer tikka wrap"),
    ("Chicken Roll", 140, "Rolls & Wraps", 1, 430, 28, 46, "Non-vegetarian", "Chicken wrap with vegetables"),
    ("Egg Roll", 90, "Rolls & Wraps", 1, 340, 14, 42, "Egg", "Egg wrapped in flatbread"),
    ("Tofu Roll", 120, "Rolls & Wraps", 1, 380, 19, 48, "Vegan", "Tofu and salad wrap"),

    ("Grilled Chicken Salad", 190, "Healthy Picks", 1, 330, 35, 18, "Non-vegetarian", "Grilled chicken and fresh salad"),
    ("Paneer Protein Bowl", 170, "Healthy Picks", 1, 420, 27, 38, "Vegetarian", "Paneer, grains and vegetables"),
    ("Tofu Power Bowl", 160, "Healthy Picks", 1, 390, 24, 42, "Vegan", "Tofu, vegetables and brown rice"),
    ("Sprouts Chaat Bowl", 80, "Healthy Picks", 1, 220, 13, 34, "Vegan", "Mixed sprouts with lemon and spices"),
    ("Moong Dal Chilla", 90, "Healthy Picks", 1, 240, 15, 32, "Vegan", "Protein-rich lentil pancakes"),

    ("Hot Chocolate", 90, "Café & Drinks", 1, 280, 9, 42, "Vegetarian", "Warm chocolate milk"),
    ("Cold Mocha", 110, "Café & Drinks", 1, 260, 7, 38, "Vegetarian", "Iced coffee and chocolate"),
    ("Iced Latte", 100, "Café & Drinks", 1, 150, 8, 15, "Vegetarian", "Chilled espresso with milk"),
    ("Banana Smoothie", 90, "Café & Drinks", 1, 210, 8, 34, "Vegetarian", "Banana blended with milk"),
    ("Mango Smoothie", 100, "Café & Drinks", 1, 230, 7, 39, "Vegetarian", "Mango and yogurt smoothie"),

    ("Chilli Tofu", 140, "Tofu Starters", 1, 290, 20, 24, "Vegan", "Tofu tossed with chilli and peppers"),
    ("Crispy Tofu Bites", 130, "Tofu Starters", 1, 340, 18, 30, "Vegan", "Crispy tofu bites"),
    ("Sesame Tofu", 145, "Tofu Starters", 1, 310, 21, 25, "Vegan", "Tofu with sesame sauce"),

    ("Vegetable Quinoa Bowl", 160, "Quinoa & Dosa", 1, 380, 13, 58, "Vegan", "Quinoa with roasted vegetables"),
    ("Chickpea Quinoa Salad", 150, "Quinoa & Dosa", 1, 360, 15, 52, "Vegan", "Quinoa, chickpeas and fresh vegetables"),
    ("Grilled Chicken Quinoa Bowl", 210, "Quinoa & Dosa", 1, 450, 38, 42, "Non-vegetarian", "Quinoa bowl with grilled chicken"),

    ("Boiled Egg (1 piece)", 15, "Fresh Fruits & Eggs", 1, 78, 6, 1, "Egg", "One boiled egg"),
    ("Boiled Egg Whites (2)", 20, "Fresh Fruits & Eggs", 1, 34, 7, 0, "Egg", "Two boiled egg whites"),
    ("Seasonal Fruit Cup", 70, "Fresh Fruits & Eggs", 1, 120, 2, 30, "Vegan", "Fresh seasonal fruit pieces"),
    ("Mixed Fruit Bowl", 100, "Fresh Fruits & Eggs", 1, 180, 3, 42, "Vegan", "Mixed fresh fruit bowl"),
]

connection.executemany("""
    INSERT OR IGNORE INTO menu
    (name, price, category, available, calories, protein, carbs, diet_type, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", initial_menu)


def get_menu(available_only=True):
    with get_connection() as connection:
        if available_only:
            rows = connection.execute(
                "SELECT * FROM menu WHERE available = 1 ORDER BY category, name"
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM menu ORDER BY category, name"
            ).fetchall()
    return [dict(row) for row in rows]


def add_menu_item(name, price, category, calories=0, protein=0, carbs=0,
                  diet_type="Vegetarian", description=""):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO menu
            (name, price, category, available, calories, protein, carbs, diet_type, description)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
        """, (name.strip(), price, category, calories, protein, carbs, diet_type, description))


def update_menu_item(item_id, name, price, category, available,
                     calories=None, protein=None, carbs=None,
                     diet_type=None, description=None):
    with get_connection() as connection:
        if calories is None:
            connection.execute("""
                UPDATE menu SET name=?, price=?, category=?, available=? WHERE id=?
            """, (name.strip(), price, category, int(available), item_id))
        else:
            connection.execute("""
                UPDATE menu
                SET name=?, price=?, category=?, available=?, calories=?, protein=?,
                    carbs=?, diet_type=?, description=?
                WHERE id=?
            """, (name.strip(), price, category, int(available), calories, protein,
                  carbs, diet_type or "Vegetarian", description or "", item_id))


def set_menu_availability(item_id, available):
    with get_connection() as connection:
        connection.execute(
            "UPDATE menu SET available = ? WHERE id = ?",
            (int(available), item_id)
        )
