""" Генератор """

import numpy as np


DISTRIBUTION_TYPES = ["по размеру очереди", "по нагруженности"]


class Distributions:
    """Распределения"""

    mean = 10.
    sigma = 10.
    lambd = 3.
    value_norm = 0
    value_ex = 0

    def __init__(self):
        self.gen_next_values()


    def _get_number(self, rand):
        """Уравнивает число"""
        num = np.ceil(rand).astype(int)
        if num <= 0:
            return 1
        return num


    def gen_next_values(self):
        """Генерирует новую длину интервала и новое значение"""

        self.value_ex += self._get_number(np.random.exponential(self.lambd))
        self.value_norm = self._get_number(np.random.normal(self.mean, self.sigma))


class Queue:
    """Очередь"""

    queues = [[]]
    distrib_type = DISTRIBUTION_TYPES[0]
    sum_elem = 0
    size_queue = []
    waiting_time = []

    def __init__(self):
        pass


    def add_queue(self):
        """Добавляет очередь в конец"""
        self.queues.append([])


    def del_queue(self):
        """Удаляет очередь с конца"""
        self.queues.pop(0)


    def put(self, element):
        """Добавляет элемент в конец очереди и его время ожидания"""
        if self.distrib_type == DISTRIBUTION_TYPES[0]:
            index = self.queues.index(min(self.queues, key=len))
        else:
            index = self.queues.index(min(self.queues, key=sum))

        self.size_queue.append(len(self.queues[index]))
        self.waiting_time.append(sum(self.queues[index]))
        self.queues[index].append(element)
        self.sum_elem += element


    def decrease(self):
        """Уменьшает очереди"""
        for index,val in enumerate(self.queues):
            if val:
                self.queues[index][0] -= 1
                if val[0] == 0:
                    self.queues[index].pop(0)


    def get_avg_size(self):
        """Возвращает средний размер очереди"""
        if len(self.size_queue) == 0:
            return 0.0
        return round(sum(self.size_queue) / len(self.size_queue), 2)


    def get_avg_wait(self):
        """Возвращает среднее время ожидания в очереди"""
        if len(self.waiting_time) == 0:
            return 0.0
        return round(sum(self.waiting_time) / len(self.waiting_time), 2)


    def clear_queue(self):
        """Очистка очередей"""
        self.queues = [[]]
        self.size_queue = []
        self.waiting_time = []
        self.sum_elem = 0
