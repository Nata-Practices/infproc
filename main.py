import tkinter as tk

from tkinter import messagebox
from tasks.first_task import GraphApp
from tasks.second_task import FloydApp
from tasks.third_task import PacketRoutingApp


class MainMenu:
    def __init__(self, _root):
        self.root = _root
        self.root.title("Главное меню")
        self.root.geometry("450x350")

        self.label = tk.Label(_root, text="Выберите лабораторную работу", font=("Courier", 14))
        self.label1 = tk.Label(_root, text="Гордеева Наталья Сергеевна", font=("Courier", 14))
        self.label.pack(pady=20)
        self.label1.pack(pady=0)

        # Создаем кнопки для 4 лабораторных работ
        self.lab1_button = tk.Button(_root, text="Лабораторная работа 1: Редактор граф", width=50, command=self.open_lab1)
        self.lab1_button.pack(pady=10)

        self.lab2_button = tk.Button(_root, text="Лабораторная работа 2: Алгоритмы Дейкстры и Флойда", width=50, command=self.open_lab2)
        self.lab2_button.pack(pady=10)

        self.lab3_button = tk.Button(_root, text="Лабораторная работа 3: Симуляция передачи пакетов", width=50, command=self.open_lab3)
        self.lab3_button.pack(pady=10)

        self.lab4_button = tk.Button(_root, text="Лабораторная работа 4", width=50, command=self.open_lab4)
        self.lab4_button.pack(pady=10)

        # Кнопка выхода
        self.exit_button = tk.Button(_root, text="Выход", width=30, command=self.exit_app)
        self.exit_button.pack(pady=20)

    def open_lab1(self):
        lab1_window = tk.Toplevel(self.root)
        GraphApp(lab1_window)

    def open_lab2(self):
        lab2_window = tk.Toplevel(self.root)
        FloydApp(lab2_window)

    def open_lab3(self):
        lab3_window = tk.Toplevel(self.root)
        PacketRoutingApp(lab3_window)

    def open_lab4(self):
        messagebox.showinfo("Лабораторная работа 4", "Лабораторная работа 4 еще не реализована.")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
