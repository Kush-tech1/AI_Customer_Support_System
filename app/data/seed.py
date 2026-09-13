from app.data.database import get_connection, initialize_database


def seed_database():
    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM faqs")

    customers = [
        (1, "Alice", "alice@example.com"),
        (2, "Bob", "bob@example.com"),
        (3, "Charlie", "charlie@example.com"),
    ]

    orders = [
        (1001, 1, "shipped", 79.99),
        (1002, 1, "delivered", 129.99),
        (1003, 2, "cancelled", 149.00),
        (1004, 2, "processing", 49.99),
        (1005, 3, "cancelled", 200.00),
    ]

    payments = [
        (5001, 1001, "captured", 79.99),
        (5002, 1002, "captured", 129.99),
        (5003, 1003, "captured", 149.00),
        (5004, 1004, "authorized", 49.99),
        (5005, 1005, "captured", 200.00),
    ]

    faqs = [
        (
            1,
            "What is your refund policy?",
            "Cancelled orders are eligible for a refund. "
            "Refunds are normally processed within 5 business days.",
        ),
        (
            2,
            "How long do refunds take?",
            "Refunds are normally processed within 5 business days.",
        ),
        (
            3,
            "Can I cancel my order?",
            "Orders can be cancelled before they are shipped.",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO customers (id, name, email)
        VALUES (?, ?, ?)
        """,
        customers,
    )

    cursor.executemany(
        """
        INSERT INTO orders (
            id,
            customer_id,
            status,
            total_amount
        )
        VALUES (?, ?, ?, ?)
        """,
        orders,
    )

    cursor.executemany(
        """
        INSERT INTO payments (
            id,
            order_id,
            status,
            amount
        )
        VALUES (?, ?, ?, ?)
        """,
        payments,
    )

    cursor.executemany(
        """
        INSERT INTO faqs (
            id,
            question,
            answer
        )
        VALUES (?, ?, ?)
        """,
        faqs,
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")