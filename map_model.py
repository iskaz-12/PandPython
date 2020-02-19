from data import *

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import random

'''
    Эта функция - приложение трёх основных уравнений SIR-модели для структуры графа. 
    На вход подаются: сам граф, город, для которого ведётся расчёт, коэффициенты заражаемости, выздоравливаемости и
    миграции. Сперва мы для удобства сохраняем значения компонентов SIR с предыдущего шага, затем вычисляем среднее 
    арифметическое этих компонент с городов, соединённых с моделируемым и потом вычисляем значение для города по формуле
    
        компонента = количество_оставшихся * формула_компоненты + количество_мигрировавших*ср_ариф_компоненты_соседей
        
'''


def infection(graph: nx.Graph, city: City, inf_prob: float, rec_prob: float, mig_coeff: float):
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

    city.sus = (1 - mig_coeff) * (sus - inf_prob * sus * inf) + mig_coeff * neigh_sus
    city.inf = (1 - mig_coeff) * (inf + inf_prob * sus * inf - rec_prob * inf) + mig_coeff * neigh_inf
    city.rec = (1 - mig_coeff) * (rec + rec_prob * inf) + mig_coeff * neigh_rec


# Количество аэропортов, которые будут взяты из общего числа
percentage = 1
# Считывание данных из файлов.
print(f"Идёт обработка полученных аэропортов... Будет выбрано {percentage * 100}% от общего числа.")
'''
    Сразу сохраняем данные в структуру графа, чтобы избежать повторных проходов по 8000 элементов (не говоря о путях).
    Но для подмоги используем словари стран и аэропортов (последний особенно удобен для работы с графом)
    Словарь городов имеет вид {имя_города: город}, словарь аэропортов - {код_аэропорта: город}
    Сами города, кстати, хранятся как объекты класса City (который написан в файле data.py). Это удобно, т.к. позволяет
    обмениваться не данными, а ссылками на объекты этого класса. Т.е., проще говоря, если мы перекинем город из словаря
    городов в словарь аэропортов, то и там, и там у нас будет всего один объект и к нему можно будет обращаться разными
    способами
'''
graph = nx.Graph()
cities = {}
airports_to_cities = {}

'''
    Небольшое описание того, что мы тут делаем. Нам нужно разобрать строку с аэропортом по токенам и получить
    интересующие нас данные - код, город, страну, широту и долготу. Строка содержит данные следующего вида:
    целые числа, дробные числа и строки, которые разделены друг с другом запятыми. Это можно было бы легко разбить с
    помощью функции split, но есть проблема - строчные данные - названия аэропортов, городов и стран - могут содержать
    запятые внутри. Например, "Harstad/Narvik Airport, Evenes". Поэтому сперва надо как-нибудь избавиться от таких запятых.
    Выход - регулярные выражения. Мы ищем все подстроки строки из базы данных и сохраняем их в массив strings, 
    а их вхождения в основную строку заменяем на s{порядковый номер убранной строки}. Но и тут есть проблема - внутри
    подстрок есть внутренние кавычки. Чтобы упростить себе работу мы просто ищем все такие кавычки внутри подстрок и
    убираем их из файла с данными. После всех этих операций строка принимает вид "id, s0, s1,..." и т.д. что позволяет
    разбить её сплитом и вычленить нужные данные.
'''
airports_file = open("databases/airports.dat", "r")
with airports_file as file:
    for line in file.readlines():
        strings = []
        # Используем регулярное выражение с паттерном "искать как можно меньше символов, заключённых между кавычками"
        inner_string = re.search(r'\".*?\"', line)
        while inner_string is not None:
            line = line.replace(inner_string.group(0), f"s{len(strings)}", 1)
            strings.append(inner_string.group(0)[1:-1])
            inner_string = re.search(r'\".*?\"', line)

        line_split = line.split(",")
        # Некоторые аэропорты не расположены в городах и вместо города имеют пустую строку. Поэтому мы создаём
        # для них "псевдогород" с названием их аэропорта.
        name = strings[1] if len(strings[1]) != 0 else strings[0]
        # Если город уже внесёт в базу данных, то мы просто добавляем его в словарь аэропортов. Если нет -
        # создаём для него объект и помещаем его в словарь городов
        supposed_city = cities[name] if cities.keys().__contains__(name) else None
        if supposed_city is None:
            supposed_city = City(name, strings[2], float(line_split[6]), float(line_split[7]))
            cities[name] = supposed_city
        airports_to_cities[strings[3]] = supposed_city
    # Далее выбираем случайное количество городов в зависимости от указанного процента выборки
    # Выбираем следующим образом: с помощью функции random.shuffle мы тасуем массив ключей (он же массив названий городов),
    # а затем выбираем из него (количество_городов * процент_выборки) элементов
    cities_to_keep = list(cities.keys())
    random.shuffle(cities_to_keep)
    cities_to_keep = cities_to_keep[:int(len(cities_to_keep) * percentage)]

    # Начинаем работать с, собственно, графом
    routes_file = open("databases/routes.dat", "r")
    with routes_file as file:
        for line in file.readlines():
            # Если среди имеющихся аэропортов нет такого, код которого есть в таблице путей, то мы пропускаем этот путь
            if not airports_to_cities.keys().__contains__(line.split(",")[2]) \
                    or not airports_to_cities.keys().__contains__(line.split(",")[4]):
                continue
            # Выбираем начальный и конечный город
            source = airports_to_cities[line.split(",")[2]]
            destination = airports_to_cities[line.split(",")[4]]
            # Если одна из точек пути - аэропорт, который мы выкинули из выборки, то его мы не учитываем
            if cities_to_keep.__contains__(source.name) and cities_to_keep.__contains__(destination.name):
                # Если одна из точек пути - город, которого нет в графе, то мы добавляем его в граф
                if not list(graph.nodes).__contains__(source):
                    graph.add_node(source)
                if not list(graph.nodes).__contains__(destination):
                    graph.add_node(destination)
                # Создаём ребро
                graph.add_edge(source, destination)
    print("Обработка аэропортов и путей завершена!")

    # Пока это не нужно
    # # Создаю словарь стран
    # # Словарь страны имеет формат {страна: [города]}
    # countries = {}
    # for city in cities.values():
    #     if countries.keys().__contains__(city.country):
    #         countries[city.country].append(city)
    #     else:
    #         countries[city.country] = [city]

    # Задаём параметры болезни
    # Пока что - статично
    inf_prob = 0.2
    rec_prob = 0.1
    mig_coeff = 0.05

    # Выбираем город, с которого начнём заражение
    cities['Conakry'].sus = 0.95
    cities['Conakry'].inf = 0.05

    # Код для визуализации
    img = plt.imread("map.jpg")
    # Цветовая карта для визуализации количества больных. Радужная показала себя лучше всего.
    colormap = 'rainbow'
    fig = plt.figure()  # type: plt.Figure
    ax_map = fig.add_subplot(111)
    # Выставляем координаты городам
    ap_positions = {}
    for ap in graph.nodes.data():
        ap_positions[ap[0]] = (ap[0].longtitude, ap[0].latitude)
    # Натягиваем карту мира на фон
    ax_map.imshow(img, extent=(-180, 180, -90, 90))
    # Рисуем нулевой этап. node_size - размер точки на карте, cmap - цветовая карта, vmin - потенциально минимальная
    # доля заболевших, vmax - потенциально максимальная
    nx.draw_networkx_nodes(graph, pos=ap_positions, node_color=[city[0].inf for city in graph.nodes.data()],
                           node_size=3,
                           cmap=plt.get_cmap(colormap), vmin=0.0, vmax=1.0)


    # С помощью этой функции идёт анимация. Мы каждый раз очищаем график, ставим карту на фон, заменяем старые данные
    # новыми и пробегаемся по всем городам функцией расчёта заражения
    def animate(i):
        for city in list(graph.nodes):
            city.old_inf = city.inf
            city.old_rec = city.rec
            city.old_sus = city.sus
        for city in graph.nodes.data():
            infection(graph, city[0], inf_prob, rec_prob, mig_coeff)

        ax_map.clear()
        ax_map.imshow(img, extent=(-180, 180, -90, 90))
        nx.draw_networkx_nodes(graph, pos=ap_positions, node_color=[city[0].inf for city in graph.nodes.data()], node_size=3,
                               cmap=plt.get_cmap(colormap), vmin=0.0, vmax=1.0)

    # Анимируем, делаем на полный экран, наслаждаемся)
    # Чтобы увеличить скорость надо уменьшить значение interval
    animation = FuncAnimation(fig, animate, frames=10000, interval=60, repeat=False)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
