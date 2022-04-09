import sqlite3
from fastapi import APIRouter
from sklearn import tree
# from database import SESSION

def check_if_registered(id, c):
    execution = 'SELECT id FROM user_data'
    c.execute(execution)
    id_list = c.fetchall()
    target = (id,)

    return target in id_list

# app = fastapi.FastAPI()
router = APIRouter()
conn = sqlite3.connect("./UserData.db", check_same_thread=False)
c = conn.cursor()

query_sql = "SELECT * FROM sqlite_master WHERE type = 'table' AND name = ?"
listOfTable = c.execute(query_sql, ('user_data',)).fetchall()
if listOfTable == []:
    c.execute('''CREATE TABLE user_data(
        id TEXT PRIMARY KEY NOT NULL,
        pwd TEXT NOT NULL );''')
    conn.commit()


# Sign up
@router.get("/sign_up/{user_id}")
async def send_user_data(user_id: str, user_pwd: str, comfirm_pwd: str):
    # http://127.0.0.1:8000/sign_up/Shon?user_pwd=12344&comfirm_pwd=12344
    response={
        'Successful':False,
        'Comfirm_pwd_wrongly':False,
        'Used_ID':False
    }

    if user_pwd != comfirm_pwd:
        response['Comfirm_pwd_wrongly']=True

    if not check_if_registered(user_id, c):
        sql_execution = 'INSERT INTO user_data (id, pwd) VALUES ("{}", "{}")'.format(user_id, user_pwd)

        c.execute(sql_execution)
        conn.commit()
        response["Successful"]=True

    else:
        response['Used_ID']=True

    return response

@router.get("/log_in/{user_id}")
async def log_in(user_id: str, user_pwd: str):
    # http://127.0.0.1:8000/log_in/Shon?user_pwd=12344
    response={
        'Registered':False,
        'Successful':False,
    }

    if not check_if_registered(user_id, c):
        response['Registered']=False
    else:

        execution = 'SELECT pwd FROM user_data WHERE id="{}"'.format(user_id)
        c.execute(execution)
        pwd_in_db = c.fetchone()[0]

        if user_pwd == pwd_in_db:
            c.close()
            conn.close()
            response['Registered']=True
            response['Successful']=True
        else:
            response['Registered']=True
            response['Successful']=False

    return response