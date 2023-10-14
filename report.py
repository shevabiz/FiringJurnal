import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import csv
from collections import defaultdict
from datetime import datetime

pdfmetrics.registerFont(TTFont('FreeSans', 'DB/Font/FreeSans/FreeSans.ttf'))
pdfmetrics.registerFont(TTFont('FreeSans-Bold', 'DB/Font/FreeSans/FreeSansBold.ttf'))


def integrated_generate_pdf_report(input_csv_path, charges_csv_path, projectiles_csv_path, shots_csv_path,
                                   output_pdf_path):
    # Зчитує дані з файлів
    charges_data = pd.read_csv(charges_csv_path)
    projectiles_data = pd.read_csv(projectiles_csv_path)
    data = pd.read_csv(input_csv_path)
    shots_data = pd.read_csv(shots_csv_path)

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

    start_date = min(dates)
    end_date = max(dates)
    total_shots = data["Витрата"].sum()
    shots_combinations = pd.DataFrame(list(grouped_data.items()), columns=['Key', 'Витрата'])
    shots_combinations[['Снаряд', 'Заряд']] = shots_combinations['Key'].str.split('|', expand=True)
    shots_combinations = shots_combinations.drop(columns=['Key'])

    # Створює PDF документ
    c = canvas.Canvas(output_pdf_path, pagesize=landscape(letter))

    # Створює Label для заголовків блоків в документі
    c.setFont("FreeSans-Bold", 16)
    c.drawString(2 * inch, 7.5 * inch, "Пострілів")
    c.drawString(6 * inch, 7.5 * inch, "Залишок БК")
    c.drawString(2 * inch, 5.7 * inch, "Настріл")
    c.drawString(6 * inch, 5.0 * inch, "Витрата по дням")
    c.setFont("FreeSans", 14)

    # Блок Пострілів
    c.drawString(2 * inch, 7.1 * inch, f"Дата: {start_date.strftime('%d.%m.%y')} по {end_date.strftime('%d.%m.%y')}")
    c.drawString(2 * inch, 6.5 * inch, f"Пострілів: {total_shots}")

    # Блок Залишок БК
    c.drawString(6 * inch, 7.1 * inch, "Заряди:")
    for index, row in charges_data.iterrows():
        c.drawString(6 * inch, (6.8 - 0.3 * index) * inch, f"{row['Name']} - {row['Quantity']}шт.")

    c.drawString(7.5 * inch, 7.1 * inch, "Снаряди:")
    for index, row in projectiles_data.iterrows():
        c.drawString(7.5 * inch, (6.8 - 0.3 * index) * inch, f"{row['Name']} - {row['Quantity']}шт.")

    # Блок Витрата по дням
    y_position = 4.6
    for index, row in finish_shots_grouped.iterrows():
        c.drawString(6 * inch, y_position * inch, f"{row['Дата']} - {row['Витрата']} шт")
        y_position -= 0.3

    # Блок Настріл
    c.drawString(2 * inch, 5.3 * inch, f"Дата: {start_date.strftime('%d.%m.%y')} по {end_date.strftime('%d.%m.%y')}")

    y_position = 5.0
    for index, row in shots_combinations.iterrows():
        c.drawString(2 * inch, y_position * inch, f"{row['Снаряд']} | {row['Заряд']} - {row['Витрата']} шт.")
        y_position -= 0.3

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

