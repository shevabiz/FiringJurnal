import csv
from pathlib import Path


def reduce_inventory(file_path, item_name):
    if not Path(file_path).exists():
        print(f"File {file_path} does not exist!")
        return

    temp_data = []
    found_item = False
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        temp_data.append(headers)

        for row in reader:
            if row[0] == item_name:
                found_item = True
                try:
                    count = int(row[1])
                    count -= 1  # зменшуємо кількість на одиницю
                    row[1] = str(count)
                except (IndexError, ValueError):
                    print(f"Error processing the count for item {item_name}.")
                    pass
            temp_data.append(row)

    if not found_item:
        print(f"Item {item_name} not found in file {file_path}!")

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(temp_data)


def update_inventory(charge_name, projectile_name):
    charges_file_path = "DB/charges.csv"
    projectiles_file_path = "DB/projectiles.csv"

    reduce_inventory(charges_file_path, charge_name)
    reduce_inventory(projectiles_file_path, projectile_name)
