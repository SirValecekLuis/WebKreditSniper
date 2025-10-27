import requests
import datetime

from webkredit.models import Meal


def get_time_for_day(year, month, day) -> str:
    local_date_str = f"{year}-{int(month):02}-{int(day):02}"
    local_date = datetime.datetime.strptime(local_date_str, "%Y-%m-%d")

    last_sunday_march = max(
        datetime.datetime(year, 3, d) for d in range(25, 32) if datetime.datetime(year, 3, d).weekday() == 6
    )
    last_sunday_october = max(
        datetime.datetime(year, 10, d) for d in range(25, 32) if datetime.datetime(year, 10, d).weekday() == 6
    )

    if last_sunday_march <= local_date < last_sunday_october:
        offset = datetime.timedelta(hours=2)
    else:
        offset = datetime.timedelta(hours=1)

    local_midnight = datetime.datetime.combine(local_date, datetime.time(0, 0, 0))
    utc_time = local_midnight - offset

    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")


def cli_get_day() -> tuple[int, int, int]:
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

    return year, month, day


def get_webkredit_url(year, month, day) -> str:
    return f"https://stravovani.vsb.cz/webkredit/Api/Ordering/Menu?Dates={get_time_for_day(year, month, day)}&CanteenId=1"


def cli_get_meal_numbers() -> list[int]:
    while True:
        numbers = input("Zadejte čísla jídel, která chcete sledovat (oddělená mezerami, např. '1 2 3'): ").strip()
        meal_numbers = numbers.split()
        if meal_numbers:
            try:
                meal_numbers = list(map(int, meal_numbers))
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
                if meal.get("item", {}).get("altId", 0) > 0:
                    food.append(Meal(meal))

    return food


def cli_print_info(url: str, meal_numbers: list[int]) -> None:
    print("\nSledovaná jídla:")
    meals = get_meals(url)
    if not meals:
        print("Nepodařil se načíst jídelníček z webkreditu. Zkontrolujte zadaný den nebo připojení k internetu.")
        exit(0)

    for number in meal_numbers:
        for meal in meals:
            if meal.number == number:
                print(meal)
    print("\nZačíná sledování dostupnosti jídel...\n")


def cli_check_meals(url: str, meal_numbers: list[int]) -> None:
    while True:
        meals = get_meals(url)
        if not meals:
            print("Nepodařil se načíst jídelníček z webkreditu. Zkontrolujte zadaný den nebo připojení k internetu.")
            break

        for number in meal_numbers:
            for meal in meals:
                if meal.number == number:
                    if meal.available > 0:
                        print(
                            f"\r{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Jídlo {meal.number} je nyní dostupné! {meal.name} | Dostupných porcí: {meal.available}\n",
                            end="", flush=True)
