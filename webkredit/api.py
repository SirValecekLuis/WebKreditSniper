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


def get_day_check(date) -> tuple[None, None, None] | tuple[int, int, int]:
    if '.' not in date:
        return None, None, None

    split = date.split('.', 2)
    if len(split) != 3:
        return None, None, None

    day, month, year = split
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None, None, None

    day, month, year = int(day), int(month), int(year)
    if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2024):
        return None, None, None

    return year, month, day


def get_meal_numbers_check(meal_numbers: list[str]) -> list[int] | None:
    int_numbers = []
    if meal_numbers and len(meal_numbers) < 11:
        for meal_number in meal_numbers:
            try:
                int_number = int(meal_number)
                if int_number < 1 or int_number > 10:
                    return None
                int_numbers.append(int_number)
            except ValueError:
                return None
        return list(set(int_numbers))

    return None


def get_webkredit_url(year, month, day) -> str:
    return f"https://stravovani.vsb.cz/webkredit/Api/Ordering/Menu?Dates={get_time_for_day(year, month, day)}&CanteenId=1"


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


def find_available_meals(meals: list[Meal], meal_numbers: list[int]) -> list[Meal]:
    available_meals = []
    for number in meal_numbers:
        for meal in meals:
            if meal.number == number and meal.available > 0:
                available_meals.append(meal)
    return available_meals
