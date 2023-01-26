import sqlite3


def sql_start():
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    #Желательно изменить в первом столбце на INTEGER, но нет времени, защита через 5 дней
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY NOT NULL, 
login CHAR(60) NOT NULL, 
password CHAR(60) NOT NULL, 
hw_scheduler_time CHAR(10) NOT NULL,
hw_alerts BOOL NOT NULL,
marks_alerts BOOL NOT NULL, 
pass_alerts BOOL NOT NULL) ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS updates(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        date_marks char(50),
        date_passes char(50),
        marks text,
        passes text
    )''')

    conn.commit()


