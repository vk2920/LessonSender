import psycopg2

# # Init DB
# if __name__ == "__main__":
#     connection = sqlite3.connect("pairs.db")
#     cursor = connection.cursor()
#     cursor.execute("""CREATE TABLE IF NOT EXISTS `users` (
#         `id` int,
#         `tg_id` int,
#         `vk_id` int,
#         `name` text,
#         `group` text);""")
#     cursor.execute("""CREATE TABLE IF NOT EXISTS `pairs` (
#         `id` int,
#         `group` text,
#         `even_week` bool,
#         `day_of_week` int,
#         `ordinal` int,
#         `lesson` text,
#         `teacher` text,
#         `type` int,
#         `location` text);""")
#     connection.commit()
#     del cursor
#     del connection
#     sys.exit()


class PSDB():
    """
    Этот класс предназначен для работы в базой данных SQLite3,
    в которой хранятся 2 таблицы: список пар (с привязкой к группе,
    дню недели и чётности недели) и список пользователей (3 идентификатора,
    ФИО и группа).
    Класс содержит следующие методы для работы с информацией в БД:
     -- __init__(self, [fname]) для создания объекта взаимодействия с БД
     -- r_get_pairs_by_group(self, day_of_week, even_week, group)
     -- r_get_pairs_by_tgid(self, day_of_week, even_week, tg_id)
     -- r_get_pairs_by_vkid(self, day_of_week, even_week, vk_id)
     -- w_register_user_by_tgid(self, tg_id, name, group)
     -- w_register_user_by_vkid(self, vk_id, name, group)
    """
    def __init__(self):
        try:
            self._connection = psycopg2.connect(
                host="ec2-34-228-154-153.compute-1.amazonaws.com",
                user="zdqtijbmodklfd",
                password="cad60afb471aeb2ef66fa20f0b1a122df9368faef38913f79e8a2c5560616209",
                database="dgrcd76bjnto5"
            )
        except Exception as _ex:
            print("[ERROR] Can't connect to PostgreSQL server", _ex)

    def __del__(self):
        if self._connection:
            self._connection.close()
            del self._connection
        print(" [INFO] Connection to PostgreSQL closed")

    def r_get_pairs_by_group(self, day_of_week: int, even_week: bool, group: str):
        """
        :param day_of_week: порядковый номер дня недели (int, 1~6)
        :param even_week: True, если неделя чётная, иначе False
        :param group: группа в формате "ИС/б-21-3-о", где
             -- ИС — направление подготовки
             -- б — бакалавриат (м — магистратура)
             -- 21 — год зачисления на первый курс
             -- 3 — номер потока
             -- о — очная форма обучения (з — заочная)
        :return: список пар на запрошенный день
        """
        pairs_list = []
        with self._connection.cursor() as cur:
            cur.execute(f"SELECT * FROM public.pairs WHERE " + \
                        f"group_name = '{group}' AND even_week = '{even_week}' AND " + \
                        f"day_of_week = '{day_of_week}' ORDER BY ordinal")
            for row in cur.fetchall():
                pairs_list.append(row)
        return pairs_list

    def r_get_pairs_by_tgid(self, day_of_week: int, even_week: bool, tg_id: int):
        """
        :param day_of_week: порядковый номер дня недели (int, 1~6)
        :param even_week: True, если неделя чётная, иначе False
        :param tg_id: id пользователя в ТГ (int)
        :return: список пар на запрошенный день
        """
        with self._connection.cursor() as cur:
            cur.execute(f"""SELECT group_name FROM public.users WHERE tg_id = {tg_id} LIMIT 1""")
            try:
                group = list(cur.fetchone())[0]
                return self.r_get_pairs_by_group(day_of_week=day_of_week, even_week=even_week, group=group)
            except:
                return []

    def r_get_exceptions_by_tgid(self, date: str, tg_id: int):
        """
        :param date: дата, неожиданные пары на которую нужно получить
        :param tg_id: id пользователя в ТГ (int)
        :return:
        """
        with self._connection.cursor() as cur:
            cur.execute(f"""SELECT group_name FROM public.users WHERE tg_id = {tg_id} LIMIT 1""")
            try:
                group = list(cur.fetchone())[0]
                return self.r_get_exceptions_by_group(date=date, group=group)
            except:
                return "Твоя группа не указана в БД"

    def r_get_exceptions_by_group(self, date: str, group: str):
        """
        :param date: дата, неожиданные пары на которую нужно получить
        :param group: группа, пары которой нужно получить
        :return: список кортежей с данными о парах, которых нет в расписании
        """
        pairs_list = []
        with self._connection.cursor() as cur:
            cur.execute(f"SELECT * FROM public.exceptions WHERE date = {date} AND group = '{group}' ORDER BY ordinal")
            for pair in cur.fetchall():
                pairs_list.append(pair)
        return pairs_list

    def w_register_user_by_tgid(self, tg_id: int, name: str, group: str):
        """
        :param tg_id: id пользователя в ТГ (int)
        :param name: ФИО пользователя
        :param group: группа пользователя в формате
        :return: True, если запись произведена успешно, иначе False
        """
        cursor = self._connection.cursor()
        res = cursor.execute(f"INSERT INTO public.users (tg_id, name, group_name) VALUES ({tg_id}, '{name}', '{group}');")
        # if res and self._connection.commit():
        if res and cursor.execute("COMMIT;"):
            return True
        return False


if __name__ == "__main__":
    psdb = PSDB()
    print(psdb.w_register_user_by_tgid(470985286, "Вадим", "ис/б-21-3-о"))
    # pairs = psdb.r_get_pairs_by_group(day_of_week=1, even_week=True, group="ис/б-21-3-о")
    # for pair in pairs:
    #     print(pair)