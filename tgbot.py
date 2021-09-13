import datetime
import logging
import time

from aiogram import Bot, Dispatcher, executor, types

from pairs import PSDB

database = None
API_TOKEN = '1941221231:AAEVvHJUmnIOl6RzcX6lUj5oossETD6I4RU'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
psdb = PSDB()

@dp.message_handler()
async def echo(message: types.Message):
    today = datetime.datetime.today().weekday()
    tomorrow = today+1 if today != 6 else 0
    msg = "Сейчас для меня нет разницы, что ты написал.\nНо я составляю ответ на основе содержимого своей базы данных\n"
    if today != 6: # Если сегодня не воскресенье
        msg += "Вот твоё расписание на сегодня:\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=today+1, even_week=False, group="ИС/б-21-3-о")
        for pair in pairs:
            msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" + \
                   str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"

    if tomorrow != 6: # Если завтра не воскресенье
        msg += "Вот твоё расписание на завтра:\n"
        pairs = psdb.r_get_pairs_by_group(day_of_week=tomorrow+1, even_week=False, group="ИС/б-21-3-о")
        for pair in pairs:
            msg += str(pair[4]) + ". " + str(pair[5]) + " (преподаёт " + str(pair[6]) + ") (" +\
                   str(pair[7]) + " в аудитории " + str(pair[8]) + ")\n"

    await message.answer(msg)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


def tgbot_start(db):
    database = db
    executor.start_polling(dp, skip_updates=True)