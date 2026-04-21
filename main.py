import tkinter as tk
from tkinter import ttk, messagebox
from model import ProductModel


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление поступлениями товаров 2.0")
        self.model = ProductModel()
        self.model.load_from_file("data.txt")

        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("1", "2", "3"), show="headings")
        self.tree.heading("1", text="Дата")
        self.tree.heading("2", text="Название товара")
        self.tree.heading("3", text="Количество")
        self.tree.pack()

        # Поля ввода
        self.e1 = tk.Entry(self.root)  # дата
        self.e1.pack()
        self.e2 = tk.Entry(self.root)  # название
        self.e2.pack()
        self.e3 = tk.Entry(self.root)  # количество
        self.e3.pack()

        # Кнопки
        tk.Button(self.root, text="Добавить", command=self.add).pack()
        tk.Button(self.root, text="Удалить", command=self.delete).pack()

        self.refresh_table()

    def refresh_table(self):
        """Обновляет таблицу"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for obj in self.model.get_all_items():
            self.tree.insert("", "end", values=(obj['date'], obj['product_name'], obj['quantity']))

    def add(self):
        """Добавляет новый элемент"""
        raw = f'"{self.e2.get()}" {self.e1.get()} {self.e3.get()}'
        success = self.model.add_from_line(raw)

        if success:
            self.model.save_to_file("data.txt")
            self.refresh_table()
            # Очищаем поля
            self.e1.delete(0, tk.END)
            self.e2.delete(0, tk.END)
            self.e3.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить запись. Проверьте лог в консоли.")

    def delete(self):
        """Удаляет выделенный элемент"""
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            self.model.delete_item(idx)
            self.model.save_to_file("data.txt")
            self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()