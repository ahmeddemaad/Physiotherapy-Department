#from crypt import methods
from distutils.log import debug
import email
from email import message
from time import strptime
from time import mktime
from webbrowser import Elinks
import pandas as pd
from datetime import datetime
from datetime import timedelta
from genericpath import exists
from unittest import result
from flask import Flask, flash, redirect, render_template,request,session,url_for
from pymysql import NULL
# from sqlalchemy import false
# from flask_mysqldb import MySQL
import mysql.connector
import re
import os
import secrets

app = Flask(__name__)
app.secret_key = "very secret key"
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="magdynasr",
    database="felcode"
)
mycursor = mydb.cursor(buffered=True)

# ----------------------------------------------------------------------------save picture-----------------------------------------------------
def save_picture(form_picture):
    fname = secrets.token_hex(16) #new name
    _, f_ext = os.path.splitext(form_picture.filename) #get rid of old name
    picture_fn = fname + f_ext #combine extention "png for example" with new name
    picture_path = os.path.join( 'static/imgs/uploads', picture_fn) #combine path with name
    picture_path = picture_path.replace('\\','/')
    form_picture.save(picture_path)
    return picture_path

# -----------------------------------------------------------------------------index-----------------------------------------------------------
@app.route('/')
@app.route('/home',methods=["GET","POST"])
def index():
    if request.method == "POST":
        email = request.form['email']
        message = request.form['message']
        sql = """INSERT INTO contact_us (email, message) VALUES (%s,%s)"""
        val = (email, message)
        mycursor.execute(sql,val)
        mydb.commit()
        return redirect(url_for('index'))

    sql1 = "SELECT name,email,id,photo,specialization FROM doctor"
    mycursor.execute(sql1)
    resultDoctor = mycursor.fetchall()
    sqlCountDoctor = "SELECT COUNT(name) FROM doctor"
    mycursor.execute(sqlCountDoctor)
    sqlCountDoctor = mycursor.fetchall()
    sql2 = "SELECT COUNT(id) FROM patient"
    mycursor.execute(sql2)
    resultPatient = mycursor.fetchall()
    sql3 = "SELECT SUM(count) FROM device"
    mycursor.execute(sql3)
    resultDevice = mycursor.fetchall()
    sql4 = "SELECT COUNT(appNo) FROM appointment"
    mycursor.execute(sql4)
    result4 = mycursor.fetchall()
    sql5 = "SELECT COUNT(feedback) FROM feedback"
    mycursor.execute(sql5)
    result5 = mycursor.fetchall()
    return render_template("index.html",dataDoctor = resultDoctor, dataPatient = resultPatient, dataDevice = resultDevice, data4 = result4,
    sqlCountDoctor = sqlCountDoctor, data5 = result5)

# ------------------------------------------------------------------------feedback--------------------------------------------------------------
@app.route('/')
@app.route('/home/feedback',methods=["GET","POST"])
def feedback():
    if request.method == "POST":
        feedbackMessage = request.form['feedback']

        sql5 = """INSERT INTO feedback (feedback) VALUES (%s)"""
        val5= (feedbackMessage,)
        mycursor.execute(sql5,val5)
        mydb.commit()
        return redirect(url_for('index'))

# ------------------------------------------------------------------------Pre Sign Up---------------------------------------------------------------------
@app.route('/preSignUp')
def preSignUp():
    return render_template('preSignUp.html')

# -------------------------------------------------------------------------My Tips---------------------------------------------------------------------
@app.route('/myTips')
def myTips():
    return render_template('myTips.html')

# -------------------------------------------------------------------------Profile---------------------------------------------------------------------
@app.route('/profileh')
def profileh():
    if 'user_patient' in session or 'user_doctor' in session and 'loggedIn' in session :  

        if 'loggedIn' in session and 'user_patient' in session :
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT * FROM patient WHERE email = %s', (session['user_patient'],))
            result = cursor.fetchall()
            sql = """SELECT appNo,doctor.name,startT,endT,dt FROM appointment join patient on patientEmail = patient.email join doctor on doctorEmail= doctor.email
                where patientEmail =  %s """
            val =(session["user_patient"],)
            cursor.execute(sql , val)
            appointment = cursor.fetchall()
            empty = True
            if appointment:
                empty = False
            return render_template('profileh.html',data = result , appointment=appointment,empty = empty)
            
        elif 'loggedIn' in session and 'user_doctor' in session :
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT * FROM doctor WHERE email = %s', (session['user_doctor'],))
            result = cursor.fetchall()
            return render_template('profileh.html',data = result,empty = True)
        else:
            return render_template('profileh.html')
    else:
        return redirect(url_for('index'))          

# ------------------------------------------------------------------------EditProfile---------------------------------------------------------------------
@app.route('/editprofile', methods=["GET","POST"])
def editprofile():
    if 'user_patient' in session or 'user_doctor' in session and 'loggedIn' in session :  

        if 'loggedIn' in session and 'user_patient' in session and request.method == "GET" :
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT * FROM patient WHERE email = %s', (session['user_patient'],))
            result = cursor.fetchall()
            sql = """SELECT appNo,doctor.name,startT,endT,dt FROM appointment join patient on patientEmail = patient.email join doctor on doctorEmail= doctor.email
                where patientEmail =  %s """
            val =(session["user_patient"],)
            cursor.execute(sql , val)
            appointment = cursor.fetchall()
            empty = True
            if appointment:
                empty = False
            return render_template('editprofile.html',data = result , appointment=appointment,empty = empty)

        elif 'loggedIn' in session and 'user_patient' in session and request.method == "POST" :
            id = request.form['id']
            name = request.form['name']
            ssn = request.form['ssn']
            sex = request.form['sex']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            birth_date = request.form['birth_date']
            credit_card = request.form['credit_card']
            insurance_num = request.form['insurance_num']
            marital_status = request.form['marital_status']
            job = request.form['job']
            photo = request.files['photo']
            phone = request.form['phone']
            pic_path = save_picture(photo)

            updatesql = "UPDATE patient SET name = %s, ssn = %s,  address = %s, email = %s, password = %s, sex = %s, birth_date = %s,marital_status = %s,job = %s,insurance_num = %s, credit_card = %s, phone = %s, photo = %s WHERE id = %s"
            updateval = (name,ssn,address,email,password, sex,birth_date,marital_status,job, insurance_num,credit_card, phone, pic_path, id)
            mycursor.execute(updatesql, updateval)
            mydb.commit()

            sql1 = "UPDATE users SET email = %s, password= %s, type= %s WHERE email = %s"
            val1 = (email,password,'patient',email)
            mycursor.execute(sql1, val1)
            mydb.commit()

            return redirect(url_for('profileh'))

        elif 'loggedIn' in session and 'user_doctor' in session and request.method == "GET":
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT * FROM doctor WHERE email = %s', (session['user_doctor'],))
            result = cursor.fetchall()
            return render_template('editprofile.html',data = result,empty = True)
        
        elif 'loggedIn' in session and 'user_doctor' in session and request.method == "POST" :
            id = request.form['id']
            name = request.form['name']
            ssn=request.form['ssn']
            sex = request.form['sex']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            birth_date = request.form['birth_date']
            specialization = request.form['specialization']
            phone = request.form['phone']
            photo = request.files['photo']
            pic_path = save_picture(photo)

            sql = "UPDATE doctor SET name =%s, ssn=%s, sex=%s, email=%s, password=%s, address=%s, birth_date=%s,  specialization=%s, phone=%s, photo=%s WHERE id = %s"
            val = (name, ssn, sex, email, password, address, birth_date,  specialization, phone, pic_path, id)
            mycursor.execute(sql,val)
            mydb.commit()

            sql1 = "UPDATE users SET email = %s, password= %s, type= %s WHERE email = %s"
            val1 = (email,password,'patient',email)
            mycursor.execute(sql1, val1)
            mydb.commit()

            return redirect(url_for('profileh'))

        else:
            return render_template('editprofile.html')
    else:
        return redirect(url_for('index'))

# ------------------------------------------------------------------------ViewDevice---------------------------------------------------------------------

@app.route('/viewdevice')
def viewdevice():

    if 'user_admin' in session :  
        sql = "SELECT device_num,device_name,device_model,technician_id,technician_name,count,description FROM device"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        return render_template('viewdevice.html',data = result)
    else:
        return render_template('index.html')

# ------------------------------------------------------------------------Login---------------------------------------------------------------------
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        userEmail = request.form['email']
        password = request.form['password']
        mycursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",(userEmail,password))
        record = mycursor.fetchone()
        
        if record:
            if record[2] == 'patient':
                session['user_patient'] = userEmail
                session['loggedIn'] = True
                return redirect(url_for('index'))
            elif record[2] == 'doctor':
                session['user_doctor'] = userEmail
                session['loggedIn'] = True
                return redirect(url_for('index')) 
            else:
                session['user_admin'] = userEmail
                session['loggedIn'] = True
                return redirect(url_for('index'))      
        else:
            return render_template('login.html',msg = True)
    else:
        return render_template('login.html',msg = False)

# ------------------------------------------------------------------------Log Out-------------------------------------------------------------------
@app.route("/logout")
def logout():
    session.pop('loggedin',None)
    session.pop('user',None)
    session.clear()
    return redirect(url_for('index'))

# ------------------------------------------------------------------------Add Doctor----------------------------------------------------------------
@app.route('/adddoctor',methods = ['POST','GET'])
def adddoctor():
    if request.method == 'POST':
        #requesting data form
        name = request.form['name']
        ssn=request.form['ssn']
        sex = request.form['sex']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        birth_date = request.form['birth_date']
        specialization= request.form['specialization']
        phone = request.form['phone']
        photo = request.files['photo']
        pic_path = save_picture(photo)

        #setting a buffered cursor => to accept one value in the input
        emailCursor =mydb.cursor(buffered=True)
        emailCursor.execute(""" SELECT * FROM doctor WHERE email = %s """ , (email,))
        emailExist = emailCursor.fetchone()

        ssnCursor =mydb.cursor(buffered=True)
        ssnCursor.execute(""" SELECT * FROM doctor WHERE ssn = %s """ , (ssn,))
        ssnExist = ssnCursor.fetchone()

        reqemailCursor =mydb.cursor(buffered=True)
        reqemailCursor.execute(""" SELECT * FROM doctorprerequest WHERE email = %s """ , (email,))
        reqemailExist = reqemailCursor.fetchone()

        reqssnCursor =mydb.cursor(buffered=True)
        reqssnCursor.execute(""" SELECT * FROM doctorprerequest WHERE ssn = %s """ , (ssn,))
        reqssnExist = reqssnCursor.fetchone()

        patientemailCursor =mydb.cursor(buffered=True)
        patientemailCursor.execute(""" SELECT * FROM patient WHERE email = %s """ , (email,))
        emailExistAsPatient = patientemailCursor.fetchone()

        patientssnCursor =mydb.cursor(buffered=True)
        patientssnCursor.execute(""" SELECT * FROM patient WHERE ssn = %s """ , (ssn,))
        ssnExistAsPatient = patientssnCursor.fetchone()

        if emailExist and ssnExist and reqssnExist and reqemailExist  :
            return render_template('adddoctor.html', emailExisits = True , ssnExisits=True , reqemailExist=True , reqssnExist=True)
        elif emailExist or ssnExist or reqemailExist or reqssnExist or emailExistAsPatient or ssnExistAsPatient :
            if emailExist :
                return render_template('adddoctor.html', emailExisits = True , ssnExisits=False , reqemailExist=False , reqssnExist=False , emailExistAsPatient=False , ssnExistAsPatient=False )
            elif ssnExist :
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=True, reqemailExist=False , reqssnExist=False , emailExistAsPatient=False , ssnExistAsPatient=False )
            elif reqssnExist:
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, reqemailExist=True , reqssnExist=False , emailExistAsPatient=False , ssnExistAsPatient=False )
            elif reqssnExist:
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, reqemailExist=False , reqssnExist=True ,emailExistAsPatient=False , ssnExistAsPatient=False  )
            elif emailExistAsPatient:
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, reqemailExist=False , reqssnExist=False ,emailExistAsPatient=True , ssnExistAsPatient=False )
            else:
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, reqemailExist=False , reqssnExist=False ,emailExistAsPatient=False , ssnExistAsPatient=True )     

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template('adddoctor.html', emailExisits = False , emailInvalid=True ,reqemailExist=False , reqssnExist=False)        
        else:    
            sql = """INSERT INTO doctorPreRequest (name, ssn, sex, email, password, address, birth_date,  specialization, phone, photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = (name, ssn, sex, email, password, address, birth_date,  specialization, phone, pic_path)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('index'))
    else:
        print('get')
        return render_template('adddoctor.html')

# ------------------------------------------------------------------------View Doctor---------------------------------------------------------------------
@app.route('/viewdoctor')
def viewdoctor():
    if 'user_admin' in session :  
        sql = "SELECT name, email, phone,specialization FROM DOCTOR"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        return render_template('viewdoctor.html',data = result)
    else:
        return redirect(url_for('index'))    

# ------------------------------------------------------------------------Add Device----------------------------------------------------------------
@app.route('/adddevice', methods = ['GET','POST'])

def adddevice():
    if 'user_admin' in session :
        if request.method == 'POST':
            if request.form:
                device_name = request.form['device_name']
                device_model = request.form['device_model']
                technician_id = request.form['technician_id']
                technician_name = request.form['technician_name']
                count = request.form['count']
                description = request.form['description']
                photo = request.files['photo']
                pic_path = save_picture(photo)

                sql = """INSERT INTO device (device_name,device_model,technician_id,technician_name,photo,count,description) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                val = (device_name,device_model,technician_id,technician_name,pic_path,count,description)
                mycursor.execute(sql,val)
                mydb.commit()
                return redirect(url_for('index'))
        return render_template('adddevice.html')
    else:
        return redirect(url_for('index'))
    
        


# ------------------------------------------------------------------------Add Patient---------------------------------------------------------------
@app.route('/addpatient', methods = ['POST', 'GET'])
def addpatient():
    if request.method == 'POST': ##check if there is post data
        name = request.form['name']
        ssn = request.form['ssn']
        sex = request.form['sex']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        birth_date = request.form['birth_date']
        credit_card = request.form['credit_card']
        insurance_num = request.form['insurance_num']
        marital_status = request.form['marital_status']
        job = request.form['job']
        photo = request.files['photo']
        phone = request.form['phone']
        pic_path = save_picture(photo)

        emailCursor =mydb.cursor(buffered=True)
        emailCursor.execute(""" SELECT * FROM patient WHERE email = %s """ , (email,))
        emailExist = emailCursor.fetchone()

        ssnCursor =mydb.cursor(buffered=True)
        ssnCursor.execute(""" SELECT * FROM patient WHERE ssn = %s """ , (ssn,))
        ssnExist = ssnCursor.fetchone()

        doctoremailCursor =mydb.cursor(buffered=True)
        doctoremailCursor.execute(""" SELECT * FROM doctor WHERE email = %s """ , (email,))
        emailExistAsDoctor = doctoremailCursor.fetchone()

        doctorssnCursor =mydb.cursor(buffered=True)
        doctorssnCursor.execute(""" SELECT * FROM doctor WHERE ssn = %s """ , (ssn,))
        ssnExistAsDoctor = doctorssnCursor.fetchone()

        if emailExist and ssnExist and emailExistAsDoctor and ssnExistAsDoctor  :
            return render_template('adddoctor.html', emailExisits = True , ssnExisits=True , emailExistAsDoctor=True , ssnExistAsDoctor=True)
        elif emailExist or ssnExist or emailExistAsDoctor or ssnExistAsDoctor :
            if emailExist :
                return render_template('adddoctor.html', emailExisits = True , ssnExisits=False , emailExistAsDoctor=False , ssnExistAsDoctor=False)
            elif ssnExist :
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=True, emailExistAsDoctor=False , ssnExistAsDoctor=False)
            elif ssnExistAsDoctor:
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, emailExistAsDoctor=True , ssnExistAsDoctor=False)
            else:    
                return render_template('adddoctor.html', emailExisits = False , ssnExisits=False, emailExistAsDoctor=False , ssnExistAsDoctor=True)

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template('adddoctor.html', emailExisits = False , emailInvalid=True ,emailExistAsDoctor=False , ssnExistAsDoctor=False)        
        else:    
        
            sql = """INSERT INTO patient (name, ssn, address, email, password, sex, birth_date,marital_status,job,insurance_num, credit_card, phone, photo) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (name,ssn,address,email,password, sex,birth_date,marital_status,job, insurance_num,credit_card, phone, pic_path)
            mycursor.execute(sql, val)
            mydb.commit()

            sql1 = """INSERT INTO users (email, password, type) VALUES (%s, %s, %s)"""
            val1 = (email,password,'patient')
            mycursor.execute(sql1, val1)
            mydb.commit()

            return redirect(url_for('index'))
    else:
        print('get')
        return render_template('addpatient.html')

# ------------------------------------------------------------------------View Patient---------------------------------------------------------------
@app.route('/viewpatient')
def viewpatient():
    
    mycursor.execute("SELECT * FROM Patient")
    myresult = mycursor.fetchall()
    return render_template('viewpatient.html', data = myresult)

# ------------------------------------------------------------------------Contact Us-----------------------------------------------------------------
@app.route('/contact_us')
def contact():
    return render_template('contact_us.html')

# ------------------------------------------------------------------------Admin Veiw Doctor---------------------------------------------------------
@app.route('/adminViewDoctor', methods = ['POST','GET'])
def adminViewDoctor():
    if 'user_admin' in session and 'loggedIn' in session:
        if request.method == 'POST'and "ssn" in request.form:

            name = request.form['name']
            ssn=request.form['ssn']
            sex = request.form['sex']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            birth_date = request.form['birth_date']
            Specialization= request.form['specialization']
            phone = request.form['phone']
            photo = request.form['photo']

            sql = """INSERT INTO doctor (name,ssn,sex,email,password,address,birth_date,specialization,phone,photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = (name,ssn,sex,email,password,address,birth_date,Specialization,phone,photo)
            mycursor.execute(sql,val)
            mydb.commit()
            
            sql = """INSERT INTO users (email,password,type) VALUES (%s,%s,%s)"""
            val = (email,password,'doctor')
            mycursor.execute(sql,val)
            mydb.commit()

            cursor = mydb.cursor(buffered=True)
            cursor.execute("""DELETE FROM doctorPreRequest WHERE ssn = %s """,(ssn,))
            mydb.commit()  
            return redirect(url_for('adminViewDoctor'))

        if request.method == 'POST' and "ssnref" in request.form:
            ssnref=request.form['ssnref']

            cursor = mydb.cursor(buffered=True)
            cursor.execute(""" DELETE FROM doctorPreRequest WHERE ssn = %s """,(ssnref,))
            mydb.commit()
            return redirect(url_for('adminViewDoctor'))
        else:
            print('get')    
            
        sql = "SELECT * FROM doctorprerequest"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        return render_template('adminViewDoctor.html',result=result)
    else:
        return redirect(url_for('index'))        

# ------------------------------------------------------------------------add appointment----------------------------------------------------------------
@app.route('/addAppointment',methods=['GET','POST'])
def addAppointment():
    if 'user_patient' in session or 'user_doctor' in session :  
        # to get name
        sql = """SELECT name from doctor 
        where email = %s"""
        val = (session['user_doctor'],)
        mycursor.execute(sql,val)
        
        name = mycursor.fetchone()
        name = name[0]
        
        if request.method == 'POST':
            #requesting data form
            startT = request.form['startT']
            date = request.form['date']

            td = timedelta(hours=1)
            startTime = datetime.strptime(startT,"%H")
            # startTime = datetime.fromtimestamp(mktime(startTime))
            print(type(startTime))
            print(type(td))
            
            dt_datetime = datetime.strptime(date,"%Y-%m-%d")
            now = datetime.now()
            difference = now - dt_datetime
            diffHours = int((difference.total_seconds()) /3600)
            if(difference.days > 0 or (difference.days == 0 and diffHours > 0)):
                return render_template('addAppointment.html', added =True,name = name,msg=True,booked = False)
            
            endT = (startTime + td).hour
            
            sql = "SELECT doctorEmail,startT,dt FROM appointment where startT = %s and dt = %s and doctorEmail = %s"
            val = (startT,date,session['user_doctor'])
            mycursor.execute(sql,val)
            result = mycursor.fetchall()
            if result:
                return render_template('addAppointment.html', added =True,name = name,msg=False,booked = True)
            
            
            
            sql = """INSERT INTO appointment (startT, endT, dt,doctorEmail,booked) VALUES (%s, %s, %s,%s,%s)"""
            val = (startT,endT,date,session['user_doctor'],0)
            mycursor.execute(sql, val)
            mydb.commit()
            
        
            
            return render_template('addAppointment.html', added =True,name = name,msg=False,booked = False)
        else:
            return render_template('addAppointment.html',added = False,name = name,msg=False,booked = False)
    else:
        return redirect(url_for('index'))       

# ------------------------------------------------------------------------view appointment----------------------------------------------------------------
@app.route('/viewAppointments')   
def viewAppointments():
    # to get name
    sql = """SELECT name FROM doctor where email = %s"""
    val = (session['user_doctor'],)
    mycursor.execute(sql,val)
    name = mycursor.fetchone()
    name = name[0]
    
    sql = "SELECT appNo,name,startT,endT,dt,booked FROM appointment join doctor on doctorEmail = email where doctorEmail = %s"
    mycursor.execute(sql,val)
    result = mycursor.fetchall()
    empty = True
    if result:
        empty = False
    return render_template('viewAppointments.html', data = result,name = name,empty = empty)

# ------------------------------------------------------------------------book now----------------------------------------------------------------
@app.route('/bookNow',methods = ['GET','POST'])
def bookNow():
    sql = "SELECT appNo,name,startT,endT,dt,booked FROM appointment join doctor on doctorEmail = email"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    result = pd.DataFrame(result)
    result.reset_index()
    if not result.empty:
        print('notEmpty')
        print(result)
        result[4] = pd.to_datetime(result[4],format="%Y-%m-%d")
        result = result[result[5] == 0]
        now = datetime.now().strftime ("%Y-%m-%d")
        result = result[result[4] >= now]
        result = result.sort_values(by=4)
        result.index = range(len(result.index))
        print(result)
        
    if request.method == 'POST' and "toFind" in request.form:
        toFind = request.form['toFind']
        return render_template('bookNow.html',data = result,now = datetime.now().date(),booked = True,toFind = toFind)
    elif request.method == 'POST':
        print("JUSt POST")
        print("JUSt POST")
        appNo = request.form['appNo']
        sql = """UPDATE appointment
        SET patientEmail = %s,
        booked = %s
        WHERE appNo = %s"""
        
        value = (session['user_patient'],1,appNo)
        mycursor.execute(sql,value)
        mydb.commit()
        return redirect(url_for('bookNow'))
        
    else:
        print("GET")
        print("GET")
        print(type(result))
        print(result)             
        return render_template('bookNow.html',data = result,now = datetime.now().date(),booked = False,toFind = "")

# ------------------------------------------------------------------------ delete appointment ----------------------------------------------------------------
@app.route('/viewAppointments/deleteAppointment', methods=['GET','POST'])
def deleteAppointment():
    if request.method == 'POST':    
        print('delete')
        print('delete')
        print('delete')
        sql = "DELETE FROM appointment where appNo = %s"
        val = request.form['appNo']
        val = int(val)
        val = (val,)
        mycursor.execute(sql,val)
        mydb.commit()
        return redirect(url_for('viewAppointments'))

# ------------------------------------------------------------------------unbook appointment ----------------------------------------------------------------
@app.route('/profileh/unBookAppointment', methods=['GET','POST'])
def unBookAppointment():
    if request.method == 'POST':    
        print('delete')
        print('delete')
        print('delete')
        sql = "UPDATE appointment SET booked = %s,patientEmail=%s WHERE appNo = %s"
        val = (0,NULL,int(request.form['appNo']))
        mycursor.execute(sql,val)
        mydb.commit()
        return redirect(url_for('profileh'))

# ------------------------------------------------------------------------messages----------------------------------------------------------------
@app.route('/messages', methods = ['GET','POST'])
def messages():
    if 'user_patient' in session or 'user_doctor' in session : 
        if request.method == 'POST':
            emailTo = request.form['emailTo']
            emailFrom=request.form['emailFrom']
            title = request.form['title']
            message = request.form['message']

            sql = """INSERT INTO messages (emailTo,emailFrom,title,message) VALUES (%s,%s,%s,%s)"""
            val = (emailTo,emailFrom,title,message)
            mycursor.execute(sql,val)
            mydb.commit()

        return render_template('messages.html')
    else:
        return redirect(url_for('index'))  

# ------------------------------------------------------------------------inbox----------------------------------------------------------------
@app.route('/inbox', methods = ['POST','GET'])
def inbox():
    if 'user_patient' in session or 'user_doctor' in session :

        if request.method == 'POST'and "deleteMessage" in request.form:
            deleteMessage = request.form['deleteMessage']

            cursor = mydb.cursor(buffered=True)
            cursor.execute(""" DELETE FROM messages WHERE id = %s """,(deleteMessage,))
            mydb.commit()
            return redirect(url_for('inbox'))

        sql = """Select * from messages where emailTo = %s"""
        if 'user_patient' in session:
            val = (session['user_patient'],)
        else:
            val = (session['user_doctor'],) 
        mycursor.execute(sql,val)
        result = mycursor.fetchall()

        return render_template('inbox.html',result=result)
    else:
        return redirect(url_for('index'))   

# ------------------------------------------------------------------------count----------------------------------------------------------------
def count():
    cursor = mydb.cursor(buffered=True)
    if 'user_patient' in session:
        cursor.execute('SELECT COUNT(*) FROM messages WHERE emailTo = %s', (session['user_patient'],))
    elif 'user_doctor' in session:
        cursor.execute('SELECT COUNT(*) FROM messages WHERE emailTo = %s', (session['user_doctor'],))
    else:
        cursor.execute('SELECT COUNT(id) FROM doctorprerequest')   
    result = cursor.fetchone()[0]
    return (result)

app.jinja_env.globals.update(count=count)

if __name__ == '__main__':
    app.run(debug = True)
