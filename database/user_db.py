import sqlite3
from utils.logger import logger


class UserDatabase:
    def __init__(self, db_file: str):
        """
        Инициализация базы данных пользователя
        """
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.set_up_db()

    def set_up_db(self) -> None:
        """
        Создание таблицы User в базе данных, если она не существует
        """
        logger.info('Setting up the database')
        with self.connection:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS User(
            userId INT PRIMARY KEY,
            fname TEXT,
            lname TEXT,
            age INT NOT NULL DEFAULT 1)
            ''')

    def check_user(self, user_id: int) -> bool:
        """
        Проверка наличия пользователя в базе данных
        """
        logger.info('Checking user')
        with self.connection:
            result = self.cursor.execute('SELECT `userId` FROM User WHERE `userId` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id: int) -> None:
        """
        Добавление пользователя в базу данных
        """
        logger.info('Adding user')
        with self.connection:
            self.cursor.execute('INSERT INTO User(UserId) VALUES (?)', (user_id,))

    def fill_db(self, data: dict) -> None:
        """
        Запись информации о пользователе из State_handlers в базу данных
        """
        logger.info('Filling database')
        with self.connection:
            self.cursor.execute('UPDATE User SET fname=?,lname=?,age=? WHERE userId=?',
                                (data['name'], data['surname'], data['age'], data['id']))
