"""
ASSIGNMENT 9B: SPRINT 2 - FUNCTIONAL STUBS
Project: Art Center Mural Order System (V1.0)
Developer: Jeet Modi
"""

# GLOBAL CONSTANTS (Pantry Rules)
MENU_FILE = "size_options.txt"
PAINT_OPTIONS = ("Acrylic", "Oil", "Watercolor", "Tempera", "Gouache")

def get_customer_info():
    """Asks for name and studio location."""
    # TODO: Ask for name and delivery location.
    name = input("Enter your name: ").title().strip()
    location = input("Enter your studio number: ").strip().upper()
    return name, location

def take_order():
    """Collects base, size, additive, and parts. Returns data."""
    # TODO: Capture base (Acrylic/Oil/Watercolor/Tempera/Gouache) and category (Coffee/Tea/Cocoa)
    while True:
        base = input(f"Select a paint base: {', '.join(PAINT_OPTIONS)}\n").strip().title()
        if base in PAINT_OPTIONS:
            break
        else:
            print("Invalid input. Please select a valid paint base option.")

    while True:
        size = input("Select a size:\nSmall\nMedium\nLarge\n").strip().lower()
        if size in ['small', 'medium', 'large']:
            break
        else:
            print("Invalid input. Please select a valid size option.")

def calculate_total(order_data):
    """Calculates price based on size and parts."""
    # TODO: Load prices from menu.txt
    return 2.20

def save_data_and_label(customer, total):
    """Appends to order_history.txt and prints the human-readable label."""
    # TODO: Write raw data for computer and formatted box.
    pass

def main():
    # 1. Identity Phase
    name, location = get_customer_info()
    print(f"Customer: {name} | Location: Studio #{location}")

    # 2. Data Collection Phase
    current_order = take_order()

    # 3. Calculation Phase
    final_price = calculate_total(current_order)

    # 4. Handoff Phase
    save_data_and_label(name, final_price)

main()