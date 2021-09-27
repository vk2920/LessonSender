import datetime
import logging

import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, bold, italic, code, underline, strikethrough, link
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from pairs import PSDB

import os


class DataInput(StatesGroup):
    r = State()


database = None
# API_TOKEN = '1941221231:AAEVvHJUmnIOl6RzcX6lUj5oossETD6I4RU'
API_TOKEN = os.environ['BOT_TOKEN']

ban_list = []
bot_version = "20210921-1800"
DEBUG_MODE = False

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

bot_keyboard = ReplyKeyboardMarkup()
bot_keyboard.add(KeyboardButton("Пары"))
bot_keyboard.row(KeyboardButton("Сегодня"), (KeyboardButton("Завтра")))
bot_keyboard.row(KeyboardButton("Чёт"), KeyboardButton("Всё"), (KeyboardButton("Нечёт")))
bot_keyboard.row(KeyboardButton("Группа"), KeyboardButton("Помощь"))

group_update_keyboard = ReplyKeyboardMarkup()
group_update_keyboard.row(KeyboardButton("Посмотреть"), KeyboardButton("Очистить"))
group_update_keyboard.add(KeyboardButton("Отмена"))

psdb = PSDB()


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
    except:
        return False

    try:
        int(code_list[2])
    except:
        return False

    if code_list[3] not in "оз":
        return False

    return True


def get_pairs(message: types.Message):
    # Определим чётность недели и номера нужных дней недели
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    today = datetime.datetime.today().weekday()
    tomorrow = today+1 if today != 6 else 0
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
    if today != 6: # Если сегодня не воскресенье
        pairs = psdb.r_get_pairs_by_group(day_of_week=today+1, even_week=even_week, group=group)
        if len(pairs) != 0:
            msg += bold("Вот твоё расписание на сегодня:") + "\n"
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
                # msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                #        str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + \
                       code(str(pair[7]) + ("" if pair[8] == "" else " в ауд. ") + str(pair[8])) + "\n\n"
        else:
            msg += bold("Сегодня нет пар") + "\n"
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
        if len(pairs) != 0:
            msg += bold("Вот твоё расписание на сегодня:") + "\n"
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
                # msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                #        str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + \
                       code(str(pair[7]) + ("" if pair[8] == "" else " в ауд. ") + str(pair[8])) + "\n\n"
        else:
            msg += bold("Сегодня нет пар") + "\n\n"
    return msg


def get_next_day(group: str):
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    tomorrow = datetime.datetime.today().weekday() + 1
    msg = ""
    monday = False

    if tomorrow == 6: # Если завтра воскресенье, то перейдём на понедельник
        monday = True
        tomorrow = 0
        even_week = not even_week

    if tomorrow != 6: # Если завтра не воскресенье
        msg += bold("Вот твоё расписание на завтра:" if not monday else "Вот твоё расписание на понедельник:") + "\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=tomorrow + 1, even_week=even_week, group=group)
        if len(pairs) != 0:
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
                # msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                #        str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + code(
                    str(pair[7]) + ("" if pair[8] == "" else " в ауд. ") + str(pair[8])) + "\n\n"
        else:
            msg += bold("Завтра выходной, хоть и не воскресенье" if not monday else "В понедельник нет пар (выходной)")
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

    if tomorrow == 6: # Если завтра воскресенье, то перейдём на понедельник
        monday = True
        tomorrow = 0
        even_week = not even_week

    if tomorrow != 6: # Если завтра не воскресенье
        group = psdb.r_user_group_is_set(tg_id=id)
        if not group:
            return "У тебя не задана группа\nИсправить это можно командой 'группа <название группы>'\n" \
                   "Проверяется текущая группа командой 'группа' без аргументов (параметров)"
        msg += bold("Вот твоё расписание на завтра:" if not monday else "Вот твоё расписание на понедельник:") + "\n"
        pairs = psdb.r_get_pairs_by_tgid(day_of_week=tomorrow + 1, even_week=even_week, tg_id=id)
        if len(pairs) != 0:
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
                # msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                #        str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + code(
                    str(pair[7]) + ("" if pair[8] == "" else " в ауд. ") + str(pair[8])) + "\n\n"
        else:
            msg += bold("Завтра выходной, хоть и не воскресенье" if not monday else "В понедельник нет пар (выходной)")
    return msg


def get_week(group, even_week):
    msg = ""
    days_of_week = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for i in range(1, 7):
        msg += bold(days_of_week[i]) + "\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=i, even_week=even_week, group=group)
        if len(pairs) != 0:
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
                # msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                #        str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + code(
                    str(pair[7]) + ("" if pair[8] == "" else " в ауд. ") + str(pair[8])) + "\n\n"
        else:
            msg += "Нет пар"
        msg += "\n\n"
    return msg


def get_help():
    return "Итак, в этом боте ты можешь узнать расписание на сегодня, " \
           "на завтра, на неделю, на 2 недели (полное расписание)\n" \
           "Тут есть следующие команды (их перечень будет расширяться):\n" \
           "    " + bold("1. пары [<название группы>]") + " — получить инфу о парах на сегодня или на завтра в зависимости от текущего времени (не злоупотребляй)\n" \
           "    " + bold("2. сегодня [<название группы>]") + " — получить инфу о парах на сегодня (и пофиг, если ты это делаешь вечером)\n" \
           "    " + bold("3. завтра [<название группы>]") + " — получить инфу о парах на следующий учебный день (отличный варик для запроса вечером)\n" \
           "    " + bold("4. чёт") + " — получить инфу о парах на чётную неделю (только если задана группа)\n" \
           "    " + bold("5. нечёт") + " — получить инфу о парах на нечётную неделю (только если задана группа)\n" \
           "    " + bold("6. всё") + " — получить инфу о парах на обе недели (только если задана группа)\n" \
           "    " + bold("7. группа [<название группы>]") + " или " + bold("группа нет") + " — так можно задать, проверить или удалить свою группу, чтобы не указывать её при запросе\n" \
           "    " + bold("8. помощь") + " — ты только что это и сделал, о возможностях этой команды уже знаешь)\n"


@dp.message_handler()
async def echo(message: types.Message):
    # Кинем сообщения в логи
    # print("")
    # print("[" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "]")
    # print("ID".ljust(len(str(message.from_user.id)), " ") + " - " + "username".ljust(len(str(message.from_user.username)), " ") + \
    #       " - " + "name".ljust(len(str(message.from_user.first_name)), " ") + ":")
    # print(str(message.from_user.id).ljust(2, " ") + " - " + str(message.from_user.username).ljust(8, " ") + " - " + str(message.from_user.first_name).ljust(4, " "))
    # print("Message: " + str(message.text))
    print("-"*40)
    print("[" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "] " + \
          str(message.from_user.first_name) + " (" + str(message.from_user.id) + " / " + \
          str(message.from_user.username) + ") написал: " + str(message.text))

    if message.from_user.id in ban_list: # Отсеяли забаненых
        await message.answer("Доступ временно закрыт (403)")
    else:
        # Текст в начале сообщения
        msg = "Я составляю ответ на основе содержимого своей базы данных\n" + \
              "Так что расписание может быть неактуальным\n" \
              "В любом случае, ты можешь предупредить администратора о несостыковках\n" \
              "Почта: vk2920@yandex.ru\n" \
              "ТГ: @vkw2920    VK: " + link('@vk_2920', 'https://vk.com/im?sel=219099321') + "\n\n"

        if DEBUG_MODE:
            msg += "Бот находится в режиме отладки (поэтапное выполнение алгоритмов с целью поиска ошибок)\n" \
                   "Это значит, что ответа может не быть (или он будет не сразу)\n\n"
        try:
            cmd = message.text.lower().replace(",", "").split(" ")
            if cmd[0] in ["пары", "gfhs", "pairs", "зфшкы"]:
                # Тут будет "интуитивное" определение требования пользователя
                # Либо это будут пары на сегодня
                # Либо это будут пары на завтра (следующий учебный день)
                msg += get_pairs(message)

            elif cmd[0] in ["сегодня", "ctujlyz"]:
                if datetime.datetime.today().weekday() == 6:
                    await message.answer("Ты долбаёб, сегодня воскресенье")
                    return 0

                if len(cmd) == 2 and is_group(cmd[1]):
                    msg += get_today(cmd[1])
                else:
                    msg += get_today_by_id(message.from_user.id)

            elif cmd[0] in ["завтра", "pfdnhf"]:
                if len(cmd) == 2 and is_group(cmd[1]):
                    msg += get_next_day(cmd[1])
                else:
                    msg += get_next_day_by_id(message.from_user.id)

            elif cmd[0] in ["группа", "uheggf"]:
                if len(cmd) != 1:
                    if cmd[1] in ["нет", "ytn", "очистить", "jxbcnbnm"]:
                        psdb.w_remove_user_group(message.from_user.id)
                    else:
                        if psdb.w_register_user_by_tgid(message.from_user.id, message.from_user.first_name, cmd[1]):
                            msg += "Ваша группа задана (или изменена)"
                        else:
                            msg += "Ошибка записи в БД, твоя группа не сохранена"
                else:
                    await message.answer('Напиши свою группу', parse_mode=types.ParseMode.MARKDOWN, reply_markup=group_update_keyboard)
                    await DataInput.r.set()
                    return 0

            elif cmd[0] in ["всё", "все", "dct", "dc`"]:
                group = psdb.r_user_group_is_set(message.from_user.id)
                if group:
                    msg += "Расписание на нечётную неделю:\n"
                    msg += get_week(group=group, even_week=False)
                    msg += "Расписание на чётную неделю:\n"
                    msg += get_week(group=group, even_week=True)
                else:
                    msg += "Группа не сохранена, поэтому ничем помочь не могу\n" \
                           "P.S.: Трюк 'неделя ис/б-21-3-о' не работает"

            elif cmd[0] in ["чёт", "x`n", "чет", "xtn"]:
                group = psdb.r_user_group_is_set(message.from_user.id)
                if group:
                    # msg += "Расписание на нечётную неделю:\n"
                    # msg += get_week(group=group, even_week=False)
                    msg += "Расписание на чётную неделю:\n"
                    msg += get_week(group=group, even_week=True)
                else:
                    msg += "Группа не сохранена, поэтому ничем помочь не могу\n" \
                           "P.S.: Трюк 'неделя ис/б-21-3-о' не работает"

            elif cmd[0] in ["нечёт", "ytx`n", "нечет", "ytxtn"]:
                group = psdb.r_user_group_is_set(message.from_user.id)
                if group:
                    msg += "Расписание на нечётную неделю:\n"
                    msg += get_week(group=group, even_week=False)
                    # msg += "Расписание на чётную неделю:\n"
                    # msg += get_week(group=group, even_week=True)
                else:
                    msg += "Группа не сохранена, поэтому ничем помочь не могу\n" \
                           "P.S.: Трюк 'неделя ис/б-21-3-о' не работает"

            elif cmd[0] in ["помощь", "help", "хелп", "хэлп", "рудз", "gjvjom"]:
                msg += get_help()

            else:
                msg += "Команда не распознана, я без понятия, что ты хочешь\n" + \
                    "Введи \"help\", чтобы узнать о моих возможностях"

        except Exception as _ex:
            print(" [" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "]")
            print(_ex)
            await message.answer("В работе бота произошла ошибка (по-любобу косяк разраба)\n" \
                                 "Это может быть связано с тем, что бот находится в режиме улучшения\n" \
                                 "Это когда разработчик добавляет или улучшает какой-то функционал бота\n" \
                                 "Текущие дата и время на сервере для поиска в логах: " + \
                                 str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")))
            return 1

        # Ассинхронный ответ на сообщение пользователя
        try:
            await message.answer(msg.replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN, reply_markup=bot_keyboard)
        except:
            msg = "На стороне сервера сработало исключение (Error 500)\n" \
                  "Методом \"научного тыка\" было определено, что это чаще всего связано с форматированием текста " \
                  "(которого нет)\n\n" + msg
            await message.answer(msg, reply_markup=bot_keyboard)


@dp.message_handler(state=DataInput.r)
async def radius(message: types.Message, state: FSMContext):
    group = message.text.lower()
    if is_group(group=group):
        psdb.w_register_user_by_tgid(message.from_user.id, message.from_user.first_name, group)
        await message.answer("Твоя группа задана".replace('\\', ''), reply_markup=bot_keyboard, parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    elif group in ["нет", "ytn", "очистить", "jxbcnbnm"]:
        psdb.w_remove_user_group(message.from_user.id)
        await message.answer("Твоя группа удалена из БД".replace('\\', ''), reply_markup=bot_keyboard, parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    elif group in ["посмотреть", "gjcvjnhtnm"]:
        group = psdb.r_user_group_is_set(message.from_user.id)
        if group:
            group = group.split("/")
            group = group[0].upper() + "/" + group[1]
            await message.answer(str("Вот твоя группа: " + bold(str(group))).replace('\\', ''), reply_markup=bot_keyboard, parse_mode=types.ParseMode.MARKDOWN)
        else:
            await message.answer("У тебя не задана группа", reply_markup=bot_keyboard)
        await state.finish()
    elif group in ["отмена", "jnvtyf"]:
        await message.answer("Смена группы отменена".replace('\\', ''), reply_markup=bot_keyboard, parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    else:
        await message.answer(bold("ВВЕДИ СВОЮ ГРУППУ").replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


def tgbot_start(db):
    database = db
    executor.start_polling(dp, skip_updates=True)