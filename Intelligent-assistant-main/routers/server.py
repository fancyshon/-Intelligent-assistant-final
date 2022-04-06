import sqlite3
from fastapi import APIRouter
from routers.LogIn import check_if_registered
from database import SESSION


# app = fastapi.FastAPI()
router = APIRouter()
conn = sqlite3.connect("./UserData.db", check_same_thread=False)
c = conn.cursor()

# Sign up
@router.get("/sign_up/{user_id}")
async def send_user_data(user_id: str, user_pwd: str, comfirm_pwd: str):
    # http://127.0.0.1:8000/sign_up/Shon?user_pwd=12344&comfirm_pwd=12344

    if not check_if_registered(user_id, c):
        sql_execution = 'INSERT INTO user_data (id, pwd) VALUES ("{}", "{}")'.format(user_id, comfirm_pwd)

        c.execute(sql_execution)
        conn.commit()

        return "Sign up successfully"
    else:
        return "This ID has been used"


@router.get("/log_in/{user_id}")
async def log_in(user_id: str, user_pwd: str):
    # http://127.0.0.1:8000/log_in/Shon?user_pwd=12344&comfirm_pwd=12344

    if not check_if_registered(user_id, c):
        return "You don't have an account, please register one"
    else:

        execution = 'SELECT pwd FROM user_data WHERE id="{}"'.format(user_id)
        c.execute(execution)
        pwd_in_db = c.fetchone()[0]

        if user_pwd == pwd_in_db:
            c.close()
            conn.close()
            return "Log in successfully"
        else:
            return "Wrong password, please try again"
