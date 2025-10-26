import requests
import time

from datetime import datetime, time, timedelta


class Meal:
    def __init__(self, meal_data: dict):
        meal_data = meal_data.get("item", {})
        self.name = meal_data.get("mealName", "Neznámé jídlo")
        self.number = meal_data.get("altId", None)
        self.available = meal_data.get("countAvailable", None)
        self.ordered_total = meal_data.get("countOrdered", None)
        self.alergens = meal_data.get("note", "")

    def __str__(self):
        return f"Jídlo {self.number}: {self.name} | Počet dostupných jídel: {self.available} | Objednáno porcí celkem: {self.ordered_total} | Alergeny: {self.alergens}"


def get_time_for_day(year, month, day) -> str:
    local_date_str = f"{year}-{int(month):02}-{int(day):02}"
    local_date = datetime.strptime(local_date_str, "%Y-%m-%d")

    last_sunday_march = max(
        datetime(year, 3, d) for d in range(25, 32) if datetime(year, 3, d).weekday() == 6
    )
    last_sunday_october = max(
        datetime(year, 10, d) for d in range(25, 32) if datetime(year, 10, d).weekday() == 6
    )

    if last_sunday_march <= local_date < last_sunday_october:
        offset = timedelta(hours=2)
    else:
        offset = timedelta(hours=1)

    local_midnight = datetime.combine(local_date, time(0, 0, 0))
    utc_time = local_midnight - offset

    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")


def get_webkredit_url() -> str:
    day, month, year = None, None, None
    while True:
        date = input("Zadejte datum ve formátu 'den.měsíc.rok', takže např. 17.5.2026: ").strip().strip('"').strip("'")
        if '.' not in date:
            print("Neplatný formát data. Zkuste to znovu.")
            continue

        day, month, year = date.split('.', 2)
        if not (day.isdigit() and month.isdigit() and year.isdigit()):
            print("Den a měsíc a rok musí být čísla. Zkuste to znovu.")
            continue

        day, month, year = int(day), int(month), int(year)
        if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2024):
            print("Den, měsíc nebo rok jsou mimo platný rozsah. Zkuste to znovu.")
            continue

        break

    return f"https://stravovani.vsb.cz/webkredit/Api/Ordering/Menu?Dates={get_time_for_day(year, month, day)}&CanteenId=1"


def get_meal_numbers() -> list:
    while True:
        numbers = input("Zadejte čísla jídel, která chcete sledovat (oddělená mezerami, např. '1 2 3'): ").strip()
        meal_numbers = numbers.split()
        if meal_numbers:
            try:
                map(int, meal_numbers)
                return meal_numbers
            except ValueError:
                print("Čísla jídel musí být platná čísla. Zkuste to znovu.")
        print("Zadejte alespoň jedno číslo jídla.")


def get_meals(url: str) -> list:
    response = requests.get(url)
    food = []

    if response.status_code != 200:
        return food

    for types in response.json().get("groups", []):
        for meal in types.get("rows", []):
            if meal.get("item", {}).get("mealKindName") == "Oběd":
                food.append(Meal(meal))

    return food


def check_meals(url: str, meal_numbers: list[int]) -> None:
    while True:
        meals = get_meals(url)
        for meal in meals:
            if meal.number in meal_numbers:
                print(meal)
            print("----")

        time.sleep(10)


def main():
    url = get_webkredit_url()
    meal_numbers = get_meal_numbers()
    check_meals(url, meal_numbers)


if __name__ == "__main__":
    main()
