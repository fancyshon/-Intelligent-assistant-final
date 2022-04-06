import sqlite3


def check_if_registered(id, c):
    execution = 'SELECT id FROM user_data'
    c.execute(execution)
    id_list = c.fetchall()
    target = (id,)

    return target in id_list

if __name__ == '__main__':
    conn = sqlite3.connect('./UserData.db')
    c = conn.cursor()
    login = False

    x = int(input('0 => Sign up, 1 => Log in\n'))

    while not login:

        if x == 0:
            print('Sign up')
            ID = input('Please enter your ID:')

            if not check_if_registered(ID, c):
                pwd = input('Please enter your password:')
                sql_execution = 'INSERT INTO user_data (id, pwd) VALUES ("{}", "{}")'.format(
                    ID, pwd)

                c.execute(sql_execution)
                conn.commit()
            else:
                print('This ID has been used')

        else:
            print('Log in')
            ID = input('Please enter your ID:')

            if not check_if_registered(ID, c):
                print("You don't have an account, please register one")
            else:
                while True:
                    pwd = input('Please enter your password:')
                    execution = 'SELECT pwd FROM user_data WHERE id="{}"'.format(
                        ID)
                    c.execute(execution)
                    pwd_in_db = c.fetchone()[0]

                    if pwd == pwd_in_db:
                        print('Log in successfully')
                        login = True
                        c.close()
                        conn.close()
                        break
                    else:
                        print('Wrong password, please try again')
