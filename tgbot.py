import datetime
import logging

import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, bold, italic, code, underline, strikethrough

from pairs import PSDB

database = None
API_TOKEN = '1941221231:AAEVvHJUmnIOl6RzcX6lUj5oossETD6I4RU'

ban_list = [1074303708,]

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
psdb = PSDB()

@dp.message_handler()
async def echo(message: types.Message):
    if message.from_user.id in ban_list: # Отсеяли забаненых
        print("[" + str(datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %H.%M.%S")) + "] " + \
              str(message.from_user.id) + " - " + str(message.from_user.username) + " - " + \
              str(message.from_user.first_name) + ": " + str(message.text))
        await message.answer("Доступ временно закрыт (кто-то там разраба оскорблял?)")
    else:
        # Запись в логах лишней не будет
        print("[" + str(datetime.datetime.today(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %H.%M.%S")) + "] " + \
              str(message.from_user.id) + " - " + str(message.from_user.username) + " - " + \
              str(message.from_user.first_name) + ": " + str(message.text))

        # Определим чётность недели и номера нужных дней недели
        even_week = int(datetime.date.today().strftime("%V")) % 2 == 0
        today = datetime.datetime.today().weekday()
        tomorrow = today+1 if today != 6 else 0

        # Текст в начале сообщения
        msg = """Сейчас для меня нет разницы, что ты написал.\n""" + \
              """Но я составляю ответ на основе содержимого своей базы данных\n""" + \
              """Здесь есть только расписание для группы создателей (ИС/б-21-3-о)\n\n"""

        # Добавим к ответу бота расписание на сегодня
        if today != 6: # Если сегодня не воскресенье
            msg += bold("Вот твоё расписание на сегодня:") + "\n"
            pairs = psdb.r_get_pairs_by_group(day_of_week=today+1, even_week=even_week, group="ИС/б-21-3-о")
            for pair in pairs:
                pair = list(pair)
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
                msg += str(pair[4]) + str(pair[5]) + "\n    " + italic(str(pair[6])) + "\n    " + code(str(pair[7]) + " в ауд. " + str(pair[8])) + "\n\n"

        # Добавим в сообщение расписание на завтра
        if tomorrow != 6: # Если завтра не воскресенье
            msg += bold("Вот твоё расписание на завтра:") + "\n"
            pairs = psdb.r_get_pairs_by_group(day_of_week=tomorrow + 1, even_week=even_week, group="ИС/б-21-3-о")
            for pair in pairs:
                pair = list(pair)
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
                    str(pair[7]) + " в ауд. " + str(pair[8])) + "\n\n"

        # Ассинхронный ответ на сообщение пользователя
        await message.answer(msg.replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


def tgbot_start(db):
    database = db
    executor.start_polling(dp, skip_updates=True)