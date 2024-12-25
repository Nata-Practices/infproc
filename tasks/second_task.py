import time
import tkinter
from tkinter import messagebox

import graphlib


class FloydApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 2: Алгоритмы Дейкстры и Флойда")
        self.canvas = tkinter.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.current_menu = None

        self.canvas.bind("<Button-1>", lambda event: graphlib.on_left_click(self, event))
        self.canvas.bind("<Button-2>", lambda event: graphlib.on_right_click(self, event, "2"))
        self.canvas.bind("<Button-3>", lambda event: graphlib.on_right_click(self, event, "2"))

        self.button_frame = tkinter.Frame(root)
        self.button_frame.pack()

        self.run_dijkstra_button = tkinter.Button(self.button_frame, text="Запустить алгоритм Дейкстры", command=lambda: self.run_algorithm("dijkstra"))
        self.run_dijkstra_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.run_floyd_button = tkinter.Button(self.button_frame, text="Запустить алгоритм Флойда", command=lambda: self.run_algorithm("floyd"))
        self.run_floyd_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.compare_button = tkinter.Button(self.button_frame, text="Сравнить время выполнения", command=self.compare_algorithms)
        self.compare_button.pack(side=tkinter.LEFT, padx=5, pady=5)

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
