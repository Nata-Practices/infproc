from tkinter import messagebox

import graphlib
from tasks.base_graph import BaseGraphApp


class GraphApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Редактор графа", "1")
        self.add_button("Найти кратчайший путь", self.find_shortest_path)
        self.add_button("Сохранить граф", lambda: graphlib.save_graph(self))
        self.add_button("Загрузить граф", lambda: graphlib.load_graph(self))

    def find_shortest_path(self):
        if not (self.start_vertex and self.end_vertex):
            messagebox.showwarning("Ошибка", "Необходимо выбрать начальную и конечную вершины.")
            return

        start_idx = self.vertices.index(self.start_vertex)
        end_idx = self.vertices.index(self.end_vertex)
        distance, path = graphlib.dijkstra(self.graph, start_idx, end_idx, True)

        if path:
            self.highlight_path(path)
            path_str = ' -> '.join(map(str, path))
            messagebox.showinfo("Кратчайший путь", f"Длина пути: {distance}\nПуть: {path_str}")
        else:
            messagebox.showwarning("Нет пути", "Путь между выбранными вершинами не существует.")

    def highlight_path(self, path):
        for edge_id in self.edges:
            self.canvas.itemconfig(edge_id, fill="black")

        edge_map = {
            (self.vertices.index(start_vertex), self.vertices.index(end_vertex)): edge_id
            for edge_id, (start_vertex, end_vertex, _, _) in self.edges.items()
        }

        for i in range(len(path) - 1):
            start_idx = path[i]
            end_idx = path[i + 1]
            edge_id = edge_map.get((start_idx, end_idx))
            if edge_id:
                self.canvas.itemconfig(edge_id, fill="blue")
            else:
                print(f"Ребро между вершинами {start_idx} и {end_idx} не найдено.")
