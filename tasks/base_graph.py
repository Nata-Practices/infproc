from tkinter import Canvas, Button, Frame, BOTH, OptionMenu, StringVar, Y, LEFT, Label

import graphlib


class BaseGraphApp:
    def __init__(self, root, title, task):
        self.root = root
        root.title(title)

        # Ширина окна и его позиционирование
        window_width, window_height = 1250 if task in (
            "1", "2") else 1300 if task == "3" else 300, 500 if task != "4" else 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = (screen_height - window_height) // 2
        position_left = (screen_width - window_width) // 2
        root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
        root.resizable(False, False)

        # Главный фрейм для разделения на верхнюю и нижнюю части
        self.top_frame = Frame(root, bg="#ffffff")
        self.top_frame.pack(fill=BOTH, expand=True)

        # Выключаем всё, что не нужно в 4 таске
        if task != "4":
            # Левая часть: Канвас для графа
            self.canvas = Canvas(self.top_frame, width=500, height=300, bg="white")
            self.canvas.pack(side=LEFT, fill=BOTH, padx=10, pady=10)

            # Правая часть: Фрейм для матрицы смежности
            self.matrix_frame = Frame(self.top_frame)
            self.matrix_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

            # Заголовок для матрицы
            self.matrix_title = Label(self.matrix_frame, text="Матрица смежности", font=("Arial", 12, "bold"))
            self.matrix_title.pack(pady=5)

            # Создание Frame для матрицы
            self.matrix_scroll_canvas = Canvas(self.matrix_frame, width=475, bg="#f0f0f0")
            self.matrix_scroll_canvas.pack(side=LEFT, fill=Y, expand=True)

            # Внутренний фрейм для размещения Entry виджетов
            self.matrix_inner_frame = Frame(self.matrix_scroll_canvas)
            self.matrix_scroll_canvas.create_window((0, 0), window=self.matrix_inner_frame, anchor='nw')

            self.matrix_inner_frame.bind("<Configure>", lambda event: self.matrix_scroll_canvas.configure(
                scrollregion=self.matrix_scroll_canvas.bbox("all")))

            # Список для хранения Entry виджетов матрицы
            self.matrix_entries = []

        # Фрейм для кнопок
        self.button_frame = Frame(self.top_frame, bg="#f0f0f0", width=200, height=450, bd=2, relief="groove")
        self.button_frame.pack(fill='x', padx=10, pady=10)
        self.buttons = []
        self.menus = []

        # Инициализация графа
        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None

        # Добавляем необходимое для 3 таски
        if task == "3":
            self.packet_info_window = None
            self.routing_table_window = None
            self.packet_log = []
            self.routing_tables = {}
            self.counter_of_tries = 0

        # Выключаем то, что не нужно в 4 таске
        if task != "4":
            # Привязка обработчиков событий
            self.canvas.bind("<Button-1>", lambda event: graphlib.on_left_click(self, event))
            self.canvas.bind("<Button-3>", lambda event: graphlib.on_right_click(self, event, task))

            # Инициализация матрицы смежности
            graphlib.update_matrix_display(self)

    def add_button(self, text, command):
        button = Button(self.button_frame, text=text, command=command)
        button.pack(pady=15, anchor="center")
        self.buttons.append(button)

    def add_option_menu(self, label_text, options, default_value=None, command=None):
        frame = Frame(self.button_frame)
        frame.pack(pady=5)
        var = StringVar(value=default_value if default_value else options[0])

        if label_text:
            label = Label(frame, text=label_text, font=("Arial", 10))
            label.pack(side="top", pady=2)

        menu = OptionMenu(frame, var, *options, command=command)
        menu.pack(side="top", padx=5, anchor="center")

        self.menus.append(menu)
        return var
