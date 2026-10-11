import sqlite3


connection = sqlite3.connect("aven_inventory.db")


connection.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL UNIQUE,
    stock INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL
)
""")


# Add initial inventory records
products = [
    ("Laptop", 150, 200),
    ("Keyboard", 300, 250),
    ("Mouse", 80, 100),
    ("Monitor", 120, 100),
    ("Printer", 40, 50)
]


connection.executemany("""
INSERT OR IGNORE INTO products
(product_name, stock, reorder_point)
VALUES (?, ?, ?)
""", products)

# Create stock movement transaction history table
connection.execute("""
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_date TEXT DEFAULT CURRENT_TIMESTAMP
)
""")


# Save changes BEFORE closing the database
connection.commit()
connection.close()


print("Aven Logistics database created successfully!")
