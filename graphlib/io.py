import json
import os
from tkinter import messagebox

from .utils import add_vertex, create_edge, set_end_vertex, set_start_vertex


def save_graph(graph, task):
    """
    Сохраняет текущий граф в файл JSON.

    Args:
        graph: Объект графа.
        task: Номер задания.
    """
    graph_data = {
        "start_vertex": graph.vertices.index(graph.start_vertex) if graph.start_vertex else None,
        "end_vertex": graph.vertices.index(graph.end_vertex) if graph.end_vertex else None,
        "vertices": [{"coords": graph.canvas.coords(v["id"])} for v in graph.vertices],
        "edges": [(graph.vertices.index(start_v), graph.vertices.index(end_v), weight) for
                  _, (start_v, end_v, weight, _) in graph.edges.items()]
    }
    if not os.path.exists("saves"):
        os.makedirs("saves")

    with open(f"saves/graph_{task}.json", "w") as file:
        json.dump(graph_data, file)
    messagebox.showinfo("Сохранение", f"Граф сохранен в файл graph_{task}.json")


def load_graph(graph, task):
    """
    Загружает граф из файла JSON.

    Args:
        graph: Объект графа.
        task: Номер задания.

    Raises:
        FileNotFoundError: Если файл с графом не найден.
        KeyError: Если формат данных некорректен.
    """
    try:
        if not os.path.exists("saves"):
            os.makedirs("saves")

        with open(f"saves/graph_{task}.json", "r") as f:
            graph_data = json.load(f)

        clear_graph(graph)

        for vertex_data in graph_data["vertices"]:
            x0, y0, x1, y1 = vertex_data["coords"]
            add_vertex(graph, (x0 + x1) // 2, (y0 + y1) // 2)

        for start_idx, end_idx, weight in graph_data["edges"]:
            start_vertex = graph.vertices[start_idx]
            end_vertex = graph.vertices[end_idx]
            create_edge(graph, start_vertex, end_vertex, weight)

        if graph_data["start_vertex"] is not None:
            graph.start_vertex = graph.vertices[graph_data["start_vertex"]]
            set_start_vertex(graph, graph.start_vertex)

        if graph_data["end_vertex"] is not None:
            graph.end_vertex = graph.vertices[graph_data["end_vertex"]]
            set_end_vertex(graph, graph.end_vertex)

    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл graph_{task}.json не найден")
    except KeyError as e:
        messagebox.showerror("Ошибка", f"Некорректный формат данных: {e}")


def clear_graph(graph):
    """
    Полностью очищает граф.

    Args:
        graph: Объект графа.
    """
    for vertex in graph.vertices:
        graph.canvas.delete(vertex["id"])
        graph.canvas.delete(vertex["text"])

    for edge_id in graph.edges:
        graph.canvas.delete(edge_id)

    graph.vertices.clear()
    graph.edges.clear()
