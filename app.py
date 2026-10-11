
import streamlit as st

import sqlite3
import database

# Page configuration
st.set_page_config(
    page_title="AIMS | Aven Logistics",
    layout="wide"
)

# AIMS Navigation Sidebar
with st.sidebar:
    st.image("aven_logo.png", width="stretch")
    st.caption("Inventory Management System")
    st.divider()

    st.markdown("### SYSTEM MODULES")

    selected_page = st.radio(
    "Navigation",
    [
        "Dashboard",
        "Inventory Records",
        "Stock Movements",
        "Replenishment",
        "Reports"
    ],
    label_visibility="collapsed"
)

    st.divider()
    st.caption("AIMS | Portfolio Prototype")


# Load inventory records from SQLite
connection = sqlite3.connect("aven_inventory.db")

connection.row_factory = sqlite3.Row

rows = connection.execute("""
    SELECT product_name, stock, reorder_point
    FROM products
""").fetchall()

inventory = [
    {
        "Product": row["product_name"],
        "Stock": row["stock"],
        "Reorder Point": row["reorder_point"],
        "Suggested Replenishment": max(
            0,
            row["reorder_point"] - row["stock"]
        )
    }
    for row in rows
]

connection.close()


# Calculate replenishment alerts
low_stock = []

for product in inventory:
    if product["Stock"] <= product["Reorder Point"]:
        low_stock.append(product)

# Calculate KPI values BEFORE displaying them
total_stock = sum(product["Stock"] for product in inventory)
total_skus = len(inventory)
reorder_alerts = len(low_stock)

# Calculate stock status overview
sufficient_stock = total_skus - reorder_alerts

# Calculate total suggested replenishment
total_replenishment = sum(
    product["Suggested Replenishment"]
    for product in inventory
)

# Display selected system module
if selected_page == "Dashboard":

    st.subheader("Inventory Dashboard")

    st.caption(
    "AVEN LOGISTICS | Inventory Control & Warehouse Operations"

)

    # Professional inventory dashboard cards
    col1, col2, col3, col4 = st.columns(4)

    dashboard_metrics = [
        ("TOTAL STOCK", total_stock, "#A78BFA"),
        ("TOTAL SKUs", total_skus, "#A78BFA"),
        ("REORDER ALERTS", reorder_alerts, "#F5B971"),
        ("REPLENISHMENT", total_replenishment, "#66D8AE")
    ]

    for col, (label, value, accent) in zip(
        [col1, col2, col3, col4],
        dashboard_metrics
    ):
        with col:
            st.markdown(
                f"""
                <div style="
                    background-color: #2C223F;
                    border: 1px solid #48365F;
                    border-top: 4px solid {accent};
                    border-radius: 12px;
                    padding: 22px;
                    min-height: 145px;
                ">
                    <div style="
                        color: #C5B8D8;
                        font-size: 13px;
                        font-weight: 600;
                    ">
                        {label}
                    </div>
                    <div style="
                        color: #FFFFFF;
                        font-size: 36px;
                        font-weight: 700;
                        margin-top: 12px;
                    ">
                        {value:,}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.subheader("Stock Replenishment Summary")

    if low_stock:
        st.dataframe(
            low_stock,
            width="stretch",
            hide_index=True
        )
    else:
        st.success("All inventory levels are sufficient.")

        st.divider()

    st.subheader("Stock Status Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sufficient Stock", sufficient_stock)

    with col2:
        st.metric("Reorder Required", reorder_alerts)

    st.subheader("Inventory Stock Status")

    stock_status_data = {
        "Status": ["Sufficient Stock", "Reorder Required"],
        "Number of SKUs": [sufficient_stock, reorder_alerts]
    }

    st.bar_chart(
        stock_status_data,
        x="Status",
        y="Number of SKUs",
        horizontal=True
    )

# Inventory Records
if selected_page == "Inventory Records":
    st.subheader("Inventory Records")

    search_product = st.text_input(
        "Search Product",
        placeholder="Enter product name..."
    )

    stock_filter = st.selectbox(
        "Filter by Stock Status",
        ["All Products", "Reorder Required", "Sufficient Stock"]
    )

    filtered_inventory = []

    for product in inventory:

        matches_search = search_product.lower() in product["Product"].lower()

        if stock_filter == "Reorder Required":
            matches_status = product["Stock"] <= product["Reorder Point"]

        elif stock_filter == "Sufficient Stock":
            matches_status = product["Stock"] > product["Reorder Point"]

        else:
            matches_status = True

        if matches_search and matches_status:
            filtered_inventory.append(product)

    st.dataframe(filtered_inventory, width="stretch")


import csv
import io

output = io.StringIO()

writer = csv.DictWriter(
    output,
    fieldnames=[
    "Product",
    "Stock",
    "Reorder Point",
    "Suggested Replenishment"
]

)

writer.writeheader()
writer.writerows(inventory)

if selected_page == "Reports":
    st.subheader("Inventory Reports")
    st.caption("Generate and download inventory and replenishment reports.")
    st.download_button(
        label="Download Inventory Report",
        data=output.getvalue(),
        file_name="aven_inventory_report.csv",
        mime="text/csv"

    )

# Replenishment Alerts
if selected_page == "Replenishment":
    st.subheader("Replenishment Alerts")

    if low_stock:
        st.warning(f"{len(low_stock)} products require replenishment.")
        st.dataframe(low_stock, width="stretch")
    else:
        st.success("All products have sufficient stock.")


# Download replenishment report
if selected_page == "Reports" and low_stock:
    replenishment_output = io.StringIO()

    replenishment_writer = csv.DictWriter(
        replenishment_output,
        fieldnames=[
            "Product",
            "Stock",
            "Reorder Point",
            "Suggested Replenishment"
        ]
    )

    replenishment_writer.writeheader()
    replenishment_writer.writerows(low_stock)

    st.download_button(
        label="Download Replenishment Report",
        data=replenishment_output.getvalue(),
        file_name="aven_replenishment_report.csv",
        mime="text/csv"
    )

# Add new inventory products
if selected_page == "Inventory Records":
    st.divider()
    st.subheader("Add New Product")

    with st.form("add_product_form"):
        product_name = st.text_input("Product Name")

        opening_stock = st.number_input(
            "Opening Stock",
            min_value=0,
            step=1,
            key="opening_stock"
        )

        reorder_point = st.number_input(
            "Reorder Point",
            min_value=0,
            step=1,
            key="reorder_point"
        )

        submitted = st.form_submit_button("Add Product")

    if submitted:
        if product_name.strip():
            try:
                connection = sqlite3.connect("aven_inventory.db")

                connection.execute("""
                    INSERT INTO products
                    (product_name, stock, reorder_point)
                    VALUES (?, ?, ?)
                """, (
                    product_name.strip(),
                    opening_stock,
                    reorder_point
                ))

                connection.commit()
                connection.close()

                st.success(f"{product_name} added successfully!")
                st.rerun()

            except sqlite3.IntegrityError:
                st.error("This product already exists.")

        else:
            st.error("Please enter a product name.")


# Stock Movement
if selected_page == "Stock Movements":
    st.divider()
    st.subheader("Stock Movement")

    with st.form("stock_movement_form"):

        selected_product = st.selectbox(
            "Select Product",
            [product["Product"] for product in inventory]
        )

        transaction_type = st.radio(
            "Transaction Type",
            ["Stock In", "Stock Out"]
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        process_transaction = st.form_submit_button(
            "Process Transaction"
        )

    if process_transaction:


        connection = sqlite3.connect("aven_inventory.db")

        current_stock = connection.execute("""
            SELECT stock FROM products
            WHERE product_name = ?
        """, (selected_product,)).fetchone()[0]

        if transaction_type == "Stock In":
            new_stock = current_stock + quantity
        else:
            new_stock = current_stock - quantity

        if new_stock < 0:
            st.error("Insufficient stock. Transaction rejected.")

        else:
            connection.execute("""
                UPDATE products
                SET stock = ?
                WHERE product_name = ?
            """, (new_stock, selected_product))

            connection.execute("""
                INSERT INTO stock_movements
                (product_name, transaction_type, quantity)
                VALUES (?, ?, ?)
            """, (selected_product, transaction_type, quantity))

            connection.commit()
            connection.close()

            st.success("Stock transaction completed successfully!")
            st.rerun()

        connection.close()

# Stock Movement History
if selected_page == "Stock Movements":
    st.divider()
    st.subheader("Stock Movement History")


    connection = sqlite3.connect("aven_inventory.db")
    connection.row_factory = sqlite3.Row

    movements = connection.execute("""
        SELECT
            transaction_date,
            product_name,
            transaction_type,
            quantity
        FROM stock_movements
        ORDER BY id DESC
    """).fetchall()

    connection.close()


# Calculate stock movement analytics
    total_stock_in = sum(
        row["quantity"]
        for row in movements
        if row["transaction_type"] == "Stock In"
    )

    total_stock_out = sum(
        row["quantity"]
        for row in movements
        if row["transaction_type"] == "Stock Out"
    )

    net_stock_movement = total_stock_in - total_stock_out

    # Display stock movement KPIs
    st.subheader("Stock Movement Analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Stock In", total_stock_in)

    with col2:
        st.metric("Total Stock Out", total_stock_out)

    with col3:
        st.metric("Net Stock Movement", net_stock_movement)

 # Stock movement comparison chart
    st.subheader("Stock In vs Stock Out")

    chart_data = {
        "Transaction Type": ["Stock In", "Stock Out"],
        "Quantity": [total_stock_in, total_stock_out]
    }

    st.bar_chart(
        chart_data,
        x="Transaction Type",
        y="Quantity"
    )

    st.divider()

    if movements:
        history = [
            {
                "Date & Time": row["transaction_date"],
                "Product": row["product_name"],
                "Transaction Type": row["transaction_type"],
                "Quantity": row["quantity"]
            }
            for row in movements
        ]

        st.dataframe(history, width="stretch")

    else:
        st.info("No stock movements recorded yet.")
