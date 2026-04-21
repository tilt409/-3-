import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import shlex
import re


class App:
    def __init__(self, root, data_list, filename):
        self.root = root
        self.items = data_list
        self.filename = filename

        self.tree = ttk.Treeview(self.root, columns=("1", "2", "3"), show="headings")
        self.tree.heading("1", text="Дата")
        self.tree.heading("2", text="Название товара")
        self.tree.heading("3", text="Количество")
        self.tree.pack()

        self.e1 = tk.Entry(self.root)
        self.e1.pack()
        self.e2 = tk.Entry(self.root)
        self.e2.pack()
        self.e3 = tk.Entry(self.root)
        self.e3.pack()

        tk.Button(self.root, text="Добавить", command=self.add).pack()
        tk.Button(self.root, text="Удалить", command=self.delete).pack()

        self.show()

    def parse_line(self, line):
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
                    'date': datetime.strptime(date_value, "%Y.%m.%d").date(),
                    'product_name': product_value,
                    'quantity': int(quantity_value)
                }
        except:
            pass
        return None

    def load_from_file(self):
        objects = []
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        obj = self.parse_line(line)
                        if obj:
                            objects.append(obj)
        except FileNotFoundError:
            pass
        return objects

    def save_to_file(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            for obj in self.items:
                file.write(f'"{obj["product_name"]}" {obj["date"].strftime("%Y.%m.%d")} {obj["quantity"]}\n')

    def show(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for obj in self.items:
            self.tree.insert("", "end", values=(obj["date"].strftime("%Y.%m.%d"), obj["product_name"], obj["quantity"]))

    def add(self):
        raw = f'"{self.e2.get()}" {self.e1.get()} {self.e3.get()}'
        new_obj = self.parse_line(raw)

        if new_obj:
            self.items.append(new_obj)
            self.save_to_file()
            self.show()

    def delete(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.items[idx]
            self.save_to_file()
            self.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, [], "data.txt")
    app.items = app.load_from_file()
    app.show()
    root.mainloop()