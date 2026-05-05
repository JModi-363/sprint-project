import sqlite3

class PaintMenu:
    """
    PaintMenu loads paint bases, sizes, and additives from the database.
    """

    def __init__(self, paint_base, size, additives, additive_parts=None):
        self.paint_base = paint_base            # list[str]
        self.size = size                        # list[str] like "Small: 1.50"
        self.additives = additives              # list[str]
        self.additive_parts = additive_parts or []  # optional list

    # -------------------------
    # Getter methods
    # -------------------------
    def get_paint_base(self):
        return self.paint_base

    def get_size(self):
        return self.size

    def get_additives(self):
        return self.additives

    def get_additive_parts(self):
        return self.additive_parts

    # -------------------------
    # Load menu from SQLite DB
    # -------------------------
    @classmethod
    def from_db(cls, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Helper to fetch rows by category
        def fetch(category):
            cursor.execute(
                "SELECT name, price FROM menu_items WHERE category = ?",
                (category,)
            )
            return cursor.fetchall()

        # Paint bases (no price)
        paint_base = [row[0] for row in fetch("paint_base")]

        # Sizes (name + price)
        size_rows = fetch("size")
        size = [f"{name}: {price:.2f}" for name, price in size_rows]

        # Additives (no price)
        additives = [row[0] for row in fetch("additives")]

        conn.close()

        return cls(
            paint_base=paint_base,
            size=size,
            additives=additives,
            additive_parts=[]
        )

    # -------------------------
    # String representation
    # -------------------------
    def __str__(self):
        return (
            f"Paint Base: {self.paint_base}\n"
            f"Size: {self.size}\n"
            f"Additives: {self.additives}\n"
            f"Additive Parts: {self.additive_parts}"
        )
