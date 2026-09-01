
#self typed below...
#to setup a database

import sqlite3
conn=sqlite3.connect('tickets.db')
conn.row_factory=sqlite3.Row 
cursor=conn.cursor()
from utilities import generate_qr

students=[
    ('Aravind', 'B251244EE', 'xxx@gmail.com', 0),
    ('Priya',   'B250222EE', 'yyy@gmail.com', 0),
    ('Anish',   'B250522EE', 'kkk@gmail.com', 0),
    ('Santosh', 'B250496CS', 'sss@gmail.com', 0),
]

#triple inverted commas must be used if you plan to break the string .
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        roll_number   TEXT NOT NULL UNIQUE,
        email         TEXT NOT NULL,
        ticket_issued INTEGER DEFAULT 0
    )
            ''')

cursor.executemany(
    '''INSERT OR IGNORE INTO students(name,roll_number,email,ticket_issued)
       VALUES (?,?,?,?)
    ''',students
)


conn.commit()  #used for saving whatever is written
conn.close()






#connecting to the database.
conn=sqlite3.connect('tickets.db')
conn.row_factory=sqlite3.Row 
cursor=conn.cursor()
cursor.execute('SELECT roll_number FROM students')
students=cursor.fetchall()

for student in students:
    roll=student['roll_number']
    generate_qr(roll)
    print(f'QR has been generated for {roll}')

conn.close()
print('all qr codes generated')    
