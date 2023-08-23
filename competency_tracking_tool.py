import sqlite3, bcrypt, getch, csv, sys, curses
from datetime import date
from os import system, path
from termcolor import cprint, colored
from curses import wrapper


class User():
    # can view their assessment results
    # can view their competencies
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
        self._update_user_competencies()


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
            pw = getpass('\n\nInput Password:    ').encode()
            if len(pw.decode()) < 8:
                cprint('\n\nYour password must be at least 8 characters long.', 'red')
                wait_for_keypress()
                continue

            confirm = getpass('\nConfirm Password:  ').encode()
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


    def _change_values_menu(self):
        e = colored('EXIT', 'light_blue', attrs=['bold'])
        print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
        print('    (F)irst Name')
        print('    (L)ast Name')
        print('    (PH)one Number')
        print('    (E)mail')
        print('    (PA)ssword')
        print(f'\n{"-"*70}\nIf the value you would like to change is not listed above,\nplease contact your administrator to rectify the information.\n{"-"*70}\n\n')


    def _update_user_competencies(self):
        competencies = cursor.execute('SELECT competency_id FROM Competencies;').fetchall()
        if not competencies:
            return

        user_competencies = cursor.execute(f'SELECT competency_id FROM User_competencies WHERE user_id={self.user_id}').fetchall()
        if not user_competencies:
            user_competencies.append(tuple())

        for c in competencies[0]:
            if c not in user_competencies[0]:
                # assign non-existent scores with assessment result or 0
                score = cursor.execute(find_query('Get Assessment Result'), (c, self.user_id)).fetchone()
                if not score:
                    score = 0

                else:
                    grades = {(0, 60): 1,
                              (60, 70): 2,
                              (70, 80): 3,
                              (80, 90): 4,
                              (90, 101): 5}
                    for g in grades.keys():
                        if score[0] in range(g[0], g[1]):
                            score = grades[g]

                cursor.execute(find_query('Assign Assessment Result'), (self.user_id, c, score))
                connection.commit()

            elif c in user_competencies[0]:
                # update old scores
                # something not working here
                score = cursor.execute(find_query('Get Assessment Result'), (c, self.user_id)).fetchone()
                if not score:
                    continue

                grades = {(0, 60): 1,
                            (60, 70): 2,
                            (70, 80): 3,
                            (80, 90): 4,
                            (90, 101): 5}
                for g in grades.keys():
                    if score[0] in range(g[0], g[1]):
                        score = grades[g]
                
                old_score = cursor.execute(find_query('Get Old Score'), (self.user_id, c)).fetchone()
                if score == old_score:
                    continue

                else:
                    cursor.execute(find_query('Update Competency Score'), (score, self.user_id, c))
                    connection.commit()
    

    def change_values(self):
        global current_user
        self._change_values_menu()
        user_input = input().upper()
        clear()

        inputs = {'F': self.change_first_name,
                'L': self.change_last_name,
                'PH': self.change_phone,
                'E': self.change_email,
                'PA': self.change_password}

        if user_input == 'EXIT':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()

        else:
            cprint('\n\nInvalid Input. Try again.', 'red')
            wait_for_keypress()
            return
    

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
            
            if len(new_password.decode()) < 8:
                cprint('\n\nYour password must be at least 8 characters long.', 'red')
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


    def change_hire_date(self):
        while True:
            clear()
            print('\n\nInput New Hire Date:  ', end='')
            new_hire_date = input()

            if new_hire_date == self.hire_date:
                print('\n\nThis is already the hire date. Would you like to cancel this change?  Y/N\n')
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
            
            self.hire_date = new_hire_date
            self._update_database('Hire Date', self.hire_date)

            cprint('\n\n--- Hire Date Updated ---', 'light_green', attrs=['bold'])
            wait_for_keypress()
            return
        
    
    def promote(self):
        if self.user_type == 1:
            cprint('\n\nUsers cannot be promoted beyond manager status.', 'red')
            wait_for_keypress()
            return
        
        self.user_type = 1
        query = find_query('Promote')
        cursor.execute(query, (self.user_id,))
        connection.commit()

        cprint('\n\n--- User Promoted ---', 'light_green', attrs=['bold'])
        wait_for_keypress()
        return


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

        self.change_values()

        clear()
        return


class Manager(User):
    # search for users by first or last name
    # view reports of users grouped by competency
    # view comptency of individual user
    # view assessments for a user
    # edit: competency, assessment, assessment result
    # delete: assessment result
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None):
        super().__init__(first_name, last_name, phone, email, hire_date, user_id, password, user_type=1)

    
    def _change_values_menu(self):
        e = colored('EXIT', 'light_blue', attrs=['bold'])
        print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
        print('    (F)irst Name')
        print('    (L)ast Name')
        print('    (PH)one Number')
        print('    (E)mail')
        print('    (PA)ssword')
        print('    (H)ire Date')
        print('    (PR)omote User')
        print(f'\n{"-"*70}\nIf the value you would like to change is not listed above,\nplease contact your administrator to rectify the information.\n{"-"*70}\n\n')


    def change_values(self):
        global current_user
        self._change_values_menu()
        user_input = input().upper()
        clear()

        inputs = {'F': current_user.change_first_name,
                'L': current_user.change_last_name,
                'PH': current_user.change_phone,
                'E': current_user.change_email,
                'PA': current_user.change_password,
                'H': current_user.change_hire_date,
                'PR': current_user.promote}

        if user_input == 'EXIT':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()

        else:
            cprint('\n\nInvalid Input. Try again.', 'red')
            wait_for_keypress()
            return


    def print_info(self):
        global current_user
        if len(str(current_user.phone)) == 10:
            phone_num = list(str(current_user.phone))
            phone_num.insert(0, '(')
            phone_num.insert(4, ') ')
            phone_num.insert(8, '-')
            phone_num = ''.join(phone_num)
        
        else:
            phone_num = current_user.phone

        if current_user.user_type == 0:
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
        cprint(f'{uid}{current_user.user_id:>50}')
        cprint(f'{fn}{current_user.first_name:>50}')
        cprint(f'{ln}{current_user.last_name:>50}')
        cprint(f'{ph}{phone_num:>50}')
        cprint(f'{e}{current_user.email:>50}')
        cprint(f'{dc}{current_user.date_created:>50}')
        cprint(f'{hd}{current_user.hire_date:>50}')
        cprint(f'{ut}{user_type:>50}')

        self.change_values()

        clear()
        return
    

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


def get_user():
    uid = colored('User ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\nEnter the {uid} to see more details, or type <{e}> to return to the main menu:  ', end='')
    user_input = input().upper()
    clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    elif user_input.isnumeric():
        query = find_query('Get User')
        values = (user_input,)

        row = cursor.execute(query, values).fetchone()

        if not row:
            cprint('\n\nNo user with this ID exists.', 'red')
            wait_for_keypress()
            return

        global current_user
        current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])
        
        global logged_in
        if current_user.user_type == 1 and current_user.user_id != logged_in.user_id:
            cprint('\n\nYou cannot make edits to this user.', 'red')
            wait_for_keypress()
            current_user = logged_in
            return

        logged_in.print_info()

    else:
        cprint('\n\nInvalid input. Try again.', 'red')
        wait_for_keypress()
        return


def get_competency():
    cid = colored('Competency ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\nEnter the {cid} to see more details,\nor type <{e}> to return to the main menu:    ', end='')
    user_input = input().upper()
    clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    elif not user_input.isnumeric(): 
        cprint('\n\nInvalid input. Try again.', 'red')
        wait_for_keypress()
        return
    
    else:
        query = find_query('Get Competency')
        values = (user_input,)

        row = cursor.execute(query, values).fetchone()

        if not row:
            cprint('\n\nNo user with this ID exists.', 'red')
            wait_for_keypress()
            return
        
        if not row[3]:
            assessment = 'N/A'

        else:
            assessment = cursor.execute(f'SELECT name FROM Assessments WHERE assessment_id={row[3]};').fetchone()

        cid = colored(f'{"Competency ID:":20}', 'white', attrs=['bold'])
        n = colored(f'{"Name:":20}', 'white', attrs=['bold'])
        dc = colored(f'{"Date Created:":20}', 'white', attrs=['bold'])
        aa = colored(f'{"Assigned Assessment:":20}', 'white', attrs=['bold'])

        cprint(f'\n\n{"Competency Information":^70}', 'white', attrs=['bold'])
        cprint('-'*70, 'light_grey')
        cprint(f'{cid}{row[0]:>50}')
        cprint(f'{n}{row[1]:>50}')
        cprint(f'{dc}{row[2]:>50}')
        cprint(f'{aa}{assessment[0]:>50}')

    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
    print('    (A)ssessment ID\n\n')
    user_input = input().upper()
    clear()

    if user_input == 'EXIT':
        return
    
    elif user_input == 'A':
        assign_assessment(row[0])

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

    x = Manager('John', 'Doe', '5555555555', 'johndoe@gmail.com', 'N/A')


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


def view_users(c=0):
    query = find_query('View Users')

    while True:
        rows = cursor.execute(query).fetchall()
        
        clear()
        cprint(f'\n\n{"User Records":^170}', 'light_grey', attrs=['bold'])
        print('-'*170)
        cprint(f'\n {"ID":5}{"First Name":23}{"Last Name":23}{"Phone":19}{"Email":33}{"Password":13}{"Status":13}{"Date Created":15}{"Hire Date":15}{"User Type":9}', 'light_grey', attrs=['bold'])
        print(f' {"-"*2:5}{"-"*20:23}{"-"*20:23}{"-"*16:19}{"-"*30:33}{"-"*10:13}{"-"*10:13}{"-"*12:15}{"-"*12:15}{"-"*9:9}')
        for row in rows:
            if len(str(row[3])) == 10:
                phone_num = list(str(row[3]))
                phone_num.insert(0, '(')
                phone_num.insert(4, ') ')
                phone_num.insert(8, '-')
                phone_num = ''.join(phone_num)
        
            else:
                phone_num = row[3]
            
            if row[6] == 1:
                status = 'Active'

            else:
                status = 'Inactive'
            
            if row[9] == 0:
                user_type = 'User'
            
            else:
                user_type = 'Manager'
            
            print(f' {row[0]:>2}   {row[1]:23}{row[2]:23}{phone_num:19}{row[4]:33}{"*"*8:13}{status:13}{row[7]:15}{row[8]:15}{user_type:9}')
        
        if c != 0:
            return
        
        if get_user() == 'EXIT':
            return
        
        else:
            continue


def view_reports():
    pass


def view_assessments(c=0):
    query = find_query('View Assessments')

    while True:
        rows = cursor.execute(query).fetchall()
        
        clear()
        cprint(f'\n\n{"Assessments":^42}', 'light_grey', attrs=['bold'])
        print('-'*42)
        cprint(f'\n{"ID":5}{"Name":25}{"Date Created":12}', 'light_grey', attrs=['bold'])
        print(f'{"-"*2:5}{"-"*22:25}{"-"*12:12}')
        for row in rows:
            print(f'{row[0]:>2}   {row[1]:25}{row[2]:12}')
        
        if c == 0:
            wait_for_keypress()
            return
        
        else:
            return
        

def view_competencies():
    query = find_query('View Competencies')

    while True:
        rows = cursor.execute(query).fetchall()
        
        clear()
        cprint(f'\n\n{"Competencies":^42}', 'light_grey', attrs=['bold'])
        print('-'*42)
        cprint(f'\n{"ID":5}{"Name":25}{"Date Created":12}', 'light_grey', attrs=['bold'])
        print(f'{"-"*2:5}{"-"*22:25}{"-"*12:12}')
        for row in rows:
            print(f'{row[0]:>2}   {row[1]:25}{row[2]:12}')

        if get_competency() == 'EXIT':
            return
        
        else:
            continue


def add_user():
    y = colored('YELLOW', 'yellow', attrs=['bold'])
    req = colored('Required', 'yellow', attrs=['bold'])
    na = colored('N/A', 'cyan', attrs=['bold'])
    print(f'\n\nPlease input your data to the fields shown following these rules:')
    print(f'Items in {y} are {req}')
    print(f'For items that are not required, please input {na} if you have no data for the given field\n\n')

    fn = colored('First Name', 'white', attrs=['bold'])
    print(f'\nPlease input the {fn}:{" "*5}', end='')
    first_name = input().capitalize()

    ln = colored('Last Name', 'white', attrs=['bold'])
    print(f'\nPlease input the {ln}:{" "*6}', end='')
    last_name = input().capitalize()

    ph = colored('Phone Number', 'white', attrs=['bold'])
    print(f'\nPlease input the {ph}:{" "*3}', end='')
    phone = input()

    e = colored('Email', 'yellow', attrs=['bold'])
    print(f'\nPlease input the {e}:{" "*10}', end='')
    email = input()

    hd = colored('Hire Date', 'white', attrs=['bold'])
    print(f'\nPlease input the {hd}:{" "*6}', end='')
    hire_date = input()
    if hire_date != 'N/A':
        hire_date = hire_date.zfill(10)

    pw = '1234'.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw, salt).decode()

    return User(first_name, last_name, phone, email, hire_date, password=hashed)


def add_assessment():
    n = colored('Name', 'light_yellow', attrs=['bold'])
    print(f'\n\nPlease input the {n} of the assessment:{" "*3}', end='')
    name = input().capitalize()

    cursor.execute(find_query('Add Assessment'), (name, get_today()))
    connection.commit()

    cprint('\n\n--- Assessment Added ---', 'light_green', attrs=['bold'])
    wait_for_keypress()
    return


def add_assessment_result():
    uid = colored('User ID', 'light_yellow', attrs=['bold'])
    aid = colored('Assessment ID', 'light_yellow', attrs=['bold'])
    dc = colored('Date Completed', 'white', attrs=['bold'])
    s = colored('Score', 'light_yellow', attrs=['bold'])

    view_users(1)

    print(f'\n\nPlease input the {uid}:{" "*10}', end='')
    user_id = input()
    if not user_id.isnumeric():
        cprint('\n\nInvalid input. Try again.')
        wait_for_keypress()
        return

    view_assessments(1)

    print(f'\n\nPlease input the {uid}:{" "*10}{user_id}')
    print(f'\n\nPlease input the {aid}:{" "*4}', end='')
    assessment_id = input()
    if not assessment_id.isnumeric():
        cprint('\n\nInvalid input. Try again.')
        wait_for_keypress()
        return
    
    clear()

    print(f'\n\nPlease input the {uid}:{" "*10}{user_id}')
    print(f'\n\nPlease input the {aid}:{" "*4}{assessment_id}')
    print(f'\n\nPlease input the {dc}:{" "*3}', end='')
    date_completed = input()

    print(f'\n\nPlease input the {s}:{" "*12}', end='')
    score = input()
    if not score.isnumeric():
        cprint('\n\nInvalid input. Try again.')
        wait_for_keypress()
        return

    cursor.execute(find_query('Add Assessment Result'), (user_id, assessment_id, date_completed, score))
    connection.commit()

    cprint('\n\n--- Assessment Result Added ---', 'light_green', attrs=['bold'])
    wait_for_keypress()
    return


def add_competency():
    n = colored('Name', 'light_yellow', attrs=['bold'])
    print(f'\n\nPlease input the {n} of the competency:{" "*12}', end='')
    name = input().capitalize()
    clear()

    cursor.execute(find_query('Add Competency'), (name, get_today()))
    connection.commit()

    view_assessments(1)

    print(f'\n\nPlease input the {n} of the competency:{" "*12}{name}')
    aid = colored('Assessment ID', 'white', attrs=['bold'])
    print(f'\n\nPlease input the {aid} (\'Enter\' to skip):{" "*3}', end='')
    assessment_id = input().upper()
    clear()

    print(f'\n\nPlease input the {n} of the competency:{" "*12}{name}')

    if assessment_id:
        print(f'\n\nPlease input the {aid} (\'Enter\' to skip):{" "*3}{assessment_id}')

        competency_id = cursor.execute(f'SELECT competency_id FROM Competencies WHERE name=\'{name}\'').fetchone()
        cursor.execute(find_query('Assign Assessment to Competency'), (assessment_id, competency_id[0]))
        connection.commit()

    cprint('\n\n--- Competency Added ---', 'light_green', attrs=['bold'])
    wait_for_keypress()
    return


def assign_assessment(competency_id):
    view_assessments(1)

    aid = colored('Assessment ID', 'white', attrs=['bold'])
    print(f'\n\nPlease input the {aid}:{" "*3}', end='')
    assessment_id = input().upper()
    clear()
    
    if not assessment_id.isnumeric(): 
        cprint('\n\nInvalid input. Try again.', 'red')
        wait_for_keypress()
        return
    
    else:
        query = find_query('Assign Assessment to Competency')
        values = (assessment_id, competency_id)

        cursor.execute(query, values)
        connection.commit()

    cprint('\n\n--- Assessment Assigned ---', 'light_green', attrs=['bold'])
    wait_for_keypress()
    return


def delete_assessment_result():
    pass


def import_data():
    # assessment results
    pass


def export_data():
    # comptetency reports
    # single user competency
    # export as csv and pdf
    pass

  
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
            global logged_in
            if row[9] == 0:
                current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])
            
            else:
                current_user = Manager(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5])

            logged_in = current_user


            query = find_query('Update Status')
            cursor.execute(query, (1, current_user.user_id))
            connection.commit()
            
            cprint('\n\n--- Successfully Logged In ---', 'light_green', attrs=['bold'])
            cprint(f'\n{"Welcome " + current_user.first_name:^30}', 'light_cyan', attrs=['bold'])
            wait_for_keypress()

            if current_user.user_type == 0:
                user_menu()

            else:
                manager_menu()

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
    print('  (M)y Information')
    print('  (A)ssessment History')
    print('  (C)ompetencies')
    cprint('  (L)og Out\n\n', 'red')


def print_manager_menu():
    clear()
    cprint(f'\n\n{"Manager Menu":^26}', 'white', attrs=['bold'])
    print('-'*26)
    print('  (M)y Information')
    print('  (C)reation Menu')
    print('  (V)iew Menu')
    print('  (S)earch Users')
    print('  (R)eports')
    cprint('  (L)og Out\n\n', 'red')


def print_creation_menu():
    clear()
    cprint(f'\n\n{"Creation Menu":^26}', 'white', attrs=['bold'])
    print('-'*26)
    print('  (U)ser')
    print('  (A)ssessment')
    print('  (AS)sessment Result')
    print('  (C)ompetency')
    cprint('  (M)ain Menu', 'light_blue')
    cprint('  (L)og out\n\n', 'red')


def print_view_menu():
    clear()
    cprint(f'\n\n{"View Menu":^26}', 'white', attrs=['bold'])
    print('-'*26)
    print('  (U)sers')
    print('  (A)ssessments')
    print('  (AS)sessment Results')
    print('  (C)ompetencies')
    cprint('  (M)ain Menu', 'light_blue')
    cprint('  (L)og Out\n\n', 'red')


def user_menu():
    global current_user
    while True:
        print_user_menu()
        inputs = {'M': current_user.print_info,
                  'A': 'assessment history',
                  'C': 'competencies'}
        
        user_input = input().upper()
        clear()

        if user_input == 'L':
            query = find_query('Update Status')
            cursor.execute(query, (0, logged_in.user_id))
            connection.commit()
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


def manager_menu():
    global current_user
    while True:
        print_manager_menu()
        inputs = {'M': current_user.print_info,
                  'C': creation_menu,
                  'V': view_menu,
                  'S': 'search users',
                  'R': 'reports'}
        
        user_input = input().upper()
        clear()

        if user_input == 'L':
            query = find_query('Update Status')
            cursor.execute(query, (0, logged_in.user_id))
            connection.commit()
            return
        
        if user_input in inputs.keys():
            if inputs[user_input]() == 'LOG OUT':
                return
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


def creation_menu():
    global current_user
    while True:
        print_creation_menu()
        inputs = {'U': add_user,
                  'A': add_assessment,
                  'AS': add_assessment_result,
                  'C': add_competency}
        
        user_input = input().upper()
        clear()

        if user_input == 'L':
            query = find_query('Update Status')
            cursor.execute(query, (0, current_user.user_id))
            connection.commit()
            return 'LOG OUT'
        
        elif user_input == 'M':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


def view_menu():
    global current_user
    while True:
        print_view_menu()
        inputs = {'U': view_users,
                  'A': view_assessments,
                  'AS': 'view assessment results',
                  'C': view_competencies}
        
        user_input = input().upper()
        clear()

        if user_input == 'L':
            query = find_query('Update Status')
            cursor.execute(query, (0, current_user.user_id))
            connection.commit()
            return 'LOG OUT'
        
        elif user_input == 'M':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            wait_for_keypress()
            continue


def main_menu():
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

    main_menu()