import time

from utils.graph_editor import *


class FloydApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 2: Алгоритмы Дейкстры и Флойда")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.graph = []
        self.vertices = []
        self.edges = {}
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.current_menu = None

        self.canvas.bind("<Button-1>", lambda event: on_left_click(self, event))
        self.canvas.bind("<Button-2>", lambda event: on_right_click(self, event, "2"))
        self.canvas.bind("<Button-3>", lambda event: on_right_click(self, event, "2"))

        # Кнопки для запуска алгоритмов
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.run_dijkstra_button = tk.Button(self.button_frame, text="Запустить алгоритм Дейкстры", command=self.run_dijkstra)
        self.run_dijkstra_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_floyd_button = tk.Button(self.button_frame, text="Запустить алгоритм Флойда", command=self.run_floyd)
        self.run_floyd_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.compare_button = tk.Button(self.button_frame, text="Сравнить время выполнения", command=self.compare_algorithms)
        self.compare_button.pack(side=tk.LEFT, padx=5, pady=5)

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
                    path = reconstruct_path(path_matrix[i], i, j)
                    if path:
                        path_str = ' -> '.join(map(str, path))
                        dist = dist_matrix[i][j]
                        result += f"Путь из {i} в {j}: {path_str}, длина: {dist}\n"
                    else:
                        result += f"Путь из {i} в {j}: не существует\n"
        messagebox.showinfo(algorithm_name, f"Время выполнения: {elapsed_time:.6f} секунд\n\n{result}")

    def show_all_pairs_paths_floyd(self, dist_matrix, next_vertex, elapsed_time):
        n = len(self.vertices)
        result = ""
        for i in range(n):
            for j in range(n):
                if i != j:
                    if dist_matrix[i][j] != float('inf'):
                        path = construct_floyd_path(next_vertex, i, j)
                        path_str = ' -> '.join(map(str, path))
                        dist = dist_matrix[i][j]
                        result += f"Путь из {i} в {j}: {path_str}, длина: {dist}\n"
                    else:
                        result += f"Путь из {i} в {j}: не существует\n"
        messagebox.showinfo("Алгоритм Флойда", f"Время выполнения: {elapsed_time:.6f} секунд\n\n{result}")

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
