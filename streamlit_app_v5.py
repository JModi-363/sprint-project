import os
import sqlite3
from datetime import datetime

import streamlit as st
from Artist import Artist
from Paint import Paint
from PaintMenu import PaintMenu

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "orders.db")


# -------------------------------------------------------------------
# Database setup and helpers
# -------------------------------------------------------------------

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_fname TEXT NOT NULL,
            artist_lname TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            paint_base TEXT NOT NULL,
            size TEXT NOT NULL,
            additives TEXT NOT NULL,
            additive_parts INTEGER NOT NULL,
            cost REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL DEFAULT 0,
            additive_parts INTEGER DEFAULT 0,
            description TEXT,
            sustainability_info TEXT,
            origin TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        default_items = [
            # Paint bases
            ("paint_base", "Acrylic", 0, 0, "Fast-drying synthetic paint", "", ""),
            ("paint_base", "Oil", 0, 0, "Slow-drying rich paint", "", ""),
            ("paint_base", "Watercolor", 0, 0, "Transparent water-based paint", "", ""),
            ("paint_base", "Tempera", 0, 0, "Fast-drying matte paint", "", ""),
            ("paint_base", "Gouache", 0, 0, "Opaque watercolor paint", "", ""),

            # Sizes
            ("size", "Small", 1.50, 0, "", "", ""),
            ("size", "Medium", 2.20, 0, "", "", ""),
            ("size", "Large", 3.00, 0, "", "", ""),

            # Additives
            ("additives", "Thickener", 0, 0, "", "", ""),
            ("additives", "Antioxidant", 0, 0, "", "", ""),
            ("additives", "Hardener", 0, 0, "", "", ""),
            ("additives", "Extender", 0, 0, "", "", ""),
            ("additives", "None", 0, 0, "", "", ""),
        ]

        cursor.executemany("""
            INSERT INTO menu_items (category, name, price, additive_parts, description, sustainability_info, origin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_items)

    conn.commit()
    conn.close()


def load_orders():
    """
    Load orders from SQLite database.
    Returns:
        list[Paint]: List of Paint order objects with attached _id and _quantity.
    """
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, artist_fname, artist_lname, location, timestamp,
               paint_base, size, additives, additive_parts, cost, quantity
        FROM orders
        ORDER BY datetime(timestamp) DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    orders = []
    for row in rows:
        (
            order_id,
            fname,
            lname,
            location,
            timestamp_str,
            paint_base,
            size,
            additives,
            additive_parts,
            cost,
            quantity,
        ) = row

        artist = Artist(fname, lname, location)
        timestamp = datetime.fromisoformat(timestamp_str)

        order = Paint(artist, paint_base, size, additives, additive_parts)
        order._id = order_id
        order._Paint__timestamp = timestamp
        order._Paint__cost = cost
        order._quantity = quantity

        orders.append(order)

    st.session_state.orders = orders
    return orders


def save_order(order, quantity=1):
    """Insert a new order into the SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    artist = order.get_artist()

    cursor.execute("""
        INSERT INTO orders (
            artist_fname, artist_lname, location, timestamp,
            paint_base, size, additives, additive_parts, cost, quantity
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        artist.get_fname(),
        artist.get_lname(),
        artist.get_location(),
        order.get_timestamp().isoformat(),
        order.get_paint_base(),
        order.get_size(),
        order.get_additives(),
        order.get_additive_parts(),
        order.get_cost(),
        quantity,
    ))

    conn.commit()
    conn.close()


def update_order_in_db(order_id, updated_order, quantity=1):
    """Update an existing order in the SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    artist = updated_order.get_artist()

    cursor.execute("""
        UPDATE orders
        SET artist_fname = ?,
            artist_lname = ?,
            location = ?,
            timestamp = ?,
            paint_base = ?,
            size = ?,
            additives = ?,
            additive_parts = ?,
            cost = ?,
            quantity = ?
        WHERE id = ?
    """, (
        artist.get_fname(),
        artist.get_lname(),
        artist.get_location(),
        updated_order.get_timestamp().isoformat(),
        updated_order.get_paint_base(),
        updated_order.get_size(),
        updated_order.get_additives(),
        updated_order.get_additive_parts(),
        updated_order.get_cost(),
        quantity,
        order_id,
    ))

    conn.commit()
    conn.close()


def delete_order_from_db(order_id):
    """Delete an order from the SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    conn.commit()
    conn.close()


# -------------------------------------------------------------------
# Menu loading
# -------------------------------------------------------------------

init_db()
menu = PaintMenu.from_db(DB_FILE_PATH)


# -------------------------------------------------------------------
# Session state initialization
# -------------------------------------------------------------------

if "artist" not in st.session_state:
    st.session_state.artist = None
if "orders" not in st.session_state:
    st.session_state.orders = None
if "action" not in st.session_state:
    st.session_state.action = "Place Order"
if "current_order_for_confirmation" not in st.session_state:
    st.session_state.current_order_for_confirmation = None
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "delete_index" not in st.session_state:
    st.session_state.delete_index = None


# -------------------------------------------------------------------
# UI helpers
# -------------------------------------------------------------------

def size_display_options():
    raw_sizes = menu.get_size()
    options = []
    for s in raw_sizes:
        name, price = [x.strip() for x in s.split(":")]
        options.append(f"{name} - ${price}")
    return options


def parse_size_name(display_value: str) -> str:
    return display_value.split(" - ")[0]


def get_size_price_map():
    mapping = {}
    for s in menu.get_size():
        name, price = [x.strip() for x in s.split(":")]
        mapping[name] = price
    return mapping


# -------------------------------------------------------------------
# Main app
# -------------------------------------------------------------------

st.title("Paint Order System")

if st.session_state.artist is None:
    st.header("Artist Login")
    with st.form("login_form"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        location = st.text_input("Studio Number")
        submitted = st.form_submit_button("Login")

        if submitted:
            if fname and lname and location:
                st.session_state.artist = Artist(fname, lname, location)
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please fill all fields.")
else:
    st.sidebar.header("Navigation")
    if st.sidebar.button("Place Order"):
        st.session_state.action = "Place Order"
        st.rerun()
    if st.sidebar.button("View Orders"):
        st.session_state.action = "View Orders"
        st.rerun()
    if st.sidebar.button("Update Order"):
        st.session_state.action = "Update Order"
        st.rerun()
    if st.sidebar.button("Delete Order"):
        st.session_state.action = "Delete Order"
        st.rerun()
    if st.sidebar.button("Refresh Orders"):
        st.session_state.orders = None
        st.rerun()

# -------------------------
# RESET DATABASE BUTTON
# -------------------------
if st.sidebar.button("RESET DATABASE"):
    if os.path.exists(DB_FILE_PATH):
        os.remove(DB_FILE_PATH)
        st.success("Database deleted. Restart the app.")
    else:
        st.info("No database file found to delete.")

    action = st.session_state.action

    # ---------------------- Place Order ----------------------
    if action == "Place Order":
        st.header("Place a New Order")

        with st.form("order_form"):
            paint_base = st.selectbox("Paint Base", menu.get_paint_base())

            size_options = size_display_options()
            size_display = st.selectbox("Size", size_options)

            additives_options = menu.get_additives()
            default_add_index = (
                additives_options.index("None") if "None" in additives_options else 0
            )
            additives = st.selectbox("Additives", additives_options, index=default_add_index)

            quantity = st.number_input("Quantity", min_value=1, step=1, value=1)

            show_parts = additives.lower() != "none"
            additive_parts = 0
            if show_parts:
                additive_parts = st.number_input(
                    "Additive Parts",
                    min_value=0,
                    step=1,
                    value=0,
                )
                if additive_parts > 0:
                    st.write(
                        f"+$0.10 per part. Total additional: ${(additive_parts * 0.10):.2f}"
                    )
                else:
                    st.write("+$0.10 per part.")

            submitted = st.form_submit_button("Review Order")

        if submitted:
            size_name = parse_size_name(size_display)
            order = Paint(
                st.session_state.artist,
                paint_base,
                size_name,
                additives,
                additive_parts,
            )
            order.calculate_cost(menu)
            st.session_state.current_order_for_confirmation = (order, quantity)
            st.rerun()

        if st.session_state.current_order_for_confirmation is not None:
            order, quantity = st.session_state.current_order_for_confirmation
            st.subheader("Confirm Order")
            st.code(str(order))
            st.write(f"Quantity: {quantity}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm and Save"):
                    save_order(order, quantity=quantity)
                    st.success("Order saved!")
                    st.session_state.orders = None
                    st.session_state.current_order_for_confirmation = None
                    st.rerun()
            with col2:
                if st.button("Cancel Order"):
                    st.info("Order cancelled.")
                    st.session_state.current_order_for_confirmation = None
                    st.rerun()

    # ---------------------- View Orders ----------------------
    elif action == "View Orders":
        st.header("View Orders")

        orders = st.session_state.orders or load_orders()

        if not orders:
            st.info("No orders found. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            data = []
            for order in orders:
                item = f"{order.get_size()} {order.get_paint_base()} - {order.get_additives()} ({order.get_additive_parts()})"
                data.append({
                    "Timestamp": order.get_timestamp().strftime("%Y-%m-%d %I:%M %p"),
                    "Item": item,
                    "Cost": f"${order.get_cost():.2f}",
                    "Quantity": getattr(order, "_quantity", 1),
                    "Artist": f"{order.get_artist().get_fname()} {order.get_artist().get_lname()}",
                })

            st.dataframe(data)

            st.subheader("Quick Actions")
            for i, order in enumerate(orders):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"Order {i+1}: {data[i]['Item']} (Qty: {data[i]['Quantity']})")
                with col2:
                    if st.button(f"Edit {i+1}", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.session_state.action = "Update Order"
                        st.rerun()
                with col3:
                    if st.button(f"Delete {i+1}", key=f"delete_{i}"):
                        st.session_state.delete_index = i
                        st.session_state.action = "Delete Order"
                        st.rerun()

    # ---------------------- Update Order ----------------------
    elif action == "Update Order":
        st.header("Update Order")

        orders = st.session_state.orders or load_orders()

        if not orders:
            st.info("No orders to update. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            idx = st.session_state.edit_index
            if idx is None or idx >= len(orders):
                st.info("Select an order to update from View Orders.")
            else:
                order = orders[idx]
                st.write(f"Updating: {order}")

                size_price_map = get_size_price_map()
                size_options = size_display_options()
                current_size_display = f"{order.get_size()} - ${size_price_map.get(order.get_size(), '0.00')}"

                with st.form("update_form"):
                    paint_base = st.selectbox(
                        "Paint Base",
                        menu.get_paint_base(),
                        index=menu.get_paint_base().index(order.get_paint_base())
                        if order.get_paint_base() in menu.get_paint_base() else 0,
                    )

                    size_index = size_options.index(current_size_display) if current_size_display in size_options else 0
                    size_display = st.selectbox("Size", size_options, index=size_index)

                    additives_options = menu.get_additives()
                    add_index = (
                        additives_options.index(order.get_additives())
                        if order.get_additives() in additives_options
                        else (additives_options.index("None") if "None" in additives_options else 0)
                    )
                    additives = st.selectbox("Additives", additives_options, index=add_index)

                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        step=1,
                        value=getattr(order, "_quantity", 1),
                    )

                    show_parts = additives.lower() != "none"
                    if show_parts:
                        additive_parts = st.number_input(
                            "Additive Parts",
                            min_value=0,
                            step=1,
                            value=order.get_additive_parts(),
                        )
                        if additive_parts > 0:
                            st.write(
                                f"+$0.10 per part. Total additional: ${(additive_parts * 0.10):.2f}"
                            )
                        else:
                            st.write("+$0.10 per part.")
                    else:
                        additive_parts = 0

                    submitted = st.form_submit_button("Review Updated Order")

                if submitted:
                    size_name = parse_size_name(size_display)
                    updated_order = Paint(
                        st.session_state.artist,
                        paint_base,
                        size_name,
                        additives,
                        additive_parts,
                    )
                    updated_order.calculate_cost(menu)

                    st.subheader("Confirm Update")
                    st.code(str(updated_order))
                    st.write(f"Quantity: {quantity}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Update"):
                            order_id = getattr(order, "_id", None)
                            if order_id is None:
                                st.error("Could not determine order ID for update.")
                            else:
                                update_order_in_db(order_id, updated_order, quantity=quantity)
                                st.success("Order updated!")
                                st.session_state.orders = None
                                st.session_state.edit_index = None
                                st.rerun()
                    with col2:
                        if st.button("Cancel Update"):
                            st.info("Update cancelled.")
                            st.session_state.edit_index = None
                            st.rerun()

    # ---------------------- Delete Order ----------------------
    elif action == "Delete Order":
        st.header("Delete Order")

        orders = st.session_state.orders or load_orders()

        if not orders:
            st.info("No orders to delete. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            idx = st.session_state.delete_index
            if idx is None or idx >= len(orders):
                st.info("Select an order to delete from View Orders.")
            else:
                order = orders[idx]
                st.write(f"Deleting: {order}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Delete"):
                        order_id = getattr(order, "_id", None)
                        if order_id is None:
                            st.error("Could not determine order ID for deletion.")
                        else:
                            delete_order_from_db(order_id)
                            st.success("Order deleted.")
                            st.session_state.orders = None
                            st.session_state.delete_index = None
                            st.rerun()
                with col2:
                    if st.button("Cancel Delete"):
                        st.info("Delete cancelled.")
                        st.session_state.delete_index = None
                        st.rerun()
