import csv
import os
from datetime import datetime

finish_shots_file_path = "DB/finish_shots.csv"
shots_file_path = "DB/shots.csv"


def save_finish_shot(shot_count):
    # Перевіряє чи існує каталог
    if not os.path.exists("DB"):
        os.mkdir("DB")

    # Перевіряє чи існує файл
    if not os.path.exists(finish_shots_file_path):
        with open(finish_shots_file_path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Дата", "Час", "Витрата"])

    current_time = datetime.now().strftime("%d.%m.%y | %H:%M:%S")
    with open(finish_shots_file_path, "a", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([current_time.split(" | ")[0], current_time.split(" | ")[1], shot_count])

    if not os.path.exists(shots_file_path):
        with open(shots_file_path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Дата", "Час", "Пострілів"])

    with open(shots_file_path, "a", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([current_time.split(" | ")[0], current_time.split(" | ")[1], shot_count])
