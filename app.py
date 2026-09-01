
#handtyped below....
from flask import Flask,jsonify,request
from flask_cors import CORS 
import sqlite3
import hmac
import hashlib
import os
from utilities import generate_qr, verify_signed_token ,create_signed_token




app = Flask(__name__)
CORS(app)

#list of dictionary of students..
students = [ {"name": "Aravind", "roll": "B251244EE", "email":"xxx@gmail.com" , "ticket_issued": True},
             {"name": "Priya", "roll": "B250222EE", "email":"yyy@gmail.com" , "ticket_issued": False},  
             {"name": "Anish", "roll": "B250522EE", "email":"kkk@gmail.com" , "ticket_issued": False}, ]

def get_db():
    conn=sqlite3.connect('tickets.db')
    conn.row_factory=sqlite3.Row #using this columns can be accessed by names...llike student['roll_number]..
    return conn

#TASK_1 : checking if server is alive. used for error testing on the fest day
#using this it can be checked if the error is with the server or the code..

@app.route('/status',methods=['GET'])
def status():
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM student')  #SELECT COUNT(*) counts all rows and returns a result that looks like this:(3,)
    count=cursor.fetchone()[0]
    conn.close()
    return jsonify({
        'status':'running','total_students':'count'
    })

from dotenv import load_dotenv
load_dotenv()  #reads '.env'
SECRET_KEY=os.environ.get('SECRET_KEY')


def verify_signed_token(token):
    token=token.replace('TICKET:',' ')
    parts=token.split('.')

    roll_number=parts[0]
    received_signature=parts[1]

    expected_signature=hmac.new(
        SECRET_KEY.encode(),
        roll_number.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    if hmac.compare_digest(received_signature,expected_signature):
        return roll_number #the above form of comparison is used to prevent hacking..
    
    return None


#TASK_2 : verifying a ticket at gate . This can be done after confirming that the server is running..
@app.route('/verify',methods=['POST'])
def verify():
    data=request.get_json()
    token=data['code']

    # Strip the prefix to get the roll number
    roll = verify_signed_token(token)

    if roll is None:
        return jsonify({ 'valid': False, 'message': 'Fake or invalid QR' })

    conn=get_db()
    cursor=conn.cursor()

    cursor.execute('SELECT * FROM students WHERE roll_number=?',(roll,))
    student=cursor.fetchone()

    if student['ticket_issued']==1:
        conn.close()
        return jsonify({'valid':False , 'message':'ALREADY SCANNED'})
    
    if student is None:
        conn.close()
        return jsonify({'valid':False , 'message':'STUDENT NOT FOUND'})
    
    cursor.execute('UPDATE students SET ticket_issued=1 WHERE roll_number=?',(roll,))

    conn.commit()
    conn.close()

    return jsonify({'valid':True,'name':student['name']})





#WE OPERATE THE ADMIN PANEL FROM HERE...
import csv
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

MAIL_USER = os.environ.get('MAIL_USER')
MAIL_PASS = os.environ.get('MAIL_PASS')

def send_ticket_email(student_name,student_email,roll_number):
    #we build the mail , the body ,from , to etc
    msg=MIMEMultipart()
    msg['From']=MAIL_USER
    msg['To']=student_email
    msg['Subject']='TATHVA 2024 Tickets'

     # Email body
    body = f"""
Hi {student_name},

Your ticket for TATHVA 2026 DAY 1 is attached below.

Show the attached QR code at the entry gate on the day of the event.
Do not share it with anyone , each QR is unique to a particular person.
Upon scanning the QR your face will be verified at the entrance , so all the students 
are strictly adviced to not sell their tickets or any such malpractise to avoid 
further action .

See you there,
Greetings,
TATHVA Committee
    """

    msg.attach(MIMEText(body, 'plain'))

    # Attach the QR code image
    qr_path = f'qrcodes/{roll_number}.png'
    with open(qr_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header(
            'Content-Disposition',
            'attachment',
            filename=f'{roll_number}_ticket.png'
        )
        msg.attach(img)

    # Send via Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)   

@app.route('/admin/upload',methods=['POST'])         
def admin_upload():
    if 'file' not in request.files:
        return jsonify({ 'error': 'No file uploaded' }), 400

    file = request.files['file']
    content = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))

    results = []
    success_count = 0
    error_count = 0

    conn = get_db()
    cursor = conn.cursor()

    for row in reader:
        name=row['name'].strip()
        roll_number=row['roll_number'].strip()
        email=row['email'].strip()

        try:
            #to insert into database ,skip if it already exists..
            cursor.execute('''INSERT OR IGNORE INTO students
                              (name,roll_number,email,ticket_issued)
                              VALUES(?,?,?,0)''', (name,roll_number,email))
             
            conn.commit()

            #to generate qr..
            generate_qr(roll_number)

            # Send email
            send_ticket_email(name, email, roll_number)

            results.append({
                'name': name,
                'roll_number': roll_number,
                'success': True
            })
            success_count += 1



        except Exception as e:
            results.append({
                'name': name,
                'roll_number': roll_number,
                'success': False,
                'error': str(e)
            })
            error_count += 1    
    
    conn.close()

    return jsonify({
        'results': results,
        'success_count': success_count,
        'error_count': error_count
    })




from flask import Flask, jsonify, request, send_from_directory

@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

#to get css file , this is technically used to start up the static files without this the css file wont start..
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)



if __name__=='__main__':
    app.run(debug=True)