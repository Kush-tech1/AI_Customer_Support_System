import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "support.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );

        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        );
        """
    )

    connection.commit()
    connection.close()


def get_order(order_id: int):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            customer_id,
            status,
            total_amount
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def get_payment(order_id: int):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            order_id,
            status,
            amount
        FROM payments
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def get_faqs():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, question, answer
        FROM faqs
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]