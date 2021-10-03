import datetime
import logging

import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import bold, italic, code, link
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import *
from functions import *

import os


class DataInput(StatesGroup):
    group = State()  # Состояние для проверки или изменения группы
    day_of_week = State()  # Состояние для получения расписания на конкретный учебный день

    admin_main = State()

    admin_add_pair_enter_group = State()
    admin_add_pair_enter_day = State()
    admin_add_pair_enter_ordinal = State()
    admin_add_pair_delete_exists_question = State()
    admin_add_pair_enter_type = State()
    admin_add_pair_enter_location = State()
    admin_add_pair_enter_lesson = State()
    admin_add_pair_enter_teacher = State()
    admin_add_pair_confirm = State()

    admin_remove_pair_enter_group = State()
    admin_remove_pair_enter_day = State()
    admin_remove_pair_enter_pair_id = State()
    admin_remove_pair_confirm = State()


database = None
# API_TOKEN = '1941221231:AAEVvHJUmnIOl6RzcX6lUj5oossETD6I4RU'
API_TOKEN = os.environ['BOT_TOKEN']

ban_list = []
admin_list = [470985286, 1943247578]
admin_list_active = []
admin = {}
days_of_week_list = ["ВС", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
days_of_week = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
bot_version = "20210921-1800"
DEBUG_MODE = False

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler()
async def standard_msg(message: types.Message):
    """
    Основной хэндлер для всех принимаемых сообщений, кроме сообщений при активных состояниях
    :param message:
    :return: Код ошибки или 0, если ошибок нет
    """
    # Кинем сообщения в логи
    print("[" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "] " +
          str(message.from_user.first_name) + " (" + str(message.from_user.id) + " / " +
          str(message.from_user.username) + ") написал: " + str(message.text))

    if message.text.lower() in ["admin", "фвьшт", "админ", "flvby"] and message.from_user.id in admin_list:
        if len(admin_list_active) != 0:
            await message.answer("Панель администрирования заблокирована, попробуй позже")
            return 0
        else:
            admin_list_active.append(message.from_user.id)
            print("Администратор зашёл в панель управления.")
            print("Список активных администраторов:")
            for admin in admin_list_active:
                print("    — " + str(admin))

            await DataInput.admin_main.set()
            await message.answer("Панель администрирования, выбери действие", reply_markup=admin_panel)
            return 0

    keyboard = admin_keyboard if message.from_user.id in admin_list else bot_keyboard

    if message.from_user.id in ban_list:  # Отсеяли забаненых
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
                    await message.answer("Я не знаю университетов с учёбой по воскресеньям")
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
                            msg += "Твоя группа задана (или изменена)"
                        else:
                            msg += "Ошибка записи в БД, твоя группа не сохранена"
                else:
                    await message.answer('Напиши свою группу', parse_mode=types.ParseMode.MARKDOWN,
                                         reply_markup=group_update_keyboard)
                    await DataInput.group.set()
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

            elif cmd[0] in ["конкретный_день", "rjyrhtnysq_ltym"]:
                await message.answer("Выбери нужный день недели", reply_markup=day_of_week_keyboard)
                await DataInput.day_of_week.set()
                return 0

            elif cmd[0] in ["помощь", "help", "хелп", "хэлп", "рудз", "gjvjom"]:
                msg += get_help()

            else:
                msg += "Команда не распознана, я без понятия, что ты хочешь\n" + \
                    "Введи \"help\", чтобы узнать о моих возможностях"

        except Exception as _ex:
            print(" [" + str(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H.%M.%S")) + "]")
            print(_ex)
            await message.answer("В работе бота произошла ошибка (по-любобу косяк разраба)\n"
                                 "Это может быть связано с тем, что бот находится в режиме улучшения\n"
                                 "Это когда разработчик добавляет или улучшает какой-то функционал бота\n"
                                 "Текущие дата и время на сервере для поиска в логах: " +
                                 str(datetime.datetime.now(pytz.timezone('Europe/Moscow'))
                                     .strftime("%Y-%m-%d %H.%M.%S")))
            return 1

        # Ассинхронный ответ на сообщение пользователя
        try:
            await message.answer(msg.replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        except:
            msg = "На стороне сервера сработало исключение (Error 500)\n" \
                  "Методом \"научного тыка\" было определено, что это чаще всего связано с форматированием текста " \
                  "(которого нет)\n\n" + msg
            await message.answer(msg, reply_markup=keyboard)


@dp.message_handler(state=DataInput.admin_main)  # Админка, главное меню
async def admin_msg(message: types.Message, state: FSMContext):
    print("Админка вызвана")
    cmd = message.text.lower()
    if cmd in ["выход", "учше", "ds[jl", "exit"]:
        await message.answer("Окей, выходим из админки)", reply_markup=bot_keyboard)
        await state.finish()
        del admin_list_active[0]
        print("Пользователь вышел из админки")
        return 0

    elif cmd in ["add pair", "lj,fdbnm gfhe", "фвв зфшк", "добавить пару"]:
        await state.finish()
        await message.answer("Выбери группу, для которой нужно добавить пару", reply_markup=select_group_keyboard)
        await DataInput.admin_add_pair_enter_group.set()
        print("Пользователь хочет добавить пару")
        return 0

    elif cmd in ["remove pair", "elfkbnm gfhe", "куьщму зфшк", "удалить пару", "e,hfnm gfhe", "убрать пару"]:
        await state.finish()
        await message.answer("Выбери группу, для которой нужно удалить пару", reply_markup=select_group_keyboard)
        await DataInput.admin_remove_pair_enter_group.set()
        print("Пользователь хочет удалить пару")
        return 0


@dp.message_handler(state=DataInput.admin_remove_pair_enter_group)  # Выбор группы при удалении пары
async def admin_remove_pair_enter_group_msg(message: types.Message, state: FSMContext):
    print("Состояние переключено на ввод группы для удаления пары")
    group = message.text.lower()
    if message.text.lower() in ["ds[jl", "exit", "выход", "учше"]:
        await message.answer("Ковальски, отмена!", reply_markup=admin_keyboard)
        await state.finish()
        await DataInput.admin_main.set()
        return 0

    if is_group(group):
        async with state.proxy() as data:
            data['selected_group'] = group

        await message.answer("Окей, группа получена, теперь выбери учебный день", reply_markup=day_of_week_keyboard)
        await DataInput.next()
        return 0
    else:
        await message.answer("И чё это за дичь?\nКто тебя учил писать название группы?")


@dp.message_handler(state=DataInput.admin_remove_pair_enter_day)  # Выбор дня при удалении пары
async def admin_remove_pair_enter_day_msg(message: types.Message, state: FSMContext):
    print("Состояние переключено на ввод учебного дня для удаления пары")
    if message.text.lower() in ["ds[jl", "exit", "выход", "учше"]:
        await message.answer("Ковальски, отмена!", reply_markup=admin_keyboard)
        await state.finish()
        await DataInput.admin_main.set()
        return 0

    day = message.text.lower().split(" ")
    dof = days_of_week_list.index(day[0].upper())
    if day[1] in ["чёт", "x`n", "чет", "xtn"]:
        even_week = True
    elif day[1] in ["нечёт", "ytx`n", "нечет", "ytxtn"]:
        even_week = False
    else:
        await message.answer("Где-то ошибка, воспользуйся клавиатурой", reply_markup=day_of_week_keyboard)
        return 0

    async with state.proxy() as data:
        group = data['selected_group']

    group_str = str(group).split("/")
    group_str = group_str[0].upper() + "/" + group_str[1]

    msg = bold("Вот список пар у выбранной группы (" + group_str + ") в выбранный день (" + days_of_week[dof] + " " +
               ("чётной недели" if even_week else "нечётной недели") + "):") + "\n\n"
    select_pair_id_keyboard = ReplyKeyboardMarkup()

    pairs = psdb.r_get_pairs_by_group(day_of_week=dof, even_week=even_week, group=group)
    for pair in pairs:
        select_pair_id_keyboard.add(KeyboardButton(str(pair[0])))

    msg += print_pairs(pairs=pairs, day_of_week=dof, even_week=even_week, with_id=True)

    await message.answer(msg.replace("\\", ""), reply_markup=select_pair_id_keyboard,
                         parse_mode=types.ParseMode.MARKDOWN)
    await DataInput.next()


@dp.message_handler(state=DataInput.admin_remove_pair_enter_pair_id)  # Выбор пары для удаления
async def admin_remove_pair_enter_pair_id_msg(message: types.Message, state: FSMContext):
    print("Состояние переключено на выбор пары для удаления")
    if message.text.lower() in ["ds[jl", "exit", "выход", "учше"]:
        await message.answer("Ковальски, отмена!", reply_markup=admin_keyboard)
        await state.finish()
        await DataInput.admin_main.set()
        return 0

    try:
        id = int(message.text.lower())
        async with state.proxy() as data:
            data['pair_id'] = id

        await DataInput.next()
        await message.answer("Выбрана пара для удаления\nТы уверен, что хочешь её удалить из таблицы?",
                             reply_markup=confirm_keyboard)
    except:
        await message.answer("У тебя появилась клавиатура, просто выбери ID пары для удаления")


@dp.message_handler(state=DataInput.admin_remove_pair_confirm)  # Подтверждение удаления
async def admin_remove_pair_confirm_msg(message: types.Message, state: FSMContext):
    print("Состояние переключено на подтверждение удаления пары")
    if message.text.lower() in ["ds[jl", "exit", "выход", "учше", "jnvtyf", "cancel", "отмена", "сфтсуд"]:
        await message.answer("Ковальски, отмена!", reply_markup=admin_keyboard)
        await state.finish()
        await DataInput.admin_main.set()
        return 0
    elif message.text.lower() in ["yes", "lf", "да", "нуы"]:
        async with state.proxy() as data:
            id = data['pair_id']
        psdb.w_remove_pair_by_pair_id(pair_id=int(id))
        print(f"Пара {id} удалена")
        await message.answer("Выбранная пара удалена", reply_markup=admin_keyboard)
        await state.finish()
        await DataInput.admin_main.set()
        return 0
    else:
        await message.answer("Используй клавиатуру, я не понимаю других команд")
        return 0


@dp.message_handler(state=DataInput.group)
async def group_msg(message: types.Message, state: FSMContext):
    group = message.text.lower()
    keyboard = admin_keyboard if message.from_user.id in admin_list else bot_keyboard

    if is_group(group=group):
        psdb.w_register_user_by_tgid(message.from_user.id, message.from_user.first_name, group)
        await message.answer("Твоя группа задана".replace('\\', ''), reply_markup=keyboard,
                             parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    elif group in ["нет", "ytn", "очистить", "jxbcnbnm"]:
        psdb.w_remove_user_group(message.from_user.id)
        await message.answer("Твоя группа удалена из БД".replace('\\', ''), reply_markup=keyboard,
                             parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    elif group in ["посмотреть", "gjcvjnhtnm"]:
        group = psdb.r_user_group_is_set(message.from_user.id)
        if group:
            group = group.split("/")
            group = group[0].upper() + "/" + group[1]
            await message.answer(str("Вот твоя группа: " + bold(str(group))).replace('\\', ''),
                                 reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN)
        else:
            await message.answer("У тебя не задана группа", reply_markup=keyboard)
        await state.finish()
    elif group in ["отмена", "jnvtyf"]:
        await message.answer("Смена группы отменена".replace('\\', ''), reply_markup=keyboard,
                             parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    else:
        await message.answer(bold("ВВЕДИ СВОЮ ГРУППУ").replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(state=DataInput.day_of_week)
async def day_of_week_msg(message: types.Message, state: FSMContext):
    day = message.text.lower().split(" ")
    if len(day) != 2:
        if day[0] in ["вернуться", "dthyenmcz"]:
            await message.answer("Возвращаемя)", reply_markup=bot_keyboard)
            await state.finish()
            return 0

        await message.answer("Введено что-то неправильное, можешь воспользоваться клавиатурой бота)",
                             reply_markup=day_of_week_keyboard)
        return 0

    if day[1] in ["чёт", "x`n", "чет", "xtn"]:
        even_week = True
    elif day[1] in ["нечёт", "ytx`n", "нечет", "ytxtn"]:
        even_week = False
    else:
        await message.answer("Ошибка в чётности недели, можешь воспользоваться клавиатурой бота)",
                             reply_markup=day_of_week_keyboard)
        return 0

    if day[0].upper() in days_of_week_list:
        day_of_week = days_of_week_list.index(day[0].upper())
    else:
        await message.answer("Ошибка в дне недели, можешь воспользоваться клавиатурой бота)",
                             reply_markup=day_of_week_keyboard)
        return 0

    msg = ""
    if day_of_week not in [0, 7]:
        group = psdb.r_user_group_is_set(message.from_user.id)
        if not group:
            await message.answer("У тебя не установлена группа, исправить это можно кнопкой \"Группа\"",
                                 reply_markup=(admin_keyboard if message.from_user.id in admin_list else bot_keyboard))
            await state.finish()
            return 0

        pairs = psdb.r_get_pairs_by_group(day_of_week=day_of_week, even_week=even_week, group=group)
        if len(pairs) != 0:
           msg += print_pairs(pairs, day_of_week, even_week)
        else:
            msg += bold("В выбранный день (" + days_of_week[day_of_week] + ") на заводе работать не планируется") + "\n"

        # Ассинхронный ответ на сообщение пользователя
        try:
            await message.answer(msg.replace('\\', ''), parse_mode=types.ParseMode.MARKDOWN,
                                 reply_markup=(admin_keyboard if message.from_user.id in admin_list else bot_keyboard))
            await state.finish()
        except:
            msg = "На стороне сервера сработало исключение (Error 500)\n" \
                  "Методом \"научного тыка\" было определено, что это чаще всего связано с форматированием текста " \
                  "(которого нет)\n\n" + msg
            await message.answer(msg, reply_markup=(admin_keyboard if message.from_user.id in admin_list else bot_keyboard))
            await state.finish()


if __name__ == '__main__':
    print(DataInput.admin_main)
    executor.start_polling(dp, skip_updates=True)
