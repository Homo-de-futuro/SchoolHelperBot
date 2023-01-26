import sqlite3
import pickle
from parse import parse

from SQL.db_start import *
# from db_start import *



def check_is_user_exists(cur, user_id):
    if cur.execute('SELECT * FROM users WHERE user_id==?', (user_id, )).fetchone() is None:     
        return False
    else:
        return True



def sql_is_user_exist(user_id):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        print('--- User already exist in db')
        cur.close()
        conn.close()

        return True
    else:
        return False



def sql_add_new_user(user_id, login, password):
    print('--- Start sql_add_new_user()')
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        print('--- User already exist in db')
        cur.close()
        conn.close()

        return False
    else:
        print('--- User not exist in db')
        try:
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)', (user_id, login, password, '15:00', '14:00', True, True))
            cur.execute('INSERT INTO updates(user_id) VALUES(?)', (user_id, ))
            print('--- User has been added')
        except Exception as ex:
            print('--- ERRROR sql_add_new_user()')
            print(ex)

        conn.commit()
        cur.close()
        conn.close()
        print('--- Finish sql_add_new_user()')

        return True



def sql_get_auth_data(user_id):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        data = cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id, )).fetchall()[0]
        auth_data = {
            'user_id': data[0],
            'login': data[1],
            'password': data[2],
        }

        cur.close()
        conn.close()

        return auth_data  
    else:
        print('--- ERROR: user not exist')
        cur.close()
        conn.close()




# def sql_update_cookies(user_id, cookies):
#     print('--- Start updating cookies')
#     cur, conn = sql_start()
#     if check_is_user_exist(cur, user_id):
#         cur.execute('UPDATE users SET cookies == ? WHERE user_id == ?', (cookies, user_id))
#         cur.close()
#         conn.close()
        
#         return False
#     else:
#         cur.close()
#         conn.close()
        
#         return True