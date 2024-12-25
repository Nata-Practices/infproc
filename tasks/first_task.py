from utils.graph_editor import *


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор Графа")
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
        self.canvas.bind("<Button-3>", lambda event: on_right_click(self, event, "1"))
        self.canvas.bind("<Button-2>", lambda event: on_right_click(self, event, "1"))

        self.find_path_button = tk.Button(root, text="Найти кратчайший путь", command=self.find_shortest_path)
        self.find_path_button.pack()

    def find_shortest_path(self):
        if self.start_vertex and self.end_vertex:
            start_idx = self.vertices.index(self.start_vertex)
            end_idx = self.vertices.index(self.end_vertex)
            result = dijkstra(self.graph, start_idx, end_idx)
            if result is not None:
                distance, path = result
                if path:
                    self.highlight_path(path)
                    path_str = ' -> '.join(map(str, path))
                    messagebox.showinfo("Кратчайший путь", f"Длина пути: {distance}\nПуть: {path_str}")
                else:
                    messagebox.showwarning("Нет пути", "Путь между выбранными вершинами не существует.")
            else:
                messagebox.showwarning("Нет пути", "Путь между выбранными вершинами не существует.")
        else:
            messagebox.showwarning("Ошибка", "Необходимо выбрать начальную и конечную вершины.")

    def highlight_path(self, path):
        for edge_id in self.edges:
            self.canvas.itemconfig(edge_id, fill="black")

        for i in range(len(path) - 1):
            start_idx = path[i]
            end_idx = path[i + 1]
            for edge_id, (start_vertex, end_vertex, _, _) in self.edges.items():
                if (self.vertices.index(start_vertex) == start_idx and
                    self.vertices.index(end_vertex) == end_idx):
                    self.canvas.itemconfig(edge_id, fill="blue")
                    break
