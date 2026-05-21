import sqlite3
from datetime import date, timedelta
import os

class DatabaseHandler:
    def __init__(self):
        """Подключение к SQLite"""
     
        self.db_path = 'mood_tracker.db'
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        print(f"✅ Подключено к SQLite: {self.db_path}")
    
    def _create_tables(self):
        """Создание таблиц по схеме из schema.sql"""
        cursor = self.conn.cursor()
     
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
     
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 5),
                productive_hours REAL CHECK (productive_hours >= 0 AND productive_hours <= 24),
                sleep_hours REAL CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, entry_date)
            )
        ''')
        
        self.conn.commit()
        print("✅ Таблицы созданы/проверены")
    
    def register_user(self, user_id, username, first_name, last_name):
        """Регистрация пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def save_entry(self, user_id, entry_date, mood_score, productive_hours, sleep_hours, comment=None):
        """Сохранение записи"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO mood_entries (user_id, entry_date, mood_score, productive_hours, sleep_hours, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, entry_date) DO UPDATE SET
                mood_score = excluded.mood_score,
                productive_hours = excluded.productive_hours,
                sleep_hours = excluded.sleep_hours,
                comment = excluded.comment,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, entry_date, mood_score, productive_hours, sleep_hours, comment))
        
        self.conn.commit()
        return True
    
    def get_today_entry(self, user_id):
        """Получить запись за сегодня"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM mood_entries 
            WHERE user_id = ? AND entry_date = ?
        ''', (user_id, date.today().isoformat()))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def has_entry_today(self, user_id):
        """Проверка, есть ли запись за сегодня"""
        return self.get_today_entry(user_id) is not None
    
    def get_entries_for_period(self, user_id, days=7):
        """Получить записи за последние N дней"""
        cursor = self.conn.cursor()
        start_date = (date.today() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT * FROM mood_entries 
            WHERE user_id = ? AND entry_date >= ?
            ORDER BY entry_date DESC
        ''', (user_id, start_date))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_entries(self, user_id):
        """Получить все записи пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM mood_entries 
            WHERE user_id = ?
            ORDER BY entry_date DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_all_entries(self, user_id):
        """Удалить все записи пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM mood_entries WHERE user_id = ?', (user_id,))
        self.conn.commit()
        return True
    
    def close(self):
        """Закрыть соединение"""
        self.conn.close()