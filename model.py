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


class ProductModel:
    """Класс-хранилище (Модель), который будем тестировать."""

    def __init__(self):
        self.items = []

    def parse_line(self, line):
        """Разбирает строку и возвращает словарь с данными или None"""
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
            raise DataParsingError(f"Ошибка разбора строки: {e}")
        return None

    def add_from_line(self, line):
        """Добавляет объект из строки. Возвращает True при успехе, False при ошибке."""
        try:
            if not line or not line.strip():
                raise DataParsingError("Пустая строка")

            parsed = self.parse_line(line)
            if not parsed:
                raise DataParsingError("Не удалось разобрать строку")

            new_obj = ProductReceipt(
                parsed['date'],
                parsed['product_name'],
                parsed['quantity']
            )
            self.items.append(new_obj)
            return True

        except Exception as e:
            print(f"[LOG ERROR] Некорректная строка '{line.strip()}': {e}")
            return False

    def load_from_file(self, filename):
        """Загружает данные из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        self.add_from_line(line)
        except FileNotFoundError:
            print(f"[LOG ERROR] Файл {filename} не найден, создан новый список")
        except Exception as e:
            print(f"[LOG ERROR] Ошибка при чтении файла: {e}")

    def save_to_file(self, filename):
        """Сохраняет данные в файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for obj in self.items:
                    f.write(f'"{obj.product_name}" {obj.date.strftime("%Y.%m.%d")} {obj.quantity}\n')
        except Exception as e:
            print(f"[LOG ERROR] Ошибка при сохранении файла: {e}")

    def delete_item(self, index):
        """Удаляет элемент по индексу"""
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False

    def get_item(self, index):
        """Возвращает элемент по индексу в виде словаря"""
        if 0 <= index < len(self.items):
            obj = self.items[index]
            return {
                'date': obj.date.strftime("%Y.%m.%d"),
                'product_name': obj.product_name,
                'quantity': obj.quantity
            }
        return None

    def get_all_items(self):
        """Возвращает все элементы в виде списка словарей"""
        return [
            {
                'date': obj.date.strftime("%Y.%m.%d"),
                'product_name': obj.product_name,
                'quantity': obj.quantity
            }
            for obj in self.items
        ]


# Модульные тесты
import unittest


class TestProductModel(unittest.TestCase):
    def setUp(self):
        self.model = ProductModel()

    def test_add_correct_line(self):
        """Тест добавления корректной строки"""
        line = '"Молоко" 2024.01.15 100'
        result = self.model.add_from_line(line)
        self.assertTrue(result)
        self.assertEqual(len(self.model.items), 1)
        self.assertEqual(self.model.items[0].product_name, "Молоко")
        self.assertEqual(self.model.items[0].quantity, 100)

    def test_add_line_with_quotes(self):
        """Тест строки с кавычками"""
        line = '"Хлеб ржаной" 2024.01.16 50'
        result = self.model.add_from_line(line)
        self.assertTrue(result)
        self.assertEqual(self.model.items[0].product_name, "Хлеб ржаной")

    def test_add_incorrect_date(self):
        """Тест с неверной датой"""
        line = '"Масло" 2024-13-45 30'
        result = self.model.add_from_line(line)
        self.assertFalse(result)
        self.assertEqual(len(self.model.items), 0)

    def test_add_incorrect_quantity(self):
        """Тест с неверным количеством"""
        line = '"Сыр" 2024.01.17 abc'
        result = self.model.add_from_line(line)
        self.assertFalse(result)
        self.assertEqual(len(self.model.items), 0)

    def test_add_empty_line(self):
        """Тест с пустой строкой"""
        result = self.model.add_from_line("")
        self.assertFalse(result)
        self.assertEqual(len(self.model.items), 0)

    def test_add_missing_fields(self):
        """Тест с недостающими полями"""
        line = '2024.01.18 50'  # нет названия
        result = self.model.add_from_line(line)
        self.assertFalse(result)
        self.assertEqual(len(self.model.items), 0)

    def test_delete_item(self):
        """Тест удаления элемента"""
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')
        self.assertEqual(len(self.model.items), 2)

        self.model.delete_item(0)
        self.assertEqual(len(self.model.items), 1)
        self.assertEqual(self.model.items[0].product_name, "Товар2")

    def test_delete_invalid_index(self):
        """Тест удаления по неверному индексу"""
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        result = self.model.delete_item(5)
        self.assertFalse(result)
        self.assertEqual(len(self.model.items), 1)

    def test_load_from_file(self):
        """Тест загрузки из файла"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write('"Молоко" 2024.01.15 100\n')
            f.write('"Хлеб" 2024.01.16 50\n')
            f.write('"Некорректная строка\n')
            f.write('"Масло" 2024.01.17 30\n')
            temp_file = f.name

        model = ProductModel()
        model.load_from_file(temp_file)

        # Должны загрузиться только 3 корректные строки
        self.assertEqual(len(model.items), 3)
        self.assertEqual(model.items[0].product_name, "Молоко")
        self.assertEqual(model.items[1].product_name, "Хлеб")
        self.assertEqual(model.items[2].product_name, "Масло")

    def test_get_all_items(self):
        """Тест получения всех элементов"""
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')

        items = self.model.get_all_items()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['product_name'], "Товар1")
        self.assertEqual(items[1]['quantity'], 20)


if __name__ == '__main__':
    unittest.main()