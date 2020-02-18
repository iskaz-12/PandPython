from data import *

import matplotlib.pyplot as plt
import networkx as nx
import random


# Бинарный поиск аэропорта в массиве
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
airports = []  # type: list
routes = []  # type: list
airports_file = open("databases/airports.dat", "r")
with airports_file as file:
    for line in file.readlines():
        strings = []
        inner_string = re.search(r'\".*?\"', line)
        while inner_string is not None:
            line = line.replace(inner_string.group(0), f"s{len(strings)}")
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

# Код для визуализации
img = plt.imread("map.jpg")
fig = plt.figure()  # type: plt.Figure
ax_map = fig.add_subplot(111)
ax_map.imshow(img, extent=(-180, 180, -90, 90))
x = []
y = []
graph = nx.DiGraph()
ap_positions = {}
for ap in airports:
    graph.add_node(ap, color='r')
    ap_positions[ap] = (ap.longtitude, ap.latitude)
for r in routes:
    graph.add_edge(r[0], r[1], color='lightsalmon')
nx.draw(graph, pos=ap_positions, node_size=1, width=1)

plt.show()
