import os
import sqlite3
from datetime import datetime
import streamlit as st
from Artist import Artist
from PaintMenu import PaintMenu
from Paint import Paint

# Session state init
if 'artist' not in st.session_state:
    st.session_state.artist = None
if 'orders' not in st.session_state:
    st.session_state.orders = None  # Lazy load
if 'action' not in st.session_state:
    st.session_state.action = 'Place Order'
if 'additive_parts_place_order' not in st.session_state:
    st.session_state.additive_parts_place_order = 0
if 'last_additives_choice_place_order' not in st.session_state:
    st.session_state.last_additives_choice_place_order = "none"
if 'additive_parts_update' not in st.session_state:
    st.session_state.additive_parts_update = 0
if 'last_additives_choice_update' not in st.session_state:
    st.session_state.last_additives_choice_update = "none"
if 'confirm_order_displayed' not in st.session_state:
    st.session_state.confirm_order_displayed = False
if 'confirm_update_displayed' not in st.session_state:
    st.session_state.confirm_update_displayed = False
if 'order_to_update_id' not in st.session_state:
    st.session_state.order_to_update_id = None
if 'order_to_update_obj' not in st.session_state:
    st.session_state.order_to_update_obj = None
if 'confirm_delete_displayed' not in st.session_state:
    st.session_state.confirm_delete_displayed = False
if 'order_to_delete_id' not in st.session_state:
    st.session_state.order_to_delete_id = None

# Shared database file path
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "orders.db")

# Menu file path
init_db()  # ensure tables exist first
menu = PaintMenu.from_db(DB_FILE_PATH)


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
        category TEXT NOT NULL,           -- 'paint_base', 'size', 'additives'
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
        list: List of Paint order objects.
    """
    import traceback
    try:
        # Initialize database if needed
        init_db()
        
        st.write(f"DEBUG: Attempting to connect to DB: {DB_FILE_PATH}")  # Debug
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        st.write("DEBUG: Connected to DB. Executing SELECT query.")  # Debug
        cursor.execute("SELECT artist_fname, artist_lname, location, timestamp, paint_base, size, additives, additive_parts, cost FROM orders")
        rows = cursor.fetchall()
        conn.close()
        st.write(f"DEBUG: Closed DB connection. Fetched {len(rows)} rows.")  # Debug
        
        orders = []
        for row in rows:
            fname, lname, location, timestamp_str, paint_base, size, additives, additive_parts, cost = row
            artist = Artist(fname, lname, location)
            timestamp = datetime.fromisoformat(timestamp_str)
            order = Paint(artist, paint_base, size, additives, additive_parts)
            # Set private attributes
            order._Paint__timestamp = timestamp
            order._Paint__cost = cost
            orders.append(order)
            st.write(f"DEBUG: Loaded order {len(orders)}: {order}")  # Debug line
        
        st.session_state.orders = orders
        return orders
    except Exception as e:
        st.error(f"Error loading orders: {e}")
        st.write(traceback.format_exc())  # Show full traceback
        st.session_state.orders = []
        return []


def save_order(order):
    """Save order to SQLite database."""
    init_db()
    st.write(f"DEBUG: Attempting to connect to DB for saving: {DB_FILE_PATH}")  # Debug
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    st.write("DEBUG: Connected to DB for saving. Executing INSERT query.")  # Debug
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
        order.get_cost()
    ))
    conn.commit()
    conn.close()
    st.write("DEBUG: Order saved successfully and DB connection closed.")  # Debug
    print("Order saved successfully.")

def update_order_in_db(order_id, updated_order):
    """Update an existing order in the SQLite database."""
    init_db()
    st.write(f"DEBUG: Attempting to connect to DB for updating: {DB_FILE_PATH}")
    
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    st.write(f"DEBUG: Connected to DB for updating. Executing UPDATE query for ID: {order_id}")
    
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
        1,              # quantity placeholder
        order_id        # WHERE clause
    ))

    conn.commit()
    conn.close()
    st.write(f"DEBUG: Order ID {order_id} updated successfully and DB connection closed.")

'''
def update_order_in_db(order_id, updated_order):
    """Update an existing order in the SQLite database."""
    init_db()
    st.write(f"DEBUG: Attempting to connect to DB for updating: {DB_FILE_PATH}") # Debug
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    st.write(f"DEBUG: Connected to DB for updating. Executing UPDATE query for ID: {order_id}") # Debug
    artist = updated_order.get_artist()
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
    1  # default for now (Phase 2 will make this dynamic)
))
    conn.commit()
    conn.close()
    st.write(f"DEBUG: Order ID {order_id} updated successfully and DB connection closed.") # Debug
    print(f"Order ID {order_id} updated successfully.")'''


def delete_order_from_db(order_id):
    """Delete an order from the SQLite database."""
    init_db()
    st.write(f"DEBUG: Attempting to connect to DB for deleting: {DB_FILE_PATH}") # Debug
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    st.write(f"DEBUG: Connected to DB for deleting. Executing DELETE query for ID: {order_id}") # Debug
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    st.write(f"DEBUG: Order ID {order_id} deleted successfully and DB connection closed.") # Debug
    print(f"Order ID {order_id} deleted successfully.")


# Main app
st.title("Paint Order System")
st.write(f"DEBUG: artist = {st.session_state.artist}")  # Debug
st.write(f"DEBUG: action = {st.session_state.action}")  # Debug

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
    # Sidebar for navigation
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
        st.session_state.orders = None  # Force reload
        st.rerun()
    action = st.session_state.action

    if action == "Place Order":
        st.header("Place a New Order")
        with st.form("order_form"):
            paint_base = st.selectbox("Paint Base", menu.get_paint_base())
            size_options = [
                f"{s.split(':')[0].strip()} - ${s.split(':')[1].strip()}"
                for s in menu.get_size()
            ]
            size = st.selectbox("Size", size_options)
            additives_options = menu.get_additives()
            additives_index = (
                additives_options.index("None") if "None" in additives_options else 0
            )
            additives = st.selectbox(
                "Additives", additives_options, index=additives_index
            )
            submitted = st.form_submit_button("Submit Order")

        # Outside the form: Additive parts input and confirmation buttons
        show_parts = additives.lower() != "none"
        if show_parts:
            # Ensure key is unique for this context or shared appropriately
            if st.session_state.get('last_additives_choice_place_order') != additives:
                st.session_state.additive_parts_place_order = 0
                st.session_state.last_additives_choice_place_order = additives

            st.session_state.additive_parts_place_order = st.number_input(
                "Additive Parts",
                min_value=0,
                step=1,
                value=st.session_state.additive_parts_place_order,
                key="parts_input_place_order"
            )
            if st.session_state.additive_parts_place_order > 0:
                st.write(
                    f"+$0.10 per part. Total additional: ${(st.session_state.additive_parts_place_order * 0.10):.2f}"
                )
            else:
                st.write("+$0.10 per part.")
        else:
            st.session_state.additive_parts_place_order = 0 # Reset if no additives selected
            st.session_state.last_additives_choice_place_order = "none" # Track last choice

        if submitted:
            # Extract size name
            size_name = size.split(' - ')[0]
            order = Paint(
                st.session_state.artist, paint_base, size_name, additives, st.session_state.additive_parts_place_order
            )
            order.calculate_cost(menu)
            st.session_state.current_order_for_confirmation = order # Store order for confirmation
            st.session_state.confirm_order_displayed = True # Show confirmation buttons
            st.rerun()

        if st.session_state.confirm_order_displayed and 'current_order_for_confirmation' in st.session_state:
            st.code(str(st.session_state.current_order_for_confirmation))
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm and Save", key="confirm_save_btn"):
                    save_order(st.session_state.current_order_for_confirmation)
                    st.session_state.orders = None  # Force reload orders for other tabs
                    st.success("Order saved!")
                    del st.session_state.current_order_for_confirmation # Clear after saving
                    st.session_state.confirm_order_displayed = False # Hide confirmation buttons
                    st.rerun()
            with col2:
                if st.button("Cancel Order", key="cancel_order_btn"):
                    st.info("Order cancelled.")
                    del st.session_state.current_order_for_confirmation # Clear
                    st.session_state.confirm_order_displayed = False # Hide confirmation buttons
                    st.rerun()


    elif action == "View Orders":
        st.header("View Orders")
        st.write(f"DEBUG: Current action = {action}")  # Debug
        orders = load_orders()
        st.write(f"DEBUG: Loaded {len(orders)} orders")  # Debug
        if not orders:
            st.info("No orders found. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            # Prepare data for dataframe
            data = []
            for order in orders:
                item = f"{order.get_size()} {order.get_paint_base()} - {order.get_additives()} ({order.get_additive_parts()})"
                data.append({
                    "Timestamp": order.get_timestamp().strftime("%Y-%m-%d %I:%M %p"),
                    "Item": item,
                    "Cost": f"${order.get_cost():.2f}",
                    "Artist": f"{order.get_artist().get_fname()} {order.get_artist().get_lname()}"
                })
            st.dataframe(data)
            # Buttons in table? Streamlit dataframe doesn't support buttons directly, so perhaps list with buttons
            st.subheader("Quick Actions")
            for i, order in enumerate(orders):
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    st.write(f"Order {i+1}: {data[i]['Item']}")
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

    elif action == "Update Order":
        st.header("Update Order")
        orders = load_orders()
        if not orders:
            st.info("No orders to update. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            if 'edit_index' in st.session_state and st.session_state.edit_index < len(orders):
                idx = st.session_state.edit_index
                order = orders[idx]
                st.write(f"Updating: {order}")
                with st.form("update_form"):
                    paint_base = st.selectbox(
                        "Paint Base",
                        menu.get_paint_base(),
                        index=menu.get_paint_base().index(order.get_paint_base())
                        if order.get_paint_base() in menu.get_paint_base() else 0,
                    )
                    size_options = [
                        f"{s.split(':')[0].strip()} - ${s.split(':')[1].strip()}"
                        for s in menu.get_size()
                    ]
                    size_display = f"{order.get_size()} - ${dict(s.split(':') for s in menu.get_size()).get(order.get_size(), '0.00')}"
                    size_index = size_options.index(size_display) if size_display in size_options else 0
                    size = st.selectbox("Size", size_options, index=size_index)
                    additives_options = menu.get_additives()
                    additives_index = (
                        additives_options.index(order.get_additives())
                        if order.get_additives() in additives_options
                        else (additives_options.index("None") if "None" in additives_options else 0)
                    )
                    additives = st.selectbox("Additives", additives_options, index=additives_index)
                    show_parts = additives.lower() != "none"
                    if show_parts:
                        additive_parts = st.number_input(
                            "Additive Parts",
                            min_value=0,
                            step=1,
                            value=order.get_additive_parts(),
                            key="parts_input",
                            on_change=update_parts,
                        )
                        if st.session_state.additive_parts > 0:
                            st.write(
                                f"+$0.10 per part. Total additional: ${(st.session_state.additive_parts * 0.10):.2f}"
                            )
                        else:
                            st.write("+$0.10 per part.")
                    else:
                        additive_parts = 0
                    submitted = st.form_submit_button("Update Order")
                    if submitted:
                        # Extract size name
                        size_name = size.split(' - ')[0]
                        updated_order = Paint(
                            st.session_state.artist, paint_base, size_name, additives, additive_parts
                        )
                        updated_order.calculate_cost(menu)
                        st.code(str(updated_order))
                        if st.button("Confirm Update"):
                            orders[idx] = updated_order
                            save_order(updated_order)  # Note: This appends, so file will have duplicate, but for simplicity
                            st.session_state.orders = None  # Force reload orders for other tabs
                            st.success("Order updated!")
                            del st.session_state.edit_index
                            st.rerun()
                # Outside form for dynamic display
                show_parts_update = additives.lower() != "none"
                if show_parts_update:
                    # Ensure key is unique for this context or shared appropriately
                    # Reset additive_parts if additives changed to None *before* input
                    if st.session_state.get('last_additives_choice_update') != additives:
                        st.session_state.additive_parts_update = 0
                        st.session_state.last_additives_choice_update = additives

                    additive_parts_value_update = st.number_input(
                        "Additive Parts",
                        min_value=0,
                        step=1,
                        value=st.session_state.additive_parts_update or order.get_additive_parts(),
                        key="parts_input_update",
                        on_change=update_parts
                    )
                    st.session_state.additive_parts_update = additive_parts_value_update
                    if st.session_state.additive_parts_update > 0:
                        st.write(
                            f"+$0.10 per part. Total additional: ${(st.session_state.additive_parts_update * 0.10):.2f}"
                        )
                    else:
                        st.write("+$0.10 per part.")
                else:
                    st.session_state.additive_parts_update = 0
                    st.session_state.last_additives_choice_update = "none"

            else:
                st.info("Select an order to update from View Orders.")

    elif action == "Delete Order":
        st.header("Delete Order")
        orders = load_orders()
        if not orders:
            st.info("No orders to delete. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            if 'delete_index' in st.session_state and st.session_state.delete_index < len(orders):
                idx = st.session_state.delete_index
                order = orders[idx]
                st.write(f"Deleting: {order}")
                if st.button("Confirm Delete"):
                    del orders[idx]
                    st.success("Order deleted from session. (File not updated for simplicity)")
                    del st.session_state.delete_index
                    st.rerun()
            else:
                st.info("Select an order to delete from View Orders.")