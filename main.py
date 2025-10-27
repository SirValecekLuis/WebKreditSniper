from webkredit.api import get_webkredit_url
from webkredit.cli import cli_get_day, cli_get_meal_numbers, cli_print_info, cli_check_meals


def main():
    year, month, date = cli_get_day()
    url = get_webkredit_url(year, month, date)
    meal_numbers = cli_get_meal_numbers()
    cli_print_info(url, meal_numbers)
    cli_check_meals(url, meal_numbers)


if __name__ == "__main__":
    main()
