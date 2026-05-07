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
    # Metadata lookup
    # -------------------------
    def get_metadata(self, category, name):
        """
        Returns metadata for a given menu item.
        NOTE: This requires PaintMenu.from_db() to load metadata fields.
        """
        # If metadata isn't loaded yet, return None safely
        if not hasattr(self, "items"):
            return None

        for item in self.items:
            if item["category"] == category and item["name"] == name:
                return {
                    "description": item.get("description", ""),
                    "sustainability_info": item.get("sustainability_info", ""),
                    "origin": item.get("origin", "")
                }
        return None

    # -------------------------
    # Load menu from SQLite DB
    # -------------------------
@classmethod
def from_db(cls, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all menu items with metadata
    cursor.execute("""
        SELECT category, name, price, additive_parts, description, sustainability_info, origin
        FROM menu_items
    """)
    rows = cursor.fetchall()
    conn.close()

    # Prepare lists for the constructor
    paint_base = []
    size = []
    additives = []
    additive_parts = []

    # Store full metadata for lookup
    items = []

    for category, name, price, parts, desc, sustain, origin in rows:
        # Save metadata entry
        items.append({
            "category": category,
            "name": name,
            "price": price,
            "additive_parts": parts,
            "description": desc,
            "sustainability_info": sustain,
            "origin": origin
        })

        # Populate the lists used by the UI
        if category == "paint_base":
            paint_base.append(name)

        elif category == "size":
            size.append(f"{name}: {price:.2f}")

        elif category == "additives":
            additives.append(name)

        # Optional additive parts list
        if category == "additives":
            additive_parts.append(parts)

    # Create instance
    menu = cls(
        paint_base=paint_base,
        size=size,
        additives=additives,
        additive_parts=additive_parts
    )

    # Attach metadata to the instance
    menu.items = items

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
