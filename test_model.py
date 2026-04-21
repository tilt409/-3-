import unittest
import tempfile
import os
from model import ProductModel, ProductReceipt, DataParsingError


class TestProductReceipt(unittest.TestCase):
    """Тесты для класса ProductReceipt"""

    def test_create_valid(self):
        obj = ProductReceipt("2024.01.15", "Молоко", "100")
        self.assertEqual(obj.product_name, "Молоко")
        self.assertEqual(obj.quantity, 100)
        self.assertEqual(obj.date.strftime("%Y.%m.%d"), "2024.01.15")

    def test_create_invalid_date(self):
        with self.assertRaises(DataParsingError):
            ProductReceipt("2024-13-45", "Молоко", "100")

    def test_create_invalid_quantity(self):
        with self.assertRaises(DataParsingError):
            ProductReceipt("2024.01.15", "Молоко", "abc")

    def test_to_dict(self):
        obj = ProductReceipt("2024.01.15", "Молоко", "100")
        d = obj.to_dict()
        self.assertEqual(d['date'], "2024.01.15")
        self.assertEqual(d['product_name'], "Молоко")
        self.assertEqual(d['quantity'], 100)


class TestProductModel(unittest.TestCase):
    def setUp(self):
        self.model = ProductModel()

    def tearDown(self):
        self.model.clear_all()

    # Тесты add_from_line
    def test_add_correct_line(self):
        result = self.model.add_from_line('"Молоко" 2024.01.15 100')
        self.assertTrue(result)
        self.assertEqual(self.model.get_count(), 1)
        self.assertEqual(self.model.get_item(0)['product_name'], "Молоко")

    def test_add_line_with_spaces(self):
        result = self.model.add_from_line('"Хлеб ржаной" 2024.01.16 50')
        self.assertTrue(result)
        self.assertEqual(self.model.items[0].product_name, "Хлеб ржаной")

    def test_add_incorrect_date(self):
        result = self.model.add_from_line('"Масло" 2024-13-45 30')
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_add_incorrect_quantity(self):
        result = self.model.add_from_line('"Сыр" 2024.01.17 abc')
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_add_empty_line(self):
        result = self.model.add_from_line("")
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_add_whitespace_line(self):
        result = self.model.add_from_line("   ")
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_add_missing_fields(self):
        result = self.model.add_from_line('2024.01.18 50')
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_add_missing_product(self):
        result = self.model.add_from_line('2024.01.18')
        self.assertFalse(result)

    def test_add_line_with_different_order(self):
        result = self.model.add_from_line('2024.01.15 "Молоко" 100')
        self.assertTrue(result)

    # Тесты add_from_dict
    def test_add_from_dict(self):
        result = self.model.add_from_dict("2024.01.15", "Молоко", "100")
        self.assertTrue(result)
        self.assertEqual(self.model.get_count(), 1)

    def test_add_from_dict_invalid(self):
        result = self.model.add_from_dict("bad-date", "Молоко", "100")
        self.assertFalse(result)

    # Тесты delete_item
    def test_delete_item(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')
        self.assertEqual(self.model.get_count(), 2)

        result = self.model.delete_item(0)
        self.assertTrue(result)
        self.assertEqual(self.model.get_count(), 1)
        self.assertEqual(self.model.get_item(0)['product_name'], "Товар2")

    def test_delete_invalid_index(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        result = self.model.delete_item(5)
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 1)

    def test_delete_negative_index(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        result = self.model.delete_item(-1)
        self.assertFalse(result)

    # Тесты get_item
    def test_get_item(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        item = self.model.get_item(0)
        self.assertEqual(item['product_name'], "Товар1")
        self.assertEqual(item['quantity'], 10)

    def test_get_item_invalid_index(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        item = self.model.get_item(99)
        self.assertIsNone(item)

    def test_get_item_negative_index(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        item = self.model.get_item(-1)
        self.assertIsNone(item)

    def test_get_item_empty_model(self):
        item = self.model.get_item(0)
        self.assertIsNone(item)

    # Тесты get_all_items
    def test_get_all_items(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')

        items = self.model.get_all_items()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['product_name'], "Товар1")
        self.assertEqual(items[1]['quantity'], 20)

    def test_get_all_items_empty(self):
        items = self.model.get_all_items()
        self.assertEqual(items, [])

    # Тесты save_to_file
    def test_save_to_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name

        try:
            self.model.add_from_line('"Товар1" 2024.01.01 10')
            self.model.add_from_line('"Товар2" 2024.01.02 20')
            result = self.model.save_to_file(temp_file)

            self.assertTrue(result)
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Товар1', content)
                self.assertIn('Товар2', content)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_save_to_file_invalid_path(self):
        result = self.model.save_to_file("/invalid/path/file.txt")
        self.assertFalse(result)
        self.assertIsNotNone(self.model.get_last_error())

    # Тесты load_from_file
    def test_load_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write('"Молоко" 2024.01.15 100\n')
            f.write('"Хлеб" 2024.01.16 50\n')
            f.write('bad line\n')
            f.write('"Масло" 2024.01.17 30\n')
            temp_file = f.name

        try:
            model = ProductModel()
            result = model.load_from_file(temp_file)
            self.assertTrue(result)
            self.assertEqual(model.get_count(), 3)
        finally:
            os.unlink(temp_file)

    def test_load_from_file_not_exists(self):
        result = self.model.load_from_file("nonexistent_file_12345.txt")
        self.assertFalse(result)
        self.assertEqual(self.model.get_count(), 0)

    def test_load_from_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            temp_file = f.name

        try:
            result = self.model.load_from_file(temp_file)
            self.assertTrue(result)
            self.assertEqual(self.model.get_count(), 0)
        finally:
            os.unlink(temp_file)

    # Тесты parse_line
    def test_parse_line_valid(self):
        result = self.model.parse_line('"Молоко" 2024.01.15 100')
        self.assertIsNotNone(result)
        self.assertEqual(result['product_name'], "Молоко")

    def test_parse_line_invalid_format(self):
        result = self.model.parse_line("just text")
        self.assertIsNone(result)

    def test_parse_line_empty(self):
        result = self.model.parse_line("")
        self.assertIsNone(result)

    # Тесты get_last_error
    def test_get_last_error(self):
        self.model.add_from_line("invalid")
        error = self.model.get_last_error()
        self.assertIsNotNone(error)

    def test_last_error_cleared_on_success(self):
        self.model.add_from_line("invalid")
        self.model.add_from_line('"Valid" 2024.01.15 100')
        self.assertIsNone(self.model.get_last_error())

    # Тесты clear_all
    def test_clear_all(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')
        self.assertEqual(self.model.get_count(), 2)

        self.model.clear_all()
        self.assertEqual(self.model.get_count(), 0)

    # Тесты get_count
    def test_get_count(self):
        self.assertEqual(self.model.get_count(), 0)
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.assertEqual(self.model.get_count(), 1)


class TestProductModelEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    def setUp(self):
        self.model = ProductModel()

    def test_add_many_items(self):
        for i in range(100):
            self.model.add_from_line(f'"Товар{i}" 2024.01.01 {i}')
        self.assertEqual(self.model.get_count(), 100)

    def test_delete_all_items(self):
        self.model.add_from_line('"Товар1" 2024.01.01 10')
        self.model.add_from_line('"Товар2" 2024.01.02 20')
        self.model.delete_item(0)
        self.model.delete_item(0)
        self.assertEqual(self.model.get_count(), 0)

    def test_special_characters_in_name(self):
        result = self.model.add_from_line('"Товар №1-2_3" 2024.01.01 100')
        self.assertTrue(result)
        self.assertEqual(self.model.get_item(0)['product_name'], "Товар №1-2_3")


if __name__ == '__main__':
    unittest.main()