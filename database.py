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
                ("Veg Sandwich", 50, "Snacks", 1, 280, 9, 38, "Vegetarian", "Fresh vegetable sandwich"),
                ("Masala Dosa", 60, "Dosa & South Indian", 1, 350, 7, 55, "Vegetarian", "Crispy dosa with spiced potato"),
                ("Veg Burger", 80, "Snacks", 1, 390, 10, 48, "Vegetarian", "Vegetable patty burger"),
                ("Cold Coffee", 40, "Café & Drinks", 1, 220, 6, 32, "Vegetarian", "Chilled coffee with milk"),
                ("French Fries", 70, "Snacks", 1, 320, 4, 42, "Vegetarian", "Crispy potato fries"),
                ("Idli Sambar", 40, "Dosa & South Indian", 1, 260, 8, 48, "Vegetarian", "Steamed idli with sambar"),
                ("Veg Fried Rice", 90, "Chinese Rice & Noodles", 1, 420, 9, 68, "Vegetarian", "Vegetable fried rice"),
                ("Lemon Juice", 30, "Café & Drinks", 1, 90, 0, 22, "Vegan", "Fresh lemon drink"),
            ]
            connection.executemany("""
                INSERT INTO menu
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
