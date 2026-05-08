import sqlite3

class PaintMenu:
    """
    PaintMenu loads paint bases, sizes, additives, and metadata from the database.
    Provides fast lookup for UI dropdowns and metadata display.
    """

    def __init__(self):
        # Lists used by the UI
        self.paint_base = []
        self.size = []
        self.additives = []
        self.additive_parts = []

        # Metadata lookup table:
        # metadata[category][name] = {description, sustainability_info, origin}
        self.metadata = {
            "paint_base": {},
            "size": {},
            "additives": {}
        }

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
    # Metadata lookup
    # -------------------------
    def get_metadata(self, category, name):
        """
        Returns metadata for a given menu item.
        """
        return self.metadata.get(category, {}).get(name, None)

    # -------------------------
    # Load menu from SQLite DB
    # -------------------------
    @classmethod
    def from_db(cls, db_path):
        menu = cls()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, name, price, additive_parts, description, sustainability_info, origin
            FROM menu_items
        """)
        rows = cursor.fetchall()
        conn.close()

        for category, name, price, parts, desc, sustain, origin in rows:

            # Populate UI lists
            if category == "paint_base":
                menu.paint_base.append(name)

            elif category == "size":
                # Store size as "Small: 1.50"
                menu.size.append(f"{name}: {price:.2f}")

            elif category == "additives":
                menu.additives.append(name)
                menu.additive_parts.append(parts)

            # Store metadata
            menu.metadata[category][name] = {
                "description": desc or "",
                "sustainability_info": sustain or "",
                "origin": origin or ""
            }

        return menu

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
