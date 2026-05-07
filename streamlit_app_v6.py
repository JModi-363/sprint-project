import os                  # For building file paths relative to this script
import sqlite3             # SQLite database for orders and menu
from datetime import datetime  # For timestamp parsing and formatting

import streamlit as st     # Streamlit UI framework
from Artist import Artist  # Artist domain model
from Paint import Paint    # Paint/order domain model
from PaintMenu import PaintMenu  # Menu loader (now metadata-aware)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# Path to the SQLite database file (orders + menu_items)
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "orders.db")


# -------------------------------------------------------------------
# Database setup and helpers
# -------------------------------------------------------------------

def init_db():
    """
    Initialize the SQLite database and create tables if they don't exist.
    Also seeds default menu_items if the table is empty.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    # Orders table: stores each paint order with artist info, paint choices, cost, and quantity
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

    # Menu items table: stores paint bases, sizes, additives, prices, and metadata
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

    # Check if menu_items is empty; if so, seed with default values
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        # Default menu items with basic descriptions for paint bases
        default_items = [
            # Paint bases (no price, but with descriptions)
            ("paint_base", "Acrylic", 0, 0, "Fast-drying synthetic paint", "", ""),
            ("paint_base", "Oil", 0, 0, "Slow-drying rich paint", "", ""),
            ("paint_base", "Watercolor", 0, 0, "Transparent water-based paint", "", ""),
            ("paint_base", "Tempera", 0, 0, "Fast-drying matte paint", "", ""),
            ("paint_base", "Gouache", 0, 0, "Opaque watercolor paint", "", ""),

            # Sizes (priced, no descriptions)
            ("size", "Small", 1.50, 0, "", "", ""),
            ("size", "Medium", 2.20, 0, "", "", ""),
            ("size", "Large", 3.00, 0, "", "", ""),

            # Additives (no price, no descriptions yet)
            ("additives", "Thickener", 0, 0, "", "", ""),
            ("additives", "Antioxidant", 0, 0, "", "", ""),
            ("additives", "Hardener", 0, 0, "", "", ""),
            ("additives", "Extender", 0, 0, "", "", ""),
            ("additives", "None", 0, 0, "", "", ""),
        ]

        # Insert default menu items into the database
        cursor.executemany("""
            INSERT INTO menu_items (category, name, price, additive_parts, description, sustainability_info, origin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_items)

    conn.commit()
    conn.close()


def load_orders(search_artist: str = "", filter_paint_base: str = ""):
    """
    Load orders from SQLite database with optional filtering by artist name and paint base.
    Returns:
        list[Paint]: List of Paint order objects with attached _id and _quantity.
    """
    init_db()  # Ensure DB and tables exist
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    # Base query selects all orders
    query = """
        SELECT id, artist_fname, artist_lname, location, timestamp,
               paint_base, size, additives, additive_parts, cost, quantity
        FROM orders
        WHERE 1=1
    """
    params = []

    # Optional filter: search by artist first or last name (partial match)
    if search_artist:
        query += " AND (artist_fname LIKE ? OR artist_lname LIKE ?)"
        params.append(f"%{search_artist}%")
        params.append(f"%{search_artist}%")

    # Optional filter: specific paint base (unless "All")
    if filter_paint_base and filter_paint_base != "All":
        query += " AND paint_base = ?"
        params.append(filter_paint_base)

    # Order results by timestamp (most recent first)
    query += " ORDER BY datetime(timestamp) DESC"

    cursor.execute(query, params)
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

        # Rebuild Artist object from stored fields
        artist = Artist(fname, lname, location)
        # Parse timestamp string back into datetime
        timestamp = datetime.fromisoformat(timestamp_str)

        # Rebuild Paint (order) object
        order = Paint(artist, paint_base, size, additives, additive_parts)
        order._id = order_id                         # Attach DB id for updates/deletes
        order._Paint__timestamp = timestamp          # Restore timestamp
        order._Paint__cost = cost                    # Restore cost
        order._quantity = quantity                   # Attach quantity

        orders.append(order)

    # Cache orders in session state for reuse across views
    st.session_state.orders = orders
    return orders


def save_order(order, quantity=1):
    """
    Insert a new order into the SQLite database.
    """
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    artist = order.get_artist()  # Get artist info from order

    # Insert a new row into orders table
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
    """
    Update an existing order in the SQLite database by id.
    """
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    artist = updated_order.get_artist()  # Get updated artist info

    # Update the row with matching id
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
    """
    Delete an order from the SQLite database by id.
    """
    init_db()
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    conn.commit()
    conn.close()


# -------------------------------------------------------------------
# Menu loading
# -------------------------------------------------------------------

# Ensure DB exists and is seeded, then load menu (with metadata) via PaintMenu
init_db()
menu = PaintMenu.from_db(DB_FILE_PATH)


# -------------------------------------------------------------------
# Session state initialization
# -------------------------------------------------------------------

# Store the logged-in artist object
if "artist" not in st.session_state:
    st.session_state.artist = None

# Cache of loaded orders
if "orders" not in st.session_state:
    st.session_state.orders = None

# Current action/view (Place, View, Update, Delete)
if "action" not in st.session_state:
    st.session_state.action = "Place Order"

# Current order awaiting confirmation (for Place Order)
if "current_order_for_confirmation" not in st.session_state:
    st.session_state.current_order_for_confirmation = None

# Index of order being edited (for Update Order)
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Index of order being deleted (for Delete Order)
if "delete_index" not in st.session_state:
    st.session_state.delete_index = None


# -------------------------------------------------------------------
# UI helpers
# -------------------------------------------------------------------

def size_display_options():
    """
    Convert raw size strings like 'Small: 1.50' into display strings like 'Small - $1.50'.
    """
    raw_sizes = menu.get_size()
    options = []
    for s in raw_sizes:
        name, price = [x.strip() for x in s.split(":")]
        options.append(f"{name} - ${price}")
    return options


def parse_size_name(display_value: str) -> str:
    """
    Extract the size name (e.g., 'Small') from a display string like 'Small - $1.50'.
    """
    return display_value.split(" - ")[0]


def get_size_price_map():
    """
    Build a mapping from size name to price string for quick lookup.
    """
    mapping = {}
    for s in menu.get_size():
        name, price = [x.strip() for x in s.split(":")]
        mapping[name] = price
    return mapping


# -------------------------------------------------------------------
# Main app
# -------------------------------------------------------------------

# App title at the top of the page
st.title("Paint Order System")

# If no artist is logged in, show login form
if st.session_state.artist is None:
    st.header("Artist Login")
    with st.form("login_form"):
        fname = st.text_input("First Name")      # Artist first name input
        lname = st.text_input("Last Name")       # Artist last name input
        location = st.text_input("Studio Number")  # Artist studio/location input
        submitted = st.form_submit_button("Login")  # Login button

        if submitted:
            # Require all fields to be filled
            if fname and lname and location:
                # Create Artist object and store in session
                st.session_state.artist = Artist(fname, lname, location)
                st.success("Logged in successfully!")
                st.rerun()  # Rerun to show main app
            else:
                st.error("Please fill all fields.")
else:
    # Sidebar navigation for different actions
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
        # Clear cached orders so they reload from DB
        st.session_state.orders = None
        st.rerun()

    # Current action determines which section to render
    action = st.session_state.action

    # ---------------------- Place Order ----------------------
    if action == "Place Order":
        st.header("Place a New Order")

        # If user clicked "Duplicate" from View Orders, pre-fill defaults from that order
        dup = st.session_state.get("duplicate_order")

        if dup:
            default_paint_base = dup["paint_base"]
            default_size = dup["size"]
            default_additives = dup["additives"]
            default_parts = dup["additive_parts"]
            default_quantity = dup["quantity"]
        else:
            # Defaults when placing a fresh order
            default_paint_base = None
            default_size = None
            default_additives = None
            default_parts = 0
            default_quantity = 1

        # Main order form for placing a new order
        with st.form("order_form"):
            # Paint base selection
            paint_base = st.selectbox(
                "Paint Base",
                menu.get_paint_base(),
                index=menu.get_paint_base().index(default_paint_base)
                if default_paint_base in menu.get_paint_base()
                else 0
            )

            # --- METADATA FOR PAINT BASE ---
            # Look up metadata for the selected paint base and display it
            meta = menu.get_metadata("paint_base", paint_base)
            if meta:
                st.info(
                    f"**Description:** {meta['description']}\n\n"
                    f"**Sustainability:** {meta['sustainability_info']}"
                )

            # Size selection (with price in label)
            size_options = size_display_options()
            size_price_map = get_size_price_map()
            default_size_display = (
                f"{default_size} - ${size_price_map[default_size]}"
                if default_size in size_price_map
                else size_options[0]
            )

            size_display = st.selectbox(
                "Size",
                size_options,
                index=size_options.index(default_size_display)
                if default_size_display in size_options
                else 0
            )

            # Additives selection
            additives_options = menu.get_additives()
            default_add_index = (
                additives_options.index("None") if "None" in additives_options else 0
            )
            additives = st.selectbox(
                "Additives",
                additives_options,
                index=additives_options.index(default_additives)
                if default_additives in additives_options
                else default_add_index
            )

            # --- METADATA FOR ADDITIVES ---
            # Look up metadata for the selected additive and display it
            meta = menu.get_metadata("additives", additives)
            if meta:
                st.info(
                    f"**Description:** {meta['description']}\n\n"
                    f"**Sustainability:** {meta['sustainability_info']}"
                )

            # Quantity of items to order
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1,
                value=default_quantity
            )

            # Show additive parts input only if additive is not "None"
            show_parts = additives.lower() != "none"
            additive_parts = 0
            if show_parts:
                additive_parts = st.number_input(
                    "Additive Parts",
                    min_value=0,
                    step=1,
                    value=default_parts
                )
                # Show cost impact of additive parts
                if additive_parts > 0:
                    st.write(
                        f"+$0.10 per part. Total additional: ${(additive_parts * 0.10):.2f}"
                    )
                else:
                    st.write("+$0.10 per part.")

            # Submit button to review the order before saving
            submitted = st.form_submit_button("Review Order")

        # After form submission, build Paint object and move to confirmation step
        if submitted:
            size_name = parse_size_name(size_display)  # Extract size name from display
            order = Paint(
                st.session_state.artist,
                paint_base,
                size_name,
                additives,
                additive_parts
            )
            order.calculate_cost(menu)  # Compute cost based on menu prices
            # Store order + quantity in session for confirmation step
            st.session_state.current_order_for_confirmation = (order, quantity)
            st.rerun()

        # If there is an order awaiting confirmation, show confirmation UI
        if st.session_state.current_order_for_confirmation is not None:
            order, quantity = st.session_state.current_order_for_confirmation
            st.subheader("Confirm Order")
            st.code(str(order))  # Show textual representation of the order

            # NEW PRICE BREAKDOWN: show per-item and total cost
            price_per_item = order.get_cost()
            total_price = price_per_item * quantity

            st.subheader("Price Breakdown")
            st.write(f"**Price per item:** ${price_per_item:.2f}")
            st.write(f"**Total for {quantity} items:** ${total_price:.2f}")

            st.write(f"Quantity: {quantity}")

            # Two-column layout for Confirm and Cancel buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm and Save"):
                    # Save order to DB with chosen quantity
                    save_order(order, quantity=quantity)
                    # Clear duplicate_order state after saving
                    st.session_state.duplicate_order = None
                    st.success("Order saved!")
                    st.rerun()

            with col2:
                if st.button("Cancel Order"):
                    # Cancel current confirmation and clear duplicate state
                    st.session_state.duplicate_order = None
                    st.info("Order cancelled.")
                    st.rerun()

    # ---------------------- View Orders ----------------------
    elif action == "View Orders":
        st.header("View Orders")

        # --- FILTER UI ---
        # Text input to filter by artist name (first or last)
        search_artist = st.text_input("Search by artist name")

        # Build list of unique paint bases from current DB for filter dropdown
        all_orders_for_filter = load_orders()  # Load all orders without filters
        unique_bases = sorted(list({o.get_paint_base() for o in all_orders_for_filter}))
        filter_paint_base = st.selectbox("Filter by paint base", ["All"] + unique_bases)

        # Load orders using the selected filters
        orders = load_orders(search_artist, filter_paint_base)

        if not orders:
            # If no orders match filters, offer to place a new one
            st.info("No orders found. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            # Build a simple table representation of orders for display
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

            # Show orders in a dataframe
            st.dataframe(data)

            # --- BASIC REPORTING SECTION ---
            st.subheader("Summary & Reporting")

            # Metric: total number of orders currently displayed
            st.metric("Total Orders Displayed", len(orders))

            # Build summary of total units per paint base
            summary = {}
            for order in orders:
                base = order.get_paint_base()
                qty = getattr(order, "_quantity", 1)
                summary[base] = summary.get(base, 0) + qty

            # Convert summary dict into a list of rows for dataframe
            summary_rows = [{"Paint Base": base, "Total Units": qty} for base, qty in summary.items()]

            # Show summary table
            st.dataframe(summary_rows)

            # Quick action buttons for each order (Edit, Delete, Duplicate)
            st.subheader("Quick Actions")
            for i, order in enumerate(orders):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    st.write(f"Order {i+1}: {data[i]['Item']} (Qty: {data[i]['Quantity']})")
                with col2:
                    if st.button(f"Edit {i+1}", key=f"edit_{i}"):
                        # Set edit_index and switch to Update Order view
                        st.session_state.edit_index = i
                        st.session_state.action = "Update Order"
                        st.rerun()
                with col3:
                    if st.button(f"Delete {i+1}", key=f"delete_{i}"):
                        # Set delete_index and switch to Delete Order view
                        st.session_state.delete_index = i
                        st.session_state.action = "Delete Order"
                        st.rerun()
                with col4:
                    if st.button(f"Duplicate {i+1}", key=f"duplicate_{i}"):
                        # Store order details in session to pre-fill Place Order form
                        st.session_state.duplicate_order = {
                            "paint_base": order.get_paint_base(),
                            "size": order.get_size(),
                            "additives": order.get_additives(),
                            "additive_parts": order.get_additive_parts(),
                            "quantity": getattr(order, "_quantity", 1),
                        }
                        st.session_state.action = "Place Order"
                        st.rerun()

    # ---------------------- Update Order ----------------------
    elif action == "Update Order":
        st.header("Update Order")

        # Use cached orders if available, otherwise load from DB
        orders = st.session_state.orders or load_orders()

        if not orders:
            # If no orders exist, suggest placing a new one
            st.info("No orders to update. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            idx = st.session_state.edit_index
            if idx is None or idx >= len(orders):
                # If no order is selected for editing, instruct user to pick from View Orders
                st.info("Select an order to update from View Orders.")
            else:
                order = orders[idx]
                st.write(f"Updating: {order}")

                # Prepare size options and current size display string
                size_price_map = get_size_price_map()
                size_options = size_display_options()
                current_size_display = f"{order.get_size()} - ${size_price_map.get(order.get_size(), '0.00')}"

                # Update form for editing an existing order
                with st.form("update_form"):
                    # Paint base selection (pre-filled with current value)
                    paint_base = st.selectbox(
                        "Paint Base",
                        menu.get_paint_base(),
                        index=menu.get_paint_base().index(order.get_paint_base())
                        if order.get_paint_base() in menu.get_paint_base() else 0,
                    )

                    # --- METADATA FOR PAINT BASE (UPDATE) ---
                    # Show metadata for the selected paint base in update mode
                    meta = menu.get_metadata("paint_base", paint_base)
                    if meta:
                        st.info(
                            f"**Description:** {meta['description']}\n\n"
                            f"**Sustainability:** {meta['sustainability_info']}"
                        )

                    # Size selection (pre-filled with current size)
                    size_index = size_options.index(current_size_display) if current_size_display in size_options else 0
                    size_display = st.selectbox("Size", size_options, index=size_index)

                    # Additives selection (pre-filled with current additive)
                    additives_options = menu.get_additives()
                    add_index = (
                        additives_options.index(order.get_additives())
                        if order.get_additives() in additives_options
                        else (additives_options.index("None") if "None" in additives_options else 0)
                    )
                    additives = st.selectbox("Additives", additives_options, index=add_index)

                    # --- METADATA FOR ADDITIVES (UPDATE) ---
                    # Show metadata for the selected additive in update mode
                    meta = menu.get_metadata("additives", additives)
                    if meta:
                        st.info(
                            f"**Description:** {meta['description']}\n\n"
                            f"**Sustainability:** {meta['sustainability_info']}"
                        )

                    # Quantity input (pre-filled with existing quantity)
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        step=1,
                        value=getattr(order, "_quantity", 1),
                    )

                    # Additive parts input shown only if additive is not "None"
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

                    # Submit button to review updated order
                    submitted = st.form_submit_button("Review Updated Order")

                # After submission, build updated Paint object and show confirmation
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
                            # Use attached _id to update the correct DB row
                            order_id = getattr(order, "_id", None)
                            if order_id is None:
                                st.error("Could not determine order ID for update.")
                            else:
                                update_order_in_db(order_id, updated_order, quantity=quantity)
                                st.success("Order updated!")
                                # Clear cached orders and edit index, then rerun
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

        # Use cached orders if available, otherwise load from DB
        orders = st.session_state.orders or load_orders()

        if not orders:
            # If no orders exist, suggest placing a new one
            st.info("No orders to delete. Would you like to place a new order?")
            if st.button("Place Order"):
                st.session_state.action = "Place Order"
                st.rerun()
        else:
            idx = st.session_state.delete_index
            if idx is None or idx >= len(orders):
                # If no order is selected for deletion, instruct user to pick from View Orders
                st.info("Select an order to delete from View Orders.")
            else:
                order = orders[idx]
                st.write(f"Deleting: {order}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Delete"):
                        # Use attached _id to delete the correct DB row
                        order_id = getattr(order, "_id", None)
                        if order_id is None:
                            st.error("Could not determine order ID for deletion.")
                        else:
                            delete_order_from_db(order_id)
                            st.success("Order deleted.")
                            # Clear cached orders and delete index, then rerun
                            st.session_state.orders = None
                            st.session_state.delete_index = None
                            st.rerun()
                with col2:
                    if st.button("Cancel Delete"):
                        st.info("Delete cancelled.")
                        st.session_state.delete_index = None
                        st.rerun()
