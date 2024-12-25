from tkinter import Canvas, Button, Frame, BOTH, Tk, OptionMenu, StringVar

import graphlib


class BaseGraphApp:
    def __init__(self, root, title, task):
        self.root = root
        self.root.title(title)

        # Центрирование окна
        window_width, window_height = 600, 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = (screen_height - window_height) // 2
        position_left = (screen_width - window_width) // 2
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        # Канва
        self.canvas = Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

        # Инициализация графа
        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None

        # Привязка обработчиков событий
        self.canvas.bind("<Button-1>", lambda event: graphlib.on_left_click(self, event))
        self.canvas.bind("<Button-3>", lambda event: graphlib.on_right_click(self, event, task))

        # Фрейм для кнопок
        self.button_frame = Frame(root)
        self.button_frame.pack()
        self.buttons = []
        self.menus = []

        if task == "3":
            self.packet_info_window = None
            self.routing_tables = {}
            self.packet_number = 1

    def add_button(self, text, command):
        button = Button(self.button_frame, text=text, command=command)
        button.pack(side="left", padx=5, pady=10)
        self.buttons.append(button)

    def add_option_menu(self, label_text, options, default_value=None, command=None):
        frame = Frame(self.root)
        frame.pack()
        var = StringVar(value=default_value if default_value else options[0])

        if label_text:
            label = Button(frame, text=label_text)
            label.pack(side="left", padx=5)
        menu = OptionMenu(frame, var, *options, command=command)
        menu.pack(side="left", padx=5)

        self.menus.append(menu)
        return var
