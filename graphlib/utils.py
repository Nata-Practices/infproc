import tkinter
from tkinter import simpledialog, Entry, END, messagebox, Label
from .tooltip import ToolTip


def get_vertex_at(graph, x, y):
    """
    Возвращает вершину, находящуюся рядом с заданными координатами (x, y).
    Если вершина не найдена, возвращается None.

    Args:
        graph: Объект графа.
        x: Координата x.
        y: Координата y.

    Returns:
        Словарь с данными вершины или None.
    """
    for vertex in graph.vertices:
        coords = graph.canvas.coords(vertex["id"])
        vx = (coords[0] + coords[2]) / 2
        vy = (coords[1] + coords[3]) / 2

        if abs(x - vx) < 15 and abs(y - vy) < 15:
            return vertex

    return None


def add_vertex(graph, x, y):
    """
    Добавляет новую вершину на граф в заданных координатах.

    Args:
        graph: Объект графа.
        x: Координата x.
        y: Координата y.
    """
    if len(graph.vertices) < 10:
        used_indices = {int(graph.canvas.itemcget(v["text"], "text")) for v in graph.vertices}
        new_index = next(i for i in range(10) if i not in used_indices)
        vertex_id = graph.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="lightblue")
        vertex_text = graph.canvas.create_text(x, y, text=str(new_index))
        graph.vertices.append({"id": vertex_id, "name": new_index, "text": vertex_text, "edges": []})
        update_graph_matrix(graph)
        update_matrix_display(graph)
        

def delete_vertex(graph, vertex):
    """
    Удаляет вершину и связанные с ней рёбра из графа.

    Args:
        graph: Объект графа.
        vertex: Вершина для удаления.
    """
    graph.canvas.delete(vertex["id"])
    graph.canvas.delete(vertex["text"])

    edges_to_delete = []

    for edge_id, (start_vertex, end_vertex, _, label_id) in list(graph.edges.items()):
        if start_vertex == vertex or end_vertex == vertex:
            edges_to_delete.append(edge_id)

    for edge_id in edges_to_delete:
        start_vertex, end_vertex, _, label_id = graph.edges[edge_id]
        graph.canvas.delete(edge_id)  # Удаляем линию ребра
        graph.canvas.delete(label_id)  # Удаляем метку веса
        del graph.edges[edge_id]

        if edge_id in start_vertex["edges"]:
            start_vertex["edges"].remove(edge_id)

    graph.vertices.remove(vertex)
    update_graph_matrix(graph)
    update_matrix_display(graph)
    

def get_edge_coords(start_vertex, end_vertex, canvas):
    """
    Вычисляет координаты начала, конца и центра ребра.

    Args:
        start_vertex: Вершина начала ребра.
        end_vertex: Вершина конца ребра.
        canvas: Холст для отрисовки.

    Returns:
        Кортеж координат: (sx, sy, ex, ey, mx, my).
    """
    start_coords = canvas.coords(start_vertex["id"])
    end_coords = canvas.coords(end_vertex["id"])
    sx, sy = (start_coords[0] + start_coords[2]) / 2, (start_coords[1] + start_coords[3]) / 2
    ex, ey = (end_coords[0] + end_coords[2]) / 2, (end_coords[1] + end_coords[3]) / 2
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    return sx, sy, ex, ey, mx, my


def create_edge(graph, start_vertex, end_vertex, weight):
    """
    Создаёт ребро между двумя вершинами с заданным весом.

    Args:
        graph: Объект графа.
        start_vertex: Вершина начала ребра.
        end_vertex: Вершина конца ребра.
        weight: Вес ребра.
    """
    sx, sy, ex, ey, mx, my = get_edge_coords(start_vertex, end_vertex, graph.canvas)
    line_id = graph.canvas.create_line(sx, sy, ex, ey, arrow=tkinter.LAST)
    label_id = graph.canvas.create_text(mx, my - 10, text=str(weight), fill="red")
    graph.edges[line_id] = (start_vertex, end_vertex, weight, label_id)
    start_vertex["edges"].append(line_id)
    update_graph_matrix(graph)


def add_edge(graph, start_vertex):
    """
    Добавляет новое ребро.

    Args:
        graph: Объект графа.
        start_vertex: Начальная вершина ребра.
    """
    end_vertex_index = simpledialog.askinteger(
        "Добавить дугу",
        f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})"
    )
    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]
        weight = simpledialog.askinteger("Вес дуги", "Введите вес дуги") or 1
        create_edge(graph, start_vertex, end_vertex, weight)
    else:
        messagebox.showwarning("Ошибка", "Данной вершины не существует")
    
    update_matrix_display(graph)


def update_edge(graph, edge_id):
    """
    Обновляет положение линии ребра и метки веса при изменении координат.

    Args:
        graph: Объект графа.
        edge_id: Идентификатор ребра.
    """
    start_vertex, end_vertex, weight, label_id = graph.edges[edge_id]
    sx, sy, ex, ey, mx, my = get_edge_coords(start_vertex, end_vertex, graph.canvas)
    graph.canvas.coords(edge_id, sx, sy, ex, ey)
    graph.canvas.coords(label_id, mx, my - 10)


def delete_edge(graph, start_vertex):
    """
    Удаляет ребро, запрашивая конечную вершину.

    Args:
        graph: Объект графа.
        start_vertex: Начальная вершина ребра.
    """
    end_vertex_index = simpledialog.askinteger(
        "Удалить дугу",
        f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})"
    )

    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]

        for edge_id, (start_v, end_v, _, label_id) in list(graph.edges.items()):
            if start_v == start_vertex and end_v == end_vertex:
                graph.canvas.delete(edge_id)
                graph.canvas.delete(label_id)
                del graph.edges[edge_id]

                if edge_id in start_vertex["edges"]:
                    start_vertex["edges"].remove(edge_id)

                update_matrix_display(graph)
                return

            messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")
    
    
def change_edge_weight(graph, start_vertex):
    """
    Изменяет вес ребра, запрашивая конечную вершину и новый вес.

    Args:
        graph: Объект графа.
        start_vertex: Начальная вершина ребра.
    """
    end_vertex_index = simpledialog.askinteger(
        "Изменить вес дуги",
        f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})"
    )

    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]

        for edge_id, (start_v, end_v, weight, label_id) in graph.edges.items():
            if start_v == start_vertex and end_v == end_vertex:
                new_weight = simpledialog.askinteger("Новый вес", "Введите новый вес дуги")

                if new_weight is not None:
                    graph.edges[edge_id] = (start_v, end_v, new_weight, label_id)
                    graph.canvas.itemconfig(label_id, text=str(new_weight))

                update_matrix_display(graph)
                return

        messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")


def change_edge_direction(graph, start_vertex):
    """
    Меняет направление ребра, запрашивая конечную вершину.

    Args:
        graph: Объект графа.
        start_vertex: Начальная вершина ребра.
    """
    end_vertex_index = simpledialog.askinteger(
        "Смена направления дуги",
        f"Введите индекс конечной вершины (0-{len(graph.vertices) - 1})"
    )

    if end_vertex_index is not None and 0 <= end_vertex_index < len(graph.vertices):
        end_vertex = graph.vertices[end_vertex_index]

        for edge_id, (start_v, end_v, weight, label_id) in graph.edges.items():
            if start_v == start_vertex and end_v == end_vertex:
                graph.edges[edge_id] = (end_vertex, start_vertex, weight, label_id)
                update_edge(graph, edge_id)
                update_matrix_display(graph)
                return

        messagebox.showwarning("Ошибка", "Дуга между этими вершинами не найдена.")


def get_adjacency_matrix(graph):
    """
    Возвращает текущую матрицу смежности графа.
    """
    n = len(graph.vertices)
    matrix = [[0 for _ in range(n)] for _ in range(n)]

    for edge in graph.edges.values():
        start_vertex, end_vertex, weight, _ = edge
        start_idx = graph.vertices.index(start_vertex)
        end_idx = graph.vertices.index(end_vertex)
        matrix[start_idx][end_idx] = weight

    return matrix


def on_matrix_change(graph, event, x, y):
    """
    Обрабатывает изменения в матрице смежности.
    При изменении веса дуги обновляет граф.
    """
    new_value = event.widget.get()

    try:
        new_weight = int(new_value)
    except ValueError:
        messagebox.showwarning("Неверный ввод", "Введите целое число для веса дуги.")
        previous_weight = get_adjacency_matrix(graph)[x][y]
        event.widget.delete(0, END)
        event.widget.insert(0, str(previous_weight))
        return

    if x < len(graph.vertices) and y < len(graph.vertices):
        edge_found = False
        edge_id = 0
        for edge_id, (start_v, end_v, weight, _) in graph.edges.items():
            if graph.vertices.index(start_v) == x and graph.vertices.index(end_v) == y:
                graph.edges[edge_id] = (start_v, end_v, new_weight, _)
                edge_found = True
                break

        if edge_found:
            _, _, _, label_id = graph.edges[edge_id]
            graph.canvas.itemconfig(label_id, text=str(new_weight))
        else:
            start_vertex = graph.vertices[x]
            end_vertex = graph.vertices[y]
            create_edge(graph, start_vertex, end_vertex, new_weight)

        update_matrix_display(graph)

def update_matrix_display(graph):
    """
    Обновляет отображение матрицы смежности в matrix_inner_frame.
    """
    # Очистка существующих Entry виджетов
    for row in graph.matrix_entries:
        for entry in row:
            entry.destroy()
    graph.matrix_entries = []

    adjacency_matrix = get_adjacency_matrix(graph)

    # Создание заголовка матрицы (номера столбцов)
    header_row = []
    for col, vertex in enumerate(graph.vertices):
        name = graph.canvas.itemcget(vertex["text"], "text")
        label = Label(
            graph.matrix_inner_frame,
            text=name,
            width=5,
            justify='center',
            bg="#d3d3d3",
            relief='groove'
        )
        label.grid(row=0, column=col + 1, padx=1, pady=1)
        header_row.append(label)
    graph.matrix_entries.append(header_row)

    # Создание строк матрицы
    for i, row_data in enumerate(adjacency_matrix):
        row_entries = []
        name = graph.canvas.itemcget(graph.vertices[i]["text"], "text")
        label = Label(
            graph.matrix_inner_frame,
            text=name,
            width=5,
            justify='center',
            bg="#d3d3d3",
            relief='groove'
        )
        label.grid(row=i + 1, column=0, padx=1, pady=1)
        row_entries.append(label)
        for j, value in enumerate(row_data):

            if i == j:
                entry = Entry(graph.matrix_inner_frame, width=5, justify='center', state='readonly', bg="#f0f0f0")
                entry.insert(0, "0")
                ToolTip(entry, "Нет связи (диагональ)")
            else:
                entry = Entry(graph.matrix_inner_frame, width=5, justify='center')
                entry.insert(0, str(value))
                entry.bind("<FocusOut>", lambda event, x=i, y=j: on_matrix_change(graph, event, x, y))

                if value > 0:
                    entry.config(bg="#ccffcc")
                elif value < 0:
                    entry.config(bg="#ffcccc")
                else:
                    entry.config(bg="#ffffff")

                start_vertex = graph.vertices[i]["name"]
                end_vertex = graph.vertices[j]["name"]
                weight = f"Вес {value}" if value != 0 else "Нет связи"
                ToolTip(entry, f"От {start_vertex} к {end_vertex}: {weight}")

            entry.grid(row=i+1, column=j+1, padx=1, pady=1)
            row_entries.append(entry)

        graph.matrix_entries.append(row_entries)

            
def update_graph_matrix(graph):
    """
    Обновляет матрицу смежности графа на основе текущих рёбер.

    Args:
        graph: Объект графа.
    """
    n = len(graph.vertices)
    graph.graph = [[0] * n for _ in range(n)]

    for edge_id, (start_vertex, end_vertex, weight, _) in list(graph.edges.items()):
        if start_vertex in graph.vertices and end_vertex in graph.vertices:
            start_idx = graph.vertices.index(start_vertex)
            end_idx = graph.vertices.index(end_vertex)
            graph.graph[start_idx][end_idx] = weight


def set_start_vertex(graph, vertex):
    """
    Устанавливает вершину как начальную.

    Args:
        graph: Объект графа.
        vertex: Вершина для установки.
    """
    if graph.start_vertex:
        graph.canvas.itemconfig(graph.start_vertex["id"], fill="lightblue")

    graph.start_vertex = vertex
    graph.canvas.itemconfig(vertex["id"], fill="green")


def set_end_vertex(graph, vertex):
    """
    Устанавливает вершину как конечную.

    Args:
        graph: Объект графа.
        vertex: Вершина для установки.
    """
    if graph.end_vertex:
        graph.canvas.itemconfig(graph.end_vertex["id"], fill="lightblue")

    graph.end_vertex = vertex
    graph.canvas.itemconfig(vertex["id"], fill="red")


def display_incidence_matrix(graph):
    """
    Отображает матрицу инцидентности текущего графа в новом окне.

    Args:
        graph: Объект графа.
    """
    n_vertices = len(graph.vertices)
    n_edges = len(graph.edges)
    incidence_matrix = [[0] * n_edges for _ in range(n_vertices)]

    for idx, (edge_id, (start_vertex, end_vertex, _, _)) in enumerate(graph.edges.items()):
        start_idx = graph.vertices.index(start_vertex)
        end_idx = graph.vertices.index(end_vertex)
        incidence_matrix[start_idx][idx] = 1
        incidence_matrix[end_idx][idx] = -1

    matrix_window = tkinter.Toplevel(graph.root)
    matrix_window.title("Матрица инцидентности")
    text_area = tkinter.Text(matrix_window, wrap=tkinter.WORD, width=50, height=20)
    text_area.pack(fill=tkinter.BOTH, expand=True)

    matrix_str = "Матрица инцидентности:\n"

    for row in incidence_matrix:
        matrix_str += " ".join(map(str, row)) + "\n"

    text_area.insert(tkinter.END, matrix_str)
    text_area.config(state=tkinter.DISABLED)
