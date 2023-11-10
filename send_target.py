import customtkinter as ctk
from tkinter import simpledialog
import csv
import os
from datetime import datetime
import subprocess


def send_target_windows():
    # Перевірка та створення директорії для файлів з даними
    os.makedirs("DB", exist_ok=True)

    # Шляхи до файлів
    MENU_DATA_PATH = "DB/menu_data.csv"
    DATA_CSV_PATH = "DB/data.csv"

    # Функція для завантаження даних випадаючих меню
    def load_menu_data():
        sub_menu = {
            "subdivision": [],
            "settlement": [],
            "purpose": [],
            "detector": [],
            "commander": []
        }
        if os.path.exists(MENU_DATA_PATH):
            with open(MENU_DATA_PATH, mode='r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for key, *values in reader:
                    sub_menu[key] = values
        return sub_menu

    # Функція для збереження даних випадаючих меню
    def save_menu_data(menu_save):
        with open(MENU_DATA_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for key, values in menu_save.items():
                writer.writerow([key] + values)

    # Функція для додавання нового елементу до випадаючого меню
    def add_to_menu(menu_add, menu_key, option_menu, option_variable):
        new_value = simpledialog.askstring(f"Додати {menu_key}", f"Введіть назву {menu_key}:")
        if new_value and new_value not in menu_add[menu_key]:
            menu_add[menu_key].append(new_value)
            option_menu.configure(values=menu_add[menu_key])
            option_variable.set(new_value)
            save_menu_data(menu_add)

    # Функція для збереження даних форми у файл CSV
    def save_data_to_csv(data, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    # Функція для читання налаштувань Signal
    def read_signal_settings():
        with open('DB/signal_settings.csv', mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            settings = next(reader)
        return settings['Sender'], settings['ReportRecipient']

    # Функція для відправлення повідомлень через Signal
    def send_signal_message(sender, recipient, message):
        command = f"signal-cli -u {sender} send -m \"{message}\" {recipient}"
        print("Виконувана команда:", command)

        subprocess.run(command, shell=True)

    def read_shots_data(file_path):
        last_count = None
        last_projectile_charge = None
        with open(file_path, mode='r', encoding='ISO 8859-5') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 3:
                    # Оновлюємо кількість при кожному знаходженні рядка з трьома стовпцями
                    last_count = row[2]
                elif len(row) > 3:
                    # Запам'ятовуємо останній рядок з даними про заряд та снаряд
                    last_projectile_charge = row[3], row[4]

        return last_count, last_projectile_charge

    # Функція для відправлення даних
    def submit_data():
        # Читання даних про кількість, заряд і снаряд
        count, projectile_charge = read_shots_data("DB/shots.csv")
        if count and projectile_charge:
            projectile, charge = projectile_charge
            expenditure = f"{count} {projectile} з {charge}"
        else:
            expenditure = "Дані не знайдено"

        data = {
            "Підрозділ": subdivision_var.get(),
            "Населений пункт": settlement_var.get(),
            "Ціль": purpose_var.get(),
            "Координати": coordinates_entry.get(),
            "Час": time_entry.get(),
            "Виявив": detector_var.get(),
            "Командир": commander_var.get(),
            "Витрата": expenditure
        }
        save_data_to_csv(data, DATA_CSV_PATH)

        # Читання налаштувань Signal
        sender, recipient = read_signal_settings()

        message_lines = [f"{key}: {value}" for key, value in data.items()]
        message = " ".join(message_lines)

        # Відправлення повідомлення
        send_signal_message(sender, recipient, message)

        # Закриття вікна після відправки
        app.after(50, app.destroy)

    def update_expenditure():
        count, projectile_charge = read_shots_data("DB/shots.csv")
        if count and projectile_charge:
            projectile, charge = projectile_charge
            expenditure = f"{count} {projectile} з {charge}"
        else:
            expenditure = "Дані не знайдено"

        expenditure_entry.delete(0, 'end')
        expenditure_entry.insert(0, expenditure)
    # Завантаження даних для випадаючих меню
    menu_data = load_menu_data()

    app = ctk.CTk()
    app.title("Форма відправки даних")
    app.geometry("500x400")

    # Змінні для випадаючих меню
    subdivision_var = ctk.StringVar()
    settlement_var = ctk.StringVar()
    purpose_var = ctk.StringVar()
    detector_var = ctk.StringVar()
    commander_var = ctk.StringVar()

    # Відступи і налаштування тексту
    vertical_padding = 5
    horizont_padding = 15
    text_size = 16
    text_colors = "grey"
    # menu_color = "white"

    # Створення віджетів для інтерфейсу
    ctk.CTkLabel(app, text="Підрозділ", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=0, column=0, pady=15, padx=horizont_padding)
    subdivision_menu = ctk.CTkOptionMenu(app, variable=subdivision_var, values=menu_data["subdivision"])
    subdivision_menu.grid(row=0, column=1, pady=vertical_padding, padx=horizont_padding)
    ctk.CTkButton(app, text="Додати", command=lambda: add_to_menu(menu_data,
                                                                  "subdivision",
                                                                  subdivision_menu,
                                                                  subdivision_var)).grid(row=0, column=2,
                                                                                         pady=vertical_padding,
                                                                                         padx=horizont_padding)

    ctk.CTkLabel(app, text="Населений пункт", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=1, column=0, pady=vertical_padding, padx=horizont_padding)
    settlement_menu = ctk.CTkOptionMenu(app, variable=settlement_var, values=menu_data["settlement"])
    settlement_menu.grid(row=1, column=1, pady=vertical_padding, padx=horizont_padding)
    ctk.CTkButton(app, text="Додати", command=lambda: add_to_menu(menu_data,
                                                                  "settlement",
                                                                  settlement_menu,
                                                                  settlement_var)).grid(row=1, column=2,
                                                                                        pady=vertical_padding,
                                                                                        padx=horizont_padding)

    ctk.CTkLabel(app, text="Ціль", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=2, column=0, pady=vertical_padding, padx=horizont_padding)
    purpose_menu = ctk.CTkOptionMenu(app, variable=purpose_var, values=menu_data["purpose"])
    purpose_menu.grid(row=2, column=1, pady=vertical_padding, padx=horizont_padding)
    ctk.CTkButton(app, text="Додати", command=lambda: add_to_menu(menu_data,
                                                                  "purpose",
                                                                  purpose_menu,
                                                                  purpose_var)).grid(row=2, column=2,
                                                                                     pady=vertical_padding,
                                                                                     padx=horizont_padding)

    ctk.CTkLabel(app, text="Координати", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=3, column=0, pady=vertical_padding, padx=horizont_padding)
    coordinates_entry = ctk.CTkEntry(app)
    coordinates_entry.grid(row=3, column=1, pady=vertical_padding, padx=horizont_padding)

    ctk.CTkLabel(app, text="Час", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=4, column=0, pady=vertical_padding, padx=horizont_padding)
    time_entry = ctk.CTkEntry(app)
    time_entry.grid(row=4, column=1, pady=vertical_padding, padx=horizont_padding)
    current_time = datetime.now().strftime("%H:%M")
    time_entry.insert(0, current_time)

    ctk.CTkLabel(app, text="Виявив", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=5, column=0, pady=vertical_padding, padx=horizont_padding)
    detector_menu = ctk.CTkOptionMenu(app, variable=detector_var, values=menu_data["detector"])
    detector_menu.grid(row=5, column=1, pady=vertical_padding, padx=horizont_padding)
    ctk.CTkButton(app, text="Додати", command=lambda: add_to_menu(menu_data,
                                                                  "detector",
                                                                  detector_menu,
                                                                  detector_var)).grid(row=5, column=2,
                                                                                      pady=vertical_padding,
                                                                                      padx=horizont_padding)

    ctk.CTkLabel(app, text="Командир", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=6, column=0, pady=vertical_padding, padx=horizont_padding)
    commander_menu = ctk.CTkOptionMenu(app, variable=commander_var, values=menu_data["commander"])
    commander_menu.grid(row=6, column=1, pady=vertical_padding, padx=horizont_padding)
    ctk.CTkButton(app, text="Додати", command=lambda: add_to_menu(menu_data,
                                                                  "commander",
                                                                  commander_menu,
                                                                  commander_var)).grid(row=6, column=2,
                                                                                       pady=vertical_padding,
                                                                                       padx=horizont_padding)

    ctk.CTkLabel(app, text="Витрата", font=("Arial", text_size, "bold"),
                 text_color=text_colors).grid(row=7, column=0, pady=vertical_padding, padx=horizont_padding)
    expenditure_entry = ctk.CTkEntry(app)
    expenditure_entry.grid(row=7, column=1, pady=vertical_padding, padx=horizont_padding)
    update_expenditure()
    submit_button = ctk.CTkButton(app, text="Відправити", fg_color="green", hover_color="red", command=submit_data)
    submit_button.grid(row=8, column=1, pady=30)

    app.mainloop()
