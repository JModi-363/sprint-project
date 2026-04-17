""" 
    Demonstrate classes and objects based on the Montycoffeeural project paint order system.
"""

class Artist:
    # class names are capitalized
    def __init__(self, fname, lname, location):
        # 🔐 These are the attributes of our class.
        # The double underscore `__` makes them "private".
        # This means they are intended to be accessed only from within this class.
        self.__fname = fname
        self.__lname = lname
        self.__location = location

    #  setters ✍️
    # A "setter" method is used to change the value of a private attribute.
    def set_fname(self, fname):
        self.__fname = fname

    def set_lname(self, lname):
        self.__lname = lname

    def set_location(self, location):
        self.__location = location

    # getters 📥
    # A "getter" method is used to retrieve the value of a private attribute.
    def get_fname(self):
        return self.__fname.lower().title()

    def get_lname(self):
        return self.__lname.lower().title()

    def get_location(self):
        return self.__location.upper()

    # 💬 __str__ method
    # This is a special "magic method" in Python.
    # It returns a user-friendly string representation of the object.
    # Instead of creating a custom `description()` method, using __str__
    # lets us just `print(my_employee_object)` to see its details.
    def __str__(self):
        return (
            f"Artist: {self.__fname} {self.__lname}\n"
            f"Location: {self.__location}\n"
        )

    # 🏭 @classmethod
    # This is a special kind of method that is bound to the class, not the instance.
    # We can call it on the class itself: `Employee.from_input()`
    # It's often used as a "factory" to create instances in different ways.
    # Here, we're using it to create an Employee object from user input.
    @classmethod
    def from_input(cls):
        """Factory method to create an Employee object from user input."""
        print("Please enter artist details.")
        fname = input("Enter your first name: ")
        lname = input("Enter your last name: ")
        location = input("Enter the studio number of the delivery location: ")

        # `cls` here refers to the class itself (Employee).
        # So, `cls(fname, lname, extension, emp_num)` is the same as
        # `Employee(fname, lname, extension, emp_num)`.
        return cls(fname, lname, location)

'''
# --- Test Area ---
# It's a good practice to have a small test block like this.
# The `if __name__ == "__main__":` part means this code will only run
# when you execute this file directly (e.g., `python Employee.py`),
# not when it's imported into another file.
if __name__ == "__main__":
    # Create an employee the "classic" way by passing arguments
    artist_1 = Artist("Elena", "Thorne", "112A")
    print("--- Testing direct instantiation ---")
    print(artist_1)  # This will automatically call the __str__ method!

    # Now, let's test our new factory method!
    print("\n--- Testing from_input() factory method ---")
    artist_from_input = Artist.from_input()
    print("\nArtist object created from input:")
    print(artist_from_input)  # This also calls __str__
'''