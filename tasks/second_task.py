import time
from tkinter import messagebox

import graphlib
from tasks.base_graph import BaseGraphApp


class FloydApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Алгоритмы Дейкстры и Флойда", "2")
        self.add_button("Запустить Дейкстру", lambda: self.run_algorithm("dijkstra"))
        self.add_button("Запустить Флойда", lambda: self.run_algorithm("floyd"))
        self.add_button("Сравнить время выполнения", lambda: self.compare_algorithms())
        self.add_button("Сохранить граф", lambda: graphlib.save_graph(self, "2"))
        self.add_button("Загрузить граф", lambda: graphlib.load_graph(self, "2"))

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
