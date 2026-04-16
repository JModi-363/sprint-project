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