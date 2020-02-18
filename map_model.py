from data import *

import matplotlib.pyplot as plt
import networkx as nx
import random


# Бинарный поиск аэропорта в массиве
# Линейный занял бы слишком много времени в случае учёта всех аэропортов
# Для этого, кстати, массив аэропортов сортируется по коду
def search_airport(array, element, lo=0, hi=None):
    hi = hi if hi is not None else len(array)
    while lo < hi:
        mid = (lo + hi) // 2
        midval = array[mid].code
        if midval < element:
            lo = mid + 1
        elif midval > element:
            hi = mid
        else:
            return array[mid]
    return None


# Считываю аэропорты и пути между ними.
# Количество аэропортов, которые будут взяты из общего числа
percentage = 1
print(f"Идёт обработка полученных аэропортов... Будет выбрано {percentage * 100}% от общего числа.")
# Списки аэропортов и путей между ними. Пути двунаправленные, очевидно
airports = []  # type: list
routes = []  # type: list
# Списки использованных стран и городов
countries = {}
cities = {}
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
        new_airport = Airport(int(line_split[0]), strings[3], strings[0], strings[1], strings[2],
                              float(line_split[6]), float(line_split[7]))
        airports.append(new_airport)
    random.shuffle(airports)
    airports = random.choices(airports, k=int(len(airports) * percentage))
    airports.sort(key=lambda ap: ap.code)

    # Добавляю пути между аэропортами
    routes_file = open("databases/routes.dat", "r")
    new_airports = []
    with routes_file as file:
        for line in file.readlines():
            source = search_airport(airports, line.split(",")[2])
            destination = search_airport(airports, line.split(",")[4])
            # Если путь соединяет два неучтённых аэропорта - его не учитываем
            if source is not None and destination is not None:
                if not new_airports.__contains__(source):
                    new_airports.append(source)
                if not new_airports.__contains__(destination):
                    new_airports.append(destination)
                routes.append((source, destination))
    # До этого все использованные аэропорты мы сохраняли в массив new_airports. Теперь мы заменим оригинальный массив
    # на него чтобы карта была более чистой
    airports = new_airports
    print("Обработка аэропортов и путей завершена!")

    # Создаю словари стран и городов
    # Словарь страны имеет формат {страна: [города]}
    # Словарь города имеет формат {город: pop:int, sus:float, inf:float, rec:float}
    for ap in airports:
        if not cities.keys().__contains__(ap.city):
            cities[ap.city] = {'pop': 1.0, 'sus': 1.0, 'inf': 0.0, 'rec': 0.0}
        if not countries.keys().__contains__(ap.country):
            countries[ap.country] = [ap.city]
        else:
            countries[ap.country].append(ap.city)

    # Задаём параметры болезни
    # Пока что - статично
    ro = 0.2
    la = 0.1
    mu = 0.05

    # Перевод данных в форму графа. Графы взяты из сторонней библиотеки NetworkX
    graph = nx.MultiGraph()
    for ap in airports:
        graph.add_node(ap)
    for r in routes:
        graph.add_edge(r[0], r[1])

    for country in sorted(countries):
        print(f"{country}:\n")
        for city in sorted(countries[country]):
            print(f"\t{city}: sus={cities[city]['sus']}, inf={cities[city]['inf']}, rec={cities[city]['rec']}\n")

    # Код для визуализации
    img = plt.imread("map.jpg")
    fig = plt.figure()  # type: plt.Figure
    ax_map = fig.add_subplot(111)
    ax_map.imshow(img, extent=(-180, 180, -90, 90))
    ap_positions = {}
    for ap in airports:
        ap_positions[ap] = (ap.longtitude, ap.latitude)
    nx.draw_networkx_nodes(graph, pos=ap_positions, node_color=range(len(airports)), node_size=3,
                           cmap=plt.get_cmap('plasma'))
    plt.show()
