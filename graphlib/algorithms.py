def floyd_warshall(graph):
    """
    Реализует алгоритм Флойда-Уоршелла для нахождения кратчайших путей
    между всеми парами вершин в графе.

    Args:
        graph: Матрица смежности графа, где graph[i][j] - вес ребра от вершины i к j.

    Returns:
        dist: Матрица кратчайших расстояний между всеми парами вершин.
        next_vertex: Матрица для восстановления путей.
    """
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


def dijkstra(graph, start, end=None, return_parent=False):
    """
    Реализует алгоритм Дейкстры для нахождения кратчайшего пути от одной вершины к другим.

    Args:
        graph: Матрица смежности графа.
        start: Индекс начальной вершины.
        end: Индекс конечной вершины (опционально).
        return_parent: Если True, возвращает массив родительских вершин.

    Returns:
        Если end указан: Кортеж (расстояние до end, путь до end).
        Если end не указан: Кортеж (массив расстояний, массив родительских вершин или None).
    """
    n = len(graph)
    dist = [float('inf')] * n
    dist[start] = 0
    visited = [False] * n
    parent = [-1] * n if return_parent else None

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
                    if return_parent:
                        parent[v] = u

    if end is not None:
        return dist[end], (reconstruct_path(parent, start, end) if return_parent else [])

    return dist, parent


def dijkstra_all_pairs(graph):
    """
    Вычисляет кратчайшие пути между всеми парами вершин в графе с помощью алгоритма Дейкстры.

    Args:
        graph: Матрица смежности графа.

    Returns:
        dist_matrix: Матрица кратчайших расстояний между всеми парами вершин.
        path_matrix: Матрица родительских вершин для восстановления путей.
    """
    n = len(graph)
    dist_matrix = []
    path_matrix = []

    for start in range(n):
        dist, parent = dijkstra(graph, start, return_parent=True)
        dist_matrix.append(dist)
        path_matrix.append(parent)

    return dist_matrix, path_matrix


def reconstruct_path(data, start, end, is_floyd=False):
    """
    Восстанавливает путь между двумя вершинами на основе данных алгоритма Дейкстры или Флойда-Уоршелла.

    Args:
        data: Массив родительских вершин (Дейкстра) или матрица next_vertex (Флойд).
        start: Индекс начальной вершины.
        end: Индекс конечной вершины.
        is_floyd: Указывает, используется ли матрица next_vertex.

    Returns:
        path: Список вершин, составляющих путь от start к end.
    """
    path = []
    current = end

    while current != -1:
        path.append(current)
        if current == start:
            break
        current = data[current] if not is_floyd else data[start][current]

    if current == -1:
        return []

    path.reverse()
    return path


def construct_floyd_path(next_vertex, start, end):
    """
    Восстанавливает путь между двумя вершинами на основе матрицы next_vertex алгоритма Флойда-Уоршелла.

    Args:
        next_vertex: Матрица для восстановления путей.
        start: Индекс начальной вершины.
        end: Индекс конечной вершины.

    Returns:
        path: Список вершин, составляющих путь от start к end.
    """
    if next_vertex[start][end] == -1:
        return []

    path = [start]

    while start != end:
        start = next_vertex[start][end]
        path.append(start)

    return path
