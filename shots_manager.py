import csv
import os
from datetime import datetime

# Шлях до файлу
shots_file_path = "DB/shots.csv"

# Перевіряє і створює папки та файли, якщо вони відсутні
if not os.path.exists("DB"):
    os.mkdir("DB")

if not os.path.exists(shots_file_path):
    with open(shots_file_path, "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Дата", "Час", "Приціл", "Кутомір", "Снаряд", "Заряд", "Таймер"])


def save_shot_data(pricil, kutomir, snaryad, zaryad, time_value):
    current_time = datetime.now()
    date_str = current_time.strftime("%d.%m.%y")
    time_str = current_time.strftime("%H:%M:%S")

    with open(shots_file_path, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_str, time_str, pricil, kutomir, snaryad, zaryad, time_value])


# Функція для перевірки наявності даних у shots.csv
def is_shots_file_empty():
    with open(shots_file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        return not bool(list(reader))


# Функція для збереження даних про позицію в shotsposition.csv
def save_position_data(firing_position, gun_commander):
    position_file_path = "DB/shotsposition.csv"
    with open(position_file_path, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Вогнева позиція", "Командир гармати"])
        writer.writerow([firing_position, gun_commander])
