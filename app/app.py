import re
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__, static_folder='static')

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
# The helper function that returns a json file of the given string query
@app.route('/search_products', methods=['POST'])
def search_products():
    search = request.json.get('search', '')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all the products with starting title as requested search input
    cursor.execute('SELECT * FROM Owns NATURAL JOIN Product WHERE status = %s AND title LIKE %s', ('notSold', f'{search}%'))
    product_table = cursor.fetchall()
    return jsonify(product_table)

# The helper function that returns a json file of the given string query
@app.route('/filter')
def filter_products():
    category = request.args.get('category')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')
    sort_order = request.args.get('sortOrder')
    # Set default values if min_price or max_price are not provided
    if not min_price or float(min_price) < 0:
        min_price = 0
    if not max_price or float(max_price) < 0:
        max_price = sys.maxsize

    # Set default sort order if not provided
    if not sort_order:
        sort_order = 'ASC'
    sort_order = sort_order.upper()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if category == 'all':
        if sort_order == 'ASC':
            cursor.execute(
                'SELECT * FROM Owns NATURAL JOIN Product WHERE status = %s AND price >= %s AND price <= %s ORDER BY price ASC',
                ('notSold', float(min_price), float(max_price), ))
            product_table = cursor.fetchall()
        else:
            cursor.execute(
                'SELECT * FROM Owns NATURAL JOIN Product WHERE status = %s AND price >= %s AND price <= %s ORDER BY price DESC',
                ('notSold', float(min_price), float(max_price), ))
            product_table = cursor.fetchall()
    else:
        if sort_order == 'ASC':
            # Get all the products with starting applied filter choice
            cursor.execute(
            'SELECT * FROM Owns NATURAL JOIN Product WHERE status = %s AND price >= %s AND price <= %s AND category = %s ORDER BY price ASC',
            ('notSold', float(min_price), float(max_price), category,))
            product_table = cursor.fetchall()
        else:
            # Get all the products with starting applied filter choice
            cursor.execute(
                'SELECT * FROM Owns NATURAL JOIN Product WHERE status = %s AND price >= %s AND price <= %s ORDER BY price DESC',
                ('notSold', float(min_price), float(max_price), category, ))
            product_table = cursor.fetchall()
    return jsonify(product_table)

# Login page elements and given checks for login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    # Checking whether the user logged in the system, redirect to the correct page using user roles
    if 'username' in session:
        if session['role'] == 'customer':
            return redirect(url_for('main_page_customer'))
        elif session['role'] == 'business':
            return redirect(url_for('main_page_business'))
        else:
            return redirect(url_for('main_page_admin'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Getting the user with the provided name
        cursor.execute('SELECT * FROM User WHERE name = % s AND password = % s', (username, password,))
        user_w_name = cursor.fetchone()
        # Getting the user with the provided name
        cursor.execute('SELECT * FROM User WHERE email = % s AND password = % s', (username, password,))
        user_w_email = cursor.fetchone()
        # Assigning user to the default choice of providing name
        user = user_w_name
        # If name is empty assign it to user with provided email, noting that user can still be empty
        if user_w_name is None:
            user = user_w_email
        # Checking whether user is empty
        if user:
            # Check whether the user is blacklisted
            cursor.execute('SELECT * FROM Blacklists WHERE userID = % s', (user['userID'],))
            isBlacklisted = cursor.fetchone()
            if isBlacklisted:
                message = "Sorry, you are blacklisted."
            else:
                # Check whether the userID exists in the Customer table, noting that userID are same in business and user
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM Customer WHERE userID = % s', (user['userID'],))
                customer = cursor.fetchone()
                if customer:
                    # userID are same in customer and user
                    session['role'] = 'customer'
                    session['loggedin'] = True
                    session['userid'] = user['userID']
                    session['username'] = user['name']
                    return redirect(url_for('main_page_customer'))
                else:
                    # Check whether the userID exists in the Business table, noting that userID are same in business and user
                    cursor.execute('SELECT * FROM Business WHERE userID = % s', (user['userID'],))
                    business = cursor.fetchone()
                    # If business exists assign session information to local storage
                    if business:
                        session['role'] = 'business'
                        session['loggedin'] = True
                        session['userid'] = user['userID']
                        session['username'] = user['name']
                        return redirect(url_for('main_page_business'))
                    # Assign admin session information to local storage
                    else:
                        session['role'] = 'admin'
                        session['loggedin'] = True
                        session['userid'] = user['userID']
                        session['username'] = user['name']
                        return redirect(url_for('main_page_admin'))
        # user not found
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
        # Check whether the given field, username, exists in the db
        cursor.execute('SELECT * FROM User WHERE name = % s', (username, ))
        account = cursor.fetchone()
        # Check whether the given field, email, exists in the db
        cursor.execute('SELECT * FROM User WHERE email = % s', (email, ))
        account_email = cursor.fetchone()
        if account:
            message = 'Username already exists.'
        elif account_email:
            message = 'Email address is already registered.'
        elif not username or not password or not email:
            message = 'Please fill out the form!'
        else:
            # The chosen role in HTML is requested by request.form.get('role') function
            role = request.form.get('role')
            # Get a new id which is unique
            new_id = get_next_id()
            # Insert the user with a new ID, given password, name and email
            cursor.execute('INSERT INTO User (password, name, email, userID) VALUES (% s, % s, %s, %s)',
                           (password, username, email, new_id,))
            mysql.connection.commit()
            # For the chosen role insert to balance default value 0 and userID Customer table
            if role == 'customer':
                cursor.execute('INSERT INTO Customer (balance, userID) VALUES (% s, % s)',
                               (0, new_id,))
                mysql.connection.commit()
            # For the chosen role insert the balance default value 0 and userID to Business table
            elif role == 'business':
                cursor.execute('INSERT INTO Business (balance, userID) VALUES (% s, % s)',
                               (0, new_id,))
                mysql.connection.commit()
            mysql.connection.commit()
            message = 'User successfully created!'
    elif request.method == 'POST':
        message = 'Please fill all the fields!'
    return render_template('register.html', message=message)


@app.route('/main_page_customer' , methods=['GET', 'POST'])
def main_page_customer():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all products that are not sold using the following query
    cursor.execute('SELECT * FROM Owns NATURAL JOIN Product WHERE status= %s', ('notSold', ))
    product_table = cursor.fetchall()
    # Pass the product table, and user session information to HTML
    return render_template('main_page_customer.html', product_table = product_table, isInSession = session['loggedin'], username = session['username'])

# to-do notifications page
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')
# to-do shopping-cart page
@app.route('/shopping_cart')
def shopping_cart():
    return render_template('shopping_cart.html')
# to-do profile page
@app.route('/profile')
def profile():
    return render_template('profile.html')
# to-do main page business product creation
@app.route('/main_page_business')
def main_page_business():
    return render_template('main_page_business.html')
# to-do main page admin reports etc
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
    # Pop all the elements that are in local storage, and leave the system
    session.pop('role', None)
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/tables')
def admin():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch data from the User table
    cursor.execute('SELECT * FROM User ORDER BY userID')
    users = cursor.fetchall()

    # Fetch data from the Customer table
    cursor.execute('SELECT * FROM Customer ORDER BY userID')
    customers = cursor.fetchall()

    # Fetch data from the Business table
    cursor.execute('SELECT * FROM Business ORDER BY userID')
    businesses = cursor.fetchall()

    # Fetch data from the Admin table
    cursor.execute('SELECT * FROM Admin ORDER BY userID')
    admins = cursor.fetchall()

    # Fetch data from the Product table
    cursor.execute('SELECT * FROM Product ORDER BY productID')
    products = cursor.fetchall()

    # Fetch data from the ProductPicture table
    cursor.execute('SELECT * FROM ProductPicture ORDER BY productID')
    product_pictures = cursor.fetchall()

    # Fetch data from the Owns table
    cursor.execute('SELECT * FROM Owns ORDER BY userID, productID')
    owns = cursor.fetchall()

    # Fetch data from the Wishes table
    cursor.execute('SELECT * FROM Wishes ORDER BY userID, productID')
    wishes = cursor.fetchall()

    # Fetch data from the PutsOnCart table
    cursor.execute('SELECT * FROM PutsOnCart ORDER BY userID, productID')
    puts_on_cart = cursor.fetchall()

    # Fetch data from the PurchaseInformation table
    cursor.execute('SELECT * FROM PurchaseInformation ORDER BY purchaseID')
    purchase_info = cursor.fetchall()

    # Fetch data from the ReturnRequestInformation table
    cursor.execute('SELECT * FROM ReturnRequestInformation ORDER BY returnID')
    return_requests = cursor.fetchall()

    # Fetch data from the HasReturnRequest table
    cursor.execute('SELECT * FROM HasReturnRequest ORDER BY returnID, productID')
    has_return_request = cursor.fetchall()

    # Fetch data from the Report table
    cursor.execute('SELECT * FROM Report ORDER BY reportID')
    reports = cursor.fetchall()

    # Fetch data from the Blacklists table
    cursor.execute('SELECT * FROM Blacklists ORDER BY userID, reportID, adminID')
    blacklists = cursor.fetchall()

    # Pass the fetched data to the render_template function
    return render_template('test_tables.html', users=users, customers=customers, businesses=businesses,
                           admins=admins, products=products, product_pictures=product_pictures,
                           owns=owns, wishes=wishes, puts_on_cart=puts_on_cart, purchase_info=purchase_info,
                           return_requests=return_requests, has_return_request=has_return_request,
                           reports=reports, blacklists=blacklists)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
