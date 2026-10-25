
from database import get_connection


def place_order(student_name, student_id, cart, pickup_time):
    student_name = student_name.strip()
    student_id = student_id.strip()

    if not student_name or not student_id:
        raise ValueError("Enter your name and student ID.")

    if not cart:
        raise ValueError("Your cart is empty.")

    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    if total <= 0:
        raise ValueError("Order total must be positive.")

    order_items = "; ".join(
        f'{item["name"]} x {item["quantity"]}'
        for item in cart
    )

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO orders (
                student_name, student_id, items,
                total, pickup_time, status
            )
            VALUES (?, ?, ?, ?, ?, 'Received')
        """, (
            student_name,
            student_id,
            order_items,
            total,
            pickup_time
        ))

        return cursor.lastrowid


def get_all_orders():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM orders ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def update_order_status(order_id, new_status):
    allowed_statuses = [
        "Received",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    with get_connection() as connection:
        connection.execute("""
            UPDATE orders SET status = ? WHERE id = ?
        """, (new_status, order_id))


def get_order_count():
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]


def get_total_sales():
    with get_connection() as connection:
        return connection.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM orders
            WHERE status != 'Cancelled'
        """).fetchone()[0]