"""
ASSIGNMENT 9B: SPRINT 2 - FUNCTIONAL STUBS
Project: Art Center Mural Order System (V1.0)
Developer: Jeet Modi
"""

# GLOBAL CONSTANTS (Pantry Rules)

MENU_FILE = "size_options.txt"
PAINT_OPTIONS = ("Acrylic", "Oil", "Watercolor", "Tempera", "Gouache")
ADDITIVES = ("Thickener", "Antioxidant", "Hardener", "Extender", "None")

PRICES = {
    "Small": 1.50,
    "Medium": 2.20,
    "Large": 3.00
}

def lookup():
    first_name = input("Please enter first name: ")
    last_name = input("Please enter last name: ")
    extension = input("Please enter your extension: ")
    emp_num = input("Please enter your employee number: ")

    return first_name, last_name, extension, emp_num

def options():
    # Options to order, print label, see history
    num = 1
    base = 3
    for base in PAINT_OPTIONS:
        print(f"{num}. {base}")
        num += 1

    num = 1
    for size, price in PRICES.items():
        print(f"Size: {size:12} | Price: ${price:.2f}")
        num += 1

    try:
        base = int(input("enter the number of your drink order: "))
        size = int(input("enter the number of your size order: "))
        return base, size

    except Exception as e:
        print("drink type [e]")

def read_orders():
    # Saved orders from text file

def save_orders():
    # Save order under username and date

def print_labels():
    
def calculate_cost():

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
