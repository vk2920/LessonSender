# LessonSender
Бот для выдачи расписания в телеграме.

В данный момент работает со следующими группами (будет дополняться):
* ИС/б-21-3-о
* ИС/б-19-2-о

<hr>

### Внимание разработчиков
Нужны люди, способные написать парсер для XLS-файла для извлечения расписания на определённую группу.
Примеры исходных файлов Вы можете найти на <a href="https://www.sevsu.ru/univers/shedule">сайте Университета</a>.\
На выходе требуется получить список кортежей формата:\
```(id, group, even_week, day_of_week, ordinal, lesson, teacher, type, location)```, где:

* id **(int)** — порядковый номер, будет задаваться автоматически в зависимости от содержания таблицы в БД (в данный момент значения не имеет)
* group **(str)** — группа, для которой будет проходить пара (если групп несколько, отдельная запись для каждой группы)
* even_week **(bool)** — True, если неделя чётная, и False, если неделя нечётная
* day_of_week **(int)** — порядковый номер дня недели
  * 1 — Понедельник
  * 2 — Вторник
  * 3 — Среда
  * 4 — Четверг
  * 5 — Пятница
  * 6 — Суббота
* ordinal **(int)** — порядковый номер пары в течение дня (1 для пары с 8:30 до 10:00, 4 для пары с 14:00 до 15:30 и т. д.)
* lesson **(str)** — название дисциплины без сокращений
* teacher **(str)** — фамилия и инициалы преподавателя, например\
  ```'Карлусов В. Ю. / Заикина Е. Н.'```, если преподаватель не один
* type **(str)** — тип занятия в соответствии с форматом записи
  * Лекция
  * Практика
  * Лабораторная работа
* location **(str)** — номер аудитории, в которой будет проходить пара (строковой параметр, ибо в номерах большинства аудиторий главного кампуса используются буквы)

***Данный проект развивается исключительно на энтузиазме и никаким образом не финансируется.***\
Если Вам удалось решить проблему парсинга файла с расписанием, то прошу сообщить об этом администратору неофициального бота.

Электронная почта: <a href="mailto:vk2920@yandex.ru">vk2920@yandex.ru</a>\
Telegram: <a href="https://t.me/vkw2920">@vkw2920</a>\
VK: <a href="https://vk.com/vk_2920">@vk_2920</a>
