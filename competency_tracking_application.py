import sqlite3, bcrypt, csv
import competency_tools as ct
from termcolor import cprint, colored
from os import path


'''User & Manager Objects'''

class User():
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None, user_type=0):
        global database
        global connection
        global cursor
        database = 'competency_tracking.db'
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        self.user_id = self._get_user_id() if user_id == 0 else user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password = self._create_password() if password == None else password
        self.date_created = ct.get_today()
        self.hire_date = hire_date
        self.user_type = user_type

        self._add_to_database()
        self._update_user_competencies()


    def _get_user_id(self):
        row = cursor.execute(ct.find_query('Get User ID:')).fetchone()
        if row == None:
            return 1

        else:
            return row[0] + 1


    def _create_password(self):
        while True:
            ct.clear()
            pw = ct.getpass('\n\nInput Password:    ')
            plength = len(pw)
            pw = pw.encode()

            if len(pw.decode()) < 8:
                cprint('\n\nYour password must be at least 8 characters long.', 'red')
                ct.wait_for_keypress()
                continue

            confirm = ct.getpass('\nConfirm Password:  ', confirm=plength).encode()
            if pw == confirm:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(pw, salt)

                ct.wait_for_keypress()
                ct.clear()
                return hashed.decode()

            else:
                cprint('\n\nPasswords do not match. Try again.', 'red')
                ct.wait_for_keypress()
                continue
        
    
    def _add_to_database(self):
        values = (self.first_name, self.last_name, self.phone, self.email, self.password, self.date_created, self.hire_date, self.user_type)
        try:
            cursor.execute(ct.find_query('Add User:'), values)
            connection.commit()

        except sqlite3.IntegrityError:
            pass
    

    def _update_database(self, name, value):
        cursor.execute(ct.find_query(f'Change {name}:'), (value, self.user_id))
        connection.commit()


    def _update_user_competencies(self):
        competencies = ct.squash_competencies(cursor.execute(ct.find_query('Get Competency IDs:')).fetchall())
        if not competencies:
            return

        user_competencies = ct.squash_competencies(cursor.execute(ct.find_query('Get User Competencies:'), (self.user_id,)).fetchall())
        if not user_competencies:
            user_competencies = []

        for c in competencies:
            score = ct.isolate_value(cursor.execute(ct.find_query('Get Assessment Result:'), (c, self.user_id)).fetchone())
            
            if not score:
                score = 0
            
            else:
                grades = {(0, 60): 0,
                            (60, 70): 1,
                            (70, 80): 2,
                            (80, 90): 3,
                            (90, 101): 4}
                for g in grades.keys():
                    if score in range(g[0], g[1]):
                        score = grades[g]

            if c not in user_competencies:
                # assign non-existent scores with assessment result or 0
                cursor.execute(ct.find_query('Assign Assessment Result:'), (self.user_id, c, score))
                connection.commit()

            elif c in user_competencies:
                # update old scores
                old_score = ct.isolate_value(cursor.execute(ct.find_query('Get Old Score:'), (self.user_id, c)).fetchone())
                if score == old_score:
                    continue

                else:
                    cursor.execute(ct.find_query('Update Competency Score:'), (score, self.user_id, c))
                    connection.commit()
    

    def change_values(self):
        ct.u_change_values_menu()
        user_input = input().upper()
        ct.clear()

        inputs = {'PH': self.change_phone,
                'E': self.change_email,
                'PA': self.change_password}

        if user_input == 'EXIT':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()

        else:
            cprint('\n\nInvalid Input. Try again.', 'red')
            ct.wait_for_keypress()
            return
    

    def change_first_name(self):
        while True:
            ct.clear()
            print('\n\nInput New First Name:  ', end='')
            new_first_name = input()

            if new_first_name == self.first_name:
                print('\n\nThis is already your first name. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue
            
            self.first_name = new_first_name
            self._update_database('First Name', self.first_name)

            cprint('\n\n--- First Name Updated ---', 'light_green', attrs=['bold'])
            ct.wait_for_keypress()
            return


    def change_last_name(self):
        while True:
            ct.clear()
            print('\n\nInput New Last Name:  ', end='')
            new_last_name = input()

            if new_last_name == self.last_name:
                print('\n\nThis is already your last name. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue
            
            self.last_name = new_last_name
            self._update_database('Last Name', self.last_name)

            cprint('\n\n--- Last Name Updated ---', 'light_green', attrs=['bold'])
            ct.wait_for_keypress()
            return


    def change_phone(self):
        while True:
            ct.clear()
            print('\n\nInput New Phone Number:    ', end='')
            new_phone = input()

            if new_phone == self.phone:
                print('\n\nThis is already your phone number. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue
            
            elif new_phone.isnumeric() == False:
                cprint('\n\nInvalid input. Must be a real phone number consisting of only digits 0-9.\nDo not include any spaces or special characters.', 'red')
                ct.wait_for_keypress()
                continue

            else:
                print('\nConfirm New Phone Number:  ', end='')
                con_phone = input()

                if new_phone == con_phone:
                    self.phone = new_phone
                    self._update_database('Phone', self.phone)
                    cprint('\n\n--- Phone Number Updated ---', 'light_green', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                else:
                    cprint('\n\nNumbers do not match', 'red')
                    ct.wait_for_keypress()
                    continue


    def change_email(self):
        while True:
            ct.clear()
            print('\n\nInput New Email:    ', end='')
            new_email = input()

            if new_email == self.email:
                print('\n\nThis is already your email. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue

            row = cursor.execute(ct.find_query('Login:'), (new_email,)).fetchone()

            if row:
                cprint('\n\nThis email is already in use. Please choose a different one.', 'red')
                ct.wait_for_keypress()
                continue

            else:
                print('\nConfirm New Email:  ', end='')
                con_email = input()

                if new_email == con_email:
                    self.email = new_email
                    self._update_database('Email', self.email)
                    cprint('\n\n--- Email Updated ---', 'light_green', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                else:
                    cprint('\n\nEmails do not match', 'red')
                    ct.wait_for_keypress()
                    continue
    

    def change_password(self):
        ct.clear()
        pw = ct.getpass('\n\nInput Old Password:  ').encode()

        if not bcrypt.checkpw(pw, self.password.encode()):
            cprint('\n\nIncorrect Password', 'red')
            ct.wait_for_keypress()
            ct.clear()
            return

        while True:
            ct.clear()
            new_password = ct.getpass('\n\nInput New Password:    ')
            plength = len(new_password)
            new_password = new_password.encode()

            if bcrypt.checkpw(new_password, self.password.encode()):
                print('\n\nThis is already your password. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue
            
            if len(new_password.decode()) < 8:
                cprint('\n\nYour password must be at least 8 characters long.', 'red')
                ct.wait_for_keypress()
                continue

            confirm_new_password = ct.getpass('\nConfirm New Password:  ', change=plength).encode()

            if new_password == confirm_new_password:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(new_password, salt)
                
                self.password = hashed.decode()
                self._update_database('Password', self.password)

                cprint('\n\n--- Password Changed ---', 'light_green', attrs=['bold'])
                ct.wait_for_keypress()
                ct.clear()
                return

            else:
                cprint('\n\nPasswords do not match. Try again.', 'red')
                ct.wait_for_keypress()
                continue


    def change_hire_date(self):
        while True:
            ct.clear()
            print('\n\nInput New Hire Date:  ', end='')
            new_hire_date = input()

            if new_hire_date == self.hire_date:
                print('\n\nThis is already the hire date. Would you like to cancel this change?  Y/N\n')
                yn = input().upper()
                
                if yn == 'Y':
                    cprint('\n\n--- Change Canceled ---', 'light_yellow', attrs=['bold'])
                    ct.wait_for_keypress()
                    return
                
                elif yn == 'N':
                    continue

                else:
                    cprint('\n\nInvalid input. Try again.', 'red')
                    ct.wait_for_keypress()
                    continue
            
            self.hire_date = new_hire_date
            self._update_database('Hire Date', self.hire_date)

            cprint('\n\n--- Hire Date Updated ---', 'light_green', attrs=['bold'])
            ct.wait_for_keypress()
            return
        
    
    def promote(self):
        if self.user_type == 1:
            cprint('\n\nUsers cannot be promoted beyond manager status.', 'red')
            ct.wait_for_keypress()
            return
        
        self.user_type = 1
        cursor.execute(ct.find_query('Promote:'), (self.user_id,))
        connection.commit()

        cprint('\n\n--- User Promoted ---', 'light_green', attrs=['bold'])
        ct.wait_for_keypress()
        return


    def print_info(self):
        phone_num = ct.convert_phone_num(self.phone)
        user_type = ct.convert_user_type(self.user_type)

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

        ct.clear()
        return


    def print_assessment_results(self, c=0):
        rows = cursor.execute(ct.find_query('View User Assessment Results:'), (self.user_id,)).fetchall()

        ct.clear()
        cprint(f'\n\n{"Assessment History":^70}', 'light_grey', attrs=['bold'])
        print('-'*70)
        cprint(f'\n{"Assessment":36}{"Date Completed":23}{"Score":11}', 'light_grey', attrs=['bold'])
        print(f'{"-"*33:36}{"-"*20:23}{"-"*11:11}')
        for row in rows:
            print(f'{row[0]:36}{row[1]:23}{row[2]:11}')

        if logged_in.user_type == 1 and c == 0:
            modify_assessment_result()
        
        elif c == 0:
            ct.wait_for_keypress()
        
        return


    def print_competencies(self):
        rows = cursor.execute(ct.find_query('View User Competencies:'), (self.user_id,)).fetchall()
        competency_scale = {0: 'No Competency - Needs training and direction',
                            1: 'Basic Competency - Needs ongoing support',
                            2: 'Intermediate Competency - Needs occasional support',
                            3: 'Advanced Competency - Completes tasks independently',
                            4: 'Expert Competency - Can effectively pass on this knowledge and can initiate optimizations'}
        
        ct.clear()
        cprint(f'\n\n{"Competency Scores":^35}{" "*15}{"Competency Scale":^100}', 'light_grey', attrs=['bold'])
        print(f'{"-"*35}{" "*15}{"-"*100}')
        cprint(f'\n{"Competency":30}{"Score":20}{"Score":8}{"Reference":92}', 'light_grey', attrs=['bold'])
        print(f'{"-"*27:30}{"-"*5:20}{"-"*5:8}{"-"*92:92}')
        for i, row in enumerate(rows):
            if i in competency_scale.keys():
                print(f'{row[0]:30}{row[1]:5}{" "*15}{i:<8}{competency_scale[i]:92}')
            
            else:
                print(f'{row[0]:30}{row[1]:5}')

        ct.wait_for_keypress()
        return


class Manager(User):
    # view reports of users grouped by competency
    def __init__(self, first_name, last_name, phone, email, hire_date, user_id=0, password=None):
        super().__init__(first_name, last_name, phone, email, hire_date, user_id, password, user_type=1)


    def change_values(self):
        global current_user
        ct.m_change_values_menu()
        user_input = input().upper()
        ct.clear()

        inputs = {'F': current_user.change_first_name,
                'L': current_user.change_last_name,
                'PH': current_user.change_phone,
                'E': current_user.change_email,
                'PA': current_user.change_password,
                'H': current_user.change_hire_date,
                'PR': current_user.promote,
                'A': current_user.print_assessment_results,
                'C': current_user.print_competencies}

        if user_input == 'EXIT':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()

        else:
            cprint('\n\nInvalid Input. Try again.', 'red')
            ct.wait_for_keypress()
            return


    def print_info(self):
        global current_user
        phone_num = ct.convert_phone_num(current_user.phone)
        user_type = ct.convert_user_type(current_user.user_type)

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

        ct.clear()
        return


'''General Functions'''

def create_database():
    global database
    database = 'competency_tracking.db'

    if path.isfile(database):
        return
    
    global connection
    global cursor
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    
    with open('create_tables.txt', 'r') as f:
        creation_queries = f.read()

    cursor.executescript(creation_queries)
    connection.commit()

    # ensures at least one manager
    pw = 'thejoker'.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw, salt).decode()
    Manager('John', 'Doe', '5555555555', 'johndoe@gmail.com', 'N/A', password=hashed)


def login():
    print(f'\n\nEnter your username:  ', end='')
    username = input()
    row = cursor.execute(ct.find_query('Login:'), (username,)).fetchone()

    if not row:
        cprint('\n\nCould not find user.', 'red')
        ct.wait_for_keypress()
        return
    
    else:
        row = cursor.execute(ct.find_query('Get User:'), (row[0],)).fetchone()
        password = ct.getpass('\nEnter your password:  ', login=username).encode()
        if not bcrypt.checkpw(password, row[5].encode()):
            cprint('\n\nIncorrect password.', 'red')
            ct.wait_for_keypress()
            return
        
        else:
            global current_user
            global logged_in
            if row[9] == 0:
                current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])
            
            else:
                current_user = Manager(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5])

            logged_in = current_user

            cursor.execute(ct.find_query('Update Status:'), (1, current_user.user_id))
            connection.commit()
            
            cprint('\n\n--- Successfully Logged In ---', 'light_green', attrs=['bold'])
            cprint(f'\n{"Welcome " + current_user.first_name:^30}', 'light_cyan', attrs=['bold'])
            ct.wait_for_keypress()

            if current_user.user_type == 0:
                user_menu()

            else:
                manager_menu()


def import_data():
    # assessment results
    # users (behind the scenes)
    pass


def export_data():
    # comptetency reports
    # single user competencies
    # export as csv and pdf
    pass


'''Get Specific Records'''

def get_user():
    uid = colored('User ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\nEnter the {uid} to see more details, or type <{e}> to return to view menu:  ', end='')
    user_input = input().upper()
    ct.clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    elif user_input.isnumeric():
        row = cursor.execute(ct.find_query('Get User:'), (user_input,)).fetchone()

        if not row:
            cprint('\n\nNo user with this ID exists.', 'red')
            ct.wait_for_keypress()
            return

        global current_user
        current_user = User(row[1], row[2], row[3], row[4], row[8], user_id=row[0], password=row[5], user_type=row[9])
        
        global logged_in
        if current_user.user_type == 1 and current_user.user_id != logged_in.user_id:
            cprint('\n\nYou cannot make edits to this user.', 'red')
            ct.wait_for_keypress()
            current_user = logged_in
            return

        logged_in.print_info()

    else:
        cprint('\n\nInvalid input. Try again.', 'red')
        ct.wait_for_keypress()
        return


def get_assessment():
    aid = colored('Assessment ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\nEnter the {aid} to see more details,\nor type <{e}> to return to the main menu:    ', end='')
    user_input = input().upper()
    ct.clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    elif not user_input.isnumeric(): 
        cprint('\n\nInvalid input. Try again.', 'red')
        ct.wait_for_keypress()
        return
    
    else:
        row = cursor.execute(ct.find_query('Get Assessment:'), (user_input,)).fetchone()

        if not row:
            cprint('\n\nNo assessment with this ID exists.', 'red')
            ct.wait_for_keypress()
            return

        cid = colored(f'{"Assessment ID:":20}', 'white', attrs=['bold'])
        n = colored(f'{"Name:":20}', 'white', attrs=['bold'])
        dc = colored(f'{"Date Created:":20}', 'white', attrs=['bold'])

        cprint(f'\n\n{"Assessment Information":^70}', 'white', attrs=['bold'])
        cprint('-'*70, 'light_grey')
        cprint(f'{cid}{row[0]:>50}')
        cprint(f'{n}{row[1]:>50}')
        cprint(f'{dc}{row[2]:>50}')

    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
    print('    (N)ame\n\n')
    user_input = input().upper()
    ct.clear()

    if user_input == 'EXIT':
        return

    else:
        cprint('\n\nInvalid Input. Try again.', 'red')
        ct.wait_for_keypress()
        return


def get_competency():
    cid = colored('Competency ID', 'white', attrs=['bold'])
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*44}\nEnter the {cid} to see more details,\nor type <{e}> to return to the main menu\n{"-"*44}\n')
    user_input = input().upper()
    ct.clear()

    if user_input == 'EXIT':
        return 'EXIT'
    
    elif not user_input.isnumeric(): 
        cprint('\n\nInvalid input. Try again.', 'red')
        ct.wait_for_keypress()
        return
    
    else:
        row = cursor.execute(ct.find_query('Get Competency:'), (user_input,)).fetchone()

        if not row:
            cprint('\n\nNo competency with this ID exists.', 'red')
            ct.wait_for_keypress()
            return
        
        assessment = ct.convert_assessment_id(row[3])

        cid = colored(f'{"Competency ID:":20}', 'white', attrs=['bold'])
        n = colored(f'{"Name:":20}', 'white', attrs=['bold'])
        dc = colored(f'{"Date Created:":20}', 'white', attrs=['bold'])
        aa = colored(f'{"Assigned Assessment:":20}', 'white', attrs=['bold'])

        cprint(f'\n\n{"Competency Information":^70}', 'white', attrs=['bold'])
        cprint('-'*70, 'light_grey')
        cprint(f'{cid}{row[0]:>50}')
        cprint(f'{n}{row[1]:>50}')
        cprint(f'{dc}{row[2]:>50}')
        cprint(f'{aa}{assessment:>50}')

    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
    print('    (N)ame')
    print('    (A)ssessment ID\n\n')
    user_input = input().upper()

    if user_input == 'EXIT':
        return
    
    elif user_input == 'A':
        ct.clear()
        assign_assessment(row[0])
    
    elif user_input == 'N':
        ct.clear()
        n = colored('Name', 'light_yellow', attrs=['bold'])
        print(f'\n\nPlease input the new {n} for this competency:  ', end='')
        name = input().title()

        cursor.execute(ct.find_query('Change Competency Name:'), (name, row[0]))
        connection.commit()
        cprint('\n\n--- Competency Name Updated ---', 'light_green', attrs=['bold'])
        ct.wait_for_keypress()
        return

    else:
        cprint('\n\nInvalid Input. Try again.', 'red')
        ct.wait_for_keypress()
        return


'''View All Records'''

def view_users(c=0, fsearch=None, lsearch=None):
    while True:
        if not fsearch and not lsearch:
            rows = cursor.execute(ct.find_query('View Users:')).fetchall()

        elif fsearch:
            rows = cursor.execute(ct.find_query('Search Users First Name:'), (fsearch,)).fetchall()
        
        elif lsearch:
            rows = cursor.execute(ct.find_query('Search Users Last Name'), (lsearch,)).fetchall()
        
        ct.clear()
        cprint(f'\n\n{"User Records":^172}', 'light_grey', attrs=['bold'])
        print('-'*172)
        cprint(f'\n {"ID":7}{"First Name":23}{"Last Name":23}{"Phone":19}{"Email":33}{"Password":13}{"Status":13}{"Date Created":15}{"Hire Date":15}{"User Type":9}', 'light_grey', attrs=['bold'])
        print(f' {"-"*4:7}{"-"*20:23}{"-"*20:23}{"-"*16:19}{"-"*30:33}{"-"*10:13}{"-"*10:13}{"-"*12:15}{"-"*12:15}{"-"*9:9}')
        for row in rows:
            phone_num = ct.convert_phone_num(row[3])
            status = ct.convert_status(row[6])
            user_type = ct.convert_user_type(row[9])
            print(f' {row[0]:>4}   {row[1]:23}{row[2]:23}{phone_num:19}{row[4]:33}{"*"*8:13}{status:13}{row[7]:15}{row[8]:15}{user_type:9}')
        
        if c != 0:
            return
        
        if get_user() == 'EXIT':
            return
        
        else:
            continue


def view_assessments(c=0, specific=0):
    while True:
        if specific > 0:
            rows = cursor.execute(ct.find_query('View Assessment:'), (specific,))

        else:
            rows = cursor.execute(ct.find_query('View Assessments:')).fetchall()
        
        ct.clear()
        cprint(f'\n\n{"Assessments":^70}', 'light_grey', attrs=['bold'])
        print('-'*70)
        cprint(f'\n{"ID":7}{"Name":51}{"Date Created":12}', 'light_grey', attrs=['bold'])
        print(f'{"-"*4:7}{"-"*48:51}{"-"*12:12}')
        for row in rows:
            print(f'{row[0]:>4}   {row[1]:51}{row[2]:12}')
        
        if c == 0:
            e = colored('EXIT', 'light_blue', attrs=['bold'])
            aid = colored('Assessment ID', attrs=['bold'])
            print(f'\n\n\n{"-"*70}\nInput an {aid} to edit the name,\nor enter <{e}> to return to view menu\n{"-"*70}\n')
            assessment_id = input().upper()
            ct.clear()

            if assessment_id == 'EXIT':
                return

            if not assessment_id.isnumeric():
                cprint('\n\nInvalid input. Try again.', 'red')
                ct.wait_for_keypress()
                continue

            else:
                assessment_id = int(assessment_id)
                view_assessments(c=1, specific=assessment_id)
                n = colored('Name', 'light_yellow', attrs=['bold'])
                print(f'\n\nPlease input the new {n} for this assessment:  ', end='')
                name = input().title()

                cursor.execute(ct.find_query('Change Assessment Name:'), (name, assessment_id))
                connection.commit()
                cprint('\n\n--- Assessment Name Updated ---', 'light_green', attrs=['bold'])

            ct.wait_for_keypress()
            return
        
        else:
            return


def view_competencies():
    while True:
        rows = cursor.execute(ct.find_query('View Competencies:')).fetchall()
        
        ct.clear()
        cprint(f'\n\n{"Competencies":^44}', 'light_grey', attrs=['bold'])
        print('-'*44)
        cprint(f'\n{"ID":7}{"Name":25}{"Date Created":12}', 'light_grey', attrs=['bold'])
        print(f'{"-"*4:7}{"-"*22:25}{"-"*12:12}')
        for row in rows:
            print(f'{row[0]:>4}   {row[1]:25}{row[2]:12}')

        if get_competency() == 'EXIT':
            return
        
        else:
            continue


def view_reports():
    pass


def search_users():
    while True:
        ct.print_search_menu()
        search = input().upper()
        ct.clear()

        if search == 'V':
            return

        print('\n\nEnter search query:  ', end='')
        query = '%' + input() + '%'
        
        if search == 'F':
            view_users(fsearch=query)

        elif search == 'L':
            view_users(lsearch=query)
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


'''Create Records'''

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

    pw = '1234'.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw, salt).decode()

    return User(first_name, last_name, phone, email, hire_date, password=hashed)


def add_assessment():
    n = colored('Name', 'light_yellow', attrs=['bold'])
    print(f'\n\nPlease input the {n} of the assessment:{" "*3}', end='')
    name = input().title()

    cursor.execute(ct.find_query('Add Assessment:'), (name, ct.get_today()))
    connection.commit()

    cprint('\n\n--- Assessment Added ---', 'light_green', attrs=['bold'])
    ct.wait_for_keypress()
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
        ct.wait_for_keypress()
        return
    
    row = cursor.execute(ct.find_query('Get User:'), (user_id,)).fetchone()
    if not row:
        cprint('\n\nNo user with this ID exists.', 'red')
        ct.wait_for_keypress()
        return

    view_assessments(1)

    print(f'\n\nPlease input the {uid}:{" "*10}{user_id}')
    print(f'\n\nPlease input the {aid}:{" "*4}', end='')
    assessment_id = input()
    if not assessment_id.isnumeric():
        cprint('\n\nInvalid input. Try again.')
        ct.wait_for_keypress()
        return

    row = cursor.execute(ct.find_query('Get Assessment:'), (assessment_id,)).fetchone()
    if not row:
        cprint('\n\nNo assessment with this ID exists.', 'red')
        ct.wait_for_keypress()
        return

    ct.clear()

    print(f'\n\nPlease input the {uid}:{" "*10}{user_id}')
    print(f'\n\nPlease input the {aid}:{" "*4}{assessment_id}')
    print(f'\n\nPlease input the {dc}:{" "*3}', end='')
    date_completed = input()

    print(f'\n\nPlease input the {s}:{" "*12}', end='')
    score = input()
    if not score.isnumeric():
        cprint('\n\nInvalid input. Try again.')
        ct.wait_for_keypress()
        return

    cursor.execute(ct.find_query('Add Assessment Result:'), (user_id, assessment_id, date_completed, score))
    connection.commit()

    cprint('\n\n--- Assessment Result Added ---', 'light_green', attrs=['bold'])
    ct.wait_for_keypress()
    return


def add_competency():
    n = colored('Name', 'light_yellow', attrs=['bold'])
    print(f'\n\nPlease input the {n} of the competency:{" "*12}', end='')
    name = input().title()
    ct.clear()

    cursor.execute(ct.find_query('Add Competency:'), (name, ct.get_today()))
    connection.commit()

    view_assessments(1)

    print(f'\n\nPlease input the {n} of the competency:{" "*12}{name}')
    aid = colored('Assessment ID', 'white', attrs=['bold'])
    print(f'\n\nPlease input the {aid} (\'Enter\' to skip):{" "*3}', end='')
    assessment_id = input().upper()
    ct.clear()

    row = cursor.execute(ct.find_query('Get Assessment:'), (assessment_id,)).fetchone()
    if not row:
        cprint('\n\nNo assessment with this ID exists.', 'red')
        ct.wait_for_keypress()
        return

    print(f'\n\nPlease input the {n} of the competency:{" "*12}{name}')

    if assessment_id:
        print(f'\n\nPlease input the {aid} (\'Enter\' to skip):{" "*3}{assessment_id}')

        competency_id = cursor.execute(ct.find_query('Get Competency ID:'), (name,)).fetchone()
        cursor.execute(ct.find_query('Assign Assessment to Competency:'), (assessment_id, competency_id[0]))
        connection.commit()

    cprint('\n\n--- Competency Added ---', 'light_green', attrs=['bold'])
    ct.wait_for_keypress()
    return


def assign_assessment(competency_id):
    view_assessments(1)

    aid = colored('Assessment ID', 'white', attrs=['bold'])
    print(f'\n\nPlease input the {aid}:{" "*3}', end='')
    assessment_id = input().upper()
    
    if not assessment_id.isnumeric(): 
        cprint('\n\nInvalid input. Try again.', 'red')
        ct.wait_for_keypress()
        return
    
    else:
        cursor.execute(ct.find_query('Assign Assessment to Competency:'), (assessment_id, competency_id))
        connection.commit()

    cprint('\n\n--- Assessment Assigned ---', 'light_green', attrs=['bold'])
    ct.wait_for_keypress()
    return


def modify_assessment_result():
    ct.print_modify_assessment_results()
    user_input = input().upper()
    ct.clear()

    if user_input == 'EXIT':
        return
    
    current_user.print_assessment_results(c=1)
    ct.print_modify_assessment_results()
    if user_input == 'E':
        n = colored('Name', 'light_yellow', attrs=['bold'])
        s = colored('Score', 'light_yellow', attrs=['bold'])
        print(f'Please enter the listed {n} of the assessment:  ', end='')
        name = input().title()

        print(f'\nPlease enter the {s} you want to edit:         ', end='')
        score = input()
        if not score.isnumeric():
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            return
        
        print(f'\nPlease enter the new {s}:                      ', end='')
        new_score = input()
        if not new_score.isnumeric():
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            return

        assessment_id = cursor.execute(ct.find_query('Get Assessment ID:'), (f'%{name}%',)).fetchone()
        cursor.execute(ct.find_query('Change Assessment Result:'), (int(new_score), current_user.user_id, assessment_id[0], int(score)))
        connection.commit()

        cprint('\n\n--- Assessment Result Updated ---', 'light_green', attrs=['bold'])
        ct.wait_for_keypress()
        return
    
    elif user_input == 'D':
        n = colored('Name', 'light_yellow', attrs=['bold'])
        s = colored('Score', 'light_yellow', attrs=['bold'])
        print(f'Please enter the listed {n} of the assessment:  ', end='')
        name = input().title()

        print(f'\nPlease enter the {s} you want to delete:       ', end='')
        score = input()
        if not score.isnumeric():
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            return

        assessment_id = cursor.execute(ct.find_query('Get Assessment ID:'), (f'%{name}%',)).fetchone()
        cursor.execute(ct.find_query('Delete Assessment Result:'), (current_user.user_id, assessment_id[0], int(score)))
        connection.commit()

        cprint('\n\n--- Assessment Result Deleted ---', 'light_red', attrs=['bold'])
        ct.wait_for_keypress()
        return


'''Menus'''

def user_menu():
    global current_user
    while True:
        ct.print_user_menu()
        inputs = {'M': current_user.print_info,
                  'A': current_user.print_assessment_results,
                  'C': current_user.print_competencies}
        
        user_input = input().upper()
        ct.clear()

        if user_input == 'L':
            cursor.execute(ct.find_query('Update Status:'), (0, logged_in.user_id))
            connection.commit()
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


def manager_menu():
    global current_user
    while True:
        ct.print_manager_menu()
        inputs = {'M': current_user.print_info,
                  'C': creation_menu,
                  'V': view_menu}
        
        user_input = input().upper()
        ct.clear()

        if user_input == 'L':
            cursor.execute(ct.find_query('Update Status:'), (0, logged_in.user_id))
            connection.commit()
            return
        
        if user_input in inputs.keys():
            if inputs[user_input]() == 'LOG OUT':
                return
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


def creation_menu():
    global current_user
    while True:
        ct.print_creation_menu()
        inputs = {'U': add_user,
                  'A': add_assessment,
                  'AS': add_assessment_result,
                  'C': add_competency}
        
        user_input = input().upper()
        ct.clear()

        if user_input == 'L':
            cursor.execute(ct.find_query('Update Status:'), (0, current_user.user_id))
            connection.commit()
            return 'LOG OUT'
        
        elif user_input == 'M':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


def view_menu():
    global current_user
    while True:
        ct.print_view_menu()
        inputs = {'U': view_users,
                  'A': view_assessments,
                  'C': view_competencies,
                  'S': search_users,
                  'R': view_reports}
        
        user_input = input().upper()
        ct.clear()

        if user_input == 'L':
            cursor.execute(ct.find_query('Update Status:'), (0, current_user.user_id))
            connection.commit()
            return 'LOG OUT'
        
        elif user_input == 'M':
            return
        
        if user_input in inputs.keys():
            inputs[user_input]()
        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


def main_menu():
    while True:
        ct.clear()
        ct.print_main_menu()
        user_input = input().upper()
        ct.clear()

        if user_input == 'Q':
            cprint('\n\nGoodbye\n\n', 'light_cyan', attrs=['bold'])
            break

        if user_input == 'L':
            login()

        
        else:
            cprint('\n\nInvalid input. Try again.', 'red')
            ct.wait_for_keypress()
            continue


'''Executes Code'''

if __name__ == '__main__':
    create_database()
    database = 'competency_tracking.db'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    ct.initialize()

    main_menu()