import tkinter

from .io import save_graph, load_graph
from .utils import get_vertex_at, add_vertex, update_edge, display_incidence_matrix, set_end_vertex, set_start_vertex, \
    delete_edge, delete_vertex, add_edge, change_edge_direction, change_edge_weight


def on_left_click(graph, event):
    """
    Обрабатывает левый клик мыши.

    Args:
        graph: Объект графа.
        event: Событие клика (координаты x, y).
    """
    vertex = get_vertex_at(graph, event.x, event.y)

    if vertex:
        graph.selected_vertex = vertex
        graph.canvas.bind("<B1-Motion>", lambda new_pos: on_mouse_drag(graph, new_pos))
        graph.canvas.bind("<ButtonRelease-1>", lambda new_pos: on_mouse_release(graph))
    else:
        add_vertex(graph, event.x, event.y)


def on_right_click(graph, event, task):
    """
    Обрабатывает правый клик мыши.

    Args:
        graph: Объект графа.
        event: Событие клика (координаты x, y).
        task: Номер задания.
    """
    vertex = get_vertex_at(graph, event.x, event.y)

    if vertex is not None:
        show_vertex_menu(graph, vertex, event.x, event.y, task)
    else:
        show_canvas_menu(graph, event.x, event.y, task)


def on_mouse_drag(graph, event):
    """
    Обрабатывает перемещение вершины при удержании левой кнопки мыши.

    Args:
        graph: Объект графа.
        event: Событие перемещения (новые координаты x, y).
    """
    vertex = graph.selected_vertex
    x, y = event.x, event.y
    graph.canvas.coords(vertex["id"], x - 15, y - 15, x + 15, y + 15)
    graph.canvas.coords(vertex["text"], x, y)

    for edge_id in vertex["edges"]:
        update_edge(graph, edge_id)

    for edge_id in graph.edges:
        start_vertex, end_vertex, weight, label_id = graph.edges[edge_id]
        if end_vertex == vertex and edge_id not in vertex["edges"]:
            update_edge(graph, edge_id)


def on_mouse_release(graph):
    """
    Обрабатывает отпускание левой кнопки мыши после перемещения вершины.

    Args:
        graph: Объект графа.
    """
    graph.canvas.unbind("<B1-Motion>")
    graph.canvas.unbind("<ButtonRelease-1>")
    graph.selected_vertex = None


def show_canvas_menu(graph, x, y, task):
    """
    Отображает контекстное меню для пустого места на холсте.

    Args:
        graph: Объект графа.
        x: Координата x для отображения меню.
        y: Координата y для отображения меню.
        task: Тип задачи (может изменять доступные опции в меню).
    """
    menu = tkinter.Menu(graph.root, tearoff=0)
    menu.add_command(label="Добавить вершину", command=lambda: add_vertex(graph, x, y))
    menu.add_command(label="Сохранить граф", command=lambda: save_graph(graph, task))
    menu.add_command(label="Загрузить граф", command=lambda: load_graph(graph, task))
    menu.add_command(label="Показать матрицу инцидентности", command=lambda: display_incidence_matrix(graph))
    graph.current_menu = menu
    menu.post(x + graph.root.winfo_rootx(), y + graph.root.winfo_rooty())


def show_vertex_menu(graph, vertex, x, y, task):
    """
    Отображает контекстное меню для вершины.

    Args:
        graph: Объект графа.
        vertex: Вершина, для которой вызывается меню.
        x: Координата x для отображения меню.
        y: Координата y для отображения меню.
        task: Тип задачи (может изменять доступные опции в меню).
    """
    graph.selected_vertex = vertex
    menu = tkinter.Menu(graph.root, tearoff=0)
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
