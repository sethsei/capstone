import sqlite3
import bcrypt
import csv
from datetime import date
from os import system, path
from termcolor import cprint, colored


class User():
    # can view their own data but no one else's
    # can change certain elements of their data, such as name, password, or email
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None):
        global database
        global connection
        global cursor

        self.user_id = self._get_user_id() if user_id == 0 else user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password = self._create_password() if password == None else password
        self.date_created = get_today()
        self.hire_date = hire_date
        self.user_type = 0

        self._add_to_database()


    def _get_user_id(self):
        query = '''
        SELECT user_id
        FROM Users
        ORDER BY user_id DESC;
        '''

        row = cursor.execute(query).fetchone()
        if row == None:
            return 1

        else:
            return row[0] + 1


    def _create_password(self):
        while True:
            clear()
            print('\n\nInput Password:    ', end='')
            pw = input()
            clear()
            print(f'\n\nInput Password:    {"*"*len(pw)}')

            print('\nConfirm Password:  ', end='')
            confirm = input()
            clear()
            print(f'\n\nInput Password:    {"*"*len(pw)}\n\nConfirm Password:  {"*"*len(confirm)}')

            pw = pw.encode()
            confirm = confirm.encode()
            if pw == confirm:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(pw, salt)

                wait_for_keypress()
                clear()
                return hashed

            else:
                cprint('\n\nPasswords do not match. Try again.', 'red')
                wait_for_keypress()
                continue
        
    
    def _add_to_database(self):
        query = find_query('Add User')
        values = (self.first_name, self.last_name, self.phone, self.email, self.password, self.date_created, self.hire_date, self.user_type)
        
        try:
            cursor.execute(query, values)
            connection.commit()

        except sqlite3.IntegrityError:
            pass


class Manager(User):
    # can view all users
    # search for users by first or last name
    # view reports of users grouped by competency
    # view comptency of individual user
    # view assessments for a user
    # add: user, competency, assessment to competency, assessment result
    # edit: user info, competency, assessment, assessment result
    # delete: assessment result
    def __init__(self):
        super().__init__()
        self.user_type = 1


def clear():
    system('clear')


def wait_for_keypress():
    print('\n\nPress any key to continue...\n\n')
    system("/bin/bash -c 'read -s -n 1 -p \"\"'")
    print()


def get_today():
    today = str(date.today()).split('-')
    today.append(today.pop(0))
    return '/'.join(today)


def export_data():
    # comptetency reports
    # single user competency
    # export as csv and pdf
    pass


def import_data():
    # assessment results
    pass


def find_query(title):
    found = False
    query = ''''''
    
    with open('queries.txt', 'r') as f:
        
        while True:
            line = f.readline()

            if line == '___END___':
                break
            
            if found:
                if line.strip().endswith(';'):
                    query += line.strip()
                    break
                
                query += line
                continue

            if line.startswith(title):
                found = True
                continue
    
    return query


def create_database():
    global database
    database = 'test.db'

    if path.isfile(database):
        return
    
    global connection
    global cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    
    with open('create_tables.txt', 'r') as f:
        queries = f.read()

    cursor.executescript(queries)
    connection.commit()


def print_main_menu():
    pass


def main():
    pass


if __name__ == '__main__':
    create_database()

    main()