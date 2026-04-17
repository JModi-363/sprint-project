"""
    Menu Class
    Reads menu.txt and stores each section as a list of strings.
    This is an example of a class that handles file reading
    and organizes data into easy-to-use attributes.
"""
import os


class PaintMenu:
    """
    A Menu object holds all the menu sections for Monty's Coffee.
    Each section is stored as a list of strings.

    Example usage:
        menu = Menu.from_file("menu.txt")
        print(menu.coffee)   # ['Espresso', 'Americano', ...]
        print(menu.prices)   # ['Small: 3.00', 'Medium: 4.00', ...]
    """

    def __init__(self, paint_base, size, additives, additive_parts):
        """
        The constructor sets up all the menu sections as attributes.
        Each attribute is a list of strings.
        'self' refers to this specific Menu object.
        """
        self.paint_base = paint_base    # List of paint base types
        self.size = size    # List of sizes and prices e.g. 'Small: 3.00'
        self.additives = additives      # List of additive options
        self.additive_parts = additive_parts      # List of pump options e.g. 'Light: 3'

    # --- Getter methods for OOP encapsulation ---
    def get_paint_base(self):
        return self.paint_base

    def get_size(self):
        return self.size

    def get_additives(self):
        return self.additives

    def get_additive_parts(self):
        return self.additive_parts

    @classmethod
    def from_file(cls, filename="paint_menu.txt"):
        """
        A classmethod that reads menu.txt and creates a Menu object.
        Each line in the file looks like:
            COFFEE ; Espresso, Americano, Latte, ...
        We split on ';' to get the header and the items,
        then split the items on ',' to get a list of strings.

        Usage:
            menu = Menu.from_file("menu.txt")
        """
        # Start with empty lists for each section
        menus = {}

        try:
            with open(filename, 'r') as file:
                for line in file:
                    # Skip blank lines
                    if ';' not in line:
                        continue

                    # Split each line into header and items
                    parts = line.strip().split(';')
                    header = parts[0].strip().upper()
                    # Split items by comma and strip extra spaces
                    items = [item.strip() for item in parts[1].split(',')]
                    menus[header] = items

            # Build and return the Menu object.
            # Accept a few common header synonyms from the data file.
            paint_base = menus.get("PAINT_BASE") or menus.get("BASES") or []
            size = menus.get("SIZE") or menus.get("PRICES") or []
            additives = menus.get("ADDITIVES") or []
            additive_parts = (
                menus.get("ADDITIVE_PARTS")
                or menus.get("PUMP_LEVELS")
                or []
            )
            return cls(
                paint_base=paint_base,
                size=size,
                additives=additives,
                additive_parts=additive_parts,
            )

        except FileNotFoundError:
            print(f"Error: '{filename}' was not found.")
            return None
        except Exception as e:
            print(f"An error occurred reading the menu: {e}")
            return None

    def __str__(self):
        """
        Defines what prints when you do print(menu).
        Lists each section and its options.
        """
        return (
            f"Paint Base:  {self.paint_base}\n"
            f"Size:  {self.size}\n"
            f"Additives:   {self.additives}\n"
            f"Additive Parts: {self.additive_parts}"
        )

'''
# Quick test - only runs if you run PaintMenu.py directly
if __name__ == "__main__":
    # Use a robust path to menu.txt in the same folder as this script
    script_dir = os.path.dirname(__file__)
    menu_file_path = os.path.join(script_dir, "paint_menu.txt")
    menu = PaintMenu.from_file(menu_file_path)
    if menu:
        print(menu)
'''