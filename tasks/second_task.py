import json
import time
import tkinter as tk

from tkinter import simpledialog, messagebox
from utils.graph_editor import dijkstra_all_pairs, floyd_warshall


class FloydApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 2: Алгоритмы Дейкстры и Флойда")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.graph = []
        self.vertices = []
        self.edges = {}
        self.current_menu = None

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_right_click)  # Для совместимости

        # Кнопки для запуска алгоритмов
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.run_dijkstra_button = tk.Button(self.button_frame, text="Запустить алгоритм Дейкстры", command=self.run_dijkstra)
        self.run_dijkstra_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_floyd_button = tk.Button(self.button_frame, text="Запустить алгоритм Флойда", command=self.run_floyd)
        self.run_floyd_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.compare_button = tk.Button(self.button_frame, text="Сравнить время выполнения", command=self.compare_algorithms)
        self.compare_button.pack(side=tk.LEFT, padx=5, pady=5)

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

    def run_dijkstra(self):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return
        start_time = time.time()
        dist_matrix, path_matrix = dijkstra_all_pairs(self.graph)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.show_all_pairs_paths(dist_matrix, path_matrix, "Алгоритм Дейкстры", elapsed_time)

    def run_floyd(self):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return
        start_time = time.time()
        dist_matrix, next_vertex = floyd_warshall(self.graph)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.show_all_pairs_paths_floyd(dist_matrix, next_vertex, elapsed_time)

    def show_all_pairs_paths(self, dist_matrix, path_matrix, algorithm_name, elapsed_time):
        n = len(self.vertices)
        result = ""
        for i in range(n):
            for j in range(n):
                if i != j:
                    path = self.reconstruct_path(path_matrix[i], i, j)
                    if path:
                        path_str = ' -> '.join(map(str, path))
                        dist = dist_matrix[i][j]
                        result += f"Путь из {i} в {j}: {path_str}, длина: {dist}\n"
                    else:
                        result += f"Путь из {i} в {j}: не существует\n"
        messagebox.showinfo(algorithm_name, f"Время выполнения: {elapsed_time:.6f} секунд\n\n{result}")

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

    def show_all_pairs_paths_floyd(self, dist_matrix, next_vertex, elapsed_time):
        n = len(self.vertices)
        result = ""
        for i in range(n):
            for j in range(n):
                if i != j:
                    if dist_matrix[i][j] != float('inf'):
                        path = self.construct_floyd_path(next_vertex, i, j)
                        path_str = ' -> '.join(map(str, path))
                        dist = dist_matrix[i][j]
                        result += f"Путь из {i} в {j}: {path_str}, длина: {dist}\n"
                    else:
                        result += f"Путь из {i} в {j}: не существует\n"
        messagebox.showinfo("Алгоритм Флойда", f"Время выполнения: {elapsed_time:.6f} секунд\n\n{result}")

    def construct_floyd_path(self, next_vertex, start, end):
        if next_vertex[start][end] == -1:
            return []
        path = [start]
        while start != end:
            start = next_vertex[start][end]
            path.append(start)
        return path

    def compare_algorithms(self):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return
        # Запуск алгоритма Дейкстры
        start_time = time.time()
        dist_matrix_dijkstra, _ = dijkstra_all_pairs(self.graph)
        time_dijkstra = time.time() - start_time

        # Запуск алгоритма Флойда
        start_time = time.time()
        dist_matrix_floyd, _ = floyd_warshall(self.graph)
        time_floyd = time.time() - start_time

        # Вывод времени выполнения
        messagebox.showinfo("Сравнение времени выполнения",
                            f"Алгоритм Дейкстры: {time_dijkstra:.6f} секунд\n"
                            f"Алгоритм Флойда: {time_floyd:.6f} секунд")

    def save_graph(self):
        graph_data = {
            "vertices": [{"coords": self.canvas.coords(v["id"])} for v in self.vertices],
            "edges": [(self.vertices.index(start_v), self.vertices.index(end_v), weight) for
                      _, (start_v, end_v, weight, _) in self.edges.items()]
        }
        with open("graph2.json", "w") as f:
            json.dump(graph_data, f)
        messagebox.showinfo("Сохранение", "Граф сохранен в файл graph2.json")

    def load_graph(self):
        try:
            with open("graph2.json", "r") as f:
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
            messagebox.showerror("Ошибка", "Файл graph2.json не найден")

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
