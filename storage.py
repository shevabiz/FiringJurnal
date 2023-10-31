import customtkinter as ctk
from tkinter import ttk
import csv
import os
from tkinter.simpledialog import askstring
from tkinter import messagebox

# Шляхи до файлів
projectile_file_path = "DB/projectiles.csv"
charge_file_path = "DB/charges.csv"

# Перевірка і створення папки та файлу, якщо вони відсутні
if not os.path.exists("DB"):
    os.mkdir("DB")

for path in [projectile_file_path, charge_file_path]:
    if not os.path.exists(path):
        with open(path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Quantity"])


def add_item_to_file(file_path, combobox):
    # Запитати користувача про назву нового пункту
    new_item = askstring("Новий пункт", "Введіть назву Заряду або Снаряду:")

    if new_item:
        # Зберегти новий пункт у файлі CSV
        with open(file_path, "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([new_item])

        # Оновити випадаюче меню
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Пропустити заголовок
            items = [row[0] for row in reader]
            combobox["values"] = items


def update_or_add_to_csv(file_path, name, quantity):
    data_dict = {}

    if os.path.exists(file_path):
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                if len(row) > 1:
                    data_dict[row[0]] = int(row[1])

    if name in data_dict:
        data_dict[name] += quantity
    else:
        data_dict[name] = quantity

    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Name", "Quantity"])
        for key, value in data_dict.items():
            csv_writer.writerow([key, value])


def load_items_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            return [row[0] for row in reader]
    return []


def show_storage_window():
    root = ctk.CTk()
    root.title("Склад БК")
    root.geometry('600x400')
    root.resizable(False, False)

    def add_projectile():
        name = projectile_choices.get()
        try:
            quantity = int(quantity_entry.get())
        except ValueError:
            return
        update_or_add_to_csv(projectile_file_path, name, quantity)
        refresh_tables()

    def add_charge():
        name = charge_choices.get()
        try:
            quantity = int(quantity_entry.get())
        except ValueError:
            return
        update_or_add_to_csv(charge_file_path, name, quantity)
        refresh_tables()

    def refresh_tables():
        for table in [projectile_table, charge_table]:
            for row in table.get_children():
                table.delete(row)

        if os.path.exists(projectile_file_path):
            with open(projectile_file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)
                for row in reader:
                    projectile_table.insert("", "end", values=row)

        if os.path.exists(charge_file_path):
            with open(charge_file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)
                for row in reader:
                    charge_table.insert("", "end", values=row)

    def add_new_projectile():
        add_item_to_file(projectile_file_path, projectile_choices)

    def add_new_charge():
        add_item_to_file(charge_file_path, charge_choices)

    def reset_quantities(file_path):
        """
        Обнулити залишки у вказаному файлі CSV.
        """
        if os.path.exists(file_path):
            data_dict = {}
            with open(file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)
                for row in reader:
                    if len(row) > 1:
                        data_dict[row[0]] = 0

            with open(file_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["Name", "Quantity"])
                for key, value in data_dict.items():
                    csv_writer.writerow([key, value])

    def reset_all_quantities():
        """
        Обнулити залишки для всіх пунктів у файлах CSV.
        """
        answer = messagebox.askyesno("Попередження", "Ви дійсно бажаєте обнулити залишки?")
        if answer:
            reset_quantities(projectile_file_path)
            reset_quantities(charge_file_path)
            refresh_tables()

    upper_frame = ctk.CTkFrame(root)
    upper_frame.pack(pady=20)

    projectile_label = ctk.CTkLabel(upper_frame, text="Снаряд:")
    projectile_label.grid(row=0, column=0, padx=10)
    projectiles = load_items_from_file(projectile_file_path)
    projectile_choices = ttk.Combobox(upper_frame, values=projectiles, width=10)
    if projectiles:
        projectile_choices.current(0)
    projectile_choices.grid(row=1, column=0, padx=10)
    projectile_add_button = ctk.CTkButton(upper_frame, text="+", width=5, command=add_new_projectile)
    projectile_add_button.grid(row=1, column=1, padx=5)

    charge_label = ctk.CTkLabel(upper_frame, text="Заряд:")
    charge_label.grid(row=0, column=2, padx=10)
    charges = load_items_from_file(charge_file_path)
    charge_choices = ttk.Combobox(upper_frame, values=charges, width=10)
    if charges:
        charge_choices.current(0)
    charge_choices.grid(row=1, column=2, padx=10)
    charge_add_button = ctk.CTkButton(upper_frame, text="+", width=5, command=add_new_charge)
    charge_add_button.grid(row=1, column=3, padx=5)

    quantity_label = ctk.CTkLabel(upper_frame, text="Кіл-ть:")
    quantity_label.grid(row=0, column=4, padx=10)
    quantity_entry = ctk.CTkEntry(upper_frame, width=40)
    quantity_entry.grid(row=1, column=4, padx=10)

    add_projectile_button = ctk.CTkButton(upper_frame, text="Додати Снаряд", command=add_projectile)
    add_projectile_button.grid(row=2, column=0, padx=10, pady=10)

    add_charge_button = ctk.CTkButton(upper_frame, text="Додати Заряд", command=add_charge)
    add_charge_button.grid(row=2, column=2, padx=10, pady=10)

    projectile_table = ttk.Treeview(root, columns=('Снаряд', 'Залишок'), show="headings")
    projectile_table.heading('Снаряд', text='Снаряд')
    projectile_table.heading('Залишок', text='Залишок')
    projectile_table.column('Снаряд', width=100, anchor='center')
    projectile_table.column('Залишок', width=100, anchor='center')
    projectile_table.pack(side='left', padx=20, pady=20)

    charge_table = ttk.Treeview(root, columns=('Заряд', 'Залишок'), show="headings")
    charge_table.heading('Заряд', text='Заряд')
    charge_table.heading('Залишок', text='Залишок')
    charge_table.column('Заряд', width=100, anchor='center')
    charge_table.column('Залишок', width=100, anchor='center')
    charge_table.pack(side='right', padx=20, pady=20)

    reset_button = ctk.CTkButton(upper_frame, text="Обнулити залишки", command=reset_all_quantities)
    reset_button.grid(row=2, column=4, padx=10, pady=10)

    refresh_tables()

    root.mainloop()


if __name__ == "__main__":
    show_storage_window()
