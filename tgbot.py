import datetime
import logging

import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, bold, italic, code, underline, strikethrough, link

from pairs import PSDB

database = None
API_TOKEN = '1941221231:AAEVvHJUmnIOl6RzcX6lUj5oossETD6I4RU'

ban_list = []

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
psdb = PSDB()

def get_pairs(message, group):
    # Запись в логах лишней не будет
    print("[" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "] " + \
          str(message.from_user.id) + " - " + str(message.from_user.username) + " - " + \
          str(message.from_user.first_name) + ": " + str(message.text))

    # Определим чётность недели и номера нужных дней недели
    even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
    today = datetime.datetime.today().weekday()
    tomorrow = today+1 if today != 6 else 0
    cmd = message.text.lower().replace(",", "").split(" ")

    # Текст в начале сообщения
    msg ="Я составляю ответ на основе содержимого своей базы данных\n" + \
          "Так что расписание может быть неактуальным\n" \
          "В любом случае, ты можешь предупредить администратора о несостыковках\n" \
          "Почта: " + link('vk2920@yandex.ru', 'mailto:vk2920@yandex.ru') + "\n" \
          "ТГ: @vk2920    VK: " + link('@vk_2920', 'https://vk.com/im?sel=219099321') + "\n\n"

    # Добавим к ответу бота расписание на сегодня
    msg += get_today(message, group=(cmd[1] if len(cmd) != 1 else "ис/б-21-3-о"))

    # Добавим в сообщение расписание на завтра
    msg += get_next_day(message, group=(cmd[1] if len(cmd) != 1 else "ис/б-21-3-о"))

    return msg

def get_today(message, group):
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

                if pair[8] == "":
                    pair[8] = "аудитория не определена"

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

def get_next_day(message, group):
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
    return msg

def get_help(message):
    return "Итак, в этом боте ты можешь узнать расписание на сегодня, " \
           "на завтра, на неделю, на 2 недели (полное расписание)\n" \
           "Тут есть следующие команды (их перечень будет расширяться):\n" \
           "    пары — получить инфу о парах на сегодня или на завтра в зависимости от текущего времени (не злоупотребляй)\n" \
           "    сегодня — получить инфу о парах на сегодня (и пофиг, если ты это делаешь вечером)\n" \
           "    завтра — получить инфу о парах на следующий учебный день (отличный варик для запроса вечером)\n" \
           "    группа — так можно задать свою группу, чтобы не указывать её при запросе\n" \
           "    помощь — ты только что это и сделал, о возможностях этой команды уже знаешь)\n"

@dp.message_handler()
async def echo(message: types.Message):
    print("Работает версия от 20210915-1925")
    if message.from_user.id in ban_list: # Отсеяли забаненых
        print("[" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "] " + \
              str(message.from_user.id) + " - " + str(message.from_user.username) + " - " + \
              str(message.from_user.first_name) + ": " + str(message.text))
        await message.answer("Доступ временно закрыт (кто-то там разраба оскорблял?)")
    else:
        cmd = message.text.lower().replace(",", "").split(" ")
        if cmd[0] == "пары":
            # Тут будет "интуитивное" определение требования пользователя
            # Либо это будут пары на сегодня
            # Либо это будут пары на завтра (следующий учебный день)
            msg = get_pairs(message, group=(cmd[1] if len(cmd) != 1 else "ис/б-21-3-о"))
        elif cmd[0] == "сегодня":
            msg = get_today(message, group=(cmd[1] if len(cmd) != 1 else "ис/б-21-3-о"))
        elif cmd[0] == "завтра":
            msg = get_next_day(message, group=(cmd[1] if len(cmd) != 1 else "ис/б-21-3-о"))
        elif cmd[0] == "группа":
            if len(cmd) != 1:
                if psdb.w_register_user_by_tgid(message.from_user.id, message.from_user.first_name, message.text.split(" ")[1]):
                    msg = "Ваша группа задана (или изменена)"
                else:
                    msg = "Ошибка записи в БД, твоя группа не сохранена"
            else:
                msg = "Не хочешь ли ты указать свою группу?\n" + \
                    "Повтори предыдущую команду, исправив свои ошибки\n" + \
                    "Не допусти опечаток в названии группы, иначе х*й тебе, а не расписание\n" + \
                    "Если чё, пиши в таком виде: ИС/б-21-3-о"
        elif cmd[0] in ["помощь", "help", "хелп", "хэлп"]:
            msg = get_help()
        else:
            msg = "Команда не распознана, я без понятия, что ты хочешь\n" + \
                "Введи \"help\", чтобы узнать о моих возможностях"

        # Ассинхронный ответ на сообщение пользователя
        await message.answer(msg.replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


def tgbot_start(db):
    database = db
    executor.start_polling(dp, skip_updates=True)