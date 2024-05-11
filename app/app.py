import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = 'abcdefgh'

app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353projectDB'

mysql = MySQL(app)

# Adding people with manual insertions can result in an error,
# it needs to be checked whether entry has been placed in sql.
def get_next_id():
  cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  # Fetch the current maximum ID from the table
  cursor.execute('SELECT * FROM User ORDER BY userID DESC')
  max_id = cursor.fetchone()
  if max_id is None:
      return str(1)  # Start from 1 if no records exist
  max_id = max_id['userID']
  return str(int(max_id) + 1)

# to-do admin registration button and admin registration page
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    # if 'username' in session:
    #     if session['role'] == 'customer':
    #         return redirect(url_for('main_page_customer'))
    #     elif session['role'] == 'business':
    #         return redirect(url_for('main_page_business'))
    #     else:
    #         return redirect(url_for('main_page_admin'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE name = % s AND password = % s', (username, password,))
        user_w_name = cursor.fetchone()
        cursor.execute('SELECT * FROM User WHERE email = % s AND password = % s', (username, password,))
        user_w_email = cursor.fetchone()
        user = user_w_name
        if user_w_name is None:
            user = user_w_email
        if user:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM Customer WHERE userID = % s', (user['userID'],))
            customer = cursor.fetchone()
            if customer:
                session['role'] = 'customer'
                session['loggedin'] = True
                session['userid'] = user['userID']
                session['username'] = user['name']
                return redirect(url_for('main_page_customer'))
            else:
                cursor.execute('SELECT * FROM Business WHERE userID = % s', (user['userID'],))
                business = cursor.fetchone()
                if business:
                    session['role'] = 'business'
                    session['loggedin'] = True
                    session['userid'] = user['userID']
                    session['username'] = user['name']
                    return redirect(url_for('main_page_business'))
                else:
                    session['role'] = 'admin'
                    session['loggedin'] = True
                    session['userid'] = user['userID']
                    session['username'] = user['name']
                    return redirect(url_for('main_page_admin'))
        else:
            message = 'Please enter correct email / username and password !'
    return render_template('login.html', message=message)

# Customer and Business registers through this
# No admin registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE name = % s', (username, ))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM User WHERE email = % s', (email, ))
        account_email = cursor.fetchone()
        if account:
            message = 'Username already exists.'
        elif account_email:
            message = 'Email address is already registered.'
        elif not username or not password:
            message = 'Please fill out the form!'
        else:
            role = request.form.get('role')
            new_id = get_next_id()
            cursor.execute('INSERT INTO User (password, name, email, userID) VALUES (% s, % s, %s, %s)',
                           (password, username, email, new_id,))
            mysql.connection.commit()
            if role == 'customer':
                cursor.execute('INSERT INTO Customer (balance, userID) VALUES (% s, % s)',
                               (0, new_id,))
                mysql.connection.commit()
            elif role == 'business':
                cursor.execute('INSERT INTO Business (balance, userID) VALUES (% s, % s)',
                               (0, new_id,))
                mysql.connection.commit()
            mysql.connection.commit()
            message = 'User successfully created!'
    elif request.method == 'POST':
        message = 'Please fill all the fields!'
    return render_template('register.html', message=message)


@app.route('/main_page_customer')
def main_page_customer():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Owns NATURAL JOIN Product WHERE status= %s', ('notSold', ))
    product_table = cursor.fetchall()
    product_header = ["title", "price", "coverPicture"]
    return render_template('main_page_customer.html', product_table = product_table, product_header = product_header, isInSession = session['loggedin'], username = session['username'])

#to-do main page business product creation
@app.route('/main_page_business')
def main_page_business():
    return render_template('main_page_business.html')
#to-do main page admin reports etc
@app.route('/main_page_admin')
def main_page_admin():
    return render_template('main_page_admin.html')
# @app.route('/money_transfer', methods=['GET', 'POST'])
# def money_transfer():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT aid FROM owns NATURAL JOIN account WHERE cid= %s', (session['userid'],))
#     accountTable = cursor.fetchall()
#     cursor.execute('SELECT aid FROM account')
#     allAccounts = cursor.fetchall()
#     header = ["Account ID"]
#     if request.method == 'POST' and 'FromAccount' in request.form and 'ToAccount' in request.form and 'TransferAmount' in request.form:
#         FromAccount = request.form['FromAccount']
#         ToAccount = request.form['ToAccount']
#         TransferAmount = request.form['TransferAmount']
#         cursor.execute('SELECT balance FROM account WHERE aid = %s', (FromAccount,))
#         fromBalance = cursor.fetchall()
#         if FromAccount == ToAccount:
#             flash('Sending money to the same account is forbidden!', category='danger')
#         elif fromBalance[0]['balance'] >= float(TransferAmount):
#             cursor.execute('UPDATE account SET balance = balance - %s WHERE aid=%s', (float(TransferAmount), FromAccount,))
#             cursor.execute('UPDATE account SET balance = balance + %s WHERE aid=%s', (float(TransferAmount), ToAccount,))
#             mysql.connection.commit()
#             flash('Transaction Successful!', category = 'success')
#         else:
#             flash("Balance not enough to transfer money", category = 'danger')
#     return render_template('money_transfer.html', accountTable = accountTable, header = header, allAccounts = allAccounts)
#
#
# @app.route('/close_account/<aid>')
# def close_account(aid):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     try:
#         cursor.execute('DELETE FROM owns WHERE aid=%s', (aid,))
#         cursor.execute('DELETE FROM account WHERE aid=%s', (aid,))
#         mysql.connection.commit()
#         return redirect(url_for('main_page'))
#     except Exception as e:
#         return f"Error deleting account: {str(e)}"  # Informative error message
#
# @app.route('/account_summary')
# def account_summary():
#     header = ['Account ID',  "Branch", "Balance", "OpenDate"]
#     header2 = ["Account ID", "Balance"]
#     header3 = ["min_budget", "max_budget"]
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT aid, branch, balance, openDate FROM account NATURAL JOIN owns WHERE cid= %s ORDER BY openDate ASC', (session['userid'],))
#     query1 = cursor.fetchall()
#     cursor.execute('SELECT aid, branch, balance, openDate FROM account NATURAL JOIN owns WHERE cid= %s AND balance > 50000 AND openDate>"2015-12-31"', (session['userid'],))
#     query2 = cursor.fetchall()
#     cursor.execute('SELECT aid, balance FROM account NATURAL JOIN owns NATURAL JOIN customer WHERE cid= %s AND account.city = customer.city', (session['userid'],))
#     query3 = cursor.fetchall()
#     cursor.execute('SELECT MIN(balance) AS min_balance, MAX(balance) AS max_balance FROM account NATURAL JOIN owns WHERE cid= %s', (session['userid'],))
#     query4 = cursor.fetchall()
#     return render_template('account_summary.html', query1 = query1, header = header, query2 = query2, query3 = query3, query4 =query4, header2=header2, header3=header3)


@app.route('/logout')
def logout():
    session.pop('role', None)
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
