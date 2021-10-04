from aiogram import types
from aiogram.utils.markdown import bold, italic, code, link

import datetime
from pairs import PSDB


psdb = PSDB()
days_of_week = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def is_group(group: str):
    group = group.split("/")
    if len(group) != 2:
        return False

    direction = group[0]
    for i in direction:
        if i not in "абвгдежзийклмнопрстуфхцчшщыэюя":
            return False

    code_list = group[1].split("-")
    if code_list[0] not in "бм":
        return False

    try:
        int(code_list[1])
    except Exception as _ex:
        return False

    try:
        int(code_list[2])
    except:
        return False

    if code_list[3] not in "оз":
        return False

    return True


def print_pairs(pairs: list, day_of_week: int, even_week: bool, with_id=False):
    if len(pairs) == 0:
        return bold(days_of_week[day_of_week] +
               (" чётной недели" if even_week else " нечётной недели") + ". На заводе не работаем") + "\n"
    msg = bold("Вот твоё расписание на выбранный день (" + days_of_week[day_of_week] +
               (" чётной недели" if even_week else " нечётной недели") + "):") + "\n"
    for pair in pairs:
        pair = list(pair)
        if pair[6] == "":
            pair[6] = "Преподаватель не определён"

        if pair[4] == 1:
            pair[4] = "8:30 ~ 10:00\n1. "
        elif pair[4] == 2:
            pair[4] = "10:10 ~ 11:40\n2. "
        elif pair[4] == 3:
            pair[4] = "11:50 ~ 13:20\n3. "
        elif pair[4] == 4:
            pair[4] = "14:00 ~ 15:30\n4. "
        elif pair[4] == 5:
            pair[4] = "15:40 ~ 17:10\n5. "
        elif pair[4] == 6:
            pair[4] = "17:20 ~ 18:50\n6. "
        elif pair[4] == 7:
            pair[4] = "19:00 ~ 20:30\n7. "
               italic(str(pair[6])) + "\n    " + code(str(pair[7]) +
        msg += str(pair[4]) + str(pair[5]) + (bold(" ID:" + str(pair[0])) if with_id else "") + "\n    " + \
               italic(str(pair[6])) + "\n    " + code(str(pair[7]) + ("" if pair[8] == "" else (" в ауд. " + pair[8]))) + "\n\n"
    return msg


def get_pairs(message: types.Message):
    # Определим чётность недели и номера нужных дней недели
    cmd = message.text.lower().replace(",", "").split(" ")

    msg = ""

    # Добавим к ответу бота расписание на сегодня
    if len(cmd) == 2 and is_group(cmd[1]):
        msg += get_today(group=cmd[1])
    else:
        msg += get_today_by_id(message.from_user.id)

    # Добавим в сообщение расписание на завтра
    if len(cmd) == 2 and cmd[1] != "" and is_group(cmd[1]):
        msg += get_next_day(group=cmd[1])
    else:
        msg += get_next_day_by_id(message.from_user.id)

    return msg


def get_today(group: str):
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    today = datetime.datetime.today().weekday()
    msg = ""
    if today != 6:  # Если сегодня не воскресенье
        pairs = psdb.r_get_pairs_by_group(day_of_week=today+1, even_week=even_week, group=group)
        msg += print_pairs(pairs, today+1, even_week)
    return msg


def get_today_by_id(id: int):
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    today = datetime.datetime.today().weekday()
    msg = ""
    if today != 6:  # Если сегодня не воскресенье
        group = psdb.r_user_group_is_set(tg_id=id)
        if not group:
            return "У тебя не задана группа\nИсправить это можно командой 'группа <название группы>'\n" \
                   "Проверяется текущая группа командой 'группа' без аргументов (параметров)"
        pairs = psdb.r_get_pairs_by_tgid(day_of_week=today+1, even_week=even_week, tg_id=id)
        msg += print_pairs(pairs, today+1, even_week)
    return msg


def get_next_day(group: str):
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    tomorrow = datetime.datetime.today().weekday() + 1
    msg = ""
    monday = False

    if tomorrow == 6:  # Если завтра воскресенье, то перейдём на понедельник
        monday = True
        tomorrow = 0
        even_week = not even_week

    if tomorrow != 6:  # Если завтра не воскресенье
        msg += bold("Вот твоё расписание на завтра:" if not monday else "Вот твоё расписание на понедельник:") + "\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=tomorrow + 1, even_week=even_week, group=group)
        msg += print_pairs(pairs, tomorrow+1, even_week)
    return msg


def get_next_day_by_id(id: int):
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    today = datetime.datetime.today().weekday()
    if today == 6:
        tomorrow = 0
        even_week = not even_week
    else:
        tomorrow = today + 1

    msg = ""
    monday = False

    if tomorrow == 6:  # Если завтра воскресенье, то перейдём на понедельник
        monday = True
        tomorrow = 0
        even_week = not even_week

    if tomorrow != 6:  # Если завтра не воскресенье
        group = psdb.r_user_group_is_set(tg_id=id)
        if not group:
            return "У тебя не задана группа\nИсправить это можно командой 'группа <название группы>'\n" \
                   "Проверяется текущая группа командой 'группа' без аргументов (параметров)"
        msg += bold("Вот твоё расписание на завтра:" if not monday else "Вот твоё расписание на понедельник:") + "\n"
        pairs = psdb.r_get_pairs_by_tgid(day_of_week=tomorrow + 1, even_week=even_week, tg_id=id)
        msg += print_pairs(pairs, tomorrow+1, even_week)
    return msg


def get_week(group, even_week):
    msg = ""
    for i in range(1, 7):
        msg += bold(days_of_week[i]) + "\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=i, even_week=even_week, group=group)
        msg += print_pairs(pairs, i, even_week)
        msg += "\n"
    return msg
