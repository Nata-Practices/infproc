import time
from tkinter import Toplevel, Text, messagebox, BOTH, END, ttk

import graphlib
from tasks.base_graph import BaseGraphApp


class FloydApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Алгоритмы Дейкстры и Флойда", "2")
        self.add_button("Запустить Дейкстру", lambda: self.run_algorithm("dijkstra"))
        self.add_button("Запустить Флойда", lambda: self.run_algorithm("floyd"))
        self.add_button("Сравнить время выполнения", lambda: self.compare_algorithms())
        self.add_button("ВЫПОЛНИТЬ ОБА АЛГОРИТМА И СРАВНИТЬ", self.run_both_algorithms)
        self.add_button("Сохранить граф", lambda: graphlib.save_graph(self))
        self.add_button("Загрузить граф", lambda: graphlib.load_graph(self))

    def run_both_algorithms(self):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return

        # Запуск алгоритма Дейкстры
        start_time_dijkstra = time.time()
        dist_matrix_dijkstra, path_matrix_dijkstra = graphlib.dijkstra_all_pairs(self.graph)
        elapsed_time_dijkstra = time.time() - start_time_dijkstra

        # Запуск алгоритма Флойда-Уоршелла
        start_time_floyd = time.time()
        dist_matrix_floyd, next_vertex_floyd = graphlib.floyd_warshall(self.graph)
        elapsed_time_floyd = time.time() - start_time_floyd

        # Подготовка результатов
        result_dijkstra = self.prepare_results(dist_matrix_dijkstra, path_matrix_dijkstra, "dijkstra")
        result_floyd = self.prepare_results(dist_matrix_floyd, next_vertex_floyd, "floyd")

        # Создание окна для отображения результатов
        result_window = Toplevel(self.root)
        result_window.title("Сравнение алгоритмов Дейкстры и Флойда")
        result_window.geometry("900x600")

        # Создание вкладок
        notebook = ttk.Notebook(result_window)
        notebook.pack(fill=BOTH, expand=True)

        # Вкладка для Дейкстры
        dijkstra_frame = ttk.Frame(notebook)
        notebook.add(dijkstra_frame, text="Дейкстра")

        # Вкладка для Флойда-Уоршелла
        floyd_frame = ttk.Frame(notebook)
        notebook.add(floyd_frame, text="Флойд-Уоршелл")

        # Вкладка для сравнения
        comparison_frame = ttk.Frame(notebook)
        notebook.add(comparison_frame, text="Сравнение")

        # Функция для создания таблицы
        def create_table(parent, data, elapsed_time, algorithm_name):
            columns = ("start", "end", "path", "distance")
            tree = ttk.Treeview(parent, columns=columns, show='headings')
            tree.heading("start", text="Начало")
            tree.heading("end", text="Конец")
            tree.heading("path", text="Путь")
            tree.heading("distance", text="Длина")

            # Создание стилей для заголовков и строк
            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
            style.configure("Treeview", font=("Arial", 10))

            # Добавление данных в таблицу
            for idx, entry in enumerate(data):
                tree.insert("", END, values=entry)
                # Альтернативная раскраска строк
                if idx % 2 == 0:
                    tree.tag_configure("evenrow", background="#E8E8E8")
                    tree.item(tree.get_children()[-1], tags=("evenrow",))
                else:
                    tree.tag_configure("oddrow", background="#FFFFFF")
                    tree.item(tree.get_children()[-1], tags=("oddrow",))

            # Настройка полос прокрутки
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            tree.pack(fill=BOTH, expand=True)

            # Отображение времени выполнения
            time_label = ttk.Label(parent, text=f"Время выполнения: {elapsed_time:.16f} секунд", font=("Arial", 12))
            time_label.pack(pady=10)

        # Подготовка данных для Дейкстры
        dijkstra_data = []
        for entry in result_dijkstra:
            dijkstra_data.append(entry)

        # Подготовка данных для Флойда-Уоршелла
        floyd_data = []
        for entry in result_floyd:
            floyd_data.append(entry)

        # Создание таблиц
        create_table(dijkstra_frame, dijkstra_data, elapsed_time_dijkstra, "Дейкстра")
        create_table(floyd_frame, floyd_data, elapsed_time_floyd, "Флойд-Уоршелл")

        # Отображение сравнения
        comparison = 'Дейкстра быстрее' if elapsed_time_dijkstra < elapsed_time_floyd else 'Флойд-Уоршелл быстрее'
        comparison_label = ttk.Label(comparison_frame, text=f"Сравнение:\n{comparison}", font=("Arial", 14))
        comparison_label.pack(pady=20)

    def prepare_results(self, dist_matrix, path_data, algorithm):
        n = len(self.vertices)
        result = []

        for i in range(n):
            for j in range(n):
                if i != j:
                    if dist_matrix[i][j] != float('inf'):
                        if algorithm == "dijkstra":
                            path = graphlib.reconstruct_path(path_data[i], i, j)
                        else:
                            path = graphlib.construct_floyd_path(path_data, i, j)

                        path_str = " -> ".join(map(str, path))
                        dist = dist_matrix[i][j]
                        result.append((i, j, path_str, dist))
                    else:
                        result.append((i, j, "Не существует", "∞"))

        return result

    def run_algorithm(self, algorithm):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return

        start_time = time.time()

        if algorithm == "dijkstra":
            dist_matrix, path_matrix = graphlib.dijkstra_all_pairs(self.graph)
            elapsed_time = time.time() - start_time
            self.show_paths(dist_matrix, path_matrix, elapsed_time, algorithm)

        elif algorithm == "floyd":
            dist_matrix, next_vertex = graphlib.floyd_warshall(self.graph)
            elapsed_time = time.time() - start_time
            self.show_paths(dist_matrix, next_vertex, elapsed_time, algorithm)

    def show_paths(self, dist_matrix, path_data, elapsed_time, algorithm):
        n = len(self.vertices)
        result = ""

        for i in range(n):
            for j in range(n):
                if i != j:
                    if dist_matrix[i][j] != float('inf'):
                        if algorithm == "dijkstra":
                            path = graphlib.reconstruct_path(path_data[i], i, j)
                        else:
                            path = graphlib.construct_floyd_path(path_data, i, j)

                        path_str = " -> ".join(map(str, path))
                        dist = dist_matrix[i][j]
                        result += f"Путь из {i} в {j}: {path_str}, длина: {dist}\n"
                    else:
                        result += f"Путь из {i} в {j}: не существует\n"

        messagebox.showinfo(
            f"Алгоритм {algorithm.capitalize()}",
            f"Время выполнения: {elapsed_time:.6f} секунд\n\n{result}",
        )

    def compare_algorithms(self):
        if not self.graph:
            messagebox.showwarning("Ошибка", "Граф пуст. Добавьте вершины и дуги.")
            return

        # Время выполнения Дейкстры
        start_time = time.time()
        graphlib.dijkstra_all_pairs(self.graph)
        time_dijkstra = time.time() - start_time

        # Время выполнения Флойда
        start_time = time.time()
        graphlib.floyd_warshall(self.graph)
        time_floyd = time.time() - start_time

        # Вывод результатов
        messagebox.showinfo(
            "Сравнение времени выполнения",
            f"Алгоритм Дейкстры: {time_dijkstra:.6f} секунд\n"
            f"Алгоритм Флойда: {time_floyd:.6f} секунд"
        )
