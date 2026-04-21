import shlex
from datetime import datetime
import re


class ProductReceipt:
    def __init__(self, date_str, product_name, quantity):
        self.date = datetime.strptime(date_str, "%Y.%m.%d").date()
        self.product_name = product_name
        self.quantity = int(quantity)


def parse_line(line):
    try:
        parts = shlex.split(line)

        date_value = None
        product_value = None
        quantity_value = None

        for part in parts:
            if re.match(r'^\d{4}\.\d{2}\.\d{2}$', part):
                date_value = part
            elif part.lstrip('-').isdigit():
                quantity_value = part
            else:
                product_value = part.strip('"')

        if date_value and product_value and quantity_value:
            return ProductReceipt(date_value, product_value, quantity_value)
    except:
        pass
    return None


while True:
    input_line = input("Введите строку (или 'end' для завершения): ")

    if input_line.lower() == 'end':
        print("Программа завершена")
        break

    obj = parse_line(input_line)

    if obj:
        print(f"Дата: {obj.date}")
        print(f"Название товара: {obj.product_name}")
        print(f"Количество: {obj.quantity}")
        print()
    else:
        print("Ошибка разбора строки\n")