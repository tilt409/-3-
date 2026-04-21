import shlex
from datetime import datetime


class ProductReceipt:
    def __init__(self, date_str, product_name, quantity):
        self.date = datetime.strptime(date_str, "%Y.%m.%d").date()
        self.product_name = product_name
        self.quantity = int(quantity)


def parse_line(line):
    try:
        parts = shlex.split(line)
        if len(parts) == 3:
            return ProductReceipt(parts[0], parts[1], parts[2])
        elif len(parts) >= 4:
            return ProductReceipt(parts[1], parts[2], parts[3])
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
        print()  # Пустая строка для разделения выводов
    else:
        print("Ошибка разбора строки\n")