from SQL.db_start import *
from SQL.db_user import *


def sql_change_hw_sheduler_time(user_id, new_time):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        cur.execute('UPDATE users SET hw_scheduler_time == ? WHERE user_id == ?', (new_time, user_id))

        conn.commit()
        cur.close()
        conn.close()
        print('--- Scheduler time has been updated')
    else:
        print('---sql_change_hw_sheduler_time(): User not exists')

def sql_get_hw_sheduler_time(user_id):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()
    print('--- Start sql_get_hw_sheduler_time')

    if check_is_user_exists(cur, user_id):
        result = cur.execute('SELECT hw_scheduler_time FROM users WHERE user_id == ?', (user_id, )).fetchone()[0]

        cur.close()
        conn.close()

        return result

    else:
        print('--- User not exist')
        return False



def sql_get_hw_alerts(user_id):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        result = cur.execute('SELECT hw_alerts FROM users WHERE user_id == ?', (user_id, )).fetchone()[0]

        cur.close()
        conn.close()

        return result
        
    else:
        return False

def sql_change_hw_alerts(user_id, bool):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    if check_is_user_exists(cur, user_id):
        cur.execute('UPDATE users SET hw_alerts == ? WHERE user_id == ?', (bool, user_id))

        conn.commit()
        cur.close()
        conn.close()

    