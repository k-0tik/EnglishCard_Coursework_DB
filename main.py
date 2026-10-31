import streamlit as st
import psycopg
import pandas as pd
import random

# ============================================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================================
st.set_page_config(
    page_title="EnglishCard",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# РАБОТА С БАЗОЙ ДАННЫХ
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
    cursor.close()

@st.cache_resource
def setup_database():
    conn = get_db_connection()
    init_database(conn)
    conn.close()


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
# ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.header ('Профиль')
        if st.session_state.user_id is None:
            username = st.text_input("Введите ваше имя:", key="login_name")
            if st.button("Войти", use_container_width=True):
                if username.strip():
                    user_id = login_user(username)
                    
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    
                    st.rerun() 
                else:
                    st.warning("Пожалуйста, введите имя.")
                    
        else:
            st.success(f"Привет, **{st.session_state.username}**!")
            st.write("Рады видеть тебя снова.")
            
            if st.button("Выйти", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()


def render_study_tab(words):
    if 'current_word' not in st.session_state or st.session_state.current_word is None:
        st.session_state.current_word = random.choice(words)
        st.session_state.current_options = generate_options(st.session_state.current_word, words)
        st.session_state.answered = False
        st.session_state.is_correct = None

    current_word = st.session_state.current_word
    st.subheader(f"Как переводится слово: **{current_word['russian_word']}** ?")
    st.divider()

    options = st.session_state.current_options

    cols = st.columns(4)

    for i, option in enumerate(options):
        with cols[i]:
            clicked = st.button(
                option, 
                key=f"btn_{i}",
                disabled=st.session_state.answered,
                use_container_width=True
            )
            
            if clicked:
                st.session_state.answered = True
                is_correct = (option == current_word['english_word'])
                st.session_state.is_correct = is_correct
                
                update_stats(st.session_state.user_id, current_word['id'], current_word['word_type'], is_correct)
                st.rerun()

    if st.session_state.answered:
        st.divider()
        if st.session_state.is_correct:
            st.success("Правильно!")
        else:
            st.error(f"Правильный ответ: **{current_word['english_word']}**")
        
        if st.button("Дальше", type="primary"):
            st.session_state.current_word = random.choice(words)
            st.session_state.current_options = generate_options(st.session_state.current_word, words)
            st.session_state.answered = False
            st.session_state.is_correct = None
            st.rerun()


def render_add_word_tab():
    with st.form(key='add_word_form', clear_on_submit=True):
        russian_word = st.text_input("Введи слово на русском:", key="add_rus")
        english_word = st.text_input("А тут его перевод на английский:", key="add_eng")
        if st.form_submit_button("Добавить", type="primary"):
            if not russian_word.strip() or not english_word.strip():
                st.warning("Пожалуйста, заполни оба поля")
            else:
                success = add_personal_word(st.session_state.user_id, russian_word.strip(), english_word.strip())
            if success:
                st.success("Словарик пополнен!")
            else:
                st.error("Такое слово уже есть в вашем словарике! Попробуйте другое.")



def render_delete_word_tab(words):
    personal_words = [] 
    for w in words:
        if w['word_type'] == 'user':
            personal_words.append(w)

    if not personal_words:
        st.info("В вашем личном словарике пока нет слов. Добавьте их во вкладке 'Добавить слово'.")
        return
    
    word = st.selectbox('Какое слово нужно удалить?', options=personal_words, format_func=lambda w: f"{w['russian_word']} - {w['english_word']}")
    if st.button("Удалить слово", type="primary"):
        if delete_personal_word(st.session_state.user_id, word['id']):
            st.toast("Почистили словарик!")
            st.rerun()
        else:
            st.error("Попробуйте еще раз.")


def render_statistics_tab(user_id):
    stats_list = get_statistics(user_id)

    if not stats_list:
        st.info("Вы пока не прошли ни одного испытания. Пора начинать!")
        return

    words_count = len(stats_list)
    total_attempts = sum(item['total_attempts'] for item in stats_list)
    total_correct = sum(item['correct_answers'] for item in stats_list)
    
    if total_attempts > 0:
        correct_percent = (total_correct / total_attempts) * 100
    else:
        correct_percent = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Изучено слов", words_count)
    with col2:
        st.metric("Всего попыток", total_attempts)
    with col3:
        st.metric("Процент успеха", f"{correct_percent:.1f}%")

    st.divider()

    st.subheader("Последние повторения")

    stats_list.sort(
        key=lambda x: x['last_reviewed'] if x['last_reviewed'] else datetime.datetime.min, 
        reverse=True
    )

    all_words = get_user_words(user_id)

    for stat in stats_list[:5]:
        for w in all_words:
            if w['id'] == stat['word_id'] and w['word_type'] == stat['word_type']:
                date_text = stat['last_reviewed'].strftime("%d.%m.%Y") if stat['last_reviewed'] else "Только что"
                st.write(f"• **{w['russian_word']}** ({w['english_word']}) — {stat['correct_answers']} из {stat['total_attempts']} верно. *{date_text}*")
                break


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    st.title("📚 EnglishCard - Изучай английский с удовольствием!")

    setup_database()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    connection = get_db_connection()
    init_database(connection)
    connection.close()
    
    render_sidebar()
    
    if st.session_state.user_id is not None:
        words = get_user_words(st.session_state.user_id)
        st.header('Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе.')
        st.text('У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения. Для этого воспрользуйся инструментами:')
        st.text('- Добавить слово ➕')
        st.text('- Удалить слово 🗑️')
        tab1, tab2, tab3, tab4 = st.tabs(["📖 Изучение", "➕ Добавить слово", "🗑️ Удалить слово", "📊 Статистика"])
        with tab1:
            st.subheader("Викторина!") 
            render_study_tab(words)
            
        with tab2:
            st.subheader("Тут ты можешь добавить новое слово для викторины")
            render_add_word_tab()
            
        with tab3:
            st.write("Тут можно удалить слово из словарика")
            render_delete_word_tab(words)
            
        with tab4:
            render_statistics_tab(st.session_state.user_id)
            
    else:
        st.info("Пожалуйста, войдите в систему через боковую панель слева, чтобы начать учиться")


if __name__ == "__main__":
    main()