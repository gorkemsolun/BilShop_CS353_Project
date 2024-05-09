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
app.config['MYSQL_DB'] = 'cs353hw4db'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if 'username' in session:
        return redirect(url_for('main_page'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE name = % s AND cid = % s', (username, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['cid']
            session['username'] = user['name']
            message = 'Logged in successfully!'
            return redirect(url_for('main_page'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE name = % s', (username, ))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM customer WHERE cid = % s', (password,))
        account_password = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
        elif account_password:
            message = 'Choose a different cid!'
        elif len(str(password)) != 5:
            message = 'Provided cid does not have 5 characters!'
        elif not username or not password:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO customer (cid, name) VALUES (% s, % s)', (password, username))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message=message)


@app.route('/main')
def main_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT aid, branch, balance, openDate FROM owns NATURAL JOIN account WHERE cid= %s', (session['userid'], ))
    table = cursor.fetchall()
    header = ["Account ID", "Branch", "Balance", "OpenDate"]
    return render_template('main.html', table = table, header = header, isInSession = session['loggedin'], username = session['username'])


@app.route('/money_transfer', methods=['GET', 'POST'])
def money_transfer():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT aid FROM owns NATURAL JOIN account WHERE cid= %s', (session['userid'],))
    accountTable = cursor.fetchall()
    cursor.execute('SELECT aid FROM account')
    allAccounts = cursor.fetchall()
    header = ["Account ID"]
    if request.method == 'POST' and 'FromAccount' in request.form and 'ToAccount' in request.form and 'TransferAmount' in request.form:
        FromAccount = request.form['FromAccount']
        ToAccount = request.form['ToAccount']
        TransferAmount = request.form['TransferAmount']
        cursor.execute('SELECT balance FROM account WHERE aid = %s', (FromAccount,))
        fromBalance = cursor.fetchall()
        if FromAccount == ToAccount:
            flash('Sending money to the same account is forbidden!', category='danger')
        elif fromBalance[0]['balance'] >= float(TransferAmount):
            cursor.execute('UPDATE account SET balance = balance - %s WHERE aid=%s', (float(TransferAmount), FromAccount,))
            cursor.execute('UPDATE account SET balance = balance + %s WHERE aid=%s', (float(TransferAmount), ToAccount,))
            mysql.connection.commit()
            flash('Transaction Successful!', category = 'success')
        else:
            flash("Balance not enough to transfer money", category = 'danger')
    return render_template('money_transfer.html', accountTable = accountTable, header = header, allAccounts = allAccounts)


@app.route('/close_account/<aid>')
def close_account(aid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('DELETE FROM owns WHERE aid=%s', (aid,))
        cursor.execute('DELETE FROM account WHERE aid=%s', (aid,))
        mysql.connection.commit()
        return redirect(url_for('main_page'))
    except Exception as e:
        return f"Error deleting account: {str(e)}"  # Informative error message

@app.route('/account_summary')
def account_summary():
    header = ['Account ID',  "Branch", "Balance", "OpenDate"]
    header2 = ["Account ID", "Balance"]
    header3 = ["min_budget", "max_budget"]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT aid, branch, balance, openDate FROM account NATURAL JOIN owns WHERE cid= %s ORDER BY openDate ASC', (session['userid'],))
    query1 = cursor.fetchall()
    cursor.execute('SELECT aid, branch, balance, openDate FROM account NATURAL JOIN owns WHERE cid= %s AND balance > 50000 AND openDate>"2015-12-31"', (session['userid'],))
    query2 = cursor.fetchall()
    cursor.execute('SELECT aid, balance FROM account NATURAL JOIN owns NATURAL JOIN customer WHERE cid= %s AND account.city = customer.city', (session['userid'],))
    query3 = cursor.fetchall()
    cursor.execute('SELECT MIN(balance) AS min_balance, MAX(balance) AS max_balance FROM account NATURAL JOIN owns WHERE cid= %s', (session['userid'],))
    query4 = cursor.fetchall()
    return render_template('account_summary.html', query1 = query1, header = header, query2 = query2, query3 = query3, query4 =query4, header2=header2, header3=header3)


@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
