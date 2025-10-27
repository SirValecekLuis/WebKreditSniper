import datetime
import time

from webkredit.api import get_meal_numbers_check, get_meals, get_day_check, find_available_meals


def cli_get_day() -> tuple[int, int, int]:
    year, month, day = None, None, None
    while True:
        date = input("Zadejte datum ve formátu 'den.měsíc.rok', takže např. 17.5.2026: ").strip().strip('"').strip("'")
        year, month, day = get_day_check(date)

        if year is None or month is None or day is None:
            print("Neplatný formát data. Zkuste to znovu. Datum musí být validní a ve formě třeba 4.11.2025.")
            continue

        break

    return year, month, day


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

        for meal in find_available_meals(meals, meal_numbers):
            print(f"Jídlo {meal.number} - {meal.name} je nyní dostupné! Počet dostupných jídel: {meal.available}")

        time.sleep(10)


def cli_get_meal_numbers() -> list[int]:
    while True:
        numbers = input("Zadejte čísla jídel, která chcete sledovat (oddělená čárkami, např. '1, 2, 3'): ").strip()
        meal_numbers = numbers.split(",")
        meal_numbers = get_meal_numbers_check(meal_numbers)
        if meal_numbers is None:
            print("Neplatný formát čísel jídel. Zkuste to znovu. Musí to být např 1, 2, 3, 5")
            continue
        return meal_numbers
