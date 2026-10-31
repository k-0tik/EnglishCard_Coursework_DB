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
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)

    request = """
        SELECT id, russian_word, english_word, 'common' AS word_type 
        FROM common_words
        
        UNION ALL
        
        SELECT id, russian_word, english_word, 'user' AS word_type 
        FROM user_words 
        WHERE user_id = %s
    """
    
    cursor.execute(request, (user_id,))
    user_words = cursor.fetchall()

    cursor.close()
    conn.close()
    print(user_words)
    return user_words


def add_personal_word(user_id, russian_word, english_word):
    conn = get_db_connection()
    cursor = conn.cursor()

    word_added = False

    cursor.execute("SELECT id FROM user_words WHERE user_id = %s AND russian_word = %s AND english_word = %s", (user_id, russian_word, english_word,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO user_words (user_id, russian_word, english_word) VALUES (%s, %s, %s)", (user_id, russian_word, english_word,))
        conn.commit()
        word_added = True
    
    cursor.close()
    conn.close()
    return word_added


def delete_personal_word(user_id, word_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    word_deleted = False
    
    cursor.execute("SELECT * FROM user_words WHERE user_id = %s AND id = %s", (user_id, word_id,))
    if cursor.fetchone() is not None:
        cursor.execute("DELETE FROM user_words WHERE user_id = %s AND id = %s", (user_id, word_id,))
        conn.commit()
        word_deleted = True
    
    cursor.close()
    conn.close()
    return word_deleted


def update_stats(user_id, word_id, word_type, is_correct):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM learning_stats WHERE user_id = %s AND word_id = %s AND word_type = %s", (user_id, word_id, word_type,))
    correct_increment = 1 if is_correct else 0
    record = cursor.fetchone()
    if record is None:
        cursor.execute("INSERT INTO learning_stats (user_id, word_id, word_type, correct_answers, total_attempts, last_reviewed) " \
        "VALUES (%s, %s, %s, %s, 1, CURRENT_TIMESTAMP)", (user_id, word_id, word_type, correct_increment))
    else:
        cursor.execute("UPDATE learning_stats " \
        "SET correct_answers = correct_answers + %s," \
        "total_attempts = total_attempts + 1," \
        "last_reviewed = CURRENT_TIMESTAMP WHERE id = %s", (correct_increment, record[0]))
    conn.commit()
    cursor.close()
    conn.close()


def get_statistics(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)

    cursor.execute("SELECT * FROM learning_stats WHERE user_id = %s", (user_id,))
    user_stats = cursor.fetchall()

    cursor.close()
    conn.close()
    print(user_stats)
    return user_stats


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def generate_options(correct_word, all_words):
    correct_translation = correct_word['english_word']

    other_translations = []
    for w in all_words:
        if w['english_word'] != correct_translation:
            other_translations.append(w['english_word'])

    while len(other_translations) < 3:
        other_translations.append("unknown")
    
    wrong_options = random.sample(other_translations, 3)
    
    options = [correct_translation] + wrong_options
    
    random.shuffle(options)
    
    return options


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
    # connection = get_db_connection()
    # init_database(connection)
    # connection.close()
    
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

# login_user(input('Введите логин: '))

# get_user_words(input('Введите айдишку: '))

# test_user_id = int(input('Введите айдишку: '))
# russian_word = input("Введите слово на русском: ")
# english_word = input("Введите перевод на английский: ")

# result = add_personal_word(test_user_id, russian_word, english_word)
    
# if result:
#     print('Слово добавлено!')
# else:
#     print('В словарике уже есть это слово, попробуйте добавить другое')

# user_id = input("Введите айдишку: ")
# word_id = input("Введите айдишку слова, которое нужно удалить: ")

# if delete_personal_word(user_id, word_id):
#     print('Слово удалено!')
# else:
#     print('В словарике нет этого слова, попробуйте другое')

# update_stats(1, 1, 'common', True)
# update_stats(1, 1, 'common', True)
# update_stats(1, 1, 'common', False)

# get_statistics(1)