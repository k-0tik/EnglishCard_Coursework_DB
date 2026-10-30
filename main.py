"""
EnglishCard - Приложение для изучения английского языка
Базовый файл-заготовка для курсовой работы
Студенту необходимо доработать этот файл в соответствии с заданием
"""

import streamlit as st
import psycopg
import pandas as pd
import random

# ============================================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================================
st.set_page_config(
    page_title="EnglishCard - Изучение английского",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# РАБОТА С БАЗОЙ ДАННЫХ (НЕОБХОДИМО РЕАЛИЗОВАТЬ)
# ============================================================

def get_db_connection():
    conn = psycopg.connect(
        host='localhost',
        dbname='english_card',
        user='postgres',
        password='postgres',
        port='5432'
    )
    return conn


def init_database(conn):
    cursor = conn.cursor()

    with open('create_tables.sql', 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()

    cursor.execute(sql_script)

    conn.commit()

    print('Tables created')
    
    # Также заполнить common_words начальными словами (минимум 10 слов)

    words_data = [
        ('яблоко', 'apple'),
        ('груша', 'pear'),
        ('дыня', 'melon'),
        ('арбуз', 'watermelon'),
        ('машина', 'car'),
        ('сок', 'juice'),
        ('вода', 'water'),
        ('голубой', 'blue'),
        ('радуга', 'rainbow'),
        ('компьютер', 'computer')
    ]

    cursor.execute("SELECT COUNT(*) FROM common_words")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO common_words(russian_word, english_word) VALUES(%s, %s)", words_data
        )
    conn.commit()
    
    print('Words inserted')

    cursor.close()

    pass


def login_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
    else:
        cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        user_id = cursor.fetchone()[0]
        conn.commit()
        
    cursor.close()
    conn.close()
    print(user_id)
    return user_id


def get_user_words(user_id):
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, russian_word, english_word FROM common_words LEFT JOIN user_words WHERE user_id = %s", (user_id,))
    user_words = cursor.fetchall()

    cursor.close()
    conn.close()
    print(user_words)
    return user_words

    TODO: Получить все слова пользователя (общие + персональные)
    Возвращает список словарей: [{'id': 1, 'russian_word': 'красный', 'english_word': 'red', 'word_type': 'common'}, ...]
    """


def add_personal_word(user_id, russian_word, english_word):
    """
    TODO: Добавить персональное слово для пользователя
    Проверить, нет ли уже такого слова
    Возвращает True/False
    """
    pass


def delete_personal_word(user_id, word_id):
    """
    TODO: Удалить персональное слово пользователя
    Возвращает True/False
    """
    pass


def update_stats(user_id, word_id, word_type, is_correct):
    """
    TODO: Обновить статистику изучения слова
    """
    pass


def get_statistics(user_id):
    """
    TODO: Получить статистику пользователя
    Возвращает словарь со статистикой
    """
    pass


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def generate_options(correct_word, all_words):
    """
    TODO: Сгенерировать 4 варианта ответа для викторины
    Один вариант - правильный перевод, остальные - случайные слова из словаря
    Если слов не хватает, можно добавить слова-заглушки
    """
    pass


# ============================================================
# ИНТЕРФЕЙС ПРИЛОЖЕНИЯ (НЕОБХОДИМО ДОРАБОТАТЬ)
# ============================================================

def render_sidebar():
    """
    TODO: Реализовать боковую панель с авторизацией
    - Поле для ввода имени
    - Кнопка входа
    - Приветствие после входа
    - Кнопка выхода
    """
    pass


def render_study_tab(words):
    """
    TODO: Реализовать вкладку изучения слов
    - Отображение текущего слова на русском
    - 4 кнопки с вариантами перевода
    - Обработка правильных/неправильных ответов
    - Кнопка следующего слова
    """
    pass


def render_add_word_tab():
    """
    TODO: Реализовать вкладку добавления слова
    - Поле для ввода слова на русском
    - Поле для ввода перевода
    - Кнопка добавления
    - Уведомление об успешном добавлении
    """
    pass


def render_delete_word_tab(words):
    """
    TODO: Реализовать вкладку удаления слова
    - Выпадающий список с персональными словами пользователя
    - Кнопка удаления
    - Подтверждение удаления
    """
    pass


def render_statistics_tab(user_id):
    """
    TODO: Реализовать вкладку статистики (дополнительное требование)
    - Количество изученных слов
    - Количество попыток
    - Процент правильных ответов
    - История последних попыток
    """
    pass


def render_schema():
    """
    TODO: Реализовать отображение схемы базы данных (дополнительное требование)
    """
    pass


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """
    Главная функция приложения
    TODO: Реализовать основную логику:
    1. Инициализация БД
    2. Авторизация пользователя
    3. Отображение вкладок с функционалом
    4. Приветственное сообщение для неавторизованных пользователей
    """
    
    st.title("📚 EnglishCard - Изучай английский с удовольствием!")
    
    # TODO: Инициализация состояния сессии
    # st.session_state.user_id
    # st.session_state.username
    
    # TODO: Инициализация БД
    # init_database()
    
    # TODO: Боковая панель с авторизацией
    # render_sidebar()
    
    # TODO: Основной контент в зависимости от авторизации
    # if st.session_state.user_id:
    #     words = get_user_words(st.session_state.user_id)
    #     # Создание вкладок
    #     tab1, tab2, tab3, tab4 = st.tabs(["📖 Изучение", "➕ Добавить слово", "🗑️ Удалить слово", "📊 Статистика"])
    #     with tab1:
    #         render_study_tab(words)
    #     # ... остальные вкладки
    # else:
    #     # Приветственное сообщение
    #     pass


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    try:
        connection = get_db_connection()
        init_database(connection)
        connection.close()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при подключении или инициализации БД: {e}")

login_user(input('Введите логин: '))

# get_user_words(input('Введите айдишку: '))