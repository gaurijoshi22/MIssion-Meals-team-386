from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if email and password:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        select_query = "SELECT password FROM credentials WHERE email = %s"
        cursor.execute(select_query, (email,))

        result = cursor.fetchone()

        if result and password == result['password']:
            select_query1 = "SELECT uid FROM credentials WHERE email = %s"
            cursor.execute(select_query1, (email,))
            result = cursor.fetchone()

            session['uid'] = result
            uid_val = result.get('uid')

            if uid_val.startswith('D'):
                return redirect('/donor_main')
            if uid_val.startswith('N'):
                return redirect('/ngo_main')
        else:

            return "Invalid email or password", 401

        mysql.cursor.close()
        mysql.connection.close()

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
                       (uid, email, pass1))
        cursor.execute('INSERT INTO donor VALUES \
                (% s, % s, % s,%s)',
                       (uid, name, mobile, address))

        mysql.connection.commit()
        flash('Registration successful!', 'success')
        return redirect('/login')
    if value == 'ngo':
        file = request.files['image']

        filename = file.filename
        # file_path = os.path.join(os.getcwd(), filename)
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
                       (uid, email, pass1))

        cursor.execute('INSERT INTO ngo VALUES \
                (% s, % s, % s,%s,%s)',
                       (uid, name, mobile, address, image_data))
        mysql.connection.commit()
        # os.remove(file_path)
        flash('Registration successful!', 'success')
        return redirect('/login')

    return render_template("signup.html")


@app.route('/donor_main', methods=['GET', 'POST'])
def donor_main():
    uid = session.get('uid')
    uid_val = uid.get('uid')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    select_query = "SELECT Uid FROM current_donations WHERE Uid = %s"
    cursor.execute(select_query, (uid_val,))
    result = cursor.fetchall()
    if (result is not None):
        select_query1 = "SELECT * FROM current_donations where Uid = %s"
        cursor.execute(select_query1, (uid_val,))
        data = cursor.fetchall()
        da = []
        for d in data:
            da.append(d)
    return render_template("donor.html", data=da)


@app.route('/donor_main/donate_food', methods=['GET', 'POST'])
def donateFood():
    uid = session.get('uid')
    uid_val = uid.get('uid')
    if request.method == 'POST':
        val = 0
        item_name = request.form.get("item_name")
        desc = request.form.get("desc")
        qty = request.form.get("qty")
        wt = request.form.get("wt")
        pdate = request.form.get("pdate")
        edate = request.form.get("edate")
        status = "Available"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO current_donations VALUES \
                    (%s,% s, % s, % s,%s,%s,%s,%s,%s)',
                       (val, uid_val, item_name, desc, qty, wt, pdate, edate, status))
        mysql.connection.commit()
        flash('done', 'success')
        return redirect("/donor_main")
    return render_template("donate_food.html")

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    # Connect to your MySQL database
    db = mysql.connector.connect(
        host="your_host",
        user="your_username",
        password="your_password",
        database="your_database"
    )

    # Execute the SQL query
    cursor = db.cursor()
    query = """
        SELECT
            D.name AS DonorName,
            COUNT(CD.Donation_id) AS DonationCount
        FROM
            donor D
        LEFT JOIN
            current_donations CD ON D.uid = CD.Uid
        WHERE
            CD.Item_date_of_production >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        GROUP BY
            D.uid
        ORDER BY
            DonationCount DESC;
    """
    cursor.execute(query)
    leaderboard_data = cursor.fetchall()

    # Close the database connection
    cursor.close()
    db.close()

    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)


@app.route('/ngo_main', methods=['GET', 'POST'])
def ngo_main():
    uid = session.get('uid')
    uid_val = uid.get('uid')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    select_query = "SELECT ngo_name FROM ngo WHERE uid = %s"
    cursor.execute(select_query, (uid_val,))
    result = cursor.fetchone()

    return render_template("ngo.html")


@app.route('/scheduleEvent', methods=['GET', 'POST'])
def scheduleEvent():
    uid = session.get('uid')
    uid_val = uid.get('uid')
    if request.method == 'POST':
        eventTitle = request.form.get("eventTitle")
        eventDate = request.form.get("eventDate")
        eventTime = request.form.get("eventTime")
        contactName = request.form.get("contactName")
        contactEmail = request.form.get("contactEmail")
        eventDescription = request.form.get("eventDescription")
        ngoReg = request.form.get("ngoReg")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        select_query = "INSERT into Event values  (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(select_query, (uid_val, eventTitle, eventDate,
                       contactName, contactEmail, eventDescription, eventTime))
        mysql.connection.commit()
        flash('Event successful!', 'success')
    return render_template("event.html")


@app.route('/logout')
def logout():
    session.pop('uid', None)
    flash('Logged Out!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
