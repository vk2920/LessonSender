import os

import psycopg2

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
            try:
                DB_HOST = os.environ["DB_HOST"]
                DB_USER = os.environ["DB_USER"]
                DB_PASSWD = os.environ["DB_PASSWD"]
                DB_NAME = os.environ["DB_NAME"]
            except:
                print("Fatal error: Can't connect to Database")

            self._connection = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME
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
            sql = f"SELECT * FROM public.pairs WHERE " + \
                  f"group_name = '{group}' AND even_week = {even_week} AND " + \
                  f"day_of_week = {day_of_week} ORDER BY ordinal"
            print("Получение списка пар по группе:")
            print(sql)
            cur.execute(sql)
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
            sql = f"""SELECT group_name FROM public.users WHERE tg_id = {tg_id} LIMIT 1"""
            print("Получение группы пользователя:")
            print(sql)
            cur.execute(sql)
            try:
                group = list(cur.fetchone())[0]
                pairs = self.r_get_pairs_by_group(day_of_week=day_of_week, even_week=even_week, group=group)
                return pairs
            except:
                try:
                    return []
                finally:
                    pass

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

    def r_user_group_is_set(self, tg_id: int):
        with self._connection.cursor() as cur:
            cur.execute(f"""SELECT group_name FROM public.users WHERE tg_id = {tg_id} LIMIT 1""")
            try:
                group = list(cur.fetchone())[0]
                return group
            except:
                return False

    def w_register_user_by_tgid(self, tg_id: int, name: str, group: str):
        """
        :param tg_id: id пользователя в ТГ (int)
        :param name: ФИО пользователя
        :param group: группа пользователя в формате
        :return: True, если запись произведена успешно, иначе False
        """
        cursor = self._connection.cursor()
        sql = f"SELECT tg_id FROM public.users WHERE tg_id = {tg_id}"
        print("Проверка на наличие пользователя:")
        print(sql)
        cursor.execute(sql)
        if len(list(cursor.fetchall())) != 0:
            sql = f"UPDATE public.users SET group_name = '{group}' WHERE tg_id = {tg_id}"
            print("Обновление группы существующего пользователя:")
            print(sql)
        else:
            sql = f"INSERT INTO public.users (tg_id, name, group_name) VALUES ({tg_id}, '{name}', '{group}');"
            print("Регистрация нового пользователя:")
            print(sql)
        cursor.execute(sql)
        self._connection.commit()
        return True


if __name__ == "__main__":
    psdb = PSDB()
    print(psdb.w_register_user_by_tgid(470985286, "Вадим", "ис/б-21-3-о"))
    # pairs = psdb.r_get_pairs_by_group(day_of_week=1, even_week=True, group="ис/б-21-3-о")
    # for pair in pairs:
    #     print(pair)