import json
import threading
import tkinter as tk

from tkinter import simpledialog, messagebox, Toplevel, Text, END
from utils.graph_editor import dijkstra_with_parent


class PacketRoutingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 3: Симуляция передачи пакетов")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.graph = []
        self.vertices = []
        self.edges = {}
        self.current_menu = None
        self.selected_method = tk.StringVar(value="Виртуальный канал")

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_right_click)  # Для совместимости

        # Панель управления
        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Label(control_frame, text="Метод маршрутизации:").pack(side=tk.LEFT)
        tk.OptionMenu(control_frame, self.selected_method, "Виртуальный канал", "Дейтаграммный метод").pack(side=tk.LEFT)

        tk.Button(control_frame, text="Выбрать узлы", command=self.select_nodes).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Запустить передачу", command=self.start_transmission).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Просмотр таблиц маршрутизации", command=self.show_routing_tables).pack(side=tk.LEFT, padx=5)

        # Окно информации о пакетах
        self.packet_info_window = None

        # Переменные для хранения узлов и пакетов
        self.start_vertex = None
        self.end_vertex = None
        self.routing_tables = {}
        self.packet_number = 1

    def on_left_click(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex:
            # Перемещение вершины
            self.selected_vertex = vertex
            self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        else:
            self.add_vertex(event.x, event.y)

    def on_mouse_drag(self, event):
        vertex = self.selected_vertex
        x, y = event.x, event.y
        self.canvas.coords(vertex["id"], x - 15, y - 15, x + 15, y + 15)
        self.canvas.coords(vertex["text"], x, y)
        for edge_id in vertex["edges"]:
            self.update_edge(edge_id)
        # Обновляем ребра, где вершина является конечной
        for edge_id in self.edges:
            start_vertex, end_vertex, weight, label_id = self.edges[edge_id]
            if end_vertex == vertex and edge_id not in vertex["edges"]:
                self.update_edge(edge_id)

    def on_mouse_release(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.selected_vertex = None

    def on_right_click(self, event):
        vertex = self.get_vertex_at(event.x, event.y)
        if vertex is not None:
            self.show_vertex_menu(vertex, event.x, event.y)
        else:
            self.show_canvas_menu(event.x, event.y)

    def get_vertex_at(self, x, y):
        for vertex in self.vertices:
            coords = self.canvas.coords(vertex["id"])
            vx = (coords[0] + coords[2]) / 2
            vy = (coords[1] + coords[3]) / 2
            if abs(x - vx) < 15 and abs(y - vy) < 15:
                return vertex
        return None

    def add_vertex(self, x, y):
        if len(self.vertices) < 10:
            vertex_id = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="lightblue")
            vertex_text = self.canvas.create_text(x, y, text=str(len(self.vertices)))
            self.vertices.append({"id": vertex_id, "text": vertex_text, "edges": []})
            self.update_graph_matrix()

    def update_edge(self, edge_id):
        start_vertex, end_vertex, weight, label_id = self.edges[edge_id]
        start_coords = self.canvas.coords(start_vertex["id"])
        end_coords = self.canvas.coords(end_vertex["id"])
        sx = (start_coords[0] + start_coords[2]) / 2
        sy = (start_coords[1] + start_coords[3]) / 2
        ex = (end_coords[0] + end_coords[2]) / 2
        ey = (end_coords[1] + end_coords[3]) / 2
        self.canvas.coords(edge_id, sx, sy, ex, ey)
        # Обновляем позицию метки веса
        mx = (sx + ex) / 2
        my = (sy + ey) / 2
        self.canvas.coords(label_id, mx, my - 10)  # Смещаем метку чуть вверх

    def show_vertex_menu(self, vertex, x, y):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Удалить вершину", command=lambda: self.delete_vertex(vertex))
        menu.add_command(label="Добавить дугу", command=lambda: self.add_edge(vertex))
        menu.add_command(label="Изменить вес дуги", command=lambda: self.change_edge_weight(vertex))
        menu.add_command(label="Сменить направление дуги", command=lambda: self.change_edge_direction(vertex))
        menu.add_command(label="Удалить дугу", command=lambda: self.delete_edge(vertex))
        self.current_menu = menu  # Сохраняем ссылку на меню
        menu.post(x + self.root.winfo_rootx(), y + self.root.winfo_rooty())

    def show_canvas_menu(self, x, y):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Добавить вершину", command=lambda: self.add_vertex(x, y))
        menu.add_command(label="Сохранить граф", command=self.save_graph)
        menu.add_command(label="Загрузить граф", command=self.load_graph)
        menu.add_command(label="Показать матрицу инцидентности", command=self.display_incidence_matrix)
        self.current_menu = menu  # Сохраняем ссылку на меню
        menu.post(x + self.root.winfo_rootx(), y + self.root.winfo_rooty())

    def add_edge(self, start_vertex):
        end_vertex_index = simpledialog.askinteger("Добавить дугу", "Введите индекс конечной вершины (0-{})".format(len(self.vertices)-1))
        if end_vertex_index is not None and 0 <= end_vertex_index < len(self.vertices):
            end_vertex = self.vertices[end_vertex_index]
            weight = simpledialog.askinteger("Вес дуги", "Введите вес дуги")
            if weight is None:
                weight = 1
            start_coords = self.canvas.coords(start_vertex["id"])
            end_coords = self.canvas.coords(end_vertex["id"])
            sx = (start_coords[0] + start_coords[2]) / 2
            sy = (start_coords[1] + start_coords[3]) / 2
            ex = (end_coords[0] + end_coords[2]) / 2
            ey = (end_coords[1] + end_coords[3]) / 2
            line_id = self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST)
            # Добавляем метку веса
            mx = (sx + ex) / 2
            my = (sy + ey) / 2
            label_id = self.canvas.create_text(mx, my - 10, text=str(weight), fill="red")
            self.edges[line_id] = (start_vertex, end_vertex, weight, label_id)
            start_vertex["edges"].append(line_id)
            self.update_graph_matrix()


    def change_edge_weight(self, start_vertex):
        end_vertex_index = simpledialog.askinteger("Изменить вес дуги", "Введите индекс конечной вершины (0-{})".format(
            len(self.vertices) - 1))
        if end_vertex_index is not None and 0 <= end_vertex_index < len(self.vertices):
            end_vertex = self.vertices[end_vertex_index]
            for edge_id, (start_v, end_v, weight, label_id) in self.edges.items():
                if start_v == start_vertex and end_v == end_vertex:
                    new_weight = simpledialog.askinteger("Новый вес", "Введите новый вес дуги")
                    if new_weight is not None:
                        self.edges[edge_id] = (start_v, end_v, new_weight, label_id)
                        self.canvas.itemconfig(label_id, text=str(new_weight))
                    return
            messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")

    def change_edge_direction(self, start_vertex):
        end_vertex_index = simpledialog.askinteger("Смена направления дуги",
                                                   "Введите индекс конечной вершины (0-{})".format(
                                                       len(self.vertices) - 1))

        if end_vertex_index is not None and 0 <= end_vertex_index < len(self.vertices):
            end_vertex = self.vertices[end_vertex_index]

            # Ищем ребро между start_vertex и end_vertex
            for edge_id, (start_v, end_v, weight, label_id) in self.edges.items():
                if start_v == start_vertex and end_v == end_vertex:
                    # Меняем направления дуги
                    self.edges[edge_id] = (end_vertex, start_vertex, weight, label_id)

                    # Обновляем графическое представление ребра
                    self.update_edge(edge_id)
                    messagebox.showinfo("Успех", "Направление дуги изменено.")
                    return

            # Если ребро не найдено
            messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")

    def delete_edge(self, start_vertex):
        end_vertex_index = simpledialog.askinteger("Удалить дугу", "Введите индекс конечной вершины (0-{})".format(
            len(self.vertices) - 1))

        if end_vertex_index is not None and 0 <= end_vertex_index < len(self.vertices):
            end_vertex = self.vertices[end_vertex_index]

            # Ищем ребро между start_vertex и end_vertex
            for edge_id, (start_v, end_v, _, label_id) in list(
                    self.edges.items()):  # Превращаем items в список для безопасного удаления
                if start_v == start_vertex and end_v == end_vertex:
                    # Удаляем графическое представление ребра
                    self.canvas.delete(edge_id)
                    self.canvas.delete(label_id)

                    # Удаляем ребро из self.edges
                    del self.edges[edge_id]

                    # Удаляем ребро из списка ребер вершины
                    if edge_id in start_vertex["edges"]:
                        start_vertex["edges"].remove(edge_id)

                    messagebox.showinfo("Успех", "Дуга удалена.")
                    return

            # Если ребро не найдено
            messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")

    def delete_vertex(self, vertex):
        self.canvas.delete(vertex["id"])
        self.canvas.delete(vertex["text"])
        for edge_id in list(self.edges):
            start_vertex, end_vertex, _, label_id = self.edges[edge_id]
            if start_vertex == vertex or end_vertex == vertex:
                self.canvas.delete(edge_id)
                self.canvas.delete(label_id)
                del self.edges[edge_id]
            else:
                if start_vertex == vertex:
                    start_vertex["edges"].remove(edge_id)
                if end_vertex == vertex:
                    end_vertex["edges"].remove(edge_id)
        self.vertices.remove(vertex)
        self.update_graph_matrix()

    def update_graph_matrix(self):
        n = len(self.vertices)
        self.graph = [[0] * n for _ in range(n)]
        for edge_id, (start_vertex, end_vertex, weight, _) in self.edges.items():
            start_idx = self.vertices.index(start_vertex)
            end_idx = self.vertices.index(end_vertex)
            self.graph[start_idx][end_idx] = weight

    def select_nodes(self):
        start_idx = simpledialog.askinteger("Выбор узлов", "Введите индекс исходного узла (0-{})".format(len(self.vertices)-1))
        end_idx = simpledialog.askinteger("Выбор узлов", "Введите индекс конечного узла (0-{})".format(len(self.vertices)-1))
        if start_idx is not None and end_idx is not None:
            if 0 <= start_idx < len(self.vertices) and 0 <= end_idx < len(self.vertices):
                self.start_vertex = self.vertices[start_idx]
                self.end_vertex = self.vertices[end_idx]
                messagebox.showinfo("Выбор узлов", f"Исходный узел: {start_idx}\nКонечный узел: {end_idx}")
            else:
                messagebox.showwarning("Ошибка", "Неверные индексы узлов.")
        else:
            messagebox.showwarning("Ошибка", "Необходимо ввести индексы узлов.")

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
        path = self.reconstruct_path(parent, start_idx, end_idx)
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
            path = self.reconstruct_path(parent, current_idx, end_idx)
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

    def reconstruct_path(self, parent, start, end):
        path = []
        current = end
        while current != -1:
            path.append(current)
            if current == start:
                break
            current = parent[current]
        if current == -1:
            return []
        path.reverse()
        return path

    def save_graph(self):
        graph_data = {
            "vertices": [{"coords": self.canvas.coords(v["id"])} for v in self.vertices],
            "edges": [(self.vertices.index(start_v), self.vertices.index(end_v), weight) for
                      _, (start_v, end_v, weight, _) in self.edges.items()]
        }
        with open("graph3.json", "w") as f:
            json.dump(graph_data, f)
        messagebox.showinfo("Сохранение", "Граф сохранен в файл graph3.json")

    def load_graph(self):
        try:
            with open("graph3.json", "r") as f:
                graph_data = json.load(f)

            # Очищаем граф перед загрузкой
            self.clear_graph()

            # Восстанавливаем вершины
            for vertex_data in graph_data["vertices"]:
                x0, y0, x1, y1 = vertex_data["coords"]
                self.add_vertex((x0 + x1) // 2, (y0 + y1) // 2)

            # Восстанавливаем рёбра (дуги)
            for start_idx, end_idx, weight in graph_data["edges"]:
                start_vertex = self.vertices[start_idx]
                end_vertex = self.vertices[end_idx]
                self.add_edge_with_weight(start_vertex, end_vertex, weight)

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл graph3.json не найден")

    def add_edge_with_weight(self, start_vertex, end_vertex, weight):
        start_coords = self.canvas.coords(start_vertex["id"])
        end_coords = self.canvas.coords(end_vertex["id"])
        sx = (start_coords[0] + start_coords[2]) / 2
        sy = (start_coords[1] + start_coords[3]) / 2
        ex = (end_coords[0] + end_coords[2]) / 2
        ey = (end_coords[1] + end_coords[3]) / 2
        line_id = self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST)

        mx = (sx + ex) / 2
        my = (sy + ey) / 2
        label_id = self.canvas.create_text(mx, my - 10, text=str(weight), fill="red")

        self.edges[line_id] = (start_vertex, end_vertex, weight, label_id)
        start_vertex["edges"].append(line_id)
        self.update_graph_matrix()

    def clear_graph(self):
        for vertex in self.vertices:
            self.canvas.delete(vertex["id"])
            self.canvas.delete(vertex["text"])
        for edge_id in self.edges:
            self.canvas.delete(edge_id)
        self.vertices.clear()
        self.edges.clear()

    def display_incidence_matrix(self):
        n_vertices = len(self.vertices)
        n_edges = len(self.edges)

        # Создание матрицы инцидентности
        incidence_matrix = [[0] * n_edges for _ in range(n_vertices)]

        for idx, (edge_id, (start_vertex, end_vertex, _, _)) in enumerate(self.edges.items()):
            start_idx = self.vertices.index(start_vertex)
            end_idx = self.vertices.index(end_vertex)
            incidence_matrix[start_idx][idx] = 1
            incidence_matrix[end_idx][idx] = -1

        # Создаем новое окно для отображения матрицы
        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("Матрица инцидентности")

        # Создаем текстовое поле для вывода матрицы
        text_area = tk.Text(matrix_window, wrap=tk.WORD, width=50, height=20)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Формируем строковое представление матрицы
        matrix_str = "Матрица инцидентности:\n"
        for row in incidence_matrix:
            matrix_str += " ".join(map(str, row)) + "\n"

        # Выводим матрицу в текстовое поле
        text_area.insert(tk.END, matrix_str)
        text_area.config(state=tk.DISABLED)  # Запрещаем редактирование поля
