from flask import Flask, render_template, request,flash,redirect,url_for,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os 
app = Flask(__name__)
app.debug = True  # Enable debug mode
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'food_donation'

app.config['UPLOAD_FOLDER'] = 'static/uploads/'

mysql = MySQL(app)


# index page
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods =['GET', 'POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if email and password:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        select_query = "SELECT password FROM credentials WHERE email = %s"
        cursor.execute(select_query, (email,))

        result = cursor.fetchone()

        if result and password == result['password']:
            
            return render_template("donor.html")
        else:
            
            return "Invalid email or password", 401

        cursor.close()
        connection.close()

    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    mobile = request.form.get("mobile")
    address = request.form.get("address")
    value = request.form.get("option")
    pass1 = request.form.get("pass1")
    pass2 = request.form.get("pass2")

    if value == 'donor':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS row_count FROM donor')
        result = cursor.fetchone()
        num = result['row_count'] + 1
        uid = "D" + str(num)
        cursor.execute('INSERT INTO credentials VALUES \
                (% s, % s, % s)',
                       (uid, email,pass1))
        cursor.execute('INSERT INTO donor VALUES \
                (% s, % s, % s,%s)',
                       (uid, name,mobile,address))
        
        mysql.connection.commit()
        flash('Registration successful!', 'success')
        return redirect('/login') 
    if value == 'ngo':
        file = request.files['image']
        
        
        filename = file.filename
        #file_path = os.path.join(os.getcwd(), filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Store the image, name, and email in the database
        image_data = open(file_path, 'rb').read()


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS row_count FROM ngo')
        result = cursor.fetchone()
        num = result['row_count'] + 1
        uid = "N" + str(num)
        cursor.execute('INSERT INTO credentials VALUES \
                (% s, % s, % s)',
                       (uid, email,pass1))
        
        cursor.execute('INSERT INTO ngo VALUES \
                (% s, % s, % s,%s,%s)',
                       (uid,name,mobile,address,image_data))
        mysql.connection.commit()
        #os.remove(file_path)
        flash('Registration successful!', 'success')
        return redirect('/login') 


    return render_template("signup.html")

@app.route('/scheduleEvent', methods=['GET', 'POST'])
def scheduleEvent():
    eventTitle = request.form.get("eventTitle")
    eventDate = request.form.get("eventDate")
    eventTime = request.form.get("eventTime")
    contactName = request.form.get("contactName")
    contactEmail = request.form.get("contactEmail")
    eventDescription = request.form.get("eventDescription")
    ngoReg = request.form.get("ngoReg")

    #uid=session['user_id'] 

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #select_query = "SELECT uid FROM credentials WHERE uid = %s"
    #cursor.execute(select_query, (uid,))

    #result = cursor.fetchone()

    select_query = "INSERT into Event values  (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(select_query, (ngoReg,eventTitle,eventDate,contactName,contactEmail,eventDescription,eventTime))
    mysql.connection.commit()
    flash('Event successful!', 'success')
    return render_template("ngo.html")



@app.route('/donor_main', methods=['GET', 'POST'])
def donor_main():
     return render_template("donor.html")


if __name__ == '__main__':
    app.run()
