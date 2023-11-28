import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import os
from datetime import datetime
import subprocess
import threading
from customtkinter import CTk, CTkEntry, CTkButton

lock = threading.Lock()


def send_signal_message_thread(sender_number, phone_number, message, attachment=None):
    threading.Thread(target=send_signal_message, args=(sender_number, phone_number, message, attachment)).start()


def send_signal_message(sender_number, phone_number, message, attachment=None):
    with lock:
        if not sender_number or not phone_number:
            print("Sender or Recipient phone number is missing.")
            return False

        message = message.replace("\n", " ")
        command = f"signal-cli -u {sender_number} send -m \"{message}\" {phone_number}"
        if attachment:
            command += f" -a {attachment}"

        print(f"Executing: {command}")

        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        stdout, stderr = result.communicate()
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(stderr.decode())
        return True


def receive_signal_messages_sync(sender_number):
    with lock:
        command = f'signal-cli -u {sender_number} receive'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            received_messages = []
            current_message = None
            is_group_message = False

            for line in result.stdout.splitlines():
                if "Group" in line:
                    is_group_message = True
                    break

                if line.startswith("Body:") and not is_group_message:
                    current_message = line.split("Body:", 1)[1].strip()

                elif "With profile key" in line and current_message is not None and not is_group_message:
                    received_messages.append(current_message)
                    current_message = None
                    is_group_message = False

                elif current_message is not None and not is_group_message:
                    current_message += "\n" + line.strip()

            return received_messages
        except Exception as e:
            print(f"Error executing receive command: {e}")
            return []


class ChatShotsWindow:
    def __init__(self):
        self.chat_window = None
        self.msg_entry = None
        self.chat_text_area = None
        self.after_id = None
        self.is_chat_window_open = False
        self.history_folder = "DB/chat_history"
        self.history_file_path = os.path.join(self.history_folder, f"{datetime.now().strftime('%Y-%m-%d')}.txt")
        self.ensure_chat_history_folder_exists()

    def ensure_chat_history_folder_exists(self):
        if not os.path.exists(self.history_folder):
            os.makedirs(self.history_folder)
        # Створю файл з архівом чату кожного дня
        if not os.path.exists(self.history_file_path):
            open(self.history_file_path, 'w').close()

    def append_message_to_history(self, sender, message):
        with open(self.history_file_path, 'a', encoding="ISO 8859-5") as f:
            f.write(f"{sender}: {message}\n")

    @staticmethod
    def get_phone_numbers():
        df = pd.read_csv("DB/signal_settings.csv")
        sender = "+" + str(df["Sender"].iloc[0])
        recipient = "+" + str(df["Recipient"].iloc[0])
        return sender, recipient

    def check_for_new_messages(self):
        if not self.is_chat_window_open:
            return
        threading.Thread(target=self.poll_for_messages).start()
        self.after_id = self.chat_window.after(15000, self.check_for_new_messages)

    def poll_for_messages(self):
        sender_number, _ = ChatShotsWindow.get_phone_numbers()
        received_messages = receive_signal_messages_sync(sender_number)
        for message_text in received_messages:
            self.chat_text_area.configure(state='normal')
            self.chat_text_area.insert(tk.END, f"\nОтримано: \n{message_text}\n\n", 'received')
            self.append_message_to_history("Отримано", message_text)
            self.chat_text_area.configure(state='disabled')
            self.chat_text_area.see(tk.END)

    def open_chat_shots_window(self, sight, anglemeter, charge, projectile, time_val):
        if not self.chat_window:
            self.chat_window = CTk()
            self.chat_window.title("Чат стрільби")
            self.chat_window.geometry("400x700")
            self.chat_window.configure(fg_color="#242424")
            self.chat_window.resizable(False, False)
            self.chat_text_area = scrolledtext.ScrolledText(self.chat_window, wrap=tk.WORD,
                                                            width=40,
                                                            height=22,
                                                            bg="#242424",
                                                            fg="white",
                                                            font=("Arial", 12),
                                                            relief=tk.FLAT,
                                                            highlightthickness=1,
                                                            highlightcolor="grey",
                                                            highlightbackground="grey",
                                                            padx=10)
            self.chat_text_area.place(relx=0.5, rely=0.3, anchor="center")
            self.chat_text_area.configure(state='disabled', )
            self.chat_text_area.tag_configure('received', foreground='orange')
            self.msg_entry = CTkEntry(self.chat_window,
                                      width=350,
                                      height=50,
                                      font=("Arial", 14),
                                      fg_color="grey",
                                      text_color="white",
                                      border_width=1,
                                      border_color="grey"
                                      )

            self.msg_entry.place(relx=0.5, rely=0.8, anchor="center")
            message_str = f"Приціл: {sight}\nКутомір: {anglemeter}\nЗаряд: {charge} і Снаряд: {projectile}"
            if time_val:
                message_str += f" (Час: {time_val})"
            self.msg_entry.insert(0, message_str)

            send_btn = CTkButton(self.chat_window,
                                 text="Відправити",
                                 command=self.send_message,
                                 width=150,
                                 font=("Arial", 14, "bold"),
                                 hover_color="green")
            send_btn.place(relx=0.5, rely=0.9, anchor="center")
            self.chat_window.bind("<Return>", lambda event: self.send_message())

            max_buttons_per_row = 3

            quick_replies = ["Навестись! ", "Стій, записати! ", "Стій! ", "Вогонь! ", "В укриття! ", "Маскуємо! "]

            for idx, reply in enumerate(quick_replies):
                row = idx // max_buttons_per_row
                col = idx % max_buttons_per_row

                btn = CTkButton(self.chat_window, text=reply,
                                text_color="white",
                                fg_color="green",
                                width=100,
                                command=lambda r=reply: self.msg_entry.insert(0, r))

                btn.place(relx=(0.20 + col * 0.30), rely=0.65 + row * 0.07, anchor="center")

            self.is_chat_window_open = True
            self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat)
            self.check_for_new_messages()
            self.chat_window.mainloop()

    def close_chat(self):
        self.is_chat_window_open = False
        if self.after_id:
            self.chat_window.after_cancel(self.after_id)
        with open(self.history_file_path, 'a', encoding="ISO 8859-5") as f:
            f.write("-------------------------------\n")
        self.chat_window.destroy()
        self.chat_window = None

    def send_message(self):
        sender_number, phone_number = self.get_phone_numbers()
        print(f"Sender number: {sender_number}, Recipient number: {phone_number}")

        send_signal_message_thread(sender_number, phone_number, self.msg_entry.get())
        self.chat_text_area.configure(state='normal')
        self.chat_text_area.insert(tk.END, f"Ви: \n{self.msg_entry.get()}\n")
        self.append_message_to_history("Ви", self.msg_entry.get())
        self.chat_text_area.configure(state='disabled')
        self.chat_text_area.see(tk.END)
        self.msg_entry.delete(0, tk.END)

    def update_chat_input(self, sight, anglemeter, charge, projectile, time_val):
        message_str = f" Приціл: {sight}\nКутомір: {anglemeter}\nЗаряд: {charge} і Снаряд: {projectile}"
        if time_val:
            message_str += f" (Час: {time_val})"
        if hasattr(self, 'chat_window') and self.chat_window and self.is_chat_window_open:
            if hasattr(self, 'msg_entry') and self.msg_entry:
                self.msg_entry.delete(0, tk.END)
                self.msg_entry.insert(0, message_str)
        else:
            self.open_chat_shots_window(sight, anglemeter, charge, projectile, time_val)


chat_window_instance = ChatShotsWindow()

if __name__ == "__main__":
    chat_window_instance = ChatShotsWindow()
