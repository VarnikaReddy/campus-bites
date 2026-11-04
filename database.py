
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

        # Create menu table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                available INTEGER DEFAULT 1
            )
        """)

        # Create orders table
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

        # Check existing menu columns
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(menu)"
            ).fetchall()
        }

        # Add nutrition columns to older databases
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

        # Check whether menu items already exist
        existing = connection.execute(
            "SELECT COUNT(*) FROM menu"
        ).fetchone()[0]

        # Insert initial menu items only if the menu is empty
        if existing == 0:

            initial_menu = [

               
                # Café & Drinks
                ("Hot Chocolate", 90, "Café & Drinks", 1, 280, 9, 42, "Vegetarian", "Warm chocolate milk"),
                ("Cold Mocha", 110, "Café & Drinks", 1, 260, 7, 38, "Vegetarian", "Iced coffee and chocolate"),
                ("Iced Latte", 100, "Café & Drinks", 1, 150, 8, 15, "Vegetarian", "Chilled espresso with milk"),
                ("Banana Smoothie", 90, "Café & Drinks", 1, 210, 8, 34, "Vegetarian", "Banana blended with milk"),
                ("Mango Smoothie", 100, "Café & Drinks", 1, 230, 7, 39, "Vegetarian", "Mango and yogurt smoothie"),
                
                # Acai and yogurt bowls
                ("Berry Acai Bowl", 180, "Acai & Yogurt Bowls", 320, 8, 52, "Vegan", "Acai, berries and granola"),
                ("Banana Peanut Butter Yogurt Bowl", 150, "Acai & Yogurt Bowls", 390, 18, 44, "Vegetarian", "Yogurt, banana and peanut butter"),
                ("Mango Coconut Yogurt Bowl", 150, "Acai & Yogurt Bowls", 330, 11, 48, "Vegetarian", "Mango, yogurt and coconut"),
                ("Chocolate Banana Yogurt Bowl", 160, "Acai & Yogurt Bowls", 380, 13, 53, "Vegetarian", "Yogurt, banana and cocoa"),
                ("Strawberry Granola Yogurt Bowl", 150, "Acai & Yogurt Bowls", 310, 12, 45, "Vegetarian", "Strawberries, yogurt and granola"),
                

                # Rolls and wraps
                   ("Veg Kathi Roll", 90, "Rolls & Wraps", 360, 10, 52, "Vegetarian", "Vegetable filling in a wrap"),
                   ("Paneer Tikka Roll", 130, "Rolls & Wraps", 440, 20, 48, "Vegetarian", "Paneer tikka wrap"),
                   ("Mushroom Roll", 110, "Rolls & Wraps", 350, 11, 49, "Vegan", "Spiced mushroom wrap"),
                   ("Tofu Roll", 120, "R3olls & Wraps", 380, 19, 48, "Vegan", "Tofu and salad wrap"),
                   ("Egg Roll", 90, "Rolls & Wraps", 340, 14, 42, "Egg", "Egg wrapped in a flatbread"),
                   ("Double Egg Roll", 110, "Rolls & Wraps", 410, 20, 43, "Egg", "Double egg flatbread roll"),
                   ("Chicken Roll", 140, "Rolls & Wraps", 430, 28, 46, "Non-vegetarian", "Chicken wrap with vegetables"),
                   ("Spicy Chicken Roll", 150, "Rolls & Wraps", 460, 29, 48, "Non-vegetarian", "Spiced chicken wrap"),

                # Healthy Picks
                ("Grilled Chicken Salad", 190, "Healthy Picks", 1, 330, 35, 18, "Non-vegetarian", "Grilled chicken and fresh salad"),
                ("Paneer Protein Bowl", 170, "Healthy Picks", 1, 420, 27, 38, "Vegetarian", "Paneer, grains and vegetables"),
                ("Tofu Power Bowl", 160, "Healthy Picks", 1, 390, 24, 42, "Vegan", "Tofu, vegetables and brown rice"),
                ("Sprouts Chaat Bowl", 80, "Healthy Picks", 1, 220, 13, 34, "Vegan", "Mixed sprouts with lemon and spices"),
                ("Moong Dal Chilla", 90, "Healthy Picks", 1, 240, 15, 32, "Vegan", "Protein-rich lentil pancakes"),

                

                # Tofu Starters
                ("Chilli Tofu", 140, "Tofu Starters", 1, 290, 20, 24, "Vegan", "Tofu tossed with chilli and peppers"),
                ("Crispy Tofu Bites", 130, "Tofu Starters", 1, 340, 18, 30, "Vegan", "Crispy tofu bites"),
                ("Sesame Tofu", 145, "Tofu Starters", 1, 310, 21, 25, "Vegan", "Tofu with sesame sauce"),

                # Quinoa & Dosa
                ("Vegetable Quinoa Bowl", 160, "Quinoa & Dosa", 1, 380, 13, 58, "Vegan", "Quinoa with roasted vegetables"),
                ("Chickpea Quinoa Salad", 150, "Quinoa & Dosa", 1, 360, 15, 52, "Vegan", "Quinoa, chickpeas and fresh vegetables"),
                ("Grilled Chicken Quinoa Bowl", 210, "Quinoa & Dosa", 1, 450, 38, 42, "Non-vegetarian", "Quinoa bowl with grilled chicken"),

                 # Fresh fruit and eggs
                    ("Boiled Egg (1 piece)", 15, "Fresh Fruits & Eggs", 78, 6, 1, "Egg", "One boiled egg"),
                    ("Boiled Egg Whites (2)", 20, "Fresh Fruits & Eggs", 34, 7, 0, "Egg", "Two boiled egg whites"),
                    ("Seasonal Fruit Cup", 70, "Fresh Fruits & Eggs", 120, 2, 30, "Vegan", "Fresh seasonal fruit pieces"),
                    ("Mixed Fruit Bowl", 100, "Fresh Fruits & Eggs", 180, 3, 42, "Vegan", "Mixed fresh fruit bowl"),
                    ("Banana and Apple Bowl", 80, "Fresh Fruits & Eggs", 160, 2, 41, "Vegan", "Fresh banana and apple"),

                 # Chinese Rice & Noodles
                ("Veg Schezwan Fried Rice", 110, "Chinese Rice & Noodles", 1, 460, 10, 72, "Vegan", "Spicy vegetable fried rice"),
                ("Egg Fried Rice", 120, "Chinese Rice & Noodles", 1, 480, 16, 70, "Egg", "Fried rice with egg"),
                ("Chicken Fried Rice", 150, "Chinese Rice & Noodles", 1, 520, 28, 68, "Non-vegetarian", "Chicken and vegetable fried rice"),
                ("Paneer Fried Rice", 140, "Chinese Rice & Noodles", 1, 540, 19, 70, "Vegetarian", "Paneer fried rice"),
                ("Mushroom Fried Rice", 130, "Chinese Rice & Noodles", 1, 430, 10, 67, "Vegan", "Mushroom and vegetable rice"),
                
                # Indian Rice & Biryani
                ("Chicken Biryani", 180, "Indian Rice & Biryani", 1, 600, 32, 78, "Non-vegetarian", "Chicken dum biryani"),
                ("Veg Biryani", 120, "Indian Rice & Biryani", 1, 470, 10, 76, "Vegetarian", "Vegetable biryani"),
                ("Paneer Biryani", 150, "Indian Rice & Biryani", 1, 560, 19, 78, "Vegetarian", "Paneer and basmati rice"),
                ("Egg Biryani", 140, "Indian Rice & Biryani", 1, 520, 19, 75, "Egg", "Biryani with boiled egg"),
                
            ]

            connection.executemany("""
                INSERT OR IGNORE INTO menu
                (
                    name,
                    price,
                    category,
                    available,
                    calories,
                    protein,
                    carbs,
                    diet_type,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, initial_menu)


def get_menu(available_only=True):
    """Retrieve menu items."""

    with get_connection() as connection:

        if available_only:
            rows = connection.execute("""
                SELECT *
                FROM menu
                WHERE available = 1
                ORDER BY category, name
            """).fetchall()

        else:
            rows = connection.execute("""
                SELECT *
                FROM menu
                ORDER BY category, name
            """).fetchall()

    return [dict(row) for row in rows]


def add_menu_item(
    name,
    price,
    category,
    calories=0,
    protein=0,
    carbs=0,
    diet_type="Vegetarian",
    description=""
):
    """Add a new menu item."""

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO menu
            (
                name,
                price,
                category,
                available,
                calories,
                protein,
                carbs,
                diet_type,
                description
            )
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
        """, (
            name.strip(),
            price,
            category,
            calories,
            protein,
            carbs,
            diet_type,
            description
        ))


def update_menu_item(
    item_id,
    name,
    price,
    category,
    available,
    calories=None,
    protein=None,
    carbs=None,
    diet_type=None,
    description=None
):
    """Update an existing menu item."""

    with get_connection() as connection:

        if calories is None:

            connection.execute("""
                UPDATE menu
                SET name = ?,
                    price = ?,
                    category = ?,
                    available = ?
                WHERE id = ?
            """, (
                name.strip(),
                price,
                category,
                int(available),
                item_id
            ))

        else:

            connection.execute("""
                UPDATE menu
                SET name = ?,
                    price = ?,
                    category = ?,
                    available = ?,
                    calories = ?,
                    protein = ?,
                    carbs = ?,
                    diet_type = ?,
                    description = ?
                WHERE id = ?
            """, (
                name.strip(),
                price,
                category,
                int(available),
                calories,
                protein,
                carbs,
                diet_type or "Vegetarian",
                description or "",
                item_id
            ))


def set_menu_availability(item_id, available):
    """Update menu item availability."""

    with get_connection() as connection:
        connection.execute("""
            UPDATE menu
            SET available = ?
            WHERE id = ?
        """, (
            int(available),
            item_id
        ))

