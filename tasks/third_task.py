import random
from tkinter import messagebox, Frame, Label, Entry, Button, StringVar, IntVar, ttk, LabelFrame

import graphlib
from tasks.base_graph import BaseGraphApp


class PacketRoutingApp(BaseGraphApp):
    def __init__(self, root):
        super().__init__(root, "Симуляция передачи пакетов", "3")

        settings_frame = Frame(root, pady=10)
        settings_frame.pack(side='top', fill='x')

        Label(settings_frame, text="Количество пакетов:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.num_packets_var = IntVar(value=1)
        self.num_packets_entry = Entry(settings_frame, textvariable=self.num_packets_var, width=5)
        self.num_packets_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        Label(settings_frame, text="Протокол:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.protocol_var = StringVar(value="TCP")
        self.protocol_menu = ttk.Combobox(settings_frame, textvariable=self.protocol_var, values=["TCP", "UDP"],
                                          state='readonly', width=10)
        self.protocol_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.protocol_menu.current(0)

        routing_frame = Frame(root, pady=10)
        routing_frame.pack(side='top', fill='x')

        self.add_button("Случайная маршрутизация", lambda: self.start_routing("random"))
        self.add_button("Лавинная маршрутизация", lambda: self.start_routing("flooding"))
        self.add_button("Маршрутизация по предыдущему опыту", lambda: self.start_routing("historical"))
        self.add_button("Сохранить граф", lambda: graphlib.save_graph(self))
        self.add_button("Загрузить граф", lambda: graphlib.load_graph(self, False))

        results_frame = Frame(root, padx=10, pady=10)
        results_frame.pack(side='bottom', fill='both', expand=True)

        routing_table_frame = LabelFrame(results_frame, text="Таблица маршрутизации", padx=10, pady=10)
        routing_table_frame.pack(side='left', fill='both', padx=5, pady=5)

        # self.routing_tree = ttk.Treeview(routing_table_frame, columns=("Destination", "Next Hop", "Hops"), show='headings')
        self.routing_tree = ttk.Treeview(routing_table_frame, columns=("Destination", "Hops"), show='headings')
        self.routing_tree.heading("Destination", text="Пункт назначения")
        # self.routing_tree.heading("Next Hop", text="Следующий узел")
        self.routing_tree.heading("Hops", text="Пройденные узлы")
        self.routing_tree.pack(fill='both', expand=True)

        packet_data_frame = LabelFrame(results_frame, text="Данные о пакетах", padx=10, pady=10)
        packet_data_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.packet_tree = ttk.Treeview(packet_data_frame,
                                        columns=("Packet ID", "Path", "Protocol", "PacketSize", "HopLimit"),
                                        show='headings')
        self.packet_tree.heading("Packet ID", text="ID пакета")
        self.packet_tree.heading("Path", text="Маршрут")
        self.packet_tree.heading("Protocol", text="Протокол")
        self.packet_tree.heading("PacketSize", text="Размер пакета")
        self.packet_tree.heading("HopLimit", text="Время жизни")
        self.packet_tree.column("Packet ID", width=10)
        self.packet_tree.column("Path", width=100)
        self.packet_tree.column("Protocol", width=10)
        self.packet_tree.column("PacketSize", width=10)
        self.packet_tree.column("HopLimit", width=10)
        self.packet_tree.pack(fill='both', expand=True)

        reset_button = Button(root, text="Сбросить таблицы", command=self.reset_tables)
        reset_button.pack(side='bottom', pady=10)

    def start_routing(self, algorithm):
        if not (self.start_vertex and self.end_vertex):
            messagebox.showwarning("Ошибка", "Необходимо выбрать начальную и конечную вершины.")
            return

        try:
            num_packets = self.num_packets_var.get()
            if num_packets < 1:
                raise ValueError
        except:
            messagebox.showwarning("Ошибка", "Количество пакетов должно быть положительным целым числом.")
            return

        protocol = self.protocol_var.get()

        self.counter_of_tries += 1
        self.reset_tables()
        routing_tables = {}

        if algorithm == "random":
            all_paths, algorithm_name = graphlib.algorithms.random_routing(self, num_packets, protocol)
        elif algorithm == "flooding":
            all_paths, algorithm_name = graphlib.algorithms.flooding_routing(self, num_packets, protocol)
        elif algorithm == "historical":
            all_paths, routing_tables, algorithm_name = graphlib.algorithms.historical_routing(self, num_packets, protocol)
        else:
            messagebox.showwarning("Ошибка", "Неизвестный алгоритм маршрутизации.")
            return

        if not all_paths:
            return

        if algorithm != "historical":
            for path in all_paths:
                destination = path[-1]["name"]
                hops = len(path) - 1
                routing_tables[destination] = {"hops": hops}

        self.update_routing_table(routing_tables)

        for packet_index, path in enumerate(all_paths, start=1):
            packet_size = random.randint(100, 1000)
            hop_limit = len(path) - 1
            if algorithm != "historical":
                self.update_packet_data(packet_index, [vertex["name"] for vertex in path], protocol, packet_size,
                                        hop_limit)
            else:
                self.update_packet_data(packet_index, [vertex for vertex in path], protocol, packet_size, hop_limit)

    def update_routing_table(self, routing_tables):
        """
        Обновляет отображение таблицы маршрутизации в GUI.

        Args:
            routing_tables: Словарь таблиц маршрутизации.
        """
        for item in self.routing_tree.get_children():
            self.routing_tree.delete(item)

        for destination, info in routing_tables.items():
            # next_hop = info.get("next_hop", "")
            hops = info.get("hops", "")
            # self.routing_tree.insert("", 'end', values=(destination, next_hop, hops))
            self.routing_tree.insert("", 'end', values=(destination, hops))

    def update_packet_data(self, packet_id, path, protocol, packet_size, hop_limit):
        """
        Обновляет отображение данных о пакетах в GUI.

        Args:
            packet_id: Идентификатор пакета.
            path: Маршрут пакета.
            protocol: Протокол передачи данных.
            packet_size: Размер пакета.
            hop_limit: Время жизни пакета.
        """
        path_str = " -> ".join(map(str, path))
        self.packet_tree.insert("", 'end', values=(packet_id, path_str, protocol, packet_size, hop_limit))

    def get_edge_weight(self, from_node, to_node):
        """
        Возвращает вес ребра между двумя узлами.

        Args:
            from_node (str): Имя начального узла.
            to_node (str): Имя конечного узла.

        Returns:
            int/float: Вес ребра. Возвращает 0, если ребро не найдено.
        """
        for edge in self.edges.values():
            if edge[0]["name"] == from_node and edge[1]["name"] == to_node:
                return edge[2]
        return 0

    def reset_tables(self):
        """
        Сбрасывает таблицы маршрутизации и данные о пакетах.
        """
        for item in self.routing_tree.get_children():
            self.routing_tree.delete(item)

        for item in self.packet_tree.get_children():
            self.packet_tree.delete(item)
