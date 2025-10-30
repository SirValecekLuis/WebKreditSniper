class Meal:
    def __init__(self, meal_data: dict):
        meal_data = meal_data.get("item", {})
        self.name = meal_data.get("mealName", None)
        self.number = meal_data.get("altId", None)
        self.available = meal_data.get("countAvailable", None)
        self.ordered_total = meal_data.get("countOrdered", None)
        self.alergens = meal_data.get("note", None)
        self.in_exchange = meal_data.get("inExchange", None)

        if self.name is None or self.number is None or self.ordered_total is None:
            raise ValueError("Jídlo obsahuje neplatné informace, prosím, kontaktuje vývojáře.")

    def __str__(self):
        return f"Jídlo {self.number}: {self.name} | Počet dostupných jídel: {self.available if self.available is not None else 'neomezeno'} | Objednáno porcí celkem: {self.ordered_total} | Alergeny: {self.alergens} | Je na burze: {'ano' if self.in_exchange else 'ne'}"
