from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


bot_keyboard = ReplyKeyboardMarkup()
bot_keyboard.row(KeyboardButton("Конкретный_день"), KeyboardButton("Пары"))
bot_keyboard.row(KeyboardButton("Сегодня"), (KeyboardButton("Завтра")))
bot_keyboard.row(KeyboardButton("Чёт"), KeyboardButton("Всё"), (KeyboardButton("Нечёт")))
bot_keyboard.row(KeyboardButton("Группа"), KeyboardButton("Помощь"))

admin_keyboard = ReplyKeyboardMarkup()
admin_keyboard.row(KeyboardButton("Конкретный_день"), KeyboardButton("Пары"))
admin_keyboard.row(KeyboardButton("Сегодня"), (KeyboardButton("Завтра")))
admin_keyboard.row(KeyboardButton("Чёт"), KeyboardButton("Всё"), (KeyboardButton("Нечёт")))
admin_keyboard.row(KeyboardButton("Группа"), KeyboardButton("Админ"), KeyboardButton("Помощь"))

admin_panel = ReplyKeyboardMarkup()
admin_panel.row(KeyboardButton("Добавить пару (NO)"), KeyboardButton("Убрать пару"))
admin_panel.row(KeyboardButton("Перенести пару (NO)"))
admin_panel.row(KeyboardButton("Выйти"))

group_update_keyboard = ReplyKeyboardMarkup()
group_update_keyboard.row(KeyboardButton("Посмотреть"), KeyboardButton("Очистить"))
group_update_keyboard.add(KeyboardButton("Отмена"))

day_of_week_keyboard = ReplyKeyboardMarkup()
day_of_week_keyboard.row(KeyboardButton("ПН Нечёт"), KeyboardButton("ВТ Нечёт"), KeyboardButton("СР Нечёт"))
day_of_week_keyboard.row(KeyboardButton("ЧТ Нечёт"), KeyboardButton("ПТ Нечёт"), KeyboardButton("СБ Нечёт"))
day_of_week_keyboard.row(KeyboardButton("ПН Чёт"), KeyboardButton("ВТ Чёт"), KeyboardButton("СР Чёт"))
day_of_week_keyboard.row(KeyboardButton("ЧТ Чёт"), KeyboardButton("ПТ Чёт"), KeyboardButton("СБ Чёт"))

select_group_keyboard = ReplyKeyboardMarkup()
select_group_keyboard.row(KeyboardButton("ИС/б-19-2-о"), KeyboardButton("ИС/б-21-3-о"))
select_group_keyboard.add(KeyboardButton("Выход"))

confirm_keyboard = ReplyKeyboardMarkup()
confirm_keyboard.row(KeyboardButton("Да"))
confirm_keyboard.add(KeyboardButton("Отмена"))
confirm_keyboard.add(KeyboardButton("Выход"))