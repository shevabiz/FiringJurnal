import tkinter as tk
import tkinter.messagebox as messagebox
import csv
from pathlib import Path

shots_file_path = "DB/shots.csv"


def show_individual_shots_archive():
    archive_window = tk.Toplevel()
    archive_window.title("Архів Пострілів")
    archive_window.geometry('500x800')
    archive_window.configure(bg='black')
    archive_window.resizable(False, False)

    # Перевірка, чи існує файл
    if not Path(shots_file_path).exists():
        messagebox.showerror("Помилка", "Файл shots.csv не знайдено.")
        return

    # Створення ListBox для відображення даних
    lb = tk.Listbox(archive_window, bg="black", fg="green", font=("Ubuntu", 14, "bold"), height=80, width=80,
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
                lb.itemconfig(tk.END, {'bg': 'black', 'fg': 'grey'})
            else:
                lb.insert(tk.END, f"{row[0]} | {' | '.join(row[1:])}")
