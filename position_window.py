import customtkinter as ctk
import csv

# Шлях до файлу з даними про позиції
shots_position_file = "DB/shotsposition.csv"


def read_last_position_data():
    try:
        with open(shots_position_file, 'r', newline='') as file:
            last_line = file.readlines()[-1]
            return last_line.strip().split(',')
    except (FileNotFoundError, IndexError):
        return "", ""


def show_position_window(parent_window, on_close_callback):
    parent_window.update()
    window = ctk.CTkToplevel(parent_window)
    window.title("Позиція")
    window.geometry("300x250")

    # Центрування вікна відносно батьківського вікна
    window_width = 300
    window_height = 250
    parent_x = parent_window.winfo_x()
    parent_y = parent_window.winfo_y()
    parent_width = parent_window.winfo_width()
    parent_height = parent_window.winfo_height()
    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2
    window.geometry(f"+{x}+{y}")

    # Заповнення полів введення останніми збереженими даними
    last_gun_number, last_direction = read_last_position_data()

    # Поле для вводу номера гармати
    gun_number_label = ctk.CTkLabel(window, text="Номер гармати:")
    gun_number_label.pack(pady=5)
    gun_number_entry = ctk.CTkEntry(window, width=200)
    gun_number_entry.pack(pady=5)
    gun_number_entry.insert(0, last_gun_number)

    # Поле для вводу дирекційного кута
    direction_label = ctk.CTkLabel(window, text="Дирекційний кут:")
    direction_label.pack(pady=5)
    direction_entry = ctk.CTkEntry(window, width=200)
    direction_entry.pack(pady=5)
    direction_entry.insert(0, last_direction)

    # Кнопка для збереження даних
    save_button = ctk.CTkButton(window, text="Зберегти",
                                command=lambda: save_position(gun_number_entry.get(), direction_entry.get(), window))
    save_button.pack(pady=20)

    # Забезпечення, щоб вікно було на передньому плані
    window.attributes('-topmost', True)

    def save_position(gun_number, direction, window_position):
        # Збереження даних у файл
        with open(shots_position_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([gun_number, direction])
        window_position.destroy()
        on_close_callback()
