import shlex
from datetime import datetime
import re


class DataParsingError(Exception):
    """Исключение для ошибок парсинга данных."""
    pass


class ProductReceipt:
    """Класс для хранения информации о товаре"""

    def __init__(self, date_str, product_name, quantity):
        try:
            self.date = datetime.strptime(date_str, "%Y.%m.%d").date()
            self.product_name = product_name
            self.quantity = int(quantity)
        except (ValueError, TypeError) as e:
            raise DataParsingError(f"Ошибка в данных: {e}")

    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'date': self.date.strftime("%Y.%m.%d"),
            'product_name': self.product_name,
            'quantity': self.quantity
        }


class ProductModel:
    """Класс-хранилище (Модель)"""

    def __init__(self):
        self.items = []
        self._last_error = None

    def parse_line(self, line):
        """Разбирает строку и возвращает словарь с данными или None"""
        if not line or not line.strip():
            return None

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
                return {
                    'date': date_value,
                    'product_name': product_value,
                    'quantity': quantity_value
                }
        except Exception as e:
            self._last_error = str(e)
            raise DataParsingError(f"Ошибка разбора строки: {e}")
        return None

    def add_from_line(self, line):
        """Добавляет объект из строки. Возвращает True при успехе, False при ошибке."""
        try:
            if not line or not line.strip():
                self._last_error = "Пустая строка"
                return False

            parsed = self.parse_line(line)
            if not parsed:
                self._last_error = "Не удалось разобрать строку"
                return False

            new_obj = ProductReceipt(
                parsed['date'],
                parsed['product_name'],
                parsed['quantity']
            )
            self.items.append(new_obj)
            self._last_error = None
            return True

        except DataParsingError as e:
            self._last_error = str(e)
            return False
        except Exception as e:
            self._last_error = str(e)
            return False

    def add_from_dict(self, date, product_name, quantity):
        """Добавляет объект из отдельных полей"""
        line = f'"{product_name}" {date} {quantity}'
        return self.add_from_line(line)

    def load_from_file(self, filename):
        """Загружает данные из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        self.add_from_line(line)
            return True
        except FileNotFoundError:
            self._last_error = f"Файл {filename} не найден"
            return False
        except Exception as e:
            self._last_error = f"Ошибка при чтении файла: {e}"
            return False

    def save_to_file(self, filename):
        """Сохраняет данные в файл. Возвращает True при успехе."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for obj in self.items:
                    f.write(f'"{obj.product_name}" {obj.date.strftime("%Y.%m.%d")} {obj.quantity}\n')
            return True
        except Exception as e:
            self._last_error = f"Ошибка при сохранении файла: {e}"
            return False

    def delete_item(self, index):
        """Удаляет элемент по индексу. Возвращает True при успехе."""
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False

    def get_item(self, index):
        """Возвращает элемент по индексу в виде словаря"""
        if 0 <= index < len(self.items):
            return self.items[index].to_dict()
        return None

    def get_all_items(self):
        """Возвращает все элементы в виде списка словарей"""
        return [obj.to_dict() for obj in self.items]

    def clear_all(self):
        """Очищает все данные"""
        self.items.clear()
        self._last_error = None

    def get_last_error(self):
        """Возвращает последнюю ошибку"""
        return self._last_error

    def get_count(self):
        """Возвращает количество элементов"""
        return len(self.items)