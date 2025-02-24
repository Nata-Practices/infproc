import random
import tkinter

from .io import save_graph, load_graph
from .utils import get_vertex_at, add_vertex, update_edge, display_incidence_matrix, set_end_vertex, set_start_vertex, \
    delete_edge, delete_vertex, add_edge, change_edge_direction, change_edge_weight, on_routing_table_window_close, \
    on_packet_info_window_close


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
        show_canvas_menu(graph, event.x, event.y)


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


def show_canvas_menu(graph, x, y):
    """
    Отображает контекстное меню для пустого места на холсте.

    Args:
        graph: Объект графа.
        x: Координата x для отображения меню.
        y: Координата y для отображения меню.
    """
    menu = tkinter.Menu(graph.root, tearoff=0)
    menu.add_command(label="Добавить вершину", command=lambda: add_vertex(graph, x, y))
    menu.add_command(label="Сохранить граф", command=lambda: save_graph(graph))
    menu.add_command(label="Загрузить граф", command=lambda: load_graph(graph))
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


def show_routing_tables(graph):
    """
    Отображение таблиц маршрутизации.

    Открывает окно для отображения таблиц маршрутизации, обновляет его содержимое
    с данными о маршрутах и весах.

    Args:
        graph: Объект графа.
    """
    if not graph.routing_table_window or not graph.routing_table_window.winfo_exists():
        graph.routing_table_window = tkinter.Toplevel(graph.root)
        graph.routing_table_window.resizable(False, False)
        graph.routing_table_window.title("Таблицы маршрутизации")
        graph.routing_table_window.protocol("WM_DELETE_WINDOW", lambda: on_routing_table_window_close(graph))

        graph.routing_table_text = tkinter.Text(graph.routing_table_window, wrap="word", width=60, height=30)
        graph.routing_table_text.pack(fill=tkinter.BOTH, expand=True)

    graph.routing_table_text.delete(1.0, tkinter.END)
    total_weight = 0

    for node_id, table in graph.routing_tables.items():
        graph.routing_table_text.insert(tkinter.END, f"Узел {node_id}:\n")

        for destination, info in table.items():
            next_hop = info["next_hop"]
            edge_weight = info["edge_weight"]
            total_weight += edge_weight
            graph.routing_table_text.insert(
                tkinter.END,
                f"  -> К {destination}: через узел {next_hop}, вес узла - {edge_weight}, конечный вес - {total_weight}\n"
            )

        graph.routing_table_text.insert(tkinter.END, "\n")


def display_packet_path(graph, path, algorithm_name, total_packets=None):
    """
    Отображение пути передачи пакетов и логирование.

    Генерирует данные о передаче пакетов, добавляет их в окно информации и выделяет путь на графе.

    Args:
        graph: Объект графа.
        path: Маршрут передачи пакета.
        algorithm_name: Название алгоритма маршрутизации.
        total_packets: Общее количество пакетов (для дейтаграммного метода).
    """
    if algorithm_name != "Маршрутизация по предыдущему опыту":
        sender = path[0]
        receiver = path[-1]
    else:
        sender = graph.vertices[path[0]]
        receiver = graph.vertices[path[-1]]
        path = [graph.vertices[elem] for elem in path]

    packet_number = len(graph.packet_log) + 1
    packet_size = random.randint(100, 1000)
    hop_limit = len(path) - 1

    marsh_info = f"Маршрутизация №{graph.counter_of_tries}\n" if algorithm_name != "Случайная маршрутизация" else \
        f"Маршрутизация №{graph.counter_of_tries} для пакетов: {total_packets}\n"

    packet_info = (
        f"{marsh_info}"
        f"Алгоритм: {algorithm_name}\n"
        f"Адрес отправителя: Вершина {sender['name']}\n"
        f"Адрес назначения: Вершина {receiver['name']}\n"
        f"Назначенный маршрут: {' -> '.join(map(str, [v['name'] for v in path]))}\n"
        f"Номер пакета: {packet_number}\n"
        f"Размер пакета: {packet_size} байт\n"
        f"Время жизни (hop limit): {hop_limit} пересылок\n"
    )

    if not graph.packet_info_window or not graph.packet_info_window.winfo_exists():
        graph.packet_info_window = tkinter.Toplevel(graph.root)
        graph.packet_info_window.resizable(False, False)
        graph.packet_info_window.title("Информация о пакетах")
        graph.packet_info_window.protocol("WM_DELETE_WINDOW", lambda: on_packet_info_window_close(graph))

        graph.packet_info_text = tkinter.Text(graph.packet_info_window, wrap="word", width=50, height=20)
        graph.packet_info_text.pack(fill=tkinter.BOTH, expand=True)

    graph.packet_log.append(packet_info)
    graph.packet_info_text.insert(tkinter.END, packet_info + "<" + ("=" * 45) + ">\n")
    graph.packet_info_text.see(tkinter.END)
    highlight_path(graph, path, packet_size, algorithm_name)


def highlight_path(graph, path, packet_size, algorithm_name):
    """
    Выделение пути на графе с анимацией перемещения одного пакета.

    Сбрасывает выделение всех рёбер, выделяет рёбра пути и запускает анимацию пакета.

    Args:
        graph: Объект графа.
        path: Список вершин, представляющий маршрут.
        packet_size: Размер пакета (для определения задержки анимации).
        algorithm_name: Название алгоритма маршрутизации.
    """
    for edge_id in graph.edges:
        graph.canvas.itemconfig(edge_id, fill="black")

    edge_map = {
        (graph.vertices.index(start_vertex), graph.vertices.index(end_vertex)): edge_id
        for edge_id, (start_vertex, end_vertex, _, _) in graph.edges.items()
    }

    if isinstance(path[0], dict):
        path = [graph.vertices.index(vertex) for vertex in path]

    for i in range(len(path) - 1):
        start_idx = path[i]
        end_idx = path[i + 1]
        edge_id = edge_map.get((start_idx, end_idx))
        if edge_id:
            graph.canvas.itemconfig(edge_id, fill="blue")

    animate_packet(graph, path, packet_size, algorithm_name)


def animate_packet(graph, path, packet_size, algorithm_name):
    """
    Анимация перемещения одного пакета по указанному пути.

    Args:
        graph: Объект графа.
        path: Список вершин, представляющий маршрут.
        packet_size: Размер пакета (для определения задержки анимации).
        algorithm_name: Название алгоритма маршрутизации.
    """
    packet_radius = 10
    delay = min(200, packet_size // 10)

    start_vertex = graph.vertices[path[0]]
    start_coords = graph.canvas.coords(start_vertex["id"])
    start_x = (start_coords[0] + start_coords[2]) / 2
    start_y = (start_coords[1] + start_coords[3]) / 2

    packet_id = graph.canvas.create_oval(
        start_x - packet_radius, start_y - packet_radius,
        start_x + packet_radius, start_y + packet_radius,
        fill="#6e14e3" if algorithm_name == "Случайная маршрутизация" else
        "#14e359" if algorithm_name == "Лавинная маршрутизация" else
        "#e314a8",
        outline="black", width=2
    )

    def move_packet(index=0):
        """
        Рекурсивное перемещение пакета по маршруту.

        Перемещает пакет от текущей вершины к следующей по маршруту, используя шаги для плавной анимации.
        После завершения перемещения к конечной вершине удаляет пакет с холста.

        Args:
            index: Индекс текущей вершины в маршруте.
        """
        if index >= len(path) - 1:
            graph.canvas.delete(packet_id)
            return

        current_coords = graph.canvas.coords(graph.vertices[path[index]]["id"])
        next_coords = graph.canvas.coords(graph.vertices[path[index + 1]]["id"])
        current_x = (current_coords[0] + current_coords[2]) / 2
        current_y = (current_coords[1] + current_coords[3]) / 2
        next_x = (next_coords[0] + next_coords[2]) / 2
        next_y = (next_coords[1] + next_coords[3]) / 2
        steps = 50
        dx = (next_x - current_x) / steps
        dy = (next_y - current_y) / steps

        def step_animation(step=0):
            """
            Рекурсивное перемещение пакета на один шаг.

            Args:
                step: Текущий шаг перемещения.
            """
            if step <= steps:
                graph.canvas.move(packet_id, dx, dy)
                graph.canvas.after(delay, lambda: step_animation(step + 1))
            else:
                move_packet(index + 1)

        step_animation()

    move_packet()
