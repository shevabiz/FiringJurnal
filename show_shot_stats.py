import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkcalendar import Calendar
import csv
from collections import defaultdict
from datetime import datetime


def copy_selected_to_clipboard(table):
    """Копіює виділені дані з таблиці до буферу обміну."""
    selected_item = table.selection()[0]
    values = table.item(selected_item, 'values')
    copy_text = ', '.join(map(str, values))
    table.clipboard_clear()
    table.clipboard_append(copy_text)
    table.update()


def select_all(_, table):
    """Виділяє всі записи в таблиці."""
    for item in table.get_children():
        table.selection_add(item)


def copy_all_selected_to_clipboard(_, table):
    """Копіює всі виділені записи до буферу обміну."""
    selected_items = table.selection()
    all_values = []
    for item in selected_items:
        values = table.item(item, 'values')
        all_values.append(', '.join(map(str, values)))
    copy_text = '\n'.join(all_values)
    table.clipboard_clear()
    table.clipboard_append(copy_text)
    table.update()


def modified_select_date_range():
    """Діалогове вікно для вибору діапазону дат."""
    dialog = tk.Toplevel()
    dialog.geometry("400x600")
    dialog.title("Виберіть діапазон дат")
    dialog.configure(bg='#242424')

    # Початкова дата
    tk.Label(dialog, text="Початкова дата:",
             bg="#242424",
             fg="white",
             font=("Ubuntu", 16, "bold")).pack(pady=10)
    start_cal = Calendar(dialog)
    start_cal.pack(pady=20, padx=20)

    # Кінцева дата
    tk.Label(dialog, text="Кінцева дата:",
             bg="#242424",
             fg="white",
             font=("Ubuntu", 16, "bold")).pack(pady=10)
    end_cal = Calendar(dialog)
    end_cal.pack(pady=20, padx=20)

    # Кнопка для підтвердження
    def confirm():
        dialog.start_date = start_cal.get_date()
        dialog.end_date = end_cal.get_date()
        dialog.destroy()

    btn = ctk.CTkButton(dialog, text="Підтвердити",
                        command=confirm)
    btn.place(relx=0.5, rely=0.95, anchor="center")

    dialog.wait_window()
    # Перевірка, чи були встановлені дати перед тим, як вікно було закрите
    if hasattr(dialog, "start_date") and hasattr(dialog, "end_date"):
        return dialog.start_date, dialog.end_date
    else:
        # Якщо вікно було закрите, повертаємо пусті дати
        return None, None


def display_shot_stats():
    start_date, end_date = modified_select_date_range()

    # Якщо користувач закрив діалогове вікно без вибору діапазону дат, просто повертаємося
    if start_date is None or end_date is None:
        return

    # Конвертація start_date і end_date у об'єкти datetime.date, якщо вони є рядками
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%m/%d/%y').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%m/%d/%y').date()

    display_stats_window = tk.Toplevel()
    display_stats_window.geometry("500x800")
    display_stats_window.title("Настріл")
    display_stats_window.configure(bg='black')

    table = ttk.Treeview(display_stats_window, height=40)
    table.pack(fill=tk.BOTH, expand=True)

    # Налаштування шрифта для таблиці
    font = ('Arial', 14)
    for column in table['columns']:
        table.heading(column, text=column, anchor=tk.CENTER)
        table.column(column, anchor=tk.CENTER)

    # Стилізація таблиці
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    font=font,
                    background='black',
                    foreground='green',
                    fieldbackground='black',
                    borderwidth=0,
                    highlightthickness=0)
    style.map('Treeview',
              background=[('selected', 'green')],
              foreground=[('selected', 'black')])

    # Налаштування стовпців
    table["columns"] = ("Дата", "Снаряд|Заряд", "Витрата")
    table.column("#0", width=0, stretch=tk.NO)
    table.column("Дата", anchor=tk.CENTER, width=100)
    table.column("Снаряд|Заряд", anchor=tk.CENTER, width=200)
    table.column("Витрата", anchor=tk.CENTER, width=100)

    table.heading("#0", text="")
    table.heading("Дата", text="Дата", anchor=tk.CENTER)
    table.heading("Снаряд|Заряд", text="Снаряд | Заряд", anchor=tk.CENTER)
    table.heading("Витрата", text="Витрата", anchor=tk.CENTER)

    # Зчитування даних з CSV файлу та групування їх
    with open("DB/shots.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)
        grouped_data = defaultdict(int)
        rows = []
        for row in reader:
            if len(row) < 6:
                continue
            date_str = row[0].split("|")[0].strip()
            date_obj = datetime.strptime(date_str, '%d.%m.%y')

            # Фільтрація даних за вказаним діапазоном дат
            if start_date <= date_obj.date() <= end_date:
                projectile = row[4]
                charge = row[3]
                key = f"{date_str}|{projectile}|{charge}"
                grouped_data[key] += 1

        current_date = None
        current_group = defaultdict(int)
        for key, value in grouped_data.items():
            date, projectile, charge = key.split("|")
            if date != current_date:
                if current_group:
                    for projectile_charge, quantity in current_group.items():
                        rows.append([current_date, projectile_charge, quantity])
                    rows.append(["", "", ""])
                current_date = date
                current_group = defaultdict(int)
            projectile_charge = f"{charge}  |  {projectile}"
            current_group[projectile_charge] += value
        if current_group:
            for projectile_charge, quantity in current_group.items():
                rows.append([current_date, projectile_charge, quantity])
            rows.append(["", "", ""])  # Додає порожній рядок
        for row in rows:
            table.insert("", tk.END, values=row)
    # Контекстне меню для копіювання
    context_menu = tk.Menu(display_stats_window, tearoff=0)
    context_menu.add_command(label="Копіювати", command=lambda: copy_selected_to_clipboard(table))

    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    table.bind("<Button-3>", show_context_menu)

    table.bind('<Control-a>', lambda event, t=table: select_all(event, t))
    table.bind('<Control-c>', lambda event, t=table: copy_all_selected_to_clipboard(event, t))

    table.yview_moveto(1)
    display_shot_stats()
