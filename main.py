import customtkinter as ctk

from tasks.first_task import GraphApp
from tasks.four_task import HTTPApp
from tasks.second_task import FloydApp
from tasks.third_task import PacketRoutingApp


class MainMenu:
    def __init__(self, _root):
        self.root = _root
        self.root.title("Главное меню")
        self.current_window = None
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 450) // 2
        y = (screen_height - 350) // 2
        self.root.geometry(f"{450}x{350}+{x}+{y}")
        self.root.resizable(False, False)

        self.label = ctk.CTkLabel(self.root, text="Выберите лабораторную работу", font=("Courier", 23))
        self.label1 = ctk.CTkLabel(self.root, text="Гордеева Наталия Сергеевна\n"
                                                   "Пудовкин Александр Павлович", font=("Courier", 14))
        self.label.pack(pady=20)
        self.label1.pack(pady=0)

        # Создаем кнопки для 4 лабораторных работ
        labs = (
            ("Лабораторная работа 1: Редактор граф", GraphApp),
            ("Лабораторная работа 2: Алгоритмы Дейкстры и Флойда", FloydApp),
            ("Лабораторная работа 3: Симуляция передачи пакетов", PacketRoutingApp),
            ("Лабораторная работа 4: HTTP сервер", HTTPApp),
        )

        for text, app_class in labs:
            btn = ctk.CTkButton(self.root, text=text, command=lambda c=app_class: self.open_lab(c))
            btn.pack(pady=10)

        # Кнопка выхода
        self.exit_button = ctk.CTkButton(self.root, text="Выход", width=30, command=self.exit_app)
        self.exit_button.pack(pady=10)

    def open_lab(self, chosen_lab):
        if self.current_window is None:
            self.root.withdraw()
            lab_window = ctk.CTkToplevel(self.root)
            self.current_window = lab_window
            chosen_lab(lab_window)
            lab_window.protocol("WM_DELETE_WINDOW", self.on_lab_close)

    def on_lab_close(self):
        if self.current_window is not None:
            self.current_window.destroy()
            self.current_window = None
            self.root.deiconify()

    def exit_app(self):
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainMenu(root)
    root.mainloop()
