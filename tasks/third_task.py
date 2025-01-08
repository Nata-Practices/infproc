from tkinter import messagebox

import graphlib
from tasks.base_graph import BaseGraphApp


class PacketRoutingApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Симуляция передачи пакетов", "3")
        self.add_button("Случайная маршрутизация", lambda: self.start_routing("random"))
        self.add_button("Лавинная маршрутизация", lambda: self.start_routing("flooding"))
        self.add_button("Маршрутизация по предыдущему опыту", lambda: self.start_routing("historical"))
        self.add_button("Сохранить граф", lambda: graphlib.save_graph(self, "3"))
        self.add_button("Загрузить граф", lambda: graphlib.load_graph(self, "3"))

    def start_routing(self, algorithm):
        if not (self.start_vertex and self.end_vertex):
            messagebox.showwarning("Ошибка", "Необходимо выбрать начальную и конечную вершины.")
            return

        self.counter_of_tries += 1

        if algorithm == "random":
            graphlib.random_routing(self)
        elif algorithm == "flooding":
            graphlib.flooding_routing(self)
        elif algorithm == "historical":
            graphlib.historical_routing(self)
