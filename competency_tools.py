import sqlite3, getch, sys, csv, pdfkit, jinja2
from os import system
from datetime import date
from termcolor import colored, cprint


'''General Functions'''

def initialize():
    global database
    global connection
    global cursor
    database = 'competency_tracking.db'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()


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


def getpass(prompt, login=None, change=None, confirm=None):
    u = '\n\nEnter your username:  '
    if login:
        username_prompt = u + login + '\n'

    else:
        username_prompt = ''

    n = '\n\nInput New Password:    '
    if change:
        change_prompt = n + '*'*change + '\n'
    
    else:
        change_prompt = ''

    p = '\n\nInput Password:    '
    if confirm:
        confirm_prompt = p + '*'*confirm + '\n'
    
    else:
        confirm_prompt = ''

    sys.stdout.write(prompt)
    sys.stdout.flush()
    password = ''
    while True:
        c = getch.getch()
        # enter character for mac, other systems may be '\r'
        if c == '\n':
            sys.stdout.write('\n')
            sys.stdout.flush()
            return password
        
        # backspace character for mac, other systems may be '\b'
        elif c == '\x7f':
            password = password[:-1:]
            clear()
            sys.stdout.write(username_prompt + change_prompt + confirm_prompt + prompt + ('*'*len(password)))
            sys.stdout.flush()

        else:
            password += c
            sys.stdout.write('*')
            sys.stdout.flush()


def squash_competencies(list_of_tuples):
    squashed = []
    try:
        for t in list_of_tuples:
            squashed.append(t[0])
        
        return squashed
    
    except:
        return None


def isolate_value(tup):
    try:
        return tup[0]
    
    except:
        return None


def create_pdf_template(rows):
    with open('html_temp.txt', 'r') as f:
        html_start = f.read()

    with open('all_competencies_pdf_template.html', 'w') as f:
        f.write(html_start)

    row = '''
            <tr>
                <td>{{name1}}</td>
                <td>{{date1}}</td>
                <td>{{score1}}</td>
            </tr>
    '''
    for i in range(rows):
        f.write(row)
    
    html_end = '''
        </tbody>
    </table>
</body>
    '''
    f.write(html_end)


def create_pdf(context, rows, html='all_competencies_pdf_template.html', output='reports/all_competencies.pdf'):

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    create_pdf_template(rows)
    html_template = html
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    output_pdf = output
    pdfkit.from_string(output_text, output_pdf, configuration=config)


'''SQL Functions'''

def find_query(title):
    found = False
    query = ''''''
    with open('queries.txt', 'r') as f:
        while True:
            line = f.readline()

            if line == '___END___':
                return 'Query Not Found'
            
            if found:
                if line.strip().endswith(';'):
                    query += line.strip()
                    return query
                
                query += line
                continue

            if line.startswith(title):
                found = True
                continue


def export_data():
    with open('reports/users.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('user_id', 'first_name', 'last_name', 'phone', 'email', 'password', 'active', 'date_created', 'hire_date', 'user_type'))
        writer.writerows(cursor.execute(find_query('CSV Users:')).fetchall())
    
    with open('reports/assessments.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('assessment_id', 'name', 'date_created'))
        writer.writerows(cursor.execute(find_query('CSV Assessments:')).fetchall())

    clear()
    cprint('\n\n--- Users and Assessments Exported ---\n\n', 'light_green', attrs=['bold'])
    print(f'This data can be found inside the {colored("Reports", attrs=["bold"])} folder as \'users.csv\' and \'assessments.csv\'')
    wait_for_keypress()


'''Print Related Functions'''

def convert_phone_num(phone):
    if len(str(phone)) == 10:
        phone_num = list(str(phone))
        phone_num.insert(0, '(')
        phone_num.insert(4, ') ')
        phone_num.insert(8, '-')
        return ''.join(phone_num)
    
    else:
        return phone
    

def convert_user_type(user_type):
    if user_type == 0:
        return 'User'
    
    else:
        return 'Manager'


def convert_status(status):
    if status == 1:
        return 'Active'

    else:
        return 'Inactive'
    

def convert_assessment_id(assessment_id):
    if not assessment_id:
        return 'None'

    else:
        assessment_name = cursor.execute(find_query('Get Assessment Name:'), (assessment_id,)).fetchone()
        return assessment_name[0]


'''Menus'''

def u_change_values_menu():
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to the menu\n{"-"*70}\n')
    print('    (PH)one Number')
    print('    (E)mail')
    print('    (PA)ssword')
    print(f'\n{"-"*70}\nIf the value you would like to change is not listed above,\nplease contact your administrator to rectify the information.\n{"-"*70}\n\n')


def m_change_values_menu():
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to change a detail please select an option below,\nor type <{e}> to return to all users\n{"-"*70}\n')
    print('    (F)irst Name')
    print('    (L)ast Name')
    print('    (PH)one Number')
    print('    (E)mail')
    print('    (PA)ssword')
    print('    (H)ire Date')
    print('    (PR)omote User')
    print(f'\n{"-"*70}\nTo view this user\'s data, please select an option below\n{"-"*70}\n')
    print('    (A)ssessment History')
    print('    (C)ompetencies\n\n')


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
    print('  (E)xport Data')
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
    print('  (AS)sessments')
    print('  (C)ompetencies')
    print('  (S)earch Users')
    print('  (AL)l Competencies Reports')
    cprint('  (M)ain Menu', 'light_blue')
    cprint('  (L)og Out\n\n', 'red')


def print_search_menu():
    clear()
    cprint(f'\n\n{"Search By":^20}', attrs=['bold'])
    print('-'*20)
    print('  (F)irst Name')
    print('  (L)ast Name')
    cprint('  (V)iew Menu\n\n', 'light_blue')


def print_modify_assessment_results():
    e = colored('EXIT', 'light_blue', attrs=['bold'])
    print(f'\n\n\n{"-"*70}\nIf you would like to make any changes, please choose an option below,\nOr type <{e}> to return to user info\n{"-"*70}\n')
    print('    (E)dit Assessment Result')
    cprint('    (D)elete Assessment Result\n\n', 'red')


'''Error Handeling'''

def not_numeric(value):
    if not value.isnumeric():
        cprint('\n\nInvalid input. Try again.', 'red')
        wait_for_keypress()
        return True


def not_record_exists(value, table):
    row = cursor.execute(find_query(f'Get {table}:'), (value,)).fetchone()
    if not row:
        cprint('\n\nNo assessment with this ID exists.', 'red')
        wait_for_keypress()
        return True


'''For Testing'''

def get_raw_string():
    for i in range(10):
        c = getch.getch()
        print(repr(c))


'''Executes Test Code'''

if __name__ == '__main__':
    create_pdf('Ninja Turtles Bro', 'Ninja Turtle History', '2.0')
    pass