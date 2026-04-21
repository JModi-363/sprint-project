import datetime  # Import the datetime library to timestamp our reports

"""
ASSIGNMENT 13B: SPRINT 6
PROJECT: Art Center Mural Order System
DEVELOPER: Jeet Modi
"""

# GLOBAL CONSTANTS: Pantry Rules
MENU_FILE = "paint_menu.txt"
DATA_FILE = "order_history.txt"
HUMAN_REPORT = "human_report.txt"
TAX_RATE = 0.05


def get_customer_info():
    """Asks for name and office location."""
    while True:
        first_name = input("Enter your first name: ").lower().strip().title()
        if first_name:
                break
        else:
                print("Please enter your first name.")
    
    while True:
        last_name = input("Enter your last name: ").lower().strip().title()
        if last_name:
                break
        else:
                print("Please enter your last name.")

    while True:
        location = input("Enter your studio number: ").strip().upper()
        if location:
            break
        else:
            print("Please enter a studio number.")

    customer = f"{first_name} {last_name}"
    return first_name, last_name, customer, location

def take_order():
    """Reads the menu from file and collects choices."""
    print("\n--- PAINT ORDER ---")
    # Defaults
    paint_base = "Acrylic"
    size = "Small"
    additives = "None"
    additive_parts = 0
    try:
        with open(MENU_FILE, "r") as f:
            for line in f:
                print(line.strip())

        paint_base = input("\nPaint Base: ").strip().lower().title()
        size = input("Size: ").strip().lower().title()
        additives = input("Additives: ").strip().lower().title()
        if additives == "None":
            additive_parts = 0
            pass
        else:
            try:
                additive_parts = int(input("How many parts? "))
            except ValueError:
                additive_parts = 0
    
    except FileNotFoundError:
        print("Menu file not found. Accepting default values.")
        paint_base = "Acrylic"
        size = "Small"
        additives = "None"
        additive_parts = 0
    
    return {"paint_base": paint_base, "size": size, "additives": additives, "additive_parts": additive_parts}

def calculate_total(order_data):
    """Calculates price by reading menu.txt."""
    base_price = 4.00
    with open(MENU_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if parts[0] == order_data["paint_base"]:
                if order_data["size"] == "Small": base_price = float(parts[1])
                elif order_data["size"] == "Medium": base_price = float(parts[2])
                else: base_price = float(parts[3])

    parts_cost = order_data["additive_parts"] * 0.10
    subtotal = base_price + parts_cost
    tax_amt = subtotal * TAX_RATE
    return subtotal + tax_amt, tax_amt

'''
class PaintOrder:
    """A modular blueprint that groups all paint variables into one unit."""
    
    def __init__(self, customer, paint_base, size, additives, additive_parts):
        self.customer = customer
        self.paint_base = paint_base
        self.size = size
        self.additives = additives
        self.additive_parts = additive_parts

    # --- SETTERS: Preparation for next week's editing ---
    def set_paint_base(self, new_paint_base):
        self.paint_base = new_paint_base

    def set_size(self, new_size):
        self.size = new_size

    def set_additives(self, new_additives):
        self.additives = new_additives

    def set_additive_parts(self, new_parts):
        self.additive_parts = new_parts

    def get_total(self):
        base = 4.00
        return base + (self.additive_parts * 0.10)

    def display_order(self):
        print("\n--- CURRENT ORDER DETAILS ---")
        print(f"[1] Customer: {self.customer}")
        print(f"[2] Paint Base: {self.paint_base}")
        print(f"[3] Size:     {self.size}")
        print(f"[4] Additives: {self.additives}")
        print(f"[5] Additive Parts: {self.additive_parts}")
        print(f"Total: ${self.get_total():.2f}")
'''

def save_data_and_label(customer, location, total, tax):
    """Saves raw data to log and overwrites a human receipt file."""
    with open(DATA_FILE, "a") as f:
        f.write(f"{customer},{location},{total:.2f}\n")
    
    with open(HUMAN_REPORT, "w") as f:
        f.write(f"ORDER TICKET - {datetime.date.today()} {datetime.datetime.now().strftime('%H:%M:%S')} \n")
        f.write(f"STUDIO: {location} | ATTN: {customer}\n")
        f.write(f"TAX: ${tax:.2f} | TOTAL: ${total:.2f}\n")

def print_data_and_label(customer, location, total, tax):
    """Prints the order details."""
    print(f"ORDER TICKET - {datetime.date.today()} {datetime.datetime.now().strftime('%H:%M:%S')} \n")
    print(f"STUDIO: {location} | ATTN: {customer}")
    print(f"TAX: ${tax:.2f} | TOTAL: ${total:.2f}")

def main():
    first_name, last_name, customer, location = get_customer_info()
    current_order = take_order()
    final_price, calculated_tax = calculate_total(current_order)
    save_data_and_label(customer=customer, location=location, total=final_price, tax=calculated_tax)
    print(f"\nUpdated Files {DATA_FILE} and {HUMAN_REPORT}.")
    print_data_and_label(customer=customer, location=location, total=final_price, tax=calculated_tax)

main()