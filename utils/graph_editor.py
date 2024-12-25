import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox


def floyd_warshall(graph):
    n = len(graph)
    dist = [[float('inf')] * n for _ in range(n)]
    next_vertex = [[-1] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if graph[i][j] != 0:
                dist[i][j] = graph[i][j]
                next_vertex[i][j] = j
            if i == j:
                dist[i][j] = 0
                next_vertex[i][j] = i

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_vertex[i][j] = next_vertex[i][k]

    return dist, next_vertex


def dijkstra_all_pairs(graph):
    n = len(graph)
    dist_matrix = []
    path_matrix = []
    for start in range(n):
        dist, parent = dijkstra_with_parent(graph, start)
        dist_matrix.append(dist)
        path_matrix.append(parent)
    return dist_matrix, path_matrix


def reconstruct_path(parent, start, end):
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


def construct_floyd_path(next_vertex, start, end):
    if next_vertex[start][end] == -1:
        return []
    path = [start]
    while start != end:
        start = next_vertex[start][end]
        path.append(start)
    return path


def dijkstra_with_parent(graph, start):
    n = len(graph)
    dist = [float('inf')] * n
    dist[start] = 0
    parent = [-1] * n
    visited = [False] * n

    for _ in range(n):
        min_dist = float('inf')
        u = -1
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i

        if u == -1:
            break

        visited[u] = True

        for v in range(n):
            if graph[u][v] > 0 and not visited[v]:
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u] + graph[u][v]
                    parent[v] = u

    return dist, parent


def dijkstra(graph, start, end):
    n = len(graph)
    dist = [float('inf')] * n
    dist[start] = 0
    visited = [False] * n
    parent = [-1] * n

    for _ in range(n):
        min_dist = float('inf')
        u = -1
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i

        if u == -1:
            break

        visited[u] = True

        for v in range(n):
            if graph[u][v] > 0 and not visited[v]:
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u] + graph[u][v]
                    parent[v] = u

    if dist[end] == float('inf'):
        return None, []
    path = []
    current = end
    while current != -1:
        path.append(current)
        current = parent[current]
    path.reverse()

    return dist[end], path


def get_vertex_at(graph, x, y):
    for vertex in graph.vertices:
        coords = graph.canvas.coords(vertex["id"])
        vx = (coords[0] + coords[2]) / 2
        vy = (coords[1] + coords[3]) / 2
        if abs(x - vx) < 15 and abs(y - vy) < 15:
            return vertex
    return None


def add_vertex(graph, x, y):
    if len(graph.vertices) < 10:
        vertex_id = graph.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="lightblue")
        vertex_text = graph.canvas.create_text(x, y, text=str(len(graph.vertices)))
        graph.vertices.append({"id": vertex_id, "text": vertex_text, "edges": []})
        update_graph_matrix(graph)


def on_left_click(graph, event):
    vertex = get_vertex_at(graph, event.x, event.y)
    if vertex:
        graph.selected_vertex = vertex
        graph.canvas.bind("<B1-Motion>", lambda new_pos: on_mouse_drag(graph, new_pos))
        graph.canvas.bind("<ButtonRelease-1>", lambda new_pos: on_mouse_release(graph))
    else:
        add_vertex(graph, event.x, event.y)


def on_right_click(graph, event, task):
    vertex = get_vertex_at(graph, event.x, event.y)
    if vertex is not None:
        show_vertex_menu(graph, vertex, event.x, event.y, task)
    else:
        show_canvas_menu(graph, event.x, event.y, task)


def on_mouse_drag(graph, event):
    vertex = graph.selected_vertex
    x, y = event.x, event.y
    graph.canvas.coords(vertex["id"], x - 15, y - 15, x + 15, y + 15)
    graph.canvas.coords(vertex["text"], x, y)
    for edge_id in vertex["edges"]:
        update_edge(graph, edge_id)
    # Обновляем ребра, где вершина является конечной
    for edge_id in graph.edges:
        start_vertex, end_vertex, weight, label_id = graph.edges[edge_id]
        if end_vertex == vertex and edge_id not in vertex["edges"]:
            update_edge(graph, edge_id)


def on_mouse_release(graph):
    graph.canvas.unbind("<B1-Motion>")
    graph.canvas.unbind("<ButtonRelease-1>")
    graph.selected_vertex = None


def update_graph_matrix(graph):
    n = len(graph.vertices)
    graph.graph = [[0] * n for _ in range(n)]
    for edge_id, (start_vertex, end_vertex, weight, _) in graph.edges.items():
        start_idx = graph.vertices.index(start_vertex)
        end_idx = graph.vertices.index(end_vertex)
        graph.graph[start_idx][end_idx] = weight


def update_edge(graph, edge_id):
    start_vertex, end_vertex, weight, label_id = graph.edges[edge_id]
    start_coords = graph.canvas.coords(start_vertex["id"])
    end_coords = graph.canvas.coords(end_vertex["id"])
    sx = (start_coords[0] + start_coords[2]) / 2
    sy = (start_coords[1] + start_coords[3]) / 2
    ex = (end_coords[0] + end_coords[2]) / 2
    ey = (end_coords[1] + end_coords[3]) / 2
    graph.canvas.coords(edge_id, sx, sy, ex, ey)
    mx = (sx + ex) / 2
    my = (sy + ey) / 2
    graph.canvas.coords(label_id, mx, my - 10)


def set_start_vertex(graph, vertex):
    if graph.start_vertex:
        graph.canvas.itemconfig(graph.start_vertex["id"], fill="lightblue")
    graph.start_vertex = vertex
    graph.canvas.itemconfig(vertex["id"], fill="green")


def set_end_vertex(graph, vertex):
    if graph.end_vertex:
        graph.canvas.itemconfig(graph.end_vertex["id"], fill="lightblue")
    graph.end_vertex = vertex
    graph.canvas.itemconfig(vertex["id"], fill="red")


def add_edge(graph, start_vertex):
    end_vertex_index = simpledialog.askinteger("Добавить дугу", "Введите индекс конечной вершины (0-{})".format(len(graph.vertices)-1))
    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]
        weight = simpledialog.askinteger("Вес дуги", "Введите вес дуги")
        if weight is None:
            weight = 1
        start_coords = graph.canvas.coords(start_vertex["id"])
        end_coords = graph.canvas.coords(end_vertex["id"])
        sx = (start_coords[0] + start_coords[2]) / 2
        sy = (start_coords[1] + start_coords[3]) / 2
        ex = (end_coords[0] + end_coords[2]) / 2
        ey = (end_coords[1] + end_coords[3]) / 2
        line_id = graph.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST)
        # Добавляем метку веса
        mx = (sx + ex) / 2
        my = (sy + ey) / 2
        label_id = graph.canvas.create_text(mx, my - 10, text=str(weight), fill="red")
        graph.edges[line_id] = (start_vertex, end_vertex, weight, label_id)
        start_vertex["edges"].append(line_id)
        update_graph_matrix(graph)


def change_edge_weight(graph, start_vertex):
    end_vertex_index = simpledialog.askinteger(
        "Изменить вес дуги", f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})")
    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]
        for edge_id, (start_v, end_v, weight, label_id) in graph.edges.items():
            if start_v == start_vertex and end_v == end_vertex:
                new_weight = simpledialog.askinteger("Новый вес", "Введите новый вес дуги")
                if new_weight is not None:
                    graph.edges[edge_id] = (start_v, end_v, new_weight, label_id)
                    graph.canvas.itemconfig(label_id, text=str(new_weight))
                return
        messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")


def change_edge_direction(graph, start_vertex):
    end_vertex_index = simpledialog.askinteger(
        "Смена направления дуги", f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})")

    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]

        for edge_id, (start_v, end_v, weight, label_id) in graph.edges.items():
            if start_v == start_vertex and end_v == end_vertex:
                graph.edges[edge_id] = (end_vertex, start_vertex, weight, label_id)
                update_edge(graph, edge_id)
                messagebox.showinfo("Успех", "Направление дуги изменено.")
                return

        messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")


def delete_edge(graph, start_vertex):
    end_vertex_index = simpledialog.askinteger(
        "Удалить дугу", f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})")

    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]

        for edge_id, (start_v, end_v, _, label_id) in list(graph.edges.items()):
            if start_v == start_vertex and end_v == end_vertex:
                graph.canvas.delete(edge_id)
                graph.canvas.delete(label_id)
                del graph.edges[edge_id]

                if edge_id in start_vertex["edges"]:
                    start_vertex["edges"].remove(edge_id)

                messagebox.showinfo("Успех", "Дуга удалена.")
                return

            messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")


def delete_vertex(graph, vertex):
    graph.canvas.delete(vertex["id"])
    graph.canvas.delete(vertex["text"])
    for edge_id in list(graph.edges):
        start_vertex, end_vertex, _, label_id = graph.edges[edge_id]
        if start_vertex == vertex or end_vertex == vertex:
            graph.canvas.delete(edge_id)
            graph.canvas.delete(label_id)
            del graph.edges[edge_id]
        else:
            if start_vertex == vertex:
                start_vertex["edges"].remove(edge_id)
            if end_vertex == vertex:
                end_vertex["edges"].remove(edge_id)
    graph.vertices.remove(vertex)
    update_graph_matrix(graph)


def save_graph(graph, task):
    graph_data = {
        "start_vertex": graph.start_vertex,
        "end_vertex": graph.end_vertex,
        "vertices": [{"coords": graph.canvas.coords(v["id"])} for v in graph.vertices],
        "edges": [(graph.vertices.index(start_v), graph.vertices.index(end_v), weight) for
                  _, (start_v, end_v, weight, _) in graph.edges.items()]
    }
    if not os.path.exists("saves"):
        os.makedirs("saves")

    with open(f"saves\graph_{task}.json", "w") as f:
        json.dump(graph_data, f)
    messagebox.showinfo("Сохранение", f"Граф сохранен в файл graph_{task}.json")


def load_graph(graph, task):
    try:
        if not os.path.exists("saves"):
            os.makedirs("saves")

        with open(f"saves\graph_{task}.json", "r") as f:
            graph_data = json.load(f)

        clear_graph(graph)

        for vertex_data in graph_data["vertices"]:
            x0, y0, x1, y1 = vertex_data["coords"]
            add_vertex(graph, (x0 + x1) // 2, (y0 + y1) // 2)

        for start_idx, end_idx, weight in graph_data["edges"]:
            start_vertex = graph.vertices[start_idx]
            end_vertex = graph.vertices[end_idx]
            add_edge_with_weight(graph, start_vertex, end_vertex, weight)

        if graph_data["start_vertex"] is not None:
            set_start_vertex(graph, graph_data["start_vertex"])
            set_end_vertex(graph, graph_data["end_vertex"])

    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл graph_{task}.json не найден")


def clear_graph(graph):
    for vertex in graph.vertices:
        graph.canvas.delete(vertex["id"])
        graph.canvas.delete(vertex["text"])
    for edge_id in graph.edges:
        graph.canvas.delete(edge_id)
    graph.vertices.clear()
    graph.edges.clear()


def add_edge_with_weight(graph, start_vertex, end_vertex, weight):
    start_coords = graph.canvas.coords(start_vertex["id"])
    end_coords = graph.canvas.coords(end_vertex["id"])
    sx = (start_coords[0] + start_coords[2]) / 2
    sy = (start_coords[1] + start_coords[3]) / 2
    ex = (end_coords[0] + end_coords[2]) / 2
    ey = (end_coords[1] + end_coords[3]) / 2
    line_id = graph.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST)

    mx = (sx + ex) / 2
    my = (sy + ey) / 2
    label_id = graph.canvas.create_text(mx, my - 10, text=str(weight), fill="red")

    graph.edges[line_id] = (start_vertex, end_vertex, weight, label_id)
    start_vertex["edges"].append(line_id)
    update_graph_matrix(graph)


def display_incidence_matrix(graph):
    n_vertices = len(graph.vertices)
    n_edges = len(graph.edges)
    incidence_matrix = [[0] * n_edges for _ in range(n_vertices)]

    for idx, (edge_id, (start_vertex, end_vertex, _, _)) in enumerate(graph.edges.items()):
        start_idx = graph.vertices.index(start_vertex)
        end_idx = graph.vertices.index(end_vertex)
        incidence_matrix[start_idx][idx] = 1
        incidence_matrix[end_idx][idx] = -1

    matrix_window = tk.Toplevel(graph.root)
    matrix_window.title("Матрица инцидентности")
    text_area = tk.Text(matrix_window, wrap=tk.WORD, width=50, height=20)
    text_area.pack(fill=tk.BOTH, expand=True)

    matrix_str = "Матрица инцидентности:\n"
    for row in incidence_matrix:
        matrix_str += " ".join(map(str, row)) + "\n"

    text_area.insert(tk.END, matrix_str)
    text_area.config(state=tk.DISABLED)


def show_canvas_menu(graph, x, y, task):
    menu = tk.Menu(graph.root, tearoff=0)
    menu.add_command(label="Добавить вершину", command=lambda: add_vertex(graph, x, y))
    menu.add_command(label="Сохранить граф", command=lambda: save_graph(graph, task))
    menu.add_command(label="Загрузить граф", command=lambda: load_graph(graph, task))
    menu.add_command(label="Показать матрицу инцидентности", command=lambda: display_incidence_matrix(graph))
    graph.current_menu = menu
    menu.post(x + graph.root.winfo_rootx(), y + graph.root.winfo_rooty())


def show_vertex_menu(graph, vertex, x, y, task):
    graph.selected_vertex = vertex
    menu = tk.Menu(graph.root, tearoff=0)
    if task != "2":
        menu.add_command(label="Установить как начальную вершину", command=lambda: set_start_vertex(graph, vertex))
        menu.add_command(label="Установить как конечную вершину", command=lambda: set_end_vertex(graph, vertex))
    menu.add_command(label="Удалить вершину", command=lambda: delete_vertex(graph, vertex))
    menu.add_command(label="Добавить дугу", command=lambda: add_edge(graph, vertex))
    menu.add_command(label="Изменить вес дуги", command=lambda: change_edge_weight(graph, vertex))
    menu.add_command(label="Сменить направление дуги", command=lambda: change_edge_direction(graph, vertex))
    menu.add_command(label="Удалить дугу", command=lambda: delete_edge(graph, vertex))
    graph.current_menu = menu
    menu.post(x + graph.root.winfo_rootx(), y + graph.root.winfo_rooty())
