""" Интерфейс генератора """

from threading import Timer
import dearpygui.dearpygui as dpg
import generator as gen


QUEUE = gen.Queue()
DISTRIB = gen.Distributions()
_SPEED = ["0.5x", "1x", "1.5x", "2x", "5x", "10x"]
_ISWORK = True


def change_work(type_work):
    """Изменение режима работы системы"""
    global _ISWORK
    match type_work:
        case 0:
            _ISWORK = True
            dpg.set_value("time_passed", "Время работы: 0")
            timer(int(dpg.get_value("time_passed").split(" ")[-1]))
        case 1:
            _ISWORK = False
        case 2:
            _ISWORK = False
            dpg.configure_item("queue_1", items=[])
            for index in range(1, len(QUEUE.queues)):
                dpg.delete_item(f"flow_{index + 1}")
            QUEUE.clear_queue()
            dpg.set_value("avg_size", "Средний размер очереди: 0")
            dpg.set_value("avg_wait", "Среднее время ожидания в очереди: 0")


def timer(sec):
    """Отсчет времени"""

    # Уменьшение очереди
    QUEUE.decrease()

    # Добавление нового элемента
    if sec == DISTRIB.value_ex:
        QUEUE.put(DISTRIB.value_norm)
        DISTRIB.gen_next_values()

    # Изменение отображения очередей и их нагруженности
    for index,val in enumerate(QUEUE.queues):
        dpg.configure_item(f"queue_{index + 1}", items=val)
        load = 0
        if QUEUE.sum_elem != 0:
            load = round(sum(QUEUE.queues[index]) / QUEUE.sum_elem, 2)
        dpg.set_value(f"load_{index + 1}", f"Нагруженность: {load}%")

    # Изменение средних характеристик
    dpg.set_value("avg_size", f"Средний размер очереди: {QUEUE.get_avg_size()}")
    dpg.set_value(
        "avg_wait", f"Среднее время ожидания в очереди: {QUEUE.get_avg_wait()}"
    )
    dpg.set_value("time_passed", f"Время работы: {sec}")

    # Увеличение времени и запуск таймера
    sec += 1
    if _ISWORK:
        Timer(1 / float(dpg.get_value("speed")[:-1]), lambda: timer(sec)).start()


def change_count_queue():
    """Меняет количество очередей"""

    def add_queue():
        """Добавляет очередь"""
        QUEUE.add_queue()
        with dpg.group(parent="queues", tag=f"flow_{len(QUEUE.queues)}"):
            dpg.add_text(f"Очередь {len(QUEUE.queues)}")
            dpg.add_text("Нагруженность: 0%", tag=f"load_{len(QUEUE.queues)}")
            dpg.add_listbox(
                items=[],
                width=200,
                tag=f"queue_{len(QUEUE.queues)}",
                num_items=15,
                enabled=True,
            )

    def del_queue():
        """Удаляет очередь"""
        dpg.delete_item(f"flow_{len(QUEUE.queues)}")
        QUEUE.del_queue()

    if int(dpg.get_value("count_points")) > len(QUEUE.queues):
        add_queue()
    else:
        del_queue()


def change_distribution_type():
    """Меняет тип распределения между очередями"""
    QUEUE.distrib_type = dpg.get_value("distrib_type")


def change_params():
    """Изменяет параметры распределений"""
    DISTRIB.mean = float(dpg.get_value("mean"))
    DISTRIB.sigma = float(dpg.get_value("sigma"))
    DISTRIB.lambd = float(dpg.get_value("lambd"))


if __name__ == "__main__":
    dpg.create_context()

    with dpg.font_registry():
        with dpg.font(r"fonts\caviar-dreams.ttf", 20) as font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.window(tag="Primary Window"):
        with dpg.group(horizontal=True):
            with dpg.group():
                with dpg.group():
                    dpg.add_text("ПАРАМЕТРЫ ПОТОКА")
                    dpg.add_text("Интенсивность")
                    dpg.add_input_text(
                        default_value="10",
                        width=300,
                        decimal=True,
                        tag="lambd",
                        callback=change_params,
                    )
                    dpg.add_text("Среднее время обработки")
                    dpg.add_input_text(
                        default_value="10",
                        width=300,
                        decimal=True,
                        tag="mean",
                        callback=change_params,
                    )
                    dpg.add_text("Среднее время отклонения\nвремени обработки")
                    dpg.add_input_text(
                        default_value="3",
                        width=300,
                        decimal=True,
                        tag="sigma",
                        callback=change_params,
                    )
                    dpg.add_text("Количество пунктов обработки")
                    dpg.add_input_int(
                        default_value=1,
                        width=300,
                        min_value=1,
                        max_value=5,
                        tag="count_points",
                        callback=change_count_queue,
                    )
                    dpg.add_text("Скорость отображения")
                    dpg.add_combo(
                        default_value=_SPEED[1], items=_SPEED, width=300, tag="speed"
                    )
                    dpg.add_text("Распределение нагрузки")
                    dpg.add_radio_button(
                        default_value=gen.DISTRIBUTION_TYPES[0],
                        items=gen.DISTRIBUTION_TYPES,
                        tag="distrib_type",
                        callback=change_distribution_type,
                    )

                with dpg.group():
                    dpg.add_text("ХАРАКТЕРИСТИКИ ОЧЕРЕДЕЙ")
                    dpg.add_text("Средний размер очереди: -", tag="avg_size")
                    dpg.add_text("Среднее время ожидания в очереди: -", tag="avg_wait")

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Старт", width=100, callback=lambda: change_work(0)
                    )
                    dpg.add_button(
                        label="Пауза", width=100, callback=lambda: change_work(1)
                    )
                    dpg.add_button(
                        label="Стоп", width=100, callback=lambda: change_work(2)
                    )
            with dpg.group():
                dpg.add_text("ПОТОК")
                dpg.add_text("Время работы: 0", tag="time_passed")
                with dpg.group(horizontal=True, tag="queues"):
                    with dpg.group(parent="queues", tag="flow_1"):
                        dpg.add_text("Очередь 1")
                        dpg.add_text("Нагруженность: 0%", tag="load_1")
                        dpg.add_listbox(
                            items=[], width=200, tag="queue_1", num_items=15
                        )
        dpg.bind_font(font)
    dpg.create_viewport(title="Generator", width=1200, height=700)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
