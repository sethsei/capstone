import sqlite3
import bcrypt
import csv
from os import system, path
from termcolor import cprint, colored


class User():
    # can view their own data but no one else's
    # can change certain elements of their data, such as name, password, or email
    def __init__(self, first_name, last_name, phone, email, password, hire_date):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password = password
        self.hire_date = hire_date
        self.user_type = 0


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


def export_data():
    # comptetency reports
    # single user competency
    # export as csv and pdf
    pass


def import_data():
    # assessment results
    pass


def create_database():
    global database
    global connection
    global cursor
    database = ''
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    with open('create_tables.txt', 'r') as f:
        cursor.executescript(f.read())

    connection.commit()


def print_main_menu():
    pass


def main():
    pass


if __name__ == '__main__':
    if not path.isfile(database):
        create_database()
    
    main()