import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import csv
from collections import defaultdict
from datetime import datetime
import os
import chardet
from reportlab.lib import colors

pdfmetrics.registerFont(TTFont('FreeSans', 'DB/Font/FreeSans/FreeSans.ttf'))
pdfmetrics.registerFont(TTFont('FreeSans-Bold', 'DB/Font/FreeSans/FreeSansBold.ttf'))


def check_new_page(y_position, c):
    """Перевірка чи потрібна нова сторінка."""
    if y_position < 1 * inch:
        c.showPage()
        y_position = 8 * inch
    return y_position


def detect_encoding(file_path):
    """Визначення кодування файлу."""
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']


def read_csv_with_detected_encoding(file_path):
    """Зчитування CSV файлу з автоматичним визначенням кодування."""
    encoding = detect_encoding(file_path)
    return pd.read_csv(file_path, encoding=encoding)


def read_last_position_data(file_path):
    try:
        with open(file_path, "r", encoding='latin-1') as sp_file:
            last_line = sp_file.readlines()[-1]
            gun_number, direction = last_line.strip().split(',')
            return gun_number, direction
    except (FileNotFoundError, IndexError):
        return "Невідомо", "Невідомо"


def integrated_generate_pdf_report(input_csv_path, charges_csv_path, projectiles_csv_path, shots_csv_path,
                                   output_pdf_path):
    # Зчитує дані з файлів з визначенням кодування
    charges_data = read_csv_with_detected_encoding(charges_csv_path)
    projectiles_data = read_csv_with_detected_encoding(projectiles_csv_path)
    data = read_csv_with_detected_encoding(input_csv_path)
    shots_data = read_csv_with_detected_encoding(shots_csv_path)
    shots_position_file_path = "DB/shotsposition.csv"
    gun_number, direction = read_last_position_data(shots_position_file_path)

    y_position = 8 * inch

    # Групує за датою і пострілами
    with open(shots_csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        grouped_data = defaultdict(int)
        dates = []
        for row in reader:
            if len(row) < 5:
                continue
            date_str = row[0].split("|")[0].strip()
            date_obj = datetime.strptime(date_str, '%d.%m.%y')
            dates.append(date_obj.date())
            projectile = row[4]
            charge = row[3]
            key = f"{projectile}|{charge}"
            grouped_data[key] += 1

    # Груаує за датою та пострілами finis_shots
    finish_shots_grouped = data.groupby('Дата')['Витрата'].sum().reset_index()

    # Сортування за датою
    finish_shots_grouped_sorted = sorted(finish_shots_grouped.to_dict('records'),
                                         key=lambda x: datetime.strptime(x['Дата'], '%d.%m.%y'))

    start_date = min(dates)
    end_date = max(dates)
    total_shots = data["Витрата"].sum()
    shots_combinations = pd.DataFrame(list(grouped_data.items()), columns=['Key', 'Витрата'])
    shots_combinations[['Снаряд', 'Заряд']] = shots_combinations['Key'].str.split('|', expand=True)
    shots_combinations = shots_combinations.drop(columns=['Key'])

    # Зчитуємо дані з файлу shotsposition.csv
    shots_position_data = ""
    if os.path.exists("DB/shotsposition.csv"):
        with open("DB/shotsposition.csv", "r") as sp_file:
            reader = csv.reader(sp_file)
            next(reader)
            shots_position_data = " | ".join(next(reader, []))

    c = canvas.Canvas(output_pdf_path, pagesize=landscape(letter))

    # Вставляє дані з shotsposition.csv як заголовок
    if shots_position_data:
        c.setFont("FreeSans-Bold", 20)
        c.drawString(1 * inch, 8 * inch, shots_position_data)
        c.setFont("FreeSans", 14)
        c.setFillColor(colors.darkgrey)
        c.drawString(5 * inch, 8 * inch, f"Номер гармати: {gun_number}")
        c.drawString(7 * inch, 8 * inch, f"Дирекційний кут: {direction}")

    # Створює Label для заголовків блоків в документі
    c.setFont("FreeSans-Bold", 16)
    c.setFillColor(colors.black)
    c.drawString(2 * inch, 7.5 * inch, "Пострілів")
    c.drawString(6 * inch, 7.5 * inch, "Залишок БК")
    c.drawString(2 * inch, 5.7 * inch, "Настріл")
    c.drawString(6 * inch, 4.1 * inch, "Витрата по дням")
    c.setFont("FreeSans", 14)

    # Блок Пострілів
    c.drawString(2 * inch, 7.1 * inch, f"Дата: {start_date.strftime('%d.%m.%y')} по {end_date.strftime('%d.%m.%y')}")
    c.drawString(2 * inch, 6.5 * inch, f"Пострілів: {total_shots}")

    # Блок Залишок БК
    c.drawString(6 * inch, 7.1 * inch, "Заряди:")
    for index, row in charges_data.iterrows():
        c.drawString(6 * inch, (6.8 - 0.3 * index) * inch, f"{row['Name']} - {row['Quantity']}шт.")

    c.drawString(8 * inch, 7.1 * inch, "Снаряди:")
    for index, row in projectiles_data.iterrows():
        c.drawString(8 * inch, (6.8 - 0.3 * index) * inch, f"{row['Name']} - {row['Quantity']}шт.")

    # Блок Витрата по дням
    y_position = 3.8
    for row in finish_shots_grouped_sorted:
        c.drawString(6 * inch, y_position * inch, f"{row['Дата']} - {row['Витрата']} шт")
        y_position -= 0.3

    # Блок Настріл
    c.drawString(2 * inch, 5.3 * inch, f"Дата: {start_date.strftime('%d.%m.%y')} по {end_date.strftime('%d.%m.%y')}")

    y_position = 5.0
    for index, row in shots_combinations.iterrows():
        c.drawString(2 * inch, y_position * inch, f"{row['Снаряд']} | {row['Заряд']} - {row['Витрата']} шт.")
        y_position -= 0.3

    y_position = check_new_page(y_position, c)
    y_position -= 0.3 * inch

    # Зберігає PDF
    c.save()


if __name__ == "__main__":
    input_csv_path = "DB/finish_shots.csv"
    charges_csv_path = "DB/charges.csv"
    projectiles_csv_path = "DB/projectiles.csv"
    shots_csv_path = "DB/shots.csv"
    output_pdf_path = "report.pdf"
    integrated_generate_pdf_report(input_csv_path, charges_csv_path, projectiles_csv_path, shots_csv_path,
                                   output_pdf_path)
