"""
    creating the paint order class for mural projects
"""

#  importing the other classes we will need
import os
from datetime import datetime
from Artist import Artist
from PaintMenu import PaintMenu


class Paint:
    # ☕ The __init__ method is the constructor for our class.
    # It's called when we create a new Paint order object.
    # We've added the artist who is ordering and a timestamp.
    def __init__(
        self, artist, paint_base, size, additives, additive_parts
    ):
        # --- Private Attributes 🔐 ---
        self.__artist = artist  # The Artist object
        # Automatically set to the current time
        self.__timestamp = datetime.now()
        self.__paint_base = paint_base
        self.__size = size
        self.__additives = additives
        self.__additive_parts = additive_parts
        self.__cost = 0.0  # Cost is calculated *after* creation.

    # --- Getters 📥 ---
    # These methods safely get the values of our private attributes.
    def get_artist(self):
        return self.__artist

    def get_timestamp(self):
        return self.__timestamp

    def get_paint_base(self):
        return self.__paint_base

    def get_size(self):
        return self.__size

    def get_additives(self):
        return self.__additives

    def get_additive_parts(self):
        return self.__additive_parts

    def get_cost(self):
        return self.__cost

    # --- Setters ✍️ ---
    # Setters are less common when logic is handled by other methods,
    # but they are included here for completeness.
    def set_paint_base(self, paint_base):
        self.__paint_base = paint_base

    def set_size(self, size):
        self.__size = size

    def set_additives(self, additives):
        self.__additives = additives

    def set_additive_parts(self, additive_parts):
        self.__additive_parts = additive_parts

    def set_cost(self, cost):
        self.__cost = cost

    # --- Magic Method: __str__ 💬 ---
    # This replaces the old `get_summary()` method.
    # It provides a user-friendly receipt of the order.
    def __str__(self):
        # The .strftime() method formats the timestamp into a readable string.
        formatted_time = self.__timestamp.strftime("%Y-%m-%d %I:%M %p")
        # The :.2f formats the cost to two decimal places (like money).
        artist_name = f"{self.__artist.get_fname()} {self.__artist.get_lname()}"
        return (
            f"---- RECEIPT ----\n"
            f"Order for: {artist_name}\n"
            f"Time: {formatted_time}\n"
            f"-----------------------\n"
            f"Item: {self.__size} {self.__paint_base}\n"
            f" - Additives: {self.__additives} ({self.__additive_parts})\n"
            f"-----------------------\n"
            f"TOTAL: ${self.__cost:.2f}\n"
            f"-----------------------"
        )

    # --- Main Logic Methods ---

    def calculate_cost(self, menu: PaintMenu):
        """
        🧮 FINAL LOGIC: Calculates the total cost of the paint order.
        - Base price is from the SIZE.
        - Upcharge is from additive parts.
        """
        base_price = 0.0
        # Find the price for the selected size.
        # The menu.prices is a list like ['Small: 3.00', 'Medium: 4.00']
        for price_entry in menu.get_size():
            size_name, price_str = price_entry.split(':')
            if size_name.strip().lower() == self.__size.lower():
                base_price = float(price_str.strip())
                break  # Found the price, no need to look further

        # Add cost for additives: $0.10 per additive part (integer)
        additives_upcharge = 0.0
        if self.__additives.lower() != "none" and self.__additive_parts:
            additives_upcharge = self.__additive_parts * 0.10

        # Set the final cost on the object
        self.__cost = base_price + additives_upcharge

    def save(self):
        """💾 Saves the completed order to the orders.txt file."""
        # --- PATH CORRECTION ---
        # Build a robust path to 'orders.txt' inside the 'MontysOOP' folder.
        # os.path.dirname(__file__) gets the directory of this script.
        # os.path.join() creates a correct path for any OS.
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, "orders.txt")

        # Format the order string to be saved in the file.
        # Record artist full name and location since Artist has no emp_num
        artist_name = f"{self.__artist.get_fname()} {self.__artist.get_lname()}"
        artist_location = self.__artist.get_location()
        order_string = (
            f"{artist_name},{artist_location},{self.__timestamp.isoformat()},"
            f"{self.__paint_base},{self.__size},"
            f"{self.__additives},{self.__additive_parts},{self.__cost:.2f}\n"
        )
        try:
            # Use the full, correct path to open the file.
            with open(file_path, "a") as f:  # 'a' for append mode
                f.write(order_string)
            print("Order saved successfully.")
        except IOError as e:
            print(f"Error saving order: {e}")

    # --- Factory Classmethod 🏭 ---
    @classmethod
    def from_input(cls, artist: Artist, menu: PaintMenu):
        """
        CORRECTED LOGIC: Factory method to create a Paint order.
        It asks for paint base, then size, additives, and number of parts.
        """
        print("\nStarting new order.")

        # --- 1. Choose Paint Base ---
        print("\n--- Paint Options ---")
        # We use enumerate to get a number for each item (e.g., 1. Latte)
        paint_options = menu.get_paint_base()
        for i, item in enumerate(paint_options):
            print(f"  {i+1}. {item}")
        while True:
            try:
                choice = int(input("Select a paint base: "))
                if 1 <= choice <= len(paint_options):
                    paint_type = paint_options[choice - 1]
                    break
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # --- 2. Choose Size ---
        print("\n--- Size Options ---")
        size_options = [s.split(':')[0].strip() for s in menu.get_size()]
        for i, item in enumerate(size_options):
            print(f"  {i+1}. {item}")
        while True:
            try:
                choice = int(input("Select a size: "))
                if 1 <= choice <= len(size_options):
                    size = size_options[choice - 1]
                    break
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")


        # --- 3. Choose Additives ---
        print("\n--- Additive Options ---")
        additives_options = menu.get_additives()
        for i, item in enumerate(additives_options):
            print(f"  {i+1}. {item}")
        while True:
            try:
                choice = int(input("Select an additive (or 'None'): "))
                if 1 <= choice <= len(additives_options):
                    additives = additives_options[choice - 1]
                    break
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # --- 4. Choose Parts Additive (integer parts) ---
        # New behavior: ask for an integer number of parts (>= 0).
        additive_parts = 0
        if additives.lower() != "none":
            print(
                "\nEnter number of additive parts (+$0.10 per part)."
            )
            while True:
                try:
                    parts_input = input("How many parts? ").strip()
                    additive_parts = int(parts_input)
                    if additive_parts >= 0:
                        break
                    else:
                        print("Please enter a non-negative integer.")
                except ValueError:
                    print("Invalid input. Please enter a whole number.")

        # Now we have all the info to create a temporary object.
        new_order = cls(artist, paint_type, size, additives, additive_parts)

        # Use the object's own method to calculate its cost based on the menu.
        new_order.calculate_cost(menu)

        # Return the fully formed, ready-to-go Paint order object.
        return new_order


# --- Test Area ---
'''
if __name__ == "__main__":
    print("--- 🧪 Testing Coffee Class 🧪 ---")

    # We need a mock Artist and PaintMenu to test.
    test_emp = Artist("Testy", "McTesterson", "1234")

    # --- PATH CORRECTION for testing ---
    # Build a robust path to 'menu.txt' for the test run.
    script_dir = os.path.dirname(__file__)
    menu_file_path = os.path.join(script_dir, "menu.txt")

    try:
        # Use the full, correct path to load the menu.
        test_menu = PaintMenu.from_file(menu_file_path)

        if test_menu:  # Proceed only if menu loaded successfully
            # 1. Test the from_input() factory method
            print("\n--- 1. Testing from_input() ---")
            # This will prompt you to enter an order in the terminal.
            my_order = Paint.from_input(test_emp, test_menu)

            # 2. Test the __str__() method (the receipt)
            print("\n--- 2. Testing __str__() ---")
            print(my_order)

            # 3. Test the save() method
            print("\n--- 3. Testing save() ---")
            my_order.save()
            print("Check 'MontysOOP/orders.txt' to see if the order was saved.")
        else:
            print("\n🔥 ERROR: Could not load menu. Aborting tests.")

    except FileNotFoundError:
        print(
            f"\n🔥 ERROR: '{menu_file_path}' not found. "
            "Cannot run tests without the menu file."
        )
'''