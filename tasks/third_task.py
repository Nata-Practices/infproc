import threading
from tkinter import Toplevel, Text, END

from utils.graph_editor import *


class PacketRoutingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 3: Симуляция передачи пакетов")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.current_menu = None
        self.start_vertex = None
        self.end_vertex = None
        self.selected_method = tk.StringVar(value="Виртуальный канал")

        self.canvas.bind("<Button-1>", lambda event: on_left_click(self, event))
        self.canvas.bind("<Button-2>", lambda event: on_right_click(self, event, "3"))
        self.canvas.bind("<Button-3>", lambda event: on_right_click(self, event, "3"))

        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Label(control_frame, text="Метод маршрутизации:").pack(side=tk.LEFT)
        tk.OptionMenu(control_frame, self.selected_method, "Виртуальный канал", "Дейтаграммный метод").pack(side=tk.LEFT)
        tk.Button(control_frame, text="Запустить передачу", command=self.start_transmission).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Просмотр таблиц маршрутизации", command=self.show_routing_tables).pack(side=tk.LEFT, padx=5)

        self.packet_info_window = None

        self.routing_tables = {}
        self.packet_number = 1

    def start_transmission(self):
        if self.start_vertex is None or self.end_vertex is None:
            messagebox.showwarning("Ошибка", "Необходимо выбрать исходный и конечный узлы.")
            return
        method = self.selected_method.get()
        if method == "Виртуальный канал":
            self.virtual_circuit_routing()
        elif method == "Дейтаграммный метод":
            self.datagram_routing()
        else:
            messagebox.showwarning("Ошибка", "Неизвестный метод маршрутизации.")

    def virtual_circuit_routing(self):
        # Используем алгоритм Дейкстры для установления пути
        start_idx = self.vertices.index(self.start_vertex)
        end_idx = self.vertices.index(self.end_vertex)
        dist, parent = dijkstra_with_parent(self.graph, start_idx)
        path = reconstruct_path(parent, start_idx, end_idx)
        if not path:
            messagebox.showwarning("Ошибка", "Путь между узлами не существует.")
            return
        # Запрашиваем размер пакета в главном потоке
        packet_size = simpledialog.askinteger("Размер пакета", "Введите размер пакета (в байтах)")
        if packet_size is None:
            packet_size = 64  # Значение по умолчанию
        # Отображаем путь и перемещаем пакет по маршруту
        threading.Thread(target=self.animate_packet, args=(path, packet_size)).start()
        # Обновляем таблицы маршрутизации
        self.update_routing_tables(path)

    def datagram_routing(self):
        # Запрашиваем размер пакета в главном потоке
        packet_size = simpledialog.askinteger("Размер пакета", "Введите размер пакета (в байтах)")
        if packet_size is None:
            packet_size = 64  # Значение по умолчанию
        # Каждый пакет выбирает маршрут независимо
        threading.Thread(target=self.animate_datagram_packets, args=(packet_size,)).start()

    def animate_packet(self, path, packet_size):
        # Анимация перемещения пакета по заданному пути
        packet_info = f"Пакет #{self.packet_number}\nОтправитель: {path[0]}\nПолучатель: {path[-1]}\nМаршрут: {path}\nРазмер: {packet_size} байт\n"
        self.show_packet_info(packet_info)
        self.packet_number += 1

        # Запускаем анимацию в главном потоке
        self.animate_movement(path)

    def animate_movement(self, path):
        # Создаем круг для отображения пакета
        packet = self.canvas.create_oval(0, 0, 20, 20, fill="yellow")
        self.move_packet_along_path(packet, path, 0)

    def move_packet_along_path(self, packet, path, index):
        if index < len(path) - 1:
            start_vertex = self.vertices[path[index]]
            end_vertex = self.vertices[path[index + 1]]
            sx, sy = self.get_vertex_center(start_vertex)
            ex, ey = self.get_vertex_center(end_vertex)
            steps = 20
            dx = (ex - sx) / steps
            dy = (ey - sy) / steps
            def animate(step=0):
                if step <= steps:
                    x = sx + dx * step
                    y = sy + dy * step
                    self.canvas.coords(packet, x - 10, y - 10, x + 10, y + 10)
                    self.root.after(50, animate, step + 1)
                else:
                    self.move_packet_along_path(packet, path, index + 1)
            animate()
        else:
            self.canvas.delete(packet)

    def get_vertex_center(self, vertex):
        coords = self.canvas.coords(vertex["id"])
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        return x, y

    def animate_datagram_packets(self, packet_size):
        # Пакет перемещается от узла к узлу
        start_idx = self.vertices.index(self.start_vertex)
        end_idx = self.vertices.index(self.end_vertex)
        current_idx = start_idx

        packet_info = f"Пакет #{self.packet_number}\nОтправитель: {start_idx}\nПолучатель: {end_idx}\nРазмер: {packet_size} байт\n"
        self.show_packet_info(packet_info)
        self.packet_number += 1

        # Создаем круг для отображения пакета
        packet = self.canvas.create_oval(0, 0, 20, 20, fill="yellow")
        self.move_datagram_packet(packet, current_idx, end_idx)

    def move_datagram_packet(self, packet, current_idx, end_idx):
        if current_idx != end_idx:
            dist, parent = dijkstra_with_parent(self.graph, current_idx)
            path = reconstruct_path(parent, current_idx, end_idx)
            if not path or len(path) < 2:
                messagebox.showwarning("Ошибка", "Путь между узлами не существует.")
                self.canvas.delete(packet)
                return
            next_idx = path[1]
            start_vertex = self.vertices[current_idx]
            end_vertex = self.vertices[next_idx]
            sx, sy = self.get_vertex_center(start_vertex)
            ex, ey = self.get_vertex_center(end_vertex)
            steps = 20
            dx = (ex - sx) / steps
            dy = (ey - sy) / steps
            def animate(step=0):
                if step <= steps:
                    x = sx + dx * step
                    y = sy + dy * step
                    self.canvas.coords(packet, x - 10, y - 10, x + 10, y + 10)
                    self.root.after(50, animate, step + 1)
                else:
                    self.move_datagram_packet(packet, next_idx, end_idx)
            animate()
        else:
            self.canvas.delete(packet)

    def highlight_edge(self, start_vertex, end_vertex, color):
        # Выделяем ребро между двумя вершинами
        for edge_id, (s_vertex, e_vertex, _, _) in self.edges.items():
            if s_vertex == start_vertex and e_vertex == end_vertex:
                self.canvas.itemconfig(edge_id, fill=color)
                break

    def show_packet_info(self, info):
        if self.packet_info_window is None or not tk.Toplevel.winfo_exists(self.packet_info_window):
            self.packet_info_window = Toplevel(self.root)
            self.packet_info_window.title("Информация о пакетах")
            self.packet_text = Text(self.packet_info_window, width=50, height=20)
            self.packet_text.pack()
        self.packet_text.insert(END, info + "\n")
        self.packet_text.see(END)

    def update_routing_tables(self, path):
        # Получаем индекс конечной вершины
        end_idx = self.vertices.index(self.end_vertex)
        # Обновляем таблицы маршрутизации для каждого узла на пути
        for idx in path:
            if idx not in self.routing_tables:
                self.routing_tables[idx] = {}
            self.routing_tables[idx][end_idx] = path

    def show_routing_tables(self):
        # Отображаем таблицы маршрутизации
        tables_window = Toplevel(self.root)
        tables_window.title("Таблицы маршрутизации")
        text = Text(tables_window, width=60, height=30)
        text.pack()
        for node_idx, table in self.routing_tables.items():
            text.insert(END, f"Узел {node_idx}:\n")
            for dest_idx, path in table.items():
                text.insert(END, f"  До узла {dest_idx}: {path}\n")
            text.insert(END, "\n")
        text.config(state='disabled')
