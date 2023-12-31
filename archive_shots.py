import os
import csv
import tkinter as tk
from customtkinter import CTkToplevel
from finish_shots_handler import finish_shots_file_path


def show_archive_shots():
    # Створення дочірнього вікна
    child = CTkToplevel()
    child.title("Архів стрільби")
    child.geometry('400x750')
    child.attributes('-topmost', True)
    child.resizable(False, False)

    # Створення Text widget для відображення даних
    text_widget = tk.Text(child, font=("Ubuntu", 14), bg="#242424", fg="green", borderwidth=0, wrap=tk.NONE, padx=10,
                          pady=5, highlightthickness=0)
    text_widget.pack(pady=(10, 20), padx=20, fill=tk.BOTH, expand=True)
    # Створення Label для відображення підсумків
    total_shots_label = tk.Label(child, font=("Ubuntu", 14), bg="#242424", fg="white")
    total_shots_label.pack(pady=(10, 20), padx=20, side=tk.BOTTOM)
    text_widget.tag_configure("total", font=("Ubuntu", 14, "bold"), foreground="grey")

    if os.path.exists(finish_shots_file_path):
        with open(finish_shots_file_path, "r") as file:
            file_content = file.readlines()
            total_shots = len(file_content) - 1
            total_shots_label.config(text="Загальна кількість пострілів: " + str(total_shots))

        rows = list(csv.reader(file_content))
        data_rows = rows[1:]

        total_expenditure = sum(int(row[2]) for row in data_rows)
        total_shots_label.config(text="Загальна витрата: " + str(total_expenditure),
                                 font=("Ubuntu", 14, "bold"), foreground="grey")

        last_date = None
        total_shots_for_day = 0
        shot_number_for_day = 1  # Для номерації пострілів кожного дня

        for row in data_rows:
            current_date = row[0].replace("-", ".")

            # Перевірка на зміну дати
            if last_date and current_date != last_date:
                total_line = f"{last_date} Пострілів: {total_shots_for_day}\n\n"
                text_widget.insert(tk.END, total_line, "total")
                total_shots_for_day = 0
                shot_number_for_day = 1

            # Додаємо відступи між стовбцями та вирівнюємо дані по центру
            spaced_row = [f"{item:^10}" for item in row[1:]]
            data_line = f"{shot_number_for_day:02}. {row[0]:^20}  " + "  ".join(spaced_row) + "\n"
            text_widget.insert(tk.END, data_line)
            total_shots_for_day += int(row[2])

            shot_number_for_day += 1
            last_date = current_date

        child.mainloop()

    if __name__ == "__main__":
        show_archive_shots()
        