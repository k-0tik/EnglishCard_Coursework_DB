CREATE table if not EXISTS users (
    id SERIAL PRIMARY KEY, 
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS common_words (
    id SERIAL PRIMARY KEY, 
    russian_word VARCHAR(50) NOT NULL,
    english_word VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_words (
    id SERIAL PRIMARY KEY, 
    user_id INTEGER NOT NULL REFERENCES users(id),
    russian_word VARCHAR(50) NOT NULL,
    english_word VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_stats (
    id SERIAL PRIMARY KEY, 
    user_id INTEGER NOT NULL REFERENCES users(id),
    word_id INTEGER NOT NULL,
    word_type VARCHAR(20) NOT NULL CHECK (word_type IN ('common', 'user')),
    correct_answers INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP
);