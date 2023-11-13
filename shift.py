import os
import shutil
from datetime import datetime
import customtkinter as ctk
import tkinter.messagebox as messagebox


def close_shift():
    shift_name = ctk.CTkInputDialog(title="Закрити зміну", text="Ком.Гармати:").get_input()

    # Помилка, якщо рядок порожній
    if not shift_name:
        messagebox.showerror("Помилка", "Назва не може бути порожньою!")
        return

    # Створює папку з назвою введеного рядка і додає поточну дату
    date_str = datetime.now().strftime("_%Y_%m_%d")
    new_folder_name = os.path.join("DB", f"{shift_name}_{date_str}")
    os.makedirs(new_folder_name, exist_ok=True)

    # Список фалів які переносяться
    files_to_move = ["shots.csv", "finish_shots.csv"]
    for file_name in files_to_move:
        src_path = os.path.join("DB", file_name)
        if os.path.exists(src_path):
            shutil.move(src_path, new_folder_name)
        else:
            messagebox.showwarning("Попередження", f"Файл {file_name} не знайдено!")

    # Список файлів які копіюються
    files_to_copy = ["projectiles.csv", "charges.csv"]
    for file_name in files_to_copy:
        src_path = os.path.join("DB", file_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, new_folder_name)
        else:
            messagebox.showwarning("Попередження", f"Файл {file_name} не знайдено!")

    # Перенос файлу звіту з корневої папки програми
    report_path = "report.pdf"
    if os.path.exists(report_path):
        shutil.move(report_path, new_folder_name)
    else:
        messagebox.showwarning("Попередження", "Файл report.pdf не знайдено!")

    # Повідомлення про успішне закриття зміни
    messagebox.showinfo("Інформація", "Зміну успішно закрито!")
