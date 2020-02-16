from data import *
import matplotlib.pyplot as plt
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
percentage = 0.1
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

routes_file = open("databases/routes.dat", "r")
new_airports = []
with routes_file as file:
    for line in file.readlines():
        source = search_airport(airports, line.split(",")[2])
        destination = search_airport(airports, line.split(",")[4])
        if source is not None and destination is not None:
            if not new_airports.__contains__(source):
                new_airports.append(source)
            if not new_airports.__contains__(destination):
                new_airports.append(destination)
            routes.append((source, destination))
airports = new_airports

# Код для визуализации
img = plt.imread("map.jpg")
fig, ax = plt.subplots()
ax.imshow(img, extent=(-180, 180, -90, 90))
x = []
y = []
for ap in new_airports:
    # if ap.id % 100 == 0:
    x.append(ap.longtitude)
    y.append(ap.latitude)
plt.scatter(x, y, marker='.', c='r')

for r in routes:
    x = [r[0].longtitude, r[1].longtitude]
    y = [r[0].latitude, r[1].latitude]
    plt.plot(x, y, c="lightsalmon", linewidth=1)

plt.show()
