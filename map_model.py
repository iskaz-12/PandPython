from data import *

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import random


def infection(graph: nx.Graph, city: City, ro: float, la: float, mi: float):
    sus = city.old_sus
    inf = city.old_inf
    rec = city.old_rec

    neigh_num = len(list(graph.neighbors(city)))
    neigh_sus = 0.0
    neigh_inf = 0.0
    neigh_rec = 0.0
    for c in graph.neighbors(city):
        neigh_sus += c.old_sus
        neigh_inf += c.old_inf
        neigh_rec += c.old_rec
    neigh_sus /= neigh_num
    neigh_inf /= neigh_num
    neigh_rec /= neigh_num

    city.sus = (1 - mi) * (sus - ro * sus * inf) + mi * neigh_sus
    city.inf = (1 - mi) * (inf + ro * sus * inf - la * inf) + mi * neigh_inf
    city.rec = (1 - mi) * (rec + la * inf) + mi * neigh_rec


# Считываю аэропорты и пути между ними.
# Количество аэропортов, которые будут взяты из общего числа
percentage = 1
print(f"Идёт обработка полученных аэропортов... Будет выбрано {percentage * 100}% от общего числа.")
graph = nx.MultiGraph()
# Списки использованных стран и городов
cities = {}
airports_to_cities = {}
airports_file = open("databases/airports.dat", "r")
with airports_file as file:
    for line in file.readlines():
        strings = []
        inner_string = re.search(r'\".*?\"', line)
        while inner_string is not None:
            line = line.replace(inner_string.group(0), f"s{len(strings)}", 1)
            strings.append(inner_string.group(0)[1:-1])
            inner_string = re.search(r'\".*?\"', line)

        line_split = line.split(",")
        name = strings[1]
        supposed_city = cities[name] if cities.keys().__contains__(name) else None
        if supposed_city is None:
            supposed_city = City(strings[1], strings[2], float(line_split[6]), float(line_split[7]))
            cities[name] = supposed_city
        airports_to_cities[strings[3]] = supposed_city
    cities_to_keep = list(cities.keys())
    random.shuffle(cities_to_keep)
    cities_to_keep = random.choices(cities_to_keep, k=int(len(cities_to_keep) * percentage))

    # Добавляю пути между аэропортами
    routes_file = open("databases/routes.dat", "r")
    with routes_file as file:
        for line in file.readlines():
            if not airports_to_cities.keys().__contains__(
                    line.split(",")[2]) or not airports_to_cities.keys().__contains__(line.split(",")[4]):
                continue
            source = airports_to_cities[line.split(",")[2]]
            destination = airports_to_cities[line.split(",")[4]]
            # Если путь соединяет два неучтённых аэропорта - его не учитываем
            if cities_to_keep.__contains__(source.name) and cities_to_keep.__contains__(destination.name):
                if not graph.nodes.data().__contains__(source):
                    graph.add_node(source)
                if not graph.nodes.data().__contains__(destination):
                    graph.add_node(destination)
                graph.add_edge(source, destination)
    # До этого все использованные аэропорты мы сохраняли в массив new_airports. Теперь мы заменим оригинальный массив
    # на него чтобы карта была более чистой
    print("Обработка аэропортов и путей завершена!")

    # Создаю словарь стран
    # Словарь страны имеет формат {страна: [города]}
    countries = {}
    for city in cities.values():
        if countries.keys().__contains__(city.country):
            countries[city.country].append(city)
        else:
            countries[city.country] = [city]

    # Задаём параметры болезни
    # Пока что - статично
    ro = 0.5
    la = 0.1
    mu = 0.05

    cities['Conakry'].sus = 0.5
    cities['Conakry'].inf = 0.5

    # Код для визуализации
    img = plt.imread("map.jpg")
    fig = plt.figure()  # type: plt.Figure
    ax_map = fig.add_subplot(111)
    ap_positions = {}
    for ap in graph.nodes.data():
        ap_positions[ap[0]] = (ap[0].longtitude, ap[0].latitude)
    ax_map.imshow(img, extent=(-180, 180, -90, 90))
    nx.draw_networkx_nodes(graph, pos=ap_positions, node_color=[city[0].inf for city in graph.nodes.data()],
                           node_size=3,
                           cmap=plt.get_cmap('rainbow'), vmin=0.0, vmax=1.0)


    def animate(i):
        ax_map.clear()
        ax_map.imshow(img, extent=(-180, 180, -90, 90))

        for city in list(graph.nodes):
            city.old_inf = city.inf
            city.old_rec = city.rec
            city.old_sus = city.sus
        for city in graph.nodes.data():
            infection(graph, city[0], ro, la, mu)

        colors = [city[0].inf for city in graph.nodes.data()]
        nx.draw_networkx_nodes(graph, pos=ap_positions, node_color=colors, node_size=3,
                               cmap=plt.get_cmap('rainbow'), vmin=0.0, vmax=1.0)


    animation = FuncAnimation(fig, animate, frames=200, interval=500, repeat=False)
    plt.show()
