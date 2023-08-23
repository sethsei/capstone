import sqlite3, bcrypt, getch, csv, sys, curses
from datetime import date
from os import system, path
from termcolor import cprint, colored
from curses import wrapper


class User():
    # can view their own data but no one else's
    # can change certain elements of their data, such as name, password, or email
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None, user_type=0):
        global database
        global connection
        global cursor
        database = 'test.db'
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        self.user_id = self._get_user_id() if user_id == 0 else user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password = self._create_password() if password == None else password
        self.date_created = get_today()
        self.hire_date = hire_date
        self.user_type = user_type

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
            pw = getpass('\n\nInput Password:    ')
            confirm = getpass('\n\nConfirm Password:  ')

            pw = pw.encode()
            confirm = confirm.encode()
            if pw == confirm:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(pw, salt)

                wait_for_keypress()
                clear()
                return hashed.decode()

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
    

    def _update_database(self, name, value):
        query = find_query(f'Change {name}')
        values = (value, self.user_id)

        cursor.execute(query, values)
        connection.commit()


    def change_first_name(self):
        while True:
            clear()
            print('\n\nInput New First Name:  ', end='')
            new_first_name = input()

            if new_first_name == self.first_name:
                print('\n\nThis is already your first name. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    wait_for_keypress()
                    continue
            
            self.first_name = new_first_name
            self._update_database('First Name', self.first_name)

            cprint('\n\n--- First Name Updated ---', 'light_green', attrs=['bold'])
            wait_for_keypress()
            return


    def change_last_name(self):
        while True:
            clear()
            print('\n\nInput New Last Name:  ', end='')
            new_last_name = input()

            if new_last_name == self.last_name:
                print('\n\nThis is already your last name. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    wait_for_keypress()
                    continue
            
            self.last_name = new_last_name
            self._update_database('Last Name', self.last_name)

            cprint('\n\n--- Last Name Updated ---', 'light_green', attrs=['bold'])
            wait_for_keypress()
            return


    def change_phone(self):
        while True:
            clear()
            print('\n\nInput New Phone Number:    ', end='')
            new_phone = input()

            if new_phone == self.phone:
                print('\n\nThis is already your phone number. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    wait_for_keypress()
                    continue
            
            elif new_phone.isnumeric() == False:
                cprint('\n\nInvalid input. Must be a real phone number consisting of only digits 0-9', 'red')
                wait_for_keypress()
                continue

            else:
                print('\nConfirm New Phone Number:  ', end='')
                con_phone = input()

                if new_phone == con_phone:
                    self.phone = new_phone
                    self._update_database('Phone', self.phone)
                    cprint('\n\n--- Phone Number Updated ---', 'light_green', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                else:
                    cprint('\n\nNumbers do not match', 'red')
                    wait_for_keypress()
                    continue


    def change_email(self):
        while True:
            clear()
            print('\n\nInput New Email:    ', end='')
            new_email = input()

            if new_email == self.email:
                print('\n\nThis is already your email. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    wait_for_keypress()
                    continue

            query = find_query('Login')
            row = cursor.execute(query, (new_email,)).fetchone()

            if row:
                cprint('\n\nThis email is already in use. Please choose a different one.', 'red')
                wait_for_keypress()
                continue

            else:
                print('\nConfirm New Email:  ', end='')
                con_email = input()

                if new_email == con_email:
                    self.email = new_email
                    self._update_database('Email', self.email)
                    cprint('\n\n--- Email Updated ---', 'light_green', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                else:
                    cprint('\n\nEmails do not match', 'red')
                    wait_for_keypress()
                    continue
    

    def change_password(self):
        clear()
        pw = getpass('\n\nInput Old Password:  ').encode()

        if not bcrypt.checkpw(pw, self.password.encode()):
            cprint('\n\nIncorrect Password', 'red')
            wait_for_keypress()
            clear()
            return

        while True:
            clear()
            new_password = getpass('\n\nInput New Password:    ').encode()

            if bcrypt.checkpw(new_password, self.password.encode()):
                print('\n\nThis is already your password. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    wait_for_keypress()
                    continue

            confirm_new_password = getpass('\nConfirm New Password:  ').encode()

            if new_password == confirm_new_password:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(new_password, salt)
                
                self.password = hashed.decode()

                cprint('\n\n--- Password Changed ---', 'light_green', attrs=['bold'])
                wait_for_keypress()
                clear()
                self._update_database('Password', self.password)
                return

            else:
                cprint('\n\nPasswords do not match. Try again.', 'red')
                wait_for_keypress()
                continue

    def print_info(self):
        if len(str(self.phone)) == 10:
            phone_num = list(str(self.phone))
            phone_num.insert(0, '(')
            phone_num.insert(4, ') ')
            phone_num.insert(8, '-')
            phone_num = ''.join(phone_num)
        
        else:
            phone_num = self.phone

        if self.user_type == 0:
            user_type = 'User'
        
        else:
            user_type = 'Manager'

        uid = colored(f'{"User ID:":20}', 'white', attrs=['bold'])
        fn = colored(f'{"First Name:":20}', 'white', attrs=['bold'])
        ln = colored(f'{"Last Name:":20}', 'white', attrs=['bold'])
        ph = colored(f'{"Phone:":20}', 'white', attrs=['bold'])
        e = colored(f'{"Email:":20}', 'white', attrs=['bold'])
        dc = colored(f'{"Date Created:":20}', 'white', attrs=['bold'])
        hd = colored(f'{"Hire Date:":20}', 'white', attrs=['bold'])
        ut = colored(f'{"User Type:":20}', 'white', attrs=['bold'])

        cprint(f'\n\n{"Account Information":^70}', 'white', attrs=['bold'])
        cprint('-'*70, 'light_grey')
        cprint(f'{uid}{self.user_id:>50}')
        cprint(f'{fn}{self.first_name:>50}')
        cprint(f'{ln}{self.last_name:>50}')
        cprint(f'{ph}{phone_num:>50}')
        cprint(f'{e}{self.email:>50}')
        cprint(f'{dc}{self.date_created:>50}')
        cprint(f'{hd}{self.hire_date:>50}')
        cprint(f'{ut}{user_type:>50}')

        change_values()

        clear()
        return


class Manager(User):
    # can view all users
    # search for users by first or last name
    # view reports of users grouped by competency
    # view comptency of individual user
    # view assessments for a user
    # add: user, competency, assessment to competency, assessment result
    # edit: user info, competency, assessment, assessment result
    # delete: assessment result
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None):
        super().__init__(first_name, last_name, phone, email, hire_date, user_id, password, user_type=1)


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


def view_users():
    query = find_query('View Users')

    while True:
        rows = cursor.execute(query).fetchall()
        
        clear()
        cprint(f'\n\n{"User Records":^170}', 'light_grey', attrs=['bold'])
        print('-'*170)
        cprint(f'\n{"ID":5}{"First Name":18}{"Last Name":18}{"Phone":17}{"Email":33}{"Password":11}{"Status":6}{"Date Created":15}{"Hire Date":15}{"User Type":12}', 'light_grey', attrs=['bold'])
        print(f'{"-"*2:5}{"-"*15:18}{"-"*15:18}{"-"*14:17}{"-"*30:33}{"-"*8:11}{"-"*6:9}{"-"*12:15}{"-"*12:15}{"-"*9:12}')
        for row in rows:
            if len(str(row[3])) == 10:
                phone_num = list(str(row[3]))
                phone_num.insert(0, '(')
                phone_num.insert(4, ') ')
                phone_num.insert(8, '-')
                phone_num = ''.join(phone_num)
        
            else:
                phone_num = row[3]
            
            print(f'{row[0]:>2}   {row[1]:18}{row[2]:18}{phone_num:<17}{row[4]:33}{"*"*8:11}{row[6]:6}   {row[7]:15}{row[8]:15}{row[9]:12}')
        
        e = get_user()
        if e == 'EXIT':
            return
        
        else:
            continue


def get_user():
    uid = colored('User ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\nEnter the {uid} to see more details, or type <{e}> to return to the main menu:  ', end='')
    user_input = input().upper()
    clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    else:
        query = find_query('Get User')
        values = (user_input,)

        row = cursor.execute(query, values).fetchone()

        global current_user
        current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])

        current_user.print_info()


def change_values_menu():
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
    print('    (F)irst Name')
    print('    (L)ast Name')
    print('    (PH)one Number')
    print('    (E)mail')
    print('    (PA)ssword')
    print(f'\n{"-"*70}\nIf the value you would like to change is not listed above,\nplease contact your administrator to rectify the information.\n{"-"*70}\n\n')


def change_values():
    global current_user
    change_values_menu()
    user_input = input().upper()
    clear()

    inputs = {'F': current_user.change_first_name,
              'L': current_user.change_last_name,
              'PH': current_user.change_phone,
              'E': current_user.change_email,
              'PA': current_user.change_password}

    if user_input == 'EXIT':
        return
    
    if user_input in inputs.keys():
        inputs[user_input]()

    else:
        cprint('\n\nInvalid Input. Try again.', 'red')
        wait_for_keypress()
        return


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


def getpass(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    password = ''
    while True:
        c = getch.getch()
        if c == '\n':
            sys.stdout.write('\n')
            sys.stdout.flush()
            return password
        password += c
        sys.stdout.write('*')
        sys.stdout.flush()


def login():
    print(f'\n\nEnter your username:  ', end='')
    username = input()

    query = find_query('Login')
    row = cursor.execute(query, (username,)).fetchone()

    if not row:
        cprint('\n\nCould not find user.', 'red')
        wait_for_keypress()
        return
    
    else:
        query = find_query('Get User')
        row = cursor.execute(query, (row[0],)).fetchone()

        password = getpass('\nEnter your password:  ').encode()
        if not bcrypt.checkpw(password, row[5].encode()):
            cprint('\n\nIncorrect password.', 'red')
            wait_for_keypress()
            return
        
        else:
            global current_user
            current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])

            query = find_query('Update Status')
            cursor.execute(query, (1, current_user.user_id))
            connection.commit()
            
            cprint('\n\n--- Successfully Logged In ---', 'light_green', attrs=['bold'])
            cprint(f'\n{"Welcome " + current_user.first_name:^30}', 'light_cyan', attrs=['bold'])
            wait_for_keypress()

            user_menu()
            return


def print_main_menu():
    cprint(f'\n\n{"Menu":^16}', 'white', attrs=['bold'])
    print('-'*16)
    print('  (L)og In')
    cprint('  (Q)uit\n\n', 'red')


def print_user_menu():
    clear()
    cprint(f'\n\n{"User Menu":^26}', 'white', attrs=['bold'])
    print('-'*26)
    print('  (U)ser Info')
    print('  (A)ssessment History')
    print('  (C)ompetencies')
    cprint('  (L)og Out\n\n', 'red')


def user_menu():
    global current_user
    while True:
        print_user_menu()
        inputs = {'U': current_user.print_info,
                  'A': 'assessment history',
                  'C': 'competencies'}
        
        user_input = input().upper()
        clear()

        if user_input == 'L':
            query = find_query('Update Status')
            cursor.execute(query, (0, current_user.user_id))
            connection.commit()
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


def main():
    while True:
        clear()
        print_main_menu()
        user_input = input().upper()
        clear()

        if user_input == 'Q':
            cprint('\n\nGoodbye\n\n', 'light_cyan', attrs=['bold'])
            break

        if user_input == 'L':
            login()

        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


if __name__ == '__main__':
    database = 'test.db'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    create_database()
    database = 'test.db'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    main()