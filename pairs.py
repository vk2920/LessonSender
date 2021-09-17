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
        cursor = self._connection.cursor()
        pairs_list = []
        for row in cursor.execute(f"""SELECT * FROM "public".pairs WHERE 
                group_name = '{group}' AND even_week = '{even_week}' AND 
                day_of_week = '{day_of_week}' ORDER BY ordinal"""):
            pairs_list.append(row)
        del cursor
        return pairs_list

    def r_get_pairs_by_tgid(self, day_of_week: int, even_week: bool, tg_id: int):
        """
        :param day_of_week: порядковый номер дня недели (int, 1~6)
        :param even_week: True, если неделя чётная, иначе False
        :param tg_id: id пользователя в ТГ (int)
        :return: список пар на запрошенный день
        """
        cursor = self._connection.cursor()
        group = list(cursor.execute(f"""SELECT group_name FROM "public".users WHERE tg_id = {tg_id} LIMIT 1"""))[0][0]
        del cursor
        return self.r_get_pairs_by_group(day_of_week, even_week, group)

    def w_register_user_by_tgid(self, tg_id: int, name: str, group: str):
        """
        :param tg_id: id пользователя в ТГ (int)
        :param name: ФИО пользователя
        :param group: группа пользователя в формате
        :return: True, если запись произведена успешно, иначе False
        """
        cursor = self._connection.cursor()
        res = cursor.execute(f"""INSERT INTO "public".users (`tg_id`, `name`, `group`) VALUES ({tg_id}, '{name}', '{group}')""")
        del cursor
        if res and self._connection.commit():
            return True
        return False

if __name__ == "__main__":
    psdb = PSDB()
    pairs = psdb.r_get_pairs_by_group(day_of_week=1, even_week=True, group="ис/б-21-3-о")
    for pair in pairs:
        print(pair)