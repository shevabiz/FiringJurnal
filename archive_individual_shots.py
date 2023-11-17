import tkinter as tk
import tkinter.messagebox as messagebox
import csv
from pathlib import Path

from customtkinter import CTkToplevel

shots_file_path = "DB/shots.csv"


def show_individual_shots_archive():
    archive_window = CTkToplevel()
    archive_window.title("Архів Пострілів")
    archive_window.geometry('520x750')
    archive_window.attributes('-topmost', True)
    archive_window.resizable(False, False)

    # Перевірка, чи існує файл
    if not Path(shots_file_path).exists():
        messagebox.showerror("Помилка", "Файл shots.csv не знайдено.")
        return

    # Створення ListBox для відображення даних
    lb = tk.Listbox(archive_window, bg="#242424", fg="green", font=("Ubuntu", 14, "bold"), height=80, width=80,
                    borderwidth=0, highlightthickness=0)
    lb.pack(pady=5, padx=10)

    with open(shots_file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            if not row:
                continue

            # Якщо рядок у форматі "дата,час,кількість"
            if len(row) == 3:
                lb.insert(tk.END, f"Пострілів: {row[2]}")
                lb.itemconfig(tk.END, {'bg': '#242424', 'fg': 'grey'})
            else:
                lb.insert(tk.END, f"{row[0]} | {' | '.join(row[1:])}")
