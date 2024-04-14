import sqlite3
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('nutrilife.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                    userId INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    password TEXT
                )''')


cursor.execute('''CREATE TABLE IF NOT EXISTS Post (
                    postId INTEGER PRIMARY KEY,
                    userId INTEGER,
                    title TEXT,
                    description TEXT,
                    pic BLOB,
                    time TIMESTAMP,
                    FOREIGN KEY (userId) REFERENCES User(userId)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Meta (
                    metaId INTEGER PRIMARY KEY,
                    userId INTEGER,
                    metaNome TEXT,
                    quantMeta INTEGER,
                    FOREIGN KEY (userId) REFERENCES User(userId)
                )''')

def insert_user(name, email, password):
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO User (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
    conn.commit()

# Example of inserting a user
insert_user("Samuel Muniz", "samuel@gmail.com", "123456")

# Commit changes and close connection
conn.close()

