from SQL.db_user import *

import json

def sql_get_last_marks_updates(user_id):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    marks_updates = {}
    marks_updates['date'] = cur.execute('SELECT date_marks FROM updates WHERE user_id == ?', (user_id, ))

    marks = cur.execute('SELECT marks FROM updates WHERE user_id == ?', (user_id, )).fetchone()[0]

    if marks is not None:
        marks_updates['marks'] = json.loads(str(marks))
    else:
        marks_updates['marks'] = marks

    return marks_updates


def sql_update_last_marks(user_id, date, marks):
    conn = sqlite3.connect("base.db")
    cur = conn.cursor()

    cur.execute('UPDATE updates SET date_marks == ? WHERE user_id == ?', (date, user_id))

    #Если передан '_', то это говорит о том, что оценок в это день еще не было.
    # if marks != '_':
    #     cur.execute('UPDATE updates SET marks == ? WHERE user_id == ?', (json.dumps(marks), user_id))
    # else:
    cur.execute('UPDATE updates SET marks == ? WHERE user_id == ?', (json.dumps(marks), user_id))

    conn.commit()
    cur.close()
    conn.close()



def sql_get_last_passes(user_id):
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()

    passes_updates = {}

    passes_updates['passes'] = cur.execute('SELECT passes FROM updates WHERE user_id == ?', (user_id, )).fetchone()[0]
    passes_updates['date'] = cur.execute('SELECT passes FROM updates WHERE user_id == ?', (user_id, )).fetchone()[0]
    if passes_updates['passes'] is not None:
        cur.close()
        conn.close()

        passes_updates['passes'] = json.loads(str(passes_updates['passes']))['passses']
        return passes_updates
    else:
        cur.close()
        conn.close()

        return None


def sql_update_passes(user_id, passes, date):
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()

    passes = {'passes':passes}
    cur.execute('UPDATE updates SET passes == ? WHERE user_id == ?', (json.dumps(passes), user_id))
    cur.execute('UPDATE updates SET date_passses WHERE user_id == ?', (date, user_id))

    conn.commit()
    cur.close()
    conn.close()
