import sqlite3
import json
from utils.logger import logger

class UserHistoryDatabase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Создаем таблицу UserHistory в базе данных, если она не существует.
        """
        logger.info('Creating UserHistory table')
        with self.connection:
            return self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserHistory(
            userID INT,
            search_date datetime DEFAULT CURRENT_DATE,
            command TEXT,
            data json)
            ''')

    def set_data(self, user_id: int, command: str, data: dict) -> None:
        """
        Вставляем пользовательские данные, команду и словарь отеля в базу данных.
        """
        logger.info('Inserting data into UserHistory')
        with self.connection:
            return self.cursor.execute('''
            INSERT INTO UserHistory(`userID`,`command`,`data`)
            VALUES (?,?,?)''', (user_id, command, json.dumps(data)))

    def get_data(self, user_id: int, count: int):
        """
        Получаем историю пользователей из базы данных.
        """
        logger.info('Retrieving data from UserHistory')
        with self.connection:
            return self.cursor.execute('''
            SELECT `search_date`,`command`,`data` FROM UserHistory
            WHERE `userID` = ? LIMIT ?''', (user_id, count))

    def delete_data(self, user_id: int) -> None:
        """
        Удаляем историю пользователей из базы данных.
        """
        logger.info('Deleting data from UserHistory')
        with self.connection:
            return self.cursor.execute('''
            DELETE FROM UserHistory WHERE `userID` = ? ''', (user_id,))
