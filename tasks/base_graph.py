from tkinter import Canvas, Button, Frame, BOTH, OptionMenu, StringVar, Y, RIGHT, LEFT

import graphlib


class BaseGraphApp:
    def __init__(self, root, title, task):
        self.root = root
        self.root.title(title)

        # Увеличиваем ширину окна для размещения графа и матрицы
        window_width, window_height = 1500, 450  # Увеличенная ширина
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = (screen_height - window_height) // 2
        position_left = (screen_width - window_width) // 2
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        # Главный фрейм для разделения на верхнюю и нижнюю части
        self.top_frame = Frame(root)
        self.top_frame.pack(fill=BOTH, expand=True)

        # Левая часть: Канвас для графа
        self.canvas = Canvas(self.top_frame, width=500, height=300, bg="white")
        self.canvas.pack(side=LEFT, fill=BOTH)

        # Правая часть: Фрейм для матрицы смежности
        self.matrix_frame = Frame(self.top_frame)
        self.matrix_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        # Заголовок для матрицы
        self.matrix_title = Button(self.matrix_frame, text="Матрица смежности", state='disabled', relief='flat')
        self.matrix_title.pack(pady=5)

        # Создание Scrollable Frame для матрицы
        self.matrix_scroll_canvas = Canvas(self.matrix_frame, width=550, bg="#f0f0f0")
        self.matrix_scroll_canvas.pack(side=LEFT, fill=Y, expand=True)

        # Внутренний фрейм для размещения Entry виджетов
        self.matrix_inner_frame = Frame(self.matrix_scroll_canvas)
        self.matrix_scroll_canvas.create_window((0, 0), window=self.matrix_inner_frame, anchor='nw')

        self.matrix_inner_frame.bind("<Configure>", lambda event: self.matrix_scroll_canvas.configure(scrollregion=self.matrix_scroll_canvas.bbox("all")))

        # Список для хранения Entry виджетов матрицы
        self.matrix_entries = []

        # Фрейм для кнопок снизу
        self.button_frame = Frame(self.top_frame)
        self.button_frame.pack(fill='x', pady=10)
        self.buttons = []
        self.menus = []

        # Инициализация графа
        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None

        # Специфичная инициализация для задачи 3
        if task == "3":
            self.packet_info_window = None
            self.routing_tables = {}
            self.packet_number = 1

        # Привязка обработчиков событий
        self.canvas.bind("<Button-1>", lambda event: graphlib.on_left_click(self, event))
        self.canvas.bind("<Button-3>", lambda event: graphlib.on_right_click(self, event, task))

        # Инициализация матрицы смежности
        graphlib.update_matrix_display(self)

    def add_button(self, text, command):
        button = Button(self.button_frame, text=text, command=command)
        button.pack(padx=15)
        self.buttons.append(button)

    def add_option_menu(self, label_text, options, default_value=None, command=None):
        frame = Frame(self.button_frame)
        frame.pack(pady=5)
        var = StringVar(value=default_value if default_value else options[0])

        if label_text:
            label = Button(frame, text=label_text)
            label.pack(side="left", padx=5)
        menu = OptionMenu(frame, var, *options, command=command)
        menu.pack(side="left", padx=5)

        self.menus.append(menu)
        return var
