"""
ASSIGNMENT 9B: SPRINT 2 - FUNCTIONAL STUBS
Project: Art Center Mural Order System (V1.0)
Developer: Jeet Modi
"""
import datetime

# GLOBAL CONSTANTS (Pantry Rules)

MENU_FILE = "size_options.txt"
HISTORY_FILE = "order_history.txt"
PAINT_OPTIONS = ("Acrylic", "Oil", "Watercolor", "Tempera", "Gouache")
ADDITIVES = ("Thickener", "Antioxidant", "Hardener", "Extender", "None")

PRICES = {
    "Small": 1.50,
    "Medium": 2.20,
    "Large": 3.00
}

'''
def lookup():
    first_name = input("Please enter first name: ")
    last_name = input("Please enter last name: ")
    extension = input("Please enter your extension: ")
    emp_num = input("Please enter your employee number: ")

    return first_name, last_name, extension, emp_num
'''

def get_customer_info():
    """Asks for name and studio location."""
    # TODO: Ask for name and delivery location.
    while True:
        name = input("Enter your name: ").title().strip()
        if name:
                break
        else:
                print("Please enter your name.")

    while True:
        location = input("Enter your studio number: ").strip().upper()
        if location:
            break
        else:
            print("Please enter a studio number.")

    return name, location

def take_order():
    """Collects base, size, additive, and parts. Returns data."""
    # TODO: Capture base (Acrylic/Oil/Watercolor/Tempera/Gouache) and category (Coffee/Tea/Cocoa)
    while True:
        base = input(f"\nSelect a paint base: {', '.join(PAINT_OPTIONS)}\n").strip().lower().title()
        if base in PAINT_OPTIONS:
            break
        else:
            print("Invalid input. Please select a valid paint base option.")

    while True:
        size = input(f"\nSelect a size:\n{chr(10).join(PRICES.keys())}\n").strip().lower().title()
        if size in PRICES:
            break
        else:
            print("Invalid input. Please select a valid size option.")

    while True:
        additive = input(f"\nSelect an additive: {', '.join(ADDITIVES)}\n").strip().lower().title()
        if additive in ADDITIVES and additive != "None":
            while True:
                parts = input("\nEnter the number of parts of additive to be added to the paint: ").strip()
                if parts.replace('.','',1).isdigit():
                    parts = float(parts)
                    break
                else:
                    print("Invalid input. Please enter a number.")
            break
        elif additive == "None":
                parts = 0
                break
        else:
            print("Invalid input. Please select a valid additive option.")

    return base, size, additive, parts

def calculate_total(order_data):
    """Calculates price based on size and parts."""
    # TODO: Load prices from menu.txt
    return 2.20

def save_data_and_label(name, location, size, base, additive, parts, total):
    while True:
        # Obtain timestamp
        timestamp = datetime.datetime.now()
        # Format the timestamp
        timestamp_str = timestamp.strftime("%m-%d-%Y %H:%M:%S")
        
        # Store in dictionary
        order_history = {
            "timestamp": timestamp_str,
            "file_name": HISTORY_FILE,
            "additive": additive,
            "parts": parts,
            "size": size,
            "base": base,
            "name": name,
            "location": location
        }

        with open(HISTORY_FILE, "a") as file:
            file.write(f"{timestamp_str}\nFile: {HISTORY_FILE}\nCustomer: {name} | Location: Studio #{location}\n)Order: {size} {base} with {parts} parts of {additive}\nTotal: ${total:.2f}\n")
        print("Order saved.\n")
        break
    """Appends to order_history.txt and prints the human-readable label."""
    # TODO: Write raw data for computer and formatted box.


def main():
    while True:
        # 1. Identity Phase
        name, location = get_customer_info()

        # 2. Data Collection Phase
        current_order = take_order()

        # 3. Calculation Phase
        final_price = calculate_total(current_order)

        # 4. Handoff Phase
        save_data_and_label(name, location, size, base, additive, parts, total)

        more_orders = input("Would you like to place another order? (Y/N): ").strip().upper()
        if more_orders == "N":
            break
        elif more_orders == "Y":
            pass
        else:
            print("Invalid input. Please enter Y or N.")

main()