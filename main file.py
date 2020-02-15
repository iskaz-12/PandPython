# -*- coding: utf-8 -*-
# !/usr/bin/env python

__author__ = 'kazakovais'

# from tkinter import *

'''
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
'''

#import pygal


# Моделирование ситуации в отдельно взятом регионе в зависимости
# от начальных входных данных

# population = int(input('Введите количество людей в данном регионе: '))
chance_of_rec = float(input('Введите значение вероятности выздоровления (от 0 до 1): '))
chance_of_infect = float(input('Введите значение вероятности заражения (от 0 до 1): '))
fraction_of_inf = float(input('Введите значение доли инфицированных в начале эпидемии (от 0 до 1): '))

# Допущение: доля восприимчивых к инфекции = 1 - доля инфицированных
fraction_of_sus = 1.0 - fraction_of_inf

#print(fraction_of_sus)

# Пусть t - количество дней, прошедших с момента начала эпидемии
t = int(input('Введите количество дней, прошедших с начала эпидемии: '))

# Построение модели SIR (неудачный вариант)
# т.к. используется одна переменная

'''
def SIR_model_sus(t):
    sus = fraction_of_sus
    inf = fraction_of_inf
    rec = 0
    for i in range(1, t):
        sus = sus - chance_of_infect * sus * inf
        inf = inf + chance_of_infect * sus * inf - chance_of_rec * inf
        rec = rec + chance_of_rec * inf
    print('Восприимчивые (чел.):', sus * population)
    print('Инфицированные (чел.):', inf * population)
    print('Выздоровевшие (чел.):', rec * population)
'''


def SIR_model(t):
    '''
    sus = []
    inf = []
    rec = []
    '''

    sus = [None] * (t + 1)
    inf = [None] * (t + 1)
    rec = [None] * (t + 1)
    sus[0] = fraction_of_sus
    inf[0] = fraction_of_inf
    rec[0] = 0
    for i in range(1, t + 1):
        sus[i] = sus[i - 1] - chance_of_infect * sus[i - 1] * inf[i - 1]
        inf[i] = inf[i - 1] + chance_of_infect * sus[i - 1] * inf[i - 1] - chance_of_rec * inf[i - 1]
        rec[i] = rec[i - 1] + chance_of_rec * inf[i - 1]

    #Небольшие проблемы с кодировкой, считает правильно
    print('Через', t, 'дней после начала эпидемии:')
    print('Восприимчивые:', sus[t])
    print('Инфицированные:', inf[t])
    print('Выздоровевшие:', rec[t])

'''
    # создание поточечного графика
    line_chart = pygal.Line()
    line_chart.title = 'Диаграмма SIR'
    line_chart.x_labels = map(str, range(1, t))
    line_chart.add('Восприимчивые', sus)
    line_chart.add('Инфицированные', inf)
    line_chart.add('Выздоровевшие', rec)

    line_chart.render_to_file('line_chart.svg')

    #работа с картой мира с помощью pygal
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = 'Некоторые страны'
    worldmap_chart.add('F countries', ['fr', 'fi'])
    worldmap_chart.add('M countries', ['ma', 'mc', 'md', 'me', 'mg',
                                       'mk', 'ml', 'mm', 'mn', 'mo',
                                       'mr', 'mt', 'mu', 'mv', 'mw',
                                       'mx', 'my', 'mz'])
    worldmap_chart.add('U countries', ['ua', 'ug', 'us', 'uy', 'uz'])
    worldmap_chart.render_to_file('world_map_chart.svg')
'''

SIR_model(t)

