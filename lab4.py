import shlex
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class PostuplenieTovarov:
    def __init__(self, date_str, nazvanie, kolichestvo):
        self.date = datetime.strptime(date_str, "%Y.%m.%d").date()
        self.nazvanie = nazvanie
        self.kolichestvo = int(kolichestvo)

    def __str__(self):
        return f"Дата: {self.date}\nТовар: {self.nazvanie}\nКоличество: {self.kolichestvo}"


def parse_line(line):
    """Парсинг строки вида: TipObekta 2025.12.12 'Молоко' 10"""
    try:
        parts = shlex.split(line)
        if len(parts) >= 4:
            return PostuplenieTovarov(parts[1], parts[2], parts[3])
    except:
        pass
    return None


def load_from_file(filename):
    """Загрузка данных из файла"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                obj = parse_line(line.strip())
                if obj:
                    data.append(obj)
        print(f"Загружено {len(data)} записей")
    except FileNotFoundError:
        print("Файл не найден, будет создан новый при сохранении")
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
    return data


def save_to_file(filename, data):
    """Сохранение данных в файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for obj in data:
                f.write(f"Postuplenie {obj.date.strftime('%Y.%m.%d')} {shlex.quote(obj.nazvanie)} {obj.kolichestvo}\n")
        print(f"Сохранено {len(data)} записей")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")


class App:
    def __init__(self, root, data_list, filename="tovary.txt"):
        self.root = root
        self.items = data_list
        self.filename = filename
        self.root.title("Учёт поступления товаров")

        # Создание таблицы
        self.tree = ttk.Treeview(self.root, columns=("date", "name", "count"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("name", text="Название товара")
        self.tree.heading("count", text="Количество")
        self.tree.column("date", width=100)
        self.tree.column("name", width=200)
        self.tree.column("count", width=100)
        self.tree.pack(pady=10)

        # Рамка для полей ввода
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="Дата (ГГГГ.ММ.ДД):").grid(row=0, column=0, padx=5)
        self.entry_date = tk.Entry(frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Название товара:").grid(row=0, column=2, padx=5)
        self.entry_name = tk.Entry(frame, width=20)
        self.entry_name.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Количество:").grid(row=0, column=4, padx=5)
        self.entry_count = tk.Entry(frame, width=10)
        self.entry_count.grid(row=0, column=5, padx=5)

        # Рамка для кнопок
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить", command=self.add, bg="green", fg="white", width=12).pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete, bg="red", fg="white", width=12).pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save, bg="blue", fg="white", width=12).pack(side=tk.LEFT,
                                                                                                        padx=5)

        # Кнопки для анализа данных
        analize_frame = tk.Frame(self.root)
        analize_frame.pack(pady=5)

        tk.Button(analize_frame, text="Максимальная поставка", command=self.max_count, bg="orange", width=18).pack(
            side=tk.LEFT, padx=5)
        tk.Button(analize_frame, text="Сумма всех поставок", command=self.total_count, bg="orange", width=18).pack(
            side=tk.LEFT, padx=5)

        self.show()

    def show(self):
        """Отображение данных в таблице"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for obj in self.items:
            self.tree.insert("", "end", values=(obj.date, obj.nazvanie, obj.kolichestvo))

    def add(self):
        """Добавление новой записи"""
        date_str = self.entry_date.get().strip()
        nazvanie = self.entry_name.get().strip()
        count_str = self.entry_count.get().strip()

        # Проверка заполнения полей
        if not date_str or not nazvanie or not count_str:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Проверка формата даты
        try:
            datetime.strptime(date_str, "%Y.%m.%d")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ГГГГ.ММ.ДД")
            return

        # Проверка количества
        try:
            kolichestvo = int(count_str)
            if kolichestvo < 0:
                messagebox.showwarning("Ошибка", "Количество не может быть отрицательным!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Количество должно быть целым числом!")
            return

        # Создание строки для парсинга
        raw = f'Postuplenie {date_str} {shlex.quote(nazvanie)} {kolichestvo}'
        new_obj = parse_line(raw)

        if new_obj:
            self.items.append(new_obj)
            self.show()
            # Очистка полей
            self.entry_date.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_count.delete(0, tk.END)
            messagebox.showinfo("Успех", "Товар добавлен!")

    def delete(self):
        """Удаление выбранной записи"""
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.items[idx]
            self.show()
            messagebox.showinfo("Успех", "Запись удалена!")
        else:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления!")

    def save(self):
        """Сохранение данных в файл"""
        save_to_file(self.filename, self.items)
        messagebox.showinfo("Успех", f"Данные сохранены в файл {self.filename}!")

    def max_count(self):
        """Поиск товара с максимальным количеством поставки"""
        if not self.items:
            messagebox.showwarning("Нет данных", "Список товаров пуст!")
            return

        max_tovar = max(self.items, key=lambda x: x.kolichestvo)
        messagebox.showinfo("Максимальная поставка",
                            f"Товар: {max_tovar.nazvanie}\n"
                            f"Количество: {max_tovar.kolichestvo}\n"
                            f"Дата: {max_tovar.date}")

    def total_count(self):
        """Подсчёт суммы всех поставок"""
        if not self.items:
            messagebox.showwarning("Нет данных", "Список товаров пуст!")
            return

        total = sum(obj.kolichestvo for obj in self.items)
        messagebox.showinfo("Общая сумма поставок", f"Всего поставлено товаров: {total} шт.")


# Пример работы со списком (как в вашем примере)
def primery_raboty():
    print("\n=== ПРИМЕРЫ РАБОТЫ СО СПИСКОМ ===\n")

    # Создание списка товаров
    my_list = [
        PostuplenieTovarov("2025.12.12", "Молоко", 100),
        PostuplenieTovarov("2025.11.12", "Хлеб", 50),
        PostuplenieTovarov("2025.10.05", "Масло", 30)
    ]

    # Поиск максимальной поставки
    max_postavka = max(my_list, key=lambda x: x.kolichestvo)
    print(f"Максимальная поставка: {max_postavka.kolichestvo} шт. - {max_postavka.nazvanie}")

    # Сумма всех поставок
    total = sum(x.kolichestvo for x in my_list)
    print(f"Общее количество товаров: {total} шт.")

    # Фильтрация по названию
    moloko_list = [obj for obj in my_list if obj.nazvanie == "Молоко"]
    for obj in moloko_list:
        print(f"Молоко: {obj.date} - {obj.kolichestvo} шт.")


# Запуск примеров
primery_raboty()

# Запуск GUI приложения
print("\n=== ЗАПУСК ГРАФИЧЕСКОГО ПРИЛОЖЕНИЯ ===\n")
my_data = load_from_file("tovary.txt")
root = tk.Tk()
main_app = App(root, my_data)
root.mainloop()