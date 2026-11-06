import re
from datetime import datetime, timedelta

from database import get_connection


# --------------------------------------------------
# STUDENT ID VALIDATION
# --------------------------------------------------

def is_valid_student_id(student_id):
    """
    Valid format:
    1RVU + 2 digit batch + BSC + 3 digit roll number

    Example: 1RVU23BSC013
    """

    pattern = r"^1RVU\d{2}BSC\d{3}$"

    return bool(
        re.fullmatch(pattern, student_id.strip().upper())
    )


# --------------------------------------------------
# STUDENT DATABASE
# --------------------------------------------------

def setup_student_table(connection):

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            missed_pickups INTEGER DEFAULT 0,
            suspended_until TEXT
        )
    """)

    columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(orders)"
        ).fetchall()
    }

    if "missed_pickup_counted" not in columns:
        connection.execute("""
            ALTER TABLE orders
            ADD COLUMN missed_pickup_counted INTEGER DEFAULT 0
        """)


# --------------------------------------------------
# CHECK STUDENT SUSPENSION
# --------------------------------------------------

def get_student_status(student_id):

    student_id = student_id.strip().upper()

    with get_connection() as connection:

        setup_student_table(connection)

        student = connection.execute("""
            SELECT *
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

    if student is None:
        return {
            "student_id": student_id,
            "missed_pickups": 0,
            "suspended": False,
            "suspended_until": None
        }

    student = dict(student)

    suspended_until = student["suspended_until"]

    is_suspended = False

    if suspended_until:

        expiry = datetime.fromisoformat(suspended_until)

        if datetime.now() < expiry:
            is_suspended = True

    return {
        "student_id": student_id,
        "missed_pickups": student["missed_pickups"],
        "suspended": is_suspended,
        "suspended_until": suspended_until
    }


# --------------------------------------------------
# PLACE ORDER
# --------------------------------------------------

def place_order(student_name, student_id, cart, pickup_time):

    student_name = student_name.strip()
    student_id = student_id.strip().upper()

    if not student_name or not student_id:
        raise ValueError("Enter your name and student ID.")

    if not is_valid_student_id(student_id):
        raise ValueError(
            "Invalid Student ID. Use this format: 1RVU23BSC013"
        )

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

        setup_student_table(connection)

        student = connection.execute("""
            SELECT *
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if student:

            suspended_until = student["suspended_until"]

            if suspended_until:

                expiry = datetime.fromisoformat(suspended_until)

                if datetime.now() < expiry:

                    raise ValueError(
                        "Your student ID is temporarily suspended "
                        f"until {expiry.strftime('%d %B %Y at %I:%M %p')} "
                        "because of missed food pickups."
                    )

            connection.execute("""
                UPDATE students
                SET student_name = ?
                WHERE student_id = ?
            """, (student_name, student_id))

        else:

            connection.execute("""
                INSERT INTO students (
                    student_id,
                    student_name,
                    missed_pickups,
                    suspended_until
                )
                VALUES (?, ?, 0, NULL)
            """, (student_id, student_name))

        cursor = connection.execute("""
            INSERT INTO orders (
                student_name,
                student_id,
                items,
                total,
                pickup_time,
                status
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


# --------------------------------------------------
# GET ALL ORDERS
# --------------------------------------------------

def get_all_orders():

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM orders
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# --------------------------------------------------
# UPDATE ORDER STATUS
# --------------------------------------------------

def update_order_status(order_id, new_status):

    allowed_statuses = [
        "Received",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled",
        "Not Picked Up"
    ]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    with get_connection() as connection:

        setup_student_table(connection)

        order = connection.execute("""
            SELECT *
            FROM orders
            WHERE id = ?
        """, (order_id,)).fetchone()

        if order is None:
            raise ValueError("Order not found.")

        connection.execute("""
            UPDATE orders
            SET status = ?
            WHERE id = ?
        """, (new_status, order_id))

        if (
            new_status == "Not Picked Up"
            and not order["missed_pickup_counted"]
        ):

            student_id = order["student_id"]

            student = connection.execute("""
                SELECT *
                FROM students
                WHERE student_id = ?
            """, (student_id,)).fetchone()

            if student is None:

                connection.execute("""
                    INSERT INTO students (
                        student_id,
                        student_name,
                        missed_pickups,
                        suspended_until
                    )
                    VALUES (?, ?, 1, NULL)
                """, (
                    student_id,
                    order["student_name"]
                ))

                missed_count = 1

            else:

                missed_count = student["missed_pickups"] + 1

                connection.execute("""
                    UPDATE students
                    SET missed_pickups = ?
                    WHERE student_id = ?
                """, (missed_count, student_id))

            # Mark this order as already counted.
            connection.execute("""
                UPDATE orders
                SET missed_pickup_counted = 1
                WHERE id = ?
            """, (order_id,))

            # Suspend for seven days after every third missed pickup.
            if missed_count % 3 == 0:

                suspension_end = (
                    datetime.now() + timedelta(days=7)
                ).isoformat(timespec="seconds")

                connection.execute("""
                    UPDATE students
                    SET suspended_until = ?
                    WHERE student_id = ?
                """, (suspension_end, student_id))

# --------------------------------------------------
# ORDER COUNT
# --------------------------------------------------

def get_order_count():

    with get_connection() as connection:

        return connection.execute("""
            SELECT COUNT(*)
            FROM orders
        """).fetchone()[0]


# --------------------------------------------------
# TOTAL SALES
# --------------------------------------------------

def get_total_sales():

    with get_connection() as connection:

        return connection.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM orders
            WHERE status NOT IN ('Cancelled', 'Not Picked Up')
        """).fetchone()[0]