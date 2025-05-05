print ("loading.")
try:
    import importlib
    importlib.import_module("pyautogui")
except ImportError:
    import pip
    print ("pyautogui not found installing ...")
    pip.main(['install', "pyautogui"])
finally:
    print ("loading....")
    import pyautogui
try:
    importlib.import_module("mysql.connector")
except ImportError:
    import pip
    print("msql connector not found installing ... ")
    pip.main(['install', "mysql-connector-python"])
finally:
    import mysql.connector
from datetime import datetime
from sys import exit
import  pyautogui

HOST = "localhost"
USER = pyautogui.prompt("Enter Username")
PASSWORD = pyautogui.password("Enter login password") 
DATABASE = pyautogui.prompt("Enter Database name")

def get_database():
    try:
        database = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        cursor = database.cursor(dictionary=True)
        return database, cursor
    except mysql.connector.Error:
        return None, None


SCREEN_WIDTH = 100


def print_center(s):
    x_pos = SCREEN_WIDTH // 2
    print((" " * x_pos), s)


def print_bar():
    print()

def print_bar_ln():
    print_bar()
    print()


def input_center(s):
    x_pos = SCREEN_WIDTH // 2
    print((" " * x_pos), s, end='')
    return input()


ROOMS_TABLE_NAME = "rooms"


class Room:
    def __init__(self):
        self.room_id = 0
        self.room_no = 0
        self.floor = ""
        self.beds = ""
        self.available = ""

    def create(self, room_id, room_no, floor, beds, available):
        self.room_id = room_id
        self.room_no = room_no
        self.floor = floor
        self.beds = beds
        self.available = available
        return self

    def create_from_record(self, record):
        self.room_id = record['id']
        self.room_no = record['room_no']
        self.floor = record['floor']
        self.beds = record['beds']
        self.available = record['available']
        return self

    def print_all(self):
        a=("Record #"+str( self.room_id))
        b=a+("\nRoom No: "+ str(self.room_no))
        c=b+("\nFloor: "+ str(self.floor))
        d=c+("\nBeds: "+ str(self.beds))
        e=d+("\navailable: "+ str(self.available))
        pyautogui.alert(e)

    def print_full(self):
        a=("Record #"+str( self.room_id))
        b=a+("\nRoom No: "+ str(self.room_no))
        c=b+("\nFloor: "+ str(self.floor))
        d=c+("\nBeds: "+ str(self.beds))
        e=d+("\navailable: "+ str(self.available))
        pyautogui.alert(e)


def create_room():
    room_id = None
    room_no = pyautogui.prompt("Enter the room no: ")
    floor = pyautogui.prompt("Enter the floor (Ex. ground, first etc.): ")
    beds = pyautogui.prompt("Enter number of beds: ")
    available = True
    return Room().create(room_id, room_no, floor, beds, available)


def print_room_header():
    print("="*100)
    print("id".ljust(3),
          "room no".ljust(15),
          "floor".ljust(15),
          "beds".ljust(15),
          "available".ljust(15)
          )
    print("="*100)


def create_rooms_table(database):
    cursor = database.cursor()
    cursor.execute("DROP table if exists {0}".format(ROOMS_TABLE_NAME))
    cursor.execute("create table {0} ("
                   "id int primary key auto_increment,"
                   "room_no int,"
                   "floor varchar(50),"
                   "beds int,"
                   "available bool)".format(ROOMS_TABLE_NAME))


def add_room(database, cursor):
    room = create_room()
    query = "insert into {0}(room_no,floor,beds,available) values({1},'{2}',{3},{4})".\
            format(ROOMS_TABLE_NAME, room.room_no, room.floor, room.beds, room.available)
    try:
        cursor.execute(query)
        database.commit()
    except mysql.connector.Error as err:
        create_rooms_table(database)
        cursor.execute(query)
        database.commit()
    pyautogui.alert("Operation Successful")


def show_room_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        room = Room().create_from_record(record)
        room.print_full()
        return room
    except mysql.connector.Error as err:
        print(err)


def show_room_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_room_header()
        for record in records:
            room = Room().create_from_record(record)
            room.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)


def get_and_print_room_by_no(cursor):
    room_no = pyautogui.prompt("Enter the room no: ")
    query = "select * from {0} where room_no={1}".format(ROOMS_TABLE_NAME, room_no)
    room = show_room_record(cursor, query)
    return room


def edit_room_by_room_no(database, cursor):
    room = get_and_print_room_by_no(cursor)
    if room is not None:
        query = "update {0} set".format(ROOMS_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        room_no = pyautogui.prompt("Enter new room no: ")
        if len(room_no) > 0:
            query += " room_no={0},".format(room_no)
        floor = pyautogui.prompt("Enter new floor: ")
        if len(floor) > 0:
            query += " floor='{0}',".format(floor)
        beds = pyautogui.prompt("Enter number of beds: ")
        if len(beds) > 0:
            query += " beds={0},".format(beds)
        query = query[0:-1] + " where id={0}".format(room.room_id)
        confirm = pyautogui.prompt("Confirm Update (Y/N): ").lower()
        if confirm == 'y':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def change_room_status(database, cursor, room_id, available):
    query = "update {0} set available={1} where id={2}".format(ROOMS_TABLE_NAME, available, room_id)
    cursor.execute(query)
    database.commit()


def delete_room_by_room_no(database, cursor):
    room = get_and_print_room_by_no(cursor)
    if room is not None:
        confirm = pyautogui.prompt("Confirm Deletion (Y/N): ").lower()
        if confirm == 'y':
            query = "delete from {0} where id={1}".format(ROOMS_TABLE_NAME, room.room_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def room_menu(database, cursor):
    while True:
        choce = (pyautogui.prompt("""
           ROOM MENU
        1. Add new room    
        2. Get room details by room no    
        3. Find available rooms by number of beds
        4. Edit Room details
        5. Delete room
        6. View all rooms
        0. Go Back"""))
        choice=int(choce)

        if choice == 1:
            add_room(database, cursor)
        elif choice == 2:
            room_no = pyautogui.prompt("Enter the room no: ")
            query = "select * from {0} where room_no={1}".format(ROOMS_TABLE_NAME, room_no)
            show_room_records(cursor, query)
        elif choice == 3:
            beds = pyautogui.prompt("Enter number of beds required: ")
            query = "select * from {0} where beds={1}".format(ROOMS_TABLE_NAME, beds)
            show_room_records(cursor, query)
        elif choice == 4:
            edit_room_by_room_no(database, cursor)
        elif choice == 5:
            delete_room_by_room_no(database, cursor)
        elif choice == 6:
            query = "select * from {0}".format(ROOMS_TABLE_NAME)
            show_room_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")


PATIENT_TABLE_NAME = "patients"

class Patient:
    def __init__(self):
        self.patient_id = 0
        self.name = ""
        self.address = ""
        self.phone = ""
        self.room_no = "0"
        self.admit_date = ""
        self.discharge_date = ""

    def create(self, patient_id, name, address, phone, room_no, admit_date, discharge_date):
        self.patient_id = patient_id
        self.name = name
        self.address = address
        self.phone = phone
        self.room_no = room_no
        self.admit_date = admit_date
        self.discharge_date = discharge_date
        return self

    def create_from_record(self, record):
        self.patient_id = record['id']
        self.name = record['name']
        self.address = record['address']
        self.phone = record['phone']
        self.room_no = record['room_no']
        self.admit_date = record['admit']
        self.discharge_date = record['discharge']
        return self

    def print_all(self):
        a = ("Patient #"+ str(self.patient_id))
        b = ("Name"+str(self.name))
        c = ("\nAddress: "+ self.address)
        d = ("\nPhone: "+ self.phone)
        e = ("\nAdmitted to room #"+ str(self.room_no), " on ", str(self.admit_date.strftime("%d %b %y")))
        f = ("\nDischarged: "+ str(self.discharge_date.strftime("%d %b %y")) if self.discharge_date is not None else None)
        finale=(a+b+c+d+"\n"+str(e)+"\n"+str(f))
        print(finale)
        pyautogui.alert(finale)
        
    def print_full(self):
        print_bar()
        a = ("Patient #"+ str(self.patient_id))
        c = ("\nAddress: "+ self.address)
        d = ("\nPhone: "+ self.phone)
        e = ("\nAdmitted to room #"+ str(self.room_no), " on ", str(self.admit_date.strftime("%d %b %y")))
        f = ("\nDischarged: "+ str(self.discharge_date.strftime("%d %b %y")) if self.discharge_date is not None else None)
        print_bar()
        pyautogui.alert(a+c+d+"\n"+str(e)+"\n"+str(f))


def create_patient(room_no):
    patient_id = None
    name = pyautogui.prompt("Enter the name: ")
    address = pyautogui.prompt("Enter the address: ")
    phone = pyautogui.prompt("Enter the phone: ")
    admit_date = datetime.now()
    return Patient().create(patient_id, name, address, phone, room_no, admit_date, None)


def print_patient_header():
    print("="*100)
    print("id".ljust(3),
          "name".ljust(15),
          "address".ljust(15),
          "phone".ljust(15),
          "room no".ljust(10),
          "admit".ljust(15),
          "discharge".ljust(15))
    print("="*100)


def create_patient_table(database):
    cursor = database.cursor()
    cursor.execute("DROP table if exists {0}".format(PATIENT_TABLE_NAME))
    cursor.execute("create table {0} ("
                   "id int primary key auto_increment,"
                   "name varchar(20),"
                   "address varchar(50),"
                   "phone varchar(10),"
                   "room_no int,"
                   "admit datetime,"
                   "discharge datetime)".format(PATIENT_TABLE_NAME))


NUMBER_OF_RECORDS_PER_PAGE = 10

def add_patient(database, cursor):
    room = get_and_print_room_by_no(cursor)
    if room is not None:
        patient = create_patient(room.room_no)
        confirm = pyautogui.confirm("Confirm discharge? (Y/N): ",buttons=['yes', 'no'])
        if confirm == 'yes':
            query = "insert into {0}(name, address, phone, room_no, admit) values('{1}','{2}','{3}',{4},'{5}')". \
                format(PATIENT_TABLE_NAME, patient.name, patient.address, patient.phone,
                       patient.room_no, patient.admit_date.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                cursor.execute(query)
                database.commit()
            except mysql.connector.Error:
                create_patient_table(database)
                cursor.execute(query)
                database.commit()
            change_room_status(database, cursor, room.room_id, False)
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Canceled")


def show_patient_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_patient_header()
        for record in records:
            patient = Patient().create_from_record(record)
            patient.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)


def show_patient_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        patient = Patient().create_from_record(record)
        patient.print_full()
        return patient
    except mysql.connector.Error as err:
        print(err)


def get_and_print_patient_by_room_no(cursor):
    room = get_and_print_room_by_no(cursor)
    if room is not None:
        query = "select * from {0} where room_no={1} order by id desc limit 1".format(PATIENT_TABLE_NAME, room.room_no)
        patient = show_patient_record(cursor, query)
        return room, patient
    return None, None


def discharge(database, cursor):
    room, patient = get_and_print_patient_by_room_no(cursor)
    if room is not None and patient is not None:
        confirm = pyautogui.confirm("Confirm discharge? (Y/N): ",buttons=['yes', 'no'])
        if confirm == 'yes':
            discharge = datetime.now()
            query = "update {0} set discharge='{1}' where id={2}".\
                format(PATIENT_TABLE_NAME, discharge.strftime("%Y-%m-%d %H:%M:%S"), patient.patient_id)
            cursor.execute(query)
            database.commit()
            change_room_status(database, cursor,room.room_id, True)
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def edit_patient_by_room_no(database, cursor):
    room, patient = get_and_print_patient_by_room_no(cursor)
    if room is not None and patient is not None:
        query = "update {0} set".format(PATIENT_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        name = pyautogui.prompt("Enter new name: ")
        if len(name) > 0:
            query += " name='{0}',".format(name)
        address = pyautogui.prompt("Enter new address: ")
        if len(address) > 0:
            query += " address='{0}',".format(address)
        phone = pyautogui.prompt("Enter number of phone: ")
        if len(phone) > 0:
            query += " phone='{0}',".format(phone)
        query = query[0:-1] + " where id={0}".format(patient.patient_id)
        confirm =  pyautogui.confirm("Confirm update? (Y/N): ",buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def delete_patient_by_room_no(database, cursor):
    room, patient = get_and_print_patient_by_room_no(cursor)
    if room is not None and patient is not None:
        confirm =  pyautogui.confirm("Confirm update? (Y/N): ",buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            query = "delete from {0} where id={1}".format(PATIENT_TABLE_NAME, patient.patient_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def patient_menu(database, cursor):
    while True:

        choice = int(pyautogui.prompt("""        
        ==============================
        ==========Patient Menu=========
        ==============================

        ENTER YOUR CHOICE:-
         
        1. New Patient
        2. Show Patient Details by name
        3. Show Patient details by patient_id
        4. Show Patient details by address
        5. Show Patient details by phone number
        6. Show Patient details by room no
        7. Show Patient details by admit date
        8. Show current list of Patients
        9. Discharge
        10. Edit Patient Details
        11. Delete Patient record
        12. View all Patients
        0. Go Back"""))
        if choice == 1:
            add_patient(database, cursor)
        elif choice == 2:
            name = pyautogui.prompt("Enter the name: ").lower()
            query = "select * from {0} where name like '%{1}%'".format(PATIENT_TABLE_NAME, name)
            show_patient_records(cursor, query)
        elif choice == 3:
            patient_id = pyautogui.prompt("Enter the patient id: ")
            query = "select * from {0} where id = {1}".format(PATIENT_TABLE_NAME, patient_id)
            show_patient_record(cursor, query)
        elif choice == 4:
            address = pyautogui.prompt("Enter the address: ").lower()
            query = "select * from {0} where address like '%{1}%'".format(PATIENT_TABLE_NAME, address)
            show_patient_records(cursor, query)
        elif choice == 5:
            phone = pyautogui.prompt("Enter the phone number: ")
            query = "select * from {0} where phone like '%{1}%'".format(PATIENT_TABLE_NAME, phone)
            show_patient_records(cursor, query)
        elif choice == 6:
            room_no = pyautogui.prompt("Enter the room_no: ")
            query = "select * from {0} where room_no = {1}".format(PATIENT_TABLE_NAME, room_no)
            show_patient_record(cursor, query)
        elif choice == 7:
            print("Enter the admit date: ")
            day = int(pyautogui.prompt("day of month: "))
            month = int(pyautogui.prompt("month: "))
            year = int(pyautogui.prompt("year: "))
            query = "select * from {0} where date(admit) = '{1}-{2}-{3}'".format(PATIENT_TABLE_NAME, year, month, day)
            show_patient_records(cursor, query)
        elif choice == 8:
            query = "select * from {0} where discharge is null".format(PATIENT_TABLE_NAME)
            show_patient_records(cursor, query)
        elif choice == 9:
            discharge(database, cursor)
        elif choice == 10:
            edit_patient_by_room_no(database, cursor)
        elif choice == 11:
            delete_patient_by_room_no(database, cursor)
        elif choice == 12:
            query = "select * from {0}".format(PATIENT_TABLE_NAME)
            show_patient_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")

            
DOCTOR_TABLE_NAME = "doctors"

class Doctor:
    def __init__(self):
        self.doctor_id = 0
        self.name = ""
        self.specialization = ""
        self.experience = ""
        self.room_no = ""  # New field for room number

    def create(self, doctor_id, name, specialization, experience, room_no):  # Include room_no parameter
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.experience = experience
        self.room_no = room_no  # Set room number
        return self

    def create_from_record(self, record):
        self.doctor_id = record['id']
        self.name = record['name']
        self.specialization = record['specialization']
        self.experience = record['experience']
        self.room_no = record['room_no']  # Set room number from record
        return self

    def print_all(self):
        a = ("Doctor #" + str(self.doctor_id))
        b = ("\nName: " + self.name)
        c = ("\nSpecialization: " + self.specialization)
        d = ("\nExperience: " + str(self.experience))
        e = ("\nRoom Number: " + str(self.room_no))  # Include room number in printout
        pyautogui.alert(a + b + c + d + e)

    def print_full(self):
        print_bar()
        a = ("Doctor #" + str(self.doctor_id))
        b = ("\nName: " + self.name)
        c = ("\nSpecialization: " + self.specialization)
        d = ("\nExperience: " + str(self.experience))
        e = ("\nRoom Number: " + str(self.room_no))  # Include room number in printout
        print_bar()
        pyautogui.alert(a + b + c + d + e)


def create_doctor():
    doctor_id = None
    name = pyautogui.prompt("Enter the name: ")
    specialization = pyautogui.prompt("Enter the specialization: ")
    experience = pyautogui.prompt("Enter the experience (in years): ")
    room_no = pyautogui.prompt("Enter the room number: ")  # Prompt for room number
    return Doctor().create(doctor_id, name, specialization, experience, room_no)


def create_doctor_table(database):
    cursor = database.cursor()
    cursor.execute("DROP TABLE IF EXISTS {0}".format(DOCTOR_TABLE_NAME))
    cursor.execute("CREATE TABLE {0} ("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "name VARCHAR(20),"
                   "specialization VARCHAR(20),"
                   "experience INT,"
                   "room_no INT)".format(DOCTOR_TABLE_NAME))


def add_doctor(database, cursor):
    doctor = create_doctor()
    query = "INSERT INTO {0}(name, specialization, experience, room_no) VALUES('{1}', '{2}', {3}, {4})". \
        format(DOCTOR_TABLE_NAME, doctor.name, doctor.specialization, doctor.experience, doctor.room_no)
    try:
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")
    except mysql.connector.Error:
        create_doctor_table(database)
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")


def show_doctor_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_doctor_header()
        for record in records:
            doctor = Doctor().create_from_record(record)
            doctor.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)

def print_doctor_header():
    print("Doctor ID | Name | Specialization | Experience | Room Number")
    print("-" * 50)

def show_doctor_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        doctor = Doctor().create_from_record(record)
        doctor.print_full()
        return doctor
    except mysql.connector.Error as err:
        print(err)


def get_and_print_doctor_by_id(cursor):
    doctor_id = pyautogui.prompt("Enter the doctor ID: ")
    query = "SELECT * FROM {0} WHERE id={1}".format(DOCTOR_TABLE_NAME, doctor_id)
    doctor = show_doctor_record(cursor, query)
    return doctor


def get_and_print_doctor_by_room(cursor):
    room_no = pyautogui.prompt("Enter the room number: ")
    query = "SELECT * FROM {0} WHERE room_no={1}".format(DOCTOR_TABLE_NAME, room_no)
    doctor = show_doctor_record(cursor, query)
    return doctor


def edit_doctor_by_id(database, cursor):
    doctor = get_and_print_doctor_by_id(cursor)
    if doctor is not None:
        query = "UPDATE {0} SET".format(DOCTOR_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        name = pyautogui.prompt("Enter new name: ")
        if len(name) > 0:
            query += " name='{0}',".format(name)
        specialization = pyautogui.prompt("Enter new specialization: ")
        if len(specialization) > 0:
            query += " specialization='{0}',".format(specialization)
        experience = pyautogui.prompt("Enter new experience: ")
        if len(experience) > 0:
            query += " experience={0},".format(experience)
        room_no = pyautogui.prompt("Enter new room number: ")
        if len(room_no) > 0:
            query += " room_no={0},".format(room_no)
        query = query[:-1] + " WHERE id={0}".format(doctor.doctor_id)
        confirm = pyautogui.confirm("Confirm update? (Y/N): ", buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def delete_doctor_by_id(database, cursor):
    doctor = get_and_print_doctor_by_id(cursor)
    if doctor is not None:
        confirm = pyautogui.confirm("Confirm deletion? (Y/N): ", buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            query = "DELETE FROM {0} WHERE id={1}".format(DOCTOR_TABLE_NAME, doctor.doctor_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def doctor_menu(database, cursor):
    while True:
        choice = int(pyautogui.prompt("""
        =============================
        ========Doctor Menu==========
        =============================
        1. Add New Doctor
        2. Show Doctor Details by ID
        3. Show Doctor Details by Room Number
        4. Edit Doctor Details
        5. Delete Doctor
        6. View All Doctors
        0. Go Back
        Enter your choice: """))
        if choice == 1:
            add_doctor(database, cursor)
        elif choice == 2:
            doctor_id = pyautogui.prompt("Enter the doctor ID: ")
            query = "SELECT * FROM {0} WHERE id={1}".format(DOCTOR_TABLE_NAME, doctor_id)
            show_doctor_record(cursor, query)
        elif choice == 3:
            get_and_print_doctor_by_room(cursor)
        elif choice == 4:
            edit_doctor_by_id(database, cursor)
        elif choice == 5:
            delete_doctor_by_id(database, cursor)
        elif choice == 6:
            query = "SELECT * FROM {0}".format(DOCTOR_TABLE_NAME)
            show_doctor_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")

PATIENT_HISTORY_TABLE_NAME = "patient_history"

class PatientPastHistory:
    def __init__(self):
        self.patient_id = 0
        self.name = ""
        self.age = ""
        self.sex = ""
        self.medical_history = ""
        self.surgical_history = ""
        self.medications = ""
        self.allergies = ""
        self.injuries_accidents = ""

    def create(self, patient_id, name, age, sex, medical_history, surgical_history, medications, allergies, injuries_accidents):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.sex = sex
        self.medical_history = medical_history
        self.surgical_history = surgical_history
        self.medications = medications
        self.allergies = allergies
        self.injuries_accidents = injuries_accidents
        return self

    def create_from_record(self, record):
        self.patient_id = record['patient_id']
        self.name = record['name']
        self.age = record['age']
        self.sex = record['sex']
        self.medical_history = record['medical_history']
        self.surgical_history = record['surgical_history']
        self.medications = record['medications']
        self.allergies = record['allergies']
        self.injuries_accidents = record['injuries_accidents']
        return self

    def print_all(self):
        a = ("Name: " + self.name)
        b = ("\nAge: " + self.age)
        c = ("\nSex: " + self.sex)
        d = ("\nMedical History: " + self.medical_history)
        e = ("\nSurgical History: " + self.surgical_history)
        f = ("\nMedications: " + self.medications)
        g = ("\nAllergies: " + self.allergies)
        h = ("\nInjuries and Accidents: " + self.injuries_accidents)
        pyautogui.alert(a + b + c + d + e + f + g + h)

    def print_full(self):
        print_bar()
        a = ("Name: " + self.name)
        b = ("\nAge: " + self.age)
        c = ("\nSex: " + self.sex)
        d = ("\nMedical History: " + self.medical_history)
        e = ("\nSurgical History: " + self.surgical_history)
        f = ("\nMedications: " + self.medications)
        g = ("\nAllergies: " + self.allergies)
        h = ("\nInjuries and Accidents: " + self.injuries_accidents)
        print_bar()
        pyautogui.alert(a + b + c + d + e + f + g + h)

def create_patient_past_history(database, cursor):
    patient_id = None  # Assume auto-incremented
    name = pyautogui.prompt("Enter patient's name: ")
    age = pyautogui.prompt("Enter patient's age: ")
    sex = pyautogui.prompt("Enter patient's sex: ")
    medical_history = pyautogui.prompt("Enter patient's medical history: ")
    surgical_history = pyautogui.prompt("Enter patient's surgical history: ")
    medications = pyautogui.prompt("Enter patient's medications: ")
    allergies = pyautogui.prompt("Enter patient's allergies: ")
    injuries_accidents = pyautogui.prompt("Enter patient's injuries and accidents: ")
    patient_history = PatientPastHistory().create(patient_id, name, age, sex, medical_history, surgical_history, medications, allergies, injuries_accidents)
    add_patient_past_history(database, cursor, patient_history)

def add_patient_past_history(database, cursor, patient_past_history):
    query = "INSERT INTO {0}(name, age, sex, medical_history, surgical_history, medications, allergies, injuries_accidents) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)". \
        format(PATIENT_HISTORY_TABLE_NAME)
    values = (patient_past_history.name, patient_past_history.age, patient_past_history.sex,
              patient_past_history.medical_history, patient_past_history.surgical_history,
              patient_past_history.medications, patient_past_history.allergies,
              patient_past_history.injuries_accidents)
    try:
        cursor.execute(query, values)
        database.commit()
        pyautogui.alert("Operation Successful")
    except mysql.connector.Error:
        create_patient_past_history_table(database)
        cursor.execute(query, values)
        database.commit()
        pyautogui.alert("Operation Successful")

def create_patient_past_history_table(database):
    cursor = database.cursor()
    cursor.execute("DROP TABLE IF EXISTS {0}".format(PATIENT_HISTORY_TABLE_NAME))
    cursor.execute("CREATE TABLE {0} ("
                   "patient_id INT PRIMARY KEY AUTO_INCREMENT,"
                   "name VARCHAR(100),"
                   "age VARCHAR(10),"
                   "sex VARCHAR(10),"
                   "medical_history TEXT,"
                   "surgical_history TEXT,"
                   "medications TEXT,"
                   "allergies TEXT,"
                   "injuries_accidents TEXT)".format(PATIENT_HISTORY_TABLE_NAME))

def print_patient_past_history_header():
    print("Patient ID | Name | Age | Sex | Medical History | Surgical History | Medications | Allergies | Injuries and Accidents")
    print("-" * 100)
    
def show_patient_past_history_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_patient_past_history_header()
        for record in records:
            patient_past_history = PatientPastHistory().create_from_record(record)
            patient_past_history.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)

def show_patient_past_history_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        patient_past_history = PatientPastHistory().create_from_record(record)
        patient_past_history.print_full()
        return patient_past_history
    except mysql.connector.Error as err:
        print(err)

def get_and_print_patient_past_history_by_id(cursor):
    patient_id = pyautogui.prompt("Enter the patient ID: ")
    query = "SELECT * FROM {0} WHERE patient_id={1}".format(PATIENT_HISTORY_TABLE_NAME, patient_id)
    patient_past_history = show_patient_past_history_record(cursor, query)
    return patient_past_history

def edit_patient_past_history_by_id(database, cursor):
    patient_past_history = get_and_print_patient_past_history_by_id(cursor)
    if patient_past_history is not None:
        query = "UPDATE {0} SET".format(PATIENT_HISTORY_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        name = pyautogui.prompt("Enter new name: ")
        if len(name) > 0:
            query += " name='{0}',".format(name)
        age = pyautogui.prompt("Enter new age: ")
        if len(age) > 0:
            query += " age='{0}',".format(age)
        sex = pyautogui.prompt("Enter new sex: ")
        if len(sex) > 0:
            query += " sex='{0}',".format(sex)
        medical_history = pyautogui.prompt("Enter new medical history: ")
        if len(medical_history) > 0:
            query += " medical_history='{0}',".format(medical_history)
        surgical_history = pyautogui.prompt("Enter new surgical history: ")
        if len(surgical_history) > 0:
            query += " surgical_history='{0}',".format(surgical_history)
        medications = pyautogui.prompt("Enter new medications: ")
        if len(medications) > 0:
            query += " medications='{0}',".format(medications)
        allergies = pyautogui.prompt("Enter new allergies: ")
        if len(allergies) > 0:
            query += " allergies='{0}',".format(allergies)
        injuries_accidents = pyautogui.prompt("Enter new injuries and accidents: ")
        if len(injuries_accidents) > 0:
            query += " injuries_accidents='{0}',".format(injuries_accidents)
        query = query[:-1] + " WHERE patient_id={0}".format(patient_past_history.patient_id)
        confirm = pyautogui.confirm("Confirm update? (Y/N): ", buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")

def delete_patient_past_history_by_id(database, cursor):
    patient_past_history = get_and_print_patient_past_history_by_id(cursor)
    if patient_past_history is not None:
        confirm = pyautogui.confirm("Confirm deletion? (Y/N): ", buttons=['yes', 'no']).lower()
        if confirm == 'yes':
            query = "DELETE FROM {0} WHERE patient_id={1}".format(PATIENT_HISTORY_TABLE_NAME, patient_past_history.patient_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")

def patient_past_history_menu(database, cursor):
    while True:
        choice = int(pyautogui.prompt("""
        ========================================
        ======== Patient History Menu ==========
        ========================================
        1. Add New Patient Past History
        2. Show Patient Past History Details by Patient ID
        3. Edit Patient Past History Details
        4. Delete Patient Past History
        5. View All Patient Past History
        0. Go Back
        Enter your choice: """))
        if choice == 1:
            create_patient_past_history(database, cursor)
        elif choice == 2:
            patient_id = pyautogui.prompt("Enter the patient ID: ")
            query = "SELECT * FROM {0} WHERE patient_id={1}".format(PATIENT_HISTORY_TABLE_NAME, patient_id)
            show_patient_past_history_record(cursor, query)
        elif choice == 3:
            edit_patient_past_history_by_id(database, cursor)
        elif choice == 4:
            delete_patient_past_history_by_id(database, cursor)
        elif choice == 5:
            query = "SELECT * FROM {0}".format(PATIENT_HISTORY_TABLE_NAME)
            show_patient_past_history_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")
  

PRESCRIPTIONS_TABLE_NAME = "prescriptions"


class Prescription:
    def __init__(self):
        self.prescription_id = 0
        self.patient_name = ""
        self.age = 0
        self.sex = ""
        self.diagnosis = ""
        self.tablets = []
        self.doctor_name = ""
        self.doctor_specialization = ""

    def create(self, patient_name, age, sex, diagnosis, tablets, doctor_name, doctor_specialization):
        self.patient_name = patient_name
        self.age = age
        self.sex = sex
        self.diagnosis = diagnosis
        self.tablets = tablets
        self.doctor_name = doctor_name
        self.doctor_specialization = doctor_specialization
        return self

    def create_from_record(self, record):
        self.prescription_id = record['id']
        self.patient_name = record['patient_name']
        self.age = record['age']
        self.sex = record['sex']
        self.diagnosis = record['diagnosis']
        self.tablets = record['tablets'].split(',') if record['tablets'] else []
        self.doctor_name = record['doctor_name']
        self.doctor_specialization = record['doctor_specialization']
        return self

    def print_all(self):
        print("=" * 100)
        print("Prescription ID: ", self.prescription_id)
        print("Patient Name: ", self.patient_name)
        print("Age: ", self.age)
        print("Sex: ", self.sex)
        print("Diagnosis: ", self.diagnosis)
        print("Tablets: ", ", ".join(self.tablets))
        print("Doctor Name: ", self.doctor_name)
        print("Doctor Specialization: ", self.doctor_specialization)


def create_prescription():
    patient_name = pyautogui.prompt("Enter patient name: ")
    age = pyautogui.prompt("Enter patient age: ")
    sex = pyautogui.prompt("Enter patient sex: ")
    diagnosis = pyautogui.prompt("Enter diagnosis: ")
    tablets = []
    for i in range(1, 11):
        tablet = pyautogui.prompt(f"Enter tablet {i} (leave blank to stop): ")
        if not tablet:
            break
        tablets.append(tablet)
    doctor_name = pyautogui.prompt("Enter doctor name: ")
    doctor_specialization = pyautogui.prompt("Enter doctor specialization: ")
    return Prescription().create(patient_name, age, sex, diagnosis, tablets, doctor_name, doctor_specialization)


def print_prescription_header():
    print("="*100)
    print("id".ljust(3),
          "Patient Name".ljust(20),
          "Age".ljust(5),
          "Sex".ljust(5),
          "Diagnosis".ljust(20),
          "Doctor Name".ljust(20),
          "Doctor Specialization".ljust(20)
          )
    print("="*100)


def create_prescriptions_table(database):
    cursor = database.cursor()
    cursor.execute("DROP table if exists {0}".format(PRESCRIPTIONS_TABLE_NAME))
    cursor.execute("create table {0} ("
                   "id int primary key auto_increment,"
                   "patient_name varchar(255),"
                   "age int,"
                   "sex varchar(10),"
                   "diagnosis varchar(255),"
                   "tablets varchar(255),"
                   "doctor_name varchar(255),"
                   "doctor_specialization varchar(255))".format(PRESCRIPTIONS_TABLE_NAME))


def add_prescription(database, cursor):
    prescription = create_prescription()
    query = "insert into {0}(patient_name,age,sex,diagnosis,tablets,doctor_name,doctor_specialization) " \
            "values('{1}',{2},'{3}','{4}','{5}','{6}','{7}')".format(PRESCRIPTIONS_TABLE_NAME,
                                                                       prescription.patient_name,
                                                                       prescription.age,
                                                                       prescription.sex,
                                                                       prescription.diagnosis,
                                                                       ','.join(prescription.tablets),
                                                                       prescription.doctor_name,
                                                                       prescription.doctor_specialization)
    try:
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")
    except mysql.connector.Error as err:
        create_prescriptions_table(database)
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")


def show_prescription_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        prescription = Prescription().create_from_record(record)
        prescription.print_all()
        return prescription
    except mysql.connector.Error as err:
        print(err)


def show_prescription_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_prescription_header()
        for record in records:
            prescription = Prescription().create_from_record(record)
            prescription.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)


def get_and_print_prescription_by_id(cursor):
    prescription_id = pyautogui.prompt("Enter the prescription ID: ")
    query = "select * from {0} where id={1}".format(PRESCRIPTIONS_TABLE_NAME, prescription_id)
    prescription = show_prescription_record(cursor, query)
    return prescription


def edit_prescription_by_id(database, cursor):
    prescription = get_and_print_prescription_by_id(cursor)
    if prescription is not None:
        query = "update {0} set".format(PRESCRIPTIONS_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        patient_name = pyautogui.prompt("Enter new patient name: ")
        if len(patient_name) > 0:
            query += " patient_name='{0}',".format(patient_name)
        age = pyautogui.prompt("Enter new age: ")
        if len(age) > 0:
            query += " age={0},".format(age)
        sex = pyautogui.prompt("Enter new sex: ")
        if len(sex) > 0:
            query += " sex='{0}',".format(sex)
        diagnosis = pyautogui.prompt("Enter new diagnosis: ")
        if len(diagnosis) > 0:
            query += " diagnosis='{0}',".format(diagnosis)
        # Editing tablets can be complex, here you need to decide the strategy
        # Let's assume we won't edit tablets here for simplicity
        doctor_name = pyautogui.prompt("Enter new doctor name: ")
        if len(doctor_name) > 0:
            query += " doctor_name='{0}',".format(doctor_name)
        doctor_specialization = pyautogui.prompt("Enter new doctor specialization: ")
        if len(doctor_specialization) > 0:
            query += " doctor_specialization='{0}',".format(doctor_specialization)
        query = query[0:-1] + " where id={0}".format(prescription.prescription_id)
        confirm = pyautogui.prompt("Confirm Update (Y/N): ").lower()
        if confirm == 'y':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def delete_prescription_by_id(database, cursor):
    prescription = get_and_print_prescription_by_id(cursor)
    if prescription is not None:
        confirm = pyautogui.prompt("Confirm Deletion (Y/N): ").lower()
        if confirm == 'y':
            query = "delete from {0} where id={1}".format(PRESCRIPTIONS_TABLE_NAME, prescription.prescription_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def prescription_menu(database, cursor):
    while True:
        choice = int(pyautogui.prompt("""
           PRESCRIPTION MENU
        1. Add New Prescription
        2. Show Prescription Details by ID
        3. Edit Prescription Details
        4. Delete Prescription
        5. View All Prescriptions
        0. Go Back"""))

        if choice == 1:
            add_prescription(database, cursor)
        elif choice == 2:
            get_and_print_prescription_by_id(cursor)
        elif choice == 3:
            edit_prescription_by_id(database, cursor)
        elif choice == 4:
            delete_prescription_by_id(database, cursor)
        elif choice == 5:
            query = "select * from {0}".format(PRESCRIPTIONS_TABLE_NAME)
            show_prescription_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")

import pyautogui
import mysql.connector

LAB_REPORTS_TABLE_NAME = "lab_reports"


class LabReport:
    def __init__(self):
        self.report_id = 0
        self.patient_name = ""
        self.age = 0
        self.sex = ""
        self.haemoglobin = 0.0
        self.rbc_count = 0.0
        self.wbc_count = 0.0
        self.blood_pressure = ""
        self.diabetic = ""
        self.other_test_report = ""

    def create(self, report_id, patient_name, age, sex, haemoglobin, rbc_count, wbc_count, blood_pressure, diabetic,
               other_test_report):
        self.report_id = report_id
        self.patient_name = patient_name
        self.age = age
        self.sex = sex
        self.haemoglobin = haemoglobin
        self.rbc_count = rbc_count
        self.wbc_count = wbc_count
        self.blood_pressure = blood_pressure
        self.diabetic = diabetic
        self.other_test_report = other_test_report
        return self

    def create_from_record(self, record):
        self.report_id = record['id']
        self.patient_name = record['patient_name']
        self.age = record['age']
        self.sex = record['sex']
        self.haemoglobin = record['haemoglobin']
        self.rbc_count = record['rbc_count']
        self.wbc_count = record['wbc_count']
        self.blood_pressure = record['blood_pressure']
        self.diabetic = record['diabetic']
        self.other_test_report = record['other_test_report']
        return self

    def print_all(self):
        print("=" * 100)
        print("Report ID: ", self.report_id)
        print("Patient Name: ", self.patient_name)
        print("Age: ", self.age)
        print("Sex: ", self.sex)
        print("Haemoglobin: ", self.haemoglobin)
        print("RBC Count: ", self.rbc_count)
        print("WBC Count: ", self.wbc_count)
        print("Blood Pressure: ", self.blood_pressure)
        print("Diabetic: ", self.diabetic)
        print("Other Test Report: ", self.other_test_report)


def create_lab_report():
    report_id = None
    patient_name = pyautogui.prompt("Enter patient name: ")
    age = pyautogui.prompt("Enter patient age: ")
    sex = pyautogui.prompt("Enter patient sex: ")
    haemoglobin = pyautogui.prompt("Enter Haemoglobin (Hb) value (13.0 to 17.0 g/dL): ")
    rbc_count = pyautogui.prompt("Enter RBC Count value (4.5 to 5.5 mill/cumm): ")
    wbc_count = pyautogui.prompt("Enter WBC Count value (4000 to 11000 cumm): ")
    blood_pressure = pyautogui.prompt("Enter Blood Pressure (ranges between 90/60mmHg and 120/80mmHg): ")
    diabetic = pyautogui.prompt("Is the patient diabetic? (Yes/No): ").lower()
    other_test_report = pyautogui.prompt("Do you have another test report? (Yes/No): ").lower()

    if other_test_report == 'yes':
        test_name = pyautogui.prompt("Enter test name: ")
        test_result = pyautogui.prompt("Enter test result: ")
        other_test_report = f"{test_name}: {test_result}"

    return LabReport().create(report_id, patient_name, age, sex, haemoglobin, rbc_count, wbc_count,
                              blood_pressure, diabetic, other_test_report)


def print_lab_report_header():
    print("="*100)
    print("id".ljust(3),
          "Patient Name".ljust(20),
          "Age".ljust(5),
          "Sex".ljust(5),
          "Haemoglobin".ljust(15),
          "RBC Count".ljust(15),
          "WBC Count".ljust(15),
          "Blood Pressure".ljust(20),
          "Diabetic".ljust(10),
          "Other Test Report".ljust(30)
          )
    print("="*100)


def create_lab_reports_table(database):
    cursor = database.cursor()
    cursor.execute("DROP table if exists {0}".format(LAB_REPORTS_TABLE_NAME))
    cursor.execute("create table {0} ("
                   "id int primary key auto_increment,"
                   "patient_name varchar(255),"
                   "age int,"
                   "sex varchar(10),"
                   "haemoglobin varchar(10),"
                   "rbc_count varchar(10),"
                   "wbc_count varchar(10),"
                   "blood_pressure varchar(20),"
                   "diabetic varchar(5),"
                   "other_test_report text)".format(LAB_REPORTS_TABLE_NAME))


def add_lab_report(database, cursor):
    lab_report = create_lab_report()
    query = "insert into {0}(patient_name,age,sex,haemoglobin,rbc_count,wbc_count,blood_pressure,diabetic," \
            "other_test_report) values('{1}',{2},'{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(
        LAB_REPORTS_TABLE_NAME, lab_report.patient_name, lab_report.age, lab_report.sex, lab_report.haemoglobin,
        lab_report.rbc_count, lab_report.wbc_count, lab_report.blood_pressure, lab_report.diabetic,
        lab_report.other_test_report)
    try:
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")
    except mysql.connector.Error as err:
        create_lab_reports_table(database)
        cursor.execute(query)
        database.commit()
        pyautogui.alert("Operation Successful")


def show_lab_report_record(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        record = records[0]
        lab_report = LabReport().create_from_record(record)
        lab_report.print_all()
        return lab_report
    except mysql.connector.Error as err:
        print(err)


def show_lab_report_records(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            pyautogui.alert("No Matching Records")
            return
        print_lab_report_header()
        for record in records:
            lab_report = LabReport().create_from_record(record)
            lab_report.print_all()
        return records
    except mysql.connector.Error as err:
        print(err)


def get_and_print_lab_report_by_id(cursor):
    report_id = pyautogui.prompt("Enter the report ID: ")
    query = "select * from {0} where id={1}".format(LAB_REPORTS_TABLE_NAME, report_id)
    lab_report = show_lab_report_record(cursor, query)
    return lab_report


def edit_lab_report_by_id(database, cursor):
    lab_report = get_and_print_lab_report_by_id(cursor)
    if lab_report is not None:
        query = "update {0} set".format(LAB_REPORTS_TABLE_NAME)
        pyautogui.alert("Input new values (leave blank to keep previous value)")
        patient_name = pyautogui.prompt("Enter new patient name: ")
        if len(patient_name) > 0:
            query += " patient_name='{0}',".format(patient_name)
        age = pyautogui.prompt("Enter new age: ")
        if len(age) > 0:
            query += " age={0},".format(age)
        sex = pyautogui.prompt("Enter new sex: ")
        if len(sex) > 0:
            query += " sex='{0}',".format(sex)
        haemoglobin = pyautogui.prompt("Enter new Haemoglobin (Hb) value: ")
        if len(haemoglobin) > 0:
            query += " haemoglobin='{0}',".format(haemoglobin)
        rbc_count = pyautogui.prompt("Enter new RBC Count value: ")
        if len(rbc_count) > 0:
            query += " rbc_count='{0}',".format(rbc_count)
        wbc_count = pyautogui.prompt("Enter new WBC Count value: ")
        if len(wbc_count) > 0:
            query += " wbc_count='{0}',".format(wbc_count)
        blood_pressure = pyautogui.prompt("Enter new Blood Pressure: ")
        if len(blood_pressure) > 0:
            query += " blood_pressure='{0}',".format(blood_pressure)
        diabetic = pyautogui.prompt("Is the patient diabetic? (Yes/No): ").lower()
        if len(diabetic) > 0:
            query += " diabetic='{0}',".format(diabetic)
        other_test_report = pyautogui.prompt("Enter new Other Test Report: ")
        if len(other_test_report) > 0:
            query += " other_test_report='{0}',".format(other_test_report)
        query = query[0:-1] + " where id={0}".format(lab_report.report_id)
        confirm = pyautogui.prompt("Confirm Update (Y/N): ").lower()
        if confirm == 'y':
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def delete_lab_report_by_id(database, cursor):
    lab_report = get_and_print_lab_report_by_id(cursor)
    if lab_report is not None:
        confirm = pyautogui.prompt("Confirm Deletion (Y/N): ").lower()
        if confirm == 'y':
            query = "delete from {0} where id={1}".format(LAB_REPORTS_TABLE_NAME, lab_report.report_id)
            cursor.execute(query)
            database.commit()
            pyautogui.alert("Operation Successful")
        else:
            pyautogui.alert("Operation Cancelled")


def lab_report_menu(database, cursor):
    while True:
        choice = int(pyautogui.prompt("""
           LAB REPORT MENU
        1. Add New Lab Report
        2. Show Lab Report Details by ID
        3. Edit Lab Report Details
        4. Delete Lab Report
        5. View All Lab Reports
        0. Go Back"""))

        if choice == 1:
            add_lab_report(database, cursor)
        elif choice == 2:
            get_and_print_lab_report_by_id(cursor)
        elif choice == 3:
            edit_lab_report_by_id(database, cursor)
        elif choice == 4:
            delete_lab_report_by_id(database, cursor)
        elif choice == 5:
            query = "select * from {0}".format(LAB_REPORTS_TABLE_NAME)
            show_lab_report_records(cursor, query)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to go back)")


# Modify the main menu to include the patient history menu
if __name__ == '__main__':
    database, cursor = get_database()
    if database is None:
        pyautogui.alert("The Database does not exist or is not accessible.")
        exit(1)
    while True:
        choice = int(pyautogui.prompt("""
                                      
         MEDICARE: HOSPITAL MANAGEMENT SYSTEM
                                      

        1. Manage Rooms
        2. Manage Patients
        3. Manage Doctors
        4. Manage Patients Past History 
        5. Manage Prescription 
        6. Manage Lab Records
        0. Exit
        Enter your choice: """))
        if choice == 1:
            room_menu(database, cursor)
        elif choice == 2:
            patient_menu(database, cursor)
        elif choice == 3:
            doctor_menu(database, cursor)
        elif choice == 4:  
            patient_past_history_menu(database, cursor)
        elif choice == 5:
            prescription_menu(database, cursor)
        elif choice == 6:
            lab_report_menu(database, cursor)
        elif choice == 0:
            break
        else:
            pyautogui.alert("Invalid choice (Press 0 to exit)")
    print_center("Goodbye")
