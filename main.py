import sys
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from storage import show_storage_window
import os
import csv
from shots_manager import shots_file_path, is_shots_file_empty, save_position_data
from datetime import datetime
from finish_shots_handler import save_finish_shot
from archive_shots import show_archive_shots
from archive_individual_shots import show_individual_shots_archive
from inventory_manager import reduce_inventory
from show_shot_stats import display_shot_stats
from report import integrated_generate_pdf_report
import webbrowser
from shift import close_shift
from chat_shots import chat_window_instance


# Перевірка і створення папки
if not os.path.exists("DB"):
    os.mkdir("DB")

# Шляхи до файлів
projectile_file_path = "DB/projectiles.csv"
charge_file_path = "DB/charges.csv"

# Створення файлів, якщо вони відсутні
for path in [projectile_file_path, charge_file_path]:
    if not os.path.exists(path):
        with open(path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Виберіть"])

# Файл де зберігаються дані про відправника і отримувача повідомлень в Signal
settings_file_path = "DB/signal_settings.csv"

settings_window = None


def send_signal_message(phone_number, message, attachment=None):
    """
    Send a message through Signal CLI to a given phone number.

    :param phone_number: The recipient's phone number.
    :param message: The message to send.
    :param attachment: Path to the attachment file. Default is None.
    """
    command = f"signal-cli -u {sender_number_var.get()} send -m \"{message}\" {phone_number}"

    if attachment:
        command += f" -a {attachment}"

    result = os.system(command)
    if result != 0:
        print(f"Помилка відправки Signal повідомлення: {command}")


def generate_and_open_report():
    # Файли з яких беруться дані для формування звіту
    input_csv_path = "DB/finish_shots.csv"
    charges_csv_path = "DB/charges.csv"
    projectiles_csv_path = "DB/projectiles.csv"
    shots_csv_path = "DB/shots.csv"
    output_pdf_path = "report.pdf"

    integrated_generate_pdf_report(input_csv_path, charges_csv_path, projectiles_csv_path, shots_csv_path,
                                   output_pdf_path)

    # Відкриття згенерованого PDF-файлу
    webbrowser.open('file://' + os.path.realpath(output_pdf_path))

    # Відправляє повідомлення в Signal
    send_signal_message(recipient_number_var.get(), 'Звіт по стрільбі', output_pdf_path)


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def load_items_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            return [row[0] for row in reader]
    return []


def about_author():
    about_window = ctk.CTkToplevel(root)
    about_window.title("Про програму")

    ctk.CTkLabel(about_window, text="Автор: Шевцов Василь", font=("Arial", 16)).pack(pady=10,
                                                                                     padx=10)
    ctk.CTkLabel(about_window, text="Е-Mail: "
                                    "shevabiz@gmail.com", font=("Arial", 16)).pack(pady=10,
                                                                                   padx=10)
    ctk.CTkLabel(about_window, text="Версія 1.4", font=("Arial", 16)).pack(pady=10,
                                                                           padx=10)


shot_count = 0
timer_id = "0"


def shoot():
    global shot_count
    current_time = datetime.now().strftime("%d.%m.%y | %H:%M:%S")
    pricil = entry1.get()
    kutomir = entry2.get()
    projectile = projectile_combobox.get() or ""
    charge = charge_combobox.get() or ""
    time_value = time_entry.get() or ""

    shot_count += 1
    journal_text.insert(tk.END,
                        f"\n{shot_count}. {current_time} | {pricil} | {kutomir} | {projectile} | {charge} "
                        f"| {time_value}")

    # Записує дані в файл
    with open(shots_file_path, "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([current_time, pricil, kutomir, projectile, charge, time_value])

    start_timer()
    projectile = projectile_combobox.get().strip()
    charge = charge_combobox.get().strip()

    if projectile:  # Перевірка, чи не порожній рядок
        reduce_inventory(projectile_file_path, projectile)

    if charge:
        reduce_inventory(charge_file_path, charge)


def update_journal():
    with open(shots_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            journal_text.insert(tk.END, ' | '.join(row) + '\n')


is_timer_running = False


def start_timer():
    global is_timer_running
    if not is_timer_running:
        is_timer_running = True
        update_timer()


def stop_timer():
    global is_timer_running
    is_timer_running = False
    timer_label.config(text="")


def stop_and_save():
    global is_timer_running
    is_timer_running = False


def update_timer():
    if not is_timer_running:
        return
    current_timer = timer_label.cget("text")
    if current_timer == "Хвилини:Секунди":
        timer_label.config(text="00:00")
        root.after(1000, update_timer)
        return

    minutes, seconds = map(int, current_timer.split(":"))
    seconds += 1
    if seconds == 60:
        seconds = 0
        minutes += 1
    timer_label.config(text=f"{minutes:02}:{seconds:02}")
    root.after(1000, update_timer)


def finish_and_save():
    global shot_count

    # Записує дані про постріл в Журнал
    shot_count = len(journal_text.get("1.0", "end-1c").strip().split("\n"))
    save_finish_shot(shot_count)

    # Очищає журнал
    journal_text.delete("1.0", "end")
    shot_count = 0

    # Очищає дані в полях після Стій, записати
    entry1.delete(0, "end")
    entry2.delete(0, "end")
    projectile_combobox.set("")
    charge_combobox.set("")
    time_entry.delete(0, "end")

    # Обнулює таймер
    if timer_id:
        root.after_cancel(timer_id)
    timer_label.config(text="00:00")


def show_settings_window():
    global settings_window, sender_number_var, recipient_number_var
    if settings_window:
        settings_window.destroy()

    settings_window = tk.Toplevel(root)
    settings_window.title("Налаштування Signal-CLI")
    settings_window.geometry("250x300")
    settings_window.configure(bg='black')

    label_sender = ctk.CTkLabel(settings_window, text="Номер для Signal-CLI:", font=("Arial", 14, "bold"),
                                text_color="grey")
    label_sender.pack(pady=10)

    entry_sender = ttk.Entry(settings_window, textvariable=sender_number_var, font=("Arial", 12, "bold"))
    entry_sender.pack(pady=5)

    label_recipient = ctk.CTkLabel(settings_window, text="Номер отримувача:", font=("Arial", 14, "bold"),
                                   text_color="grey")
    label_recipient.pack(pady=10)

    entry_recipient = ttk.Entry(settings_window, textvariable=recipient_number_var, font=("Arial", 12, "bold"))
    entry_recipient.pack(pady=5)

    save_button = ctk.CTkButton(settings_window, text="Зберегти", font=("Arial", 12), text_color="white",
                                command=save_settings)
    save_button.pack(pady=20)


def save_settings():
    global sender_number_var, recipient_number_var
    sender_number = sender_number_var.get()
    recipient_number = recipient_number_var.get()

    # Зберігає дані про отримувача і відправника введених в Налаштуваннях
    with open(settings_file_path, "w", newline='') as csv_file:
        writer_setting = csv.writer(csv_file)
        writer_setting.writerow(["Sender", "Recipient"])
        writer_setting.writerow([sender_number, recipient_number])

    if settings_window:
        settings_window.destroy()


def load_settings():
    global sender_number_var, recipient_number_var
    if os.path.exists(settings_file_path):
        with open(settings_file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            sender, recipient = next(reader)
            sender_number_var.set(sender)
            recipient_number_var.set(recipient)


# Посилання на Донат
def open_donate_link():
    webbrowser.open('https://send.monobank.ua/jar/AWPTFLk2cC')


root = ctk.CTk()
root.title("Журнал стрільб")
root.geometry('500x700')
root.resizable(False, False)

sender_number_var = tk.StringVar()
recipient_number_var = tk.StringVar()

# Створення верхнього меню
menu = tk.Menu(root)
root.config(menu=menu)
help_menu = tk.Menu(menu)
restart_icon = tk.PhotoImage(file="DB/img/restart.png")
restart_icon = restart_icon.subsample(28)
menu.add_command(image=restart_icon, command=restart_program)
menu.add_cascade(label="Допомога", menu=help_menu, font=("Arial", 10))
menu.add_command(label="Звіт", font=("Arial", 10), command=generate_and_open_report)
help_menu.add_command(label="Налаштування", command=show_settings_window, font=("Arial", 10))
help_menu.add_command(label="Закрити зміну", command=close_shift, font=("Arial", 10))
help_menu.add_command(label="Про автора", command=about_author, font=("Arial", 10))

donat_btn = ctk.CTkButton(root, text="Підтримати проєкт",
                          command=open_donate_link,
                          font=("Arial", 14, "bold"),
                          fg_color="#242424",
                          text_color="white",
                          hover_color="#242424")

donat_btn.place(relx=0.35, rely=0.95)
# Кнопки в центрі
btn1 = ctk.CTkButton(root, text="Архів стрільби", command=show_archive_shots)
btn1.place(relx=0.3, rely=0.05, anchor="center")

btn2 = ctk.CTkButton(root, text="Архів Пострілів", command=show_individual_shots_archive)
btn2.place(relx=0.7, rely=0.05, anchor="center")

# Таймер
timer_label = tk.Label(root, text="00:00", font=("Ubuntu", 24, "bold"), bg="#242424", fg="green")
timer_label.place(relx=0.5, rely=0.13, anchor="center")

# Поля для вводу
lbl1 = ctk.CTkLabel(root, text="Приціл:", font=("Arial", 14, "bold"), text_color="white")
lbl1.place(relx=0.1, rely=0.2, anchor="center")
entry1 = ctk.CTkEntry(root, width=70)
entry1.place(relx=0.3, rely=0.2, anchor="center")

lbl2 = ctk.CTkLabel(root, text="Кутомір:", font=("Arial", 14, "bold"), text_color="white")
lbl2.place(relx=0.1, rely=0.25, anchor="center")
entry2 = ctk.CTkEntry(root, width=70)
entry2.place(relx=0.3, rely=0.25, anchor="center")


# Обмеження для поля Приціл
def restrict_pricil_input(_):
    value = entry1.get()
    if not all(c.isdigit() or c == "." for c in value) or len(value) > 7:
        entry1.delete(0, tk.END)
        entry1.insert(0, value[:-1])


# Обмеження для поля Час
def restrict_time_input(_):
    value = time_entry.get()
    if not all(c.isdigit() or c == "." for c in value) or len(value) > 7:
        time_entry.delete(0, tk.END)
        time_entry.insert(0, value[:-1])


def restrict_kutomir_input(event):
    if event.keysym in ("BackSpace", "Delete"):
        return

    value = entry2.get()

    # Дозволяє ввід лише цифри і один дефіс
    if not all(char.isdigit() or char == '-' for char in value) or value.count("-") > 1:
        entry2.delete(0, tk.END)
        entry2.insert(0, value[:-1])
        return

    # Автоматично додає дефіс після двох цифр
    if len(value.replace("-", "")) == 2 and "-" not in value:
        entry2.insert(2, "-")
        return

    # Перевіряє, чи є дефіс в правильному місці
    if len(value) >= 3 and "-" in value and not value[2] == "-":
        entry2.delete(0, tk.END)
        entry2.insert(0, value[:-1])
        return

    # Дозволяє лише дві цифри перед і після дефісу
    parts = value.split("-")
    if any(len(part) > 2 for part in parts):
        entry2.delete(0, tk.END)
        entry2.insert(0, value[:-1])


entry1.bind("<KeyRelease>", restrict_pricil_input)
entry2.bind("<KeyRelease>", restrict_kutomir_input)


def combined_function():
    stop_and_save()
    finish_and_save()


# Випадаюче меню
charge_label = ctk.CTkLabel(root, text="Заряд:", font=("Arial", 14, "bold"), text_color="white")
charge_label.place(relx=0.5, rely=0.2, anchor="center")
charge_combobox = ttk.Combobox(root, values=load_items_from_file(charge_file_path), width=7, font=("Arial", 12))
charge_combobox.place(relx=0.7, rely=0.2, anchor="center")

projectile_label = ctk.CTkLabel(root, text="Снаряд:", font=("Arial", 14, "bold"), text_color="white")
projectile_label.place(relx=0.5, rely=0.25, anchor="center")
projectile_combobox = ttk.Combobox(root, values=load_items_from_file(projectile_file_path), width=7, font=("Arial", 12))
projectile_combobox.place(relx=0.7, rely=0.25, anchor="center")
# Час для вибраних снарядів
time_label = ctk.CTkLabel(root, text="Час:", font=("Arial", 14, "bold"), text_color="white")
time_label.place(relx=0.9, rely=0.22, anchor="center")
time_entry = ctk.CTkEntry(root, width=60)
time_entry.place(relx=0.9, rely=0.25, anchor="center")

# Кнопки
save_btn = ctk.CTkButton(root, text="Стій, записати", font=("Arial", 14, "bold"), text_color="white", fg_color="green")
save_btn.configure(command=combined_function)
save_btn.place(relx=0.2, rely=0.35, anchor="center")


def on_send_button_clicked():
    # Стчичує дані з полів які повині відправлятися в Чат Пострілів
    sight_val = entry1.get()
    anglemeter_val = entry2.get()
    charge_val = charge_combobox.get()
    projectile_val = projectile_combobox.get()
    time_val = time_entry.get()

    # Оновляє поля в Чаті пострілів
    chat_window_instance.update_chat_input(sight_val, anglemeter_val, charge_val, projectile_val, time_val)


send_btn = ctk.CTkButton(root, text="Відправити", font=("Arial", 14, "bold"), text_color="white", fg_color="blue")
send_btn.configure(command=on_send_button_clicked)
send_btn.place(relx=0.5, rely=0.35, anchor="center")

shoot_btn = ctk.CTkButton(root, text="Постріл", command=shoot, font=("Arial", 14, "bold"), text_color="white")
shoot_btn.place(relx=0.8, rely=0.35, anchor="center")
root.bind("<Control_L>", lambda e: shoot())

# Журнал стрільби
journal_label = ctk.CTkLabel(root, text="Журнал стрільби:", font=("Arial", 14, "bold"), text_color="white")
journal_label.place(relx=0.5, rely=0.4, anchor="n")
journal_text = tk.Text(root, height=13, width=50, font=("Ubuntu", 12), fg="green", bg="black", highlightthickness=0)
journal_text.configure(font=("Ubuntu", 12), fg="green")
journal_text.place(relx=0.5, rely=0.6, anchor="center")

# Кнопки внизу
btn_sklad = ctk.CTkButton(root, text="Склад", command=show_storage_window,
                          font=("Arial", 14, "bold"),
                          text_color="white")
btn_sklad.place(relx=0.3, rely=0.85, anchor="center")

btn_settings = ctk.CTkButton(root, text="Настріл", command=display_shot_stats,
                             font=("Arial", 14, "bold"),
                             text_color="white")
btn_settings.place(relx=0.7, rely=0.85, anchor="center")

update_timer()


# Функція для показу вікна введення даних про вогневу позицію, якщо shots.csv порожній
def show_input_window():
    def save_and_close():
        firing_position = firing_position_entry.get()
        gun_commander = gun_commander_entry.get()
        save_position_data(firing_position, gun_commander)
        input_window.destroy()

    input_window = ctk.CTkToplevel(root)
    input_window.geometry("300x250")
    input_window.title("Ведіть дані")
    input_window.resizable(False, False)

    tk.Label(input_window, text="Вогнева позиція:", background="#242424",
             font=("Arial", 12, "bold",),
             fg="grey").pack(pady=5)
    firing_position_entry = tk.Entry(input_window, font=("Arial", 12))
    firing_position_entry.pack(pady=10)

    tk.Label(input_window, text="Командир гармати:",
             background="#242424",
             font=("Arial", 12, "bold"),
             fg="grey").pack(pady=5)
    gun_commander_entry = tk.Entry(input_window, font=("Arial", 12))
    gun_commander_entry.pack(pady=10)

    ctk.CTkButton(input_window, text="Записати", command=save_and_close, font=("Arial", 14)).pack(pady=20)

    input_window.grab_set()
    input_window.wait_window()


# Перерка чи файл shots.csv містить данні
if is_shots_file_empty():
    show_input_window()

# Загружає дані налаштувань Signal
load_settings()

root.mainloop()

# v.1.4 - При вході в програму якщо файл shots.csv не має даних - появляється вікно з полями вводу Вогнева позиція,
#         Командир гармати і кнопка Записати
#         дані запсуються в файл DB/shotsposition.csv
#         Відобразив дані з файлу shotsposition.csv  як заголовок звіту
