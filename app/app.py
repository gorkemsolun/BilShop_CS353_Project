import os
import sys
import base64
import json

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
import re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__, static_folder="static")

app.secret_key = "abcdefgh"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "cs353projectDB"

mysql = MySQL(app)


# Adding people with manual insertions can result in an error,
# It needs to be checked whether entry has been placed in sql.
def get_next_ID():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM User ORDER BY CONVERT(user_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["user_ID"]
    return str(int(max_id) + 1)


def get_next_ID_product():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Product ORDER BY CONVERT(product_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["product_ID"]
    return str(int(max_id) + 1)


# The helper function that returns a json file of the given string query
# This function is used to get the next available ID for the Purchase_Information table
# by getting the maximum ID from the table and incrementing it by 1
def get_next_ID_purchase_info():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Purchase_Information ORDER BY CONVERT(purchase_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["purchase_ID"]
    return str(int(max_id) + 1)


# The helper function that returns a json file of the given string query
# This function is used to get the next available ID for the Comment table
# by getting the maximum ID from the table and incrementing it by 1
def get_next_ID_comment():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Comment ORDER BY CONVERT(comment_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["comment_ID"]
    return str(int(max_id) + 1)


def generate_report_id():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Report ORDER BY CONVERT(report_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return str(1)  # Start from 1 if no records exist
    max_id = max_id["report_ID"]
    return str(int(max_id) + 1)


# The helper function that returns a json file of the given string query
# This function is used to get the next available ID for the Notification table
# by getting the maximum ID from the table and incrementing it by 1
def get_next_ID_notification():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Notification ORDER BY CONVERT(notification_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["notification_ID"]
    return str(int(max_id) + 1)


# The helper function that returns a json file of the given string query
@app.route("/search_products", methods=["POST"])
def search_products():
    search = request.json.get("search", "")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all the products with starting title as requested search input
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status = %s AND title LIKE %s",
        ("not_sold", f"{search}%"),
    )
    product_table = cursor.fetchall()
    return jsonify(product_table)


# The helper function that returns a json file of the given string query
# This function is used to get the next available ID for the Purchase_Information table
# by getting the maximum ID from the table and incrementing it by 1
@app.route("/search_products_business", methods=["POST"])
def search_products_business():
    search = request.json.get("search", "")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all the products with starting title as requested search input
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE user_ID = %s AND title LIKE %s",
        (session["user_ID"], f"{search}%"),
    )
    product_table = cursor.fetchall()
    return jsonify(product_table)


# Filter the products based on the given parameters and return the result as a json file
# Business version of the filter function that filters the products of the business
@app.route("/filter_business")
def filter_products_business():
    category = request.args.get("category")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort_order = request.args.get("sort_order")
    # Set default values if min_price or max_price are not provided
    if not min_price or float(min_price) < 0:
        min_price = 0
    if not max_price or float(max_price) < 0:
        max_price = sys.maxsize

    # Set default sort order if not provided
    if not sort_order:
        sort_order = "ASC"
    sort_order = sort_order.upper()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if category == "all":
        if sort_order == "ASC":
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE price >= %s AND price <= %s AND user_ID = %s ORDER BY price ASC",
                (
                    float(min_price),
                    float(max_price),
                    session["user_ID"],
                ),
            )
            product_table = cursor.fetchall()
        else:
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE price >= %s AND price <= %s AND user_ID = %s ORDER BY price DESC",
                (
                    float(min_price),
                    float(max_price),
                    session["user_ID"],
                ),
            )
            product_table = cursor.fetchall()
    else:
        if sort_order == "ASC":
            # Get all the products with starting applied filter choice
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE price >= %s AND price <= %s AND category = %s AND user_ID = %s ORDER BY price ASC",
                (
                    float(min_price),
                    float(max_price),
                    category,
                    session["user_ID"],
                ),
            )
            product_table = cursor.fetchall()
        else:
            # Get all the products with starting applied filter choice
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE price >= %s AND price <= %s AND user_ID = %s ORDER BY price DESC",
                (
                    float(min_price),
                    float(max_price),
                    category,
                    session["user_ID"],
                ),
            )
            product_table = cursor.fetchall()
    return jsonify(product_table)


# The helper function that returns a json file of the given string query
# Filter the products based on the given parameters and return the result as a json file
@app.route("/filter")
def filter_products():
    category = request.args.get("category")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort_order = request.args.get("sort_order")
    # Set default values if min_price or max_price are not provided
    if not min_price or float(min_price) < 0:
        min_price = 0
    if not max_price or float(max_price) < 0:
        max_price = sys.maxsize

    # Set default sort order if not provided
    if not sort_order:
        sort_order = "ASC"
    sort_order = sort_order.upper()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if category == "all":
        if sort_order == "ASC":
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status = %s AND price >= %s AND price <= %s ORDER BY price ASC",
                (
                    "not_sold",
                    float(min_price),
                    float(max_price),
                ),
            )
            product_table = cursor.fetchall()
        else:
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status = %s AND price >= %s AND price <= %s ORDER BY price DESC",
                (
                    "not_sold",
                    float(min_price),
                    float(max_price),
                ),
            )
            product_table = cursor.fetchall()
    else:
        if sort_order == "ASC":
            # Get all the products with starting applied filter choice
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status = %s AND price >= %s AND price <= %s AND category = %s ORDER BY price ASC",
                (
                    "not_sold",
                    float(min_price),
                    float(max_price),
                    category,
                ),
            )
            product_table = cursor.fetchall()
        else:
            # Get all the products with starting applied filter choice
            cursor.execute(
                "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status = %s AND price >= %s AND price <= %s ORDER BY price DESC",
                (
                    "not_sold",
                    float(min_price),
                    float(max_price),
                    category,
                ),
            )
            product_table = cursor.fetchall()
    return jsonify(product_table)


# # Login page elements and given checks for login
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if "username" in session:
        if session["role"] == "customer":
            return redirect(url_for("customer_main_page"))
        elif session["role"] == "business":
            return redirect(url_for("business_main_page"))
        else:
            return redirect(url_for("admin_main_page"))
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM User WHERE name = % s", (username,))
        user_w_name = cursor.fetchone()
        cursor.execute("SELECT * FROM User WHERE email = % s", (username,))
        user_w_email = cursor.fetchone()
        user = user_w_name if user_w_name is not None else user_w_email
        if (
            user
            and check_password_hash(user["password"], password)
            or (username == "admin" and password == "admin")
        ):
            cursor.execute(
                "SELECT * FROM Blacklists WHERE user_ID = % s", (user["user_ID"],)
            )
            isBlacklisted = cursor.fetchone()
            if isBlacklisted:
                message = "Sorry, you are blacklisted."
            else:
                cursor.execute(
                    "SELECT * FROM Customer WHERE user_ID = % s", (user["user_ID"],)
                )
                customer = cursor.fetchone()
                if customer:
                    session["role"] = "customer"
                    session["loggedin"] = True
                    session["user_ID"] = user["user_ID"]
                    session["username"] = user["name"]
                    return redirect(url_for("customer_main_page"))
                else:
                    cursor.execute(
                        "SELECT * FROM Business WHERE user_ID = % s", (user["user_ID"],)
                    )
                    business = cursor.fetchone()
                    if business:
                        session["role"] = "business"
                        session["loggedin"] = True
                        session["user_ID"] = user["user_ID"]
                        session["username"] = user["name"]
                        return redirect(url_for("business_main_page"))
                    else:
                        session["role"] = "admin"
                        session["loggedin"] = True
                        session["user_ID"] = user["user_ID"]
                        session["username"] = user["name"]
                        return redirect(url_for("admin_main_page"))
        else:
            message = "Please enter correct email / username and password !"
    return render_template("login.html", message=message)


# # Customer and Business registers through this
# # No admin registration is allowed
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Check for valid email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message = "Please enter a valid email format!"
            return render_template("register.html", message=message)

        # Check for strong password
        if not re.match(r"[A-Za-z0-9@#$%^&+=*!(){}[\]:;<>,.?~`_|\\-]{8,}", password):
            message = "Password must be at least 8 characters long and contain a combination of letters, numbers, and special characters!"
            return render_template("register.html", message=message)
        # Hash the password
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM User WHERE name = % s", (username,))
        account = cursor.fetchone()
        cursor.execute("SELECT * FROM User WHERE email = % s", (email,))
        account_email = cursor.fetchone()
        if account:
            message = "Username already exists."
        elif account_email:
            message = "Email address is already registered."
        else:
            role = request.form.get("role")
            new_id = get_next_ID()
            cursor.execute(
                "INSERT INTO User (password, name, email, user_ID) VALUES (% s, % s, %s, %s)",
                (
                    hashed_password,
                    username,
                    email,
                    new_id,
                ),
            )
            mysql.connection.commit()
            if role == "customer":
                cursor.execute(
                    "INSERT INTO Customer (balance, user_ID) VALUES (% s, % s)",
                    (
                        0,
                        new_id,
                    ),
                )
                mysql.connection.commit()
            elif role == "business":
                cursor.execute(
                    "INSERT INTO Business (balance, user_ID) VALUES (% s, % s)",
                    (
                        0,
                        new_id,
                    ),
                )
                mysql.connection.commit()
            message = "User successfully created!"
            return render_template("login.html", message=message)
    elif request.method == "POST":
        message = "Please fill all the fields!"
    return render_template("register.html", message=message)


# Notificaion page for the user
# This page will be used to show the notifications to the user
# The notifications will be fetched from the database
# Link to this page will be provided in the navigation bar
@app.route("/notifications")
def notifications():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = 10
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get paginated notifications for the user
    cursor.execute(
        "SELECT * FROM Notification WHERE user_ID = %s LIMIT %s OFFSET %s",
        (session["user_ID"], per_page, offset),
    )
    notifications = cursor.fetchall()
    role = session["role"]
    return render_template(
        "notifications.html", notifications=notifications, page=page, role=role
    )


# Delete the notification from the database and redirect to the notifications page
@app.route("/notification_delete/<notification_ID>", methods=["POST", "DELETE"])
def notification_delete(notification_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "DELETE FROM Notification WHERE notification_ID = %s", (notification_ID,)
    )
    mysql.connection.commit()
    return redirect(url_for("notifications"))


# Delete all notifications from the database and redirect to the notifications page
@app.route("/notification_delete_all", methods=["POST", "DELETE"])
def notification_delete_all():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Notification WHERE user_ID = %s", (session["user_ID"],))
    mysql.connection.commit()
    return redirect(url_for("notifications"))


# Send a notification to the user with the given user_ID
# If the user_ID is not provided, send the notification to all users
# notification can only be sent by the admins
@app.route("/admin_notification_send", methods=["GET", "POST"])
def admin_notification_send():
    # If the user is not an admin, redirect to the main page
    if session["role"] != "admin":
        if session["role"] == "customer":
            return redirect(
                url_for("customer_main_page")
            )  # Redirect to the customer main page
        elif session["role"] == "business":
            return redirect(url_for("business_main_page"))
        else:
            return redirect(
                url_for("login")
            )  # Redirect to the login page if the user is not logged in

    # Message to be shown to the user
    message = ""
    if request.method == "POST":
        notification_title = request.form["title"]
        notification_text = request.form["text"]
        notification_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification_image_binary_data = None

        # If an image is provided, read the binary data of the image
        if "image" in request.files:
            notification_image = request.files["image"]
            notification_image_binary_data = notification_image.read()  # Read the image

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Get all users
        cursor.execute("SELECT user_ID FROM User")
        users = cursor.fetchall()
        for user in users:
            notification_ID = (
                get_next_ID_notification()
            )  # Get the next available notification ID

            cursor.execute(
                "INSERT INTO Notification (notification_title, notification_text, notification_date, user_ID, notification_image, notification_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    notification_title,
                    notification_text,
                    notification_date,
                    user["user_ID"],
                    notification_image_binary_data,
                    notification_ID,
                ),
            )
            mysql.connection.commit()

        message = (
            "Notification sent successfully!"  # Set the message to be shown to the user
        )

    return render_template("admin_notification_send.html", message=message)


# Customer main page to show the products that are not sold
# The products will be fetched from the database
# Customer will have the ability to add products to the cart
# Customer will have the ability to search for products
# Customer will have the ability to filter products
@app.route("/customer_main_page", methods=["GET", "POST"])
def customer_main_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the page number from the request parameters
    page = max(request.args.get("page", default=1, type=int), 1)

    # Set the number of items per page
    items_per_page = 10
    # Calculate the offset based on the page number and items per page
    offset = (page - 1) * items_per_page
    # Get all products that are not sold using the following query with paging
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status= %s LIMIT %s OFFSET %s",
        ("not_sold", items_per_page, offset),
    )
    product_table = cursor.fetchall()
    # Pass the customer product table, page number, and user session information to HTML
    return render_template(
        "customer_main_page.html",
        product_table=product_table,
        page=page,
        is_in_session=session["loggedin"],
        username=session["username"],
    )


# Business main page to show the products that are not sold by the business
# The business products will be fetched from the database
# Business will have the ability to create and edit a product
@app.route("/business_main_page")
def business_main_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the page number from the request parameters
    page = max(request.args.get("page", default=1, type=int), 1)
    # Set the number of items per page
    items_per_page = 10
    # Calculate the offset based on the page number and items per page
    offset = (page - 1) * items_per_page
    # Modify the query to include paging
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE user_ID = %s LIMIT %s OFFSET %s",
        (session["user_ID"], items_per_page, offset),
    )
    product_table = cursor.fetchall()
    return render_template(
        "business_main_page.html",
        product_table=product_table,
        page=page,
        is_in_session=session["loggedin"],
        username=session["username"],
    )


# This function is used to create a product for the business
@app.route("/business_product_create", methods=["GET", "POST"])
def business_product_create():
    message = ""  # Message to be shown to the user

    # If a POST request is made, then the form is filled
    if request.method == "POST":
        required_fields = ["title", "price", "amount", "category"]

        # Check if all required fields are filled
        if all(field in request.form for field in required_fields):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            title = request.form["title"]
            price = request.form["price"]
            amount = request.form["amount"]
            category = request.form["category"]
            product_ID = get_next_ID_product()
            status = "not_sold"

            query = "INSERT INTO Product (product_ID, title, price, category, product_status"
            values = [product_ID, title, price, category, status]

            optional_fields = [
                "product_description",
                "cover_picture",
                "proportions",
                "mass",
                "color",
                "product_date",
            ]

            # Check if optional fields are filled
            for field in optional_fields:
                # If the field is date, convert it to datetime object and add it to the query
                if field == "date" and field in request.form and request.form[field]:
                    query += f", {field}"
                    date = datetime.strptime(request.form[field], "%Y-%m-%dT%H:%M")
                    values.append(date)
                # If the field is filled, add it to the query
                elif field in request.form and request.form[field]:
                    query += f", {field}"

                    # If the field is not cover_picture, add it to the query as a string
                    if field != "cover_picture":
                        values.append(request.form[field])

                    # If the field is cover_picture, add it to the query as binary data
                    else:
                        cover_picture = request.files["cover_picture"]
                        cover_picture_binary_data = cover_picture.read()
                        values.append(cover_picture_binary_data)

            # Add the values to the query
            query += ") VALUES (" + ", ".join(["%s"] * len(values)) + ")"

            # Insert the picture into Product_Picture
            picture = request.files["pictures"]
            picture_binary_data = picture.read()

            # Try to insert the product into the database
            try:
                cursor.execute(query, values)
                cursor.execute(
                    "INSERT INTO Owns(user_ID, product_ID, amount) VALUES (%s, %s, %s)",
                    (session["user_ID"], product_ID, int(amount)),
                )
                cursor.execute(
                    "INSERT INTO Product_Picture(product_ID, picture) VALUES (%s, %s)",
                    (product_ID, picture_binary_data),
                )
                mysql.connection.commit()
                flash("Product created successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
                mysql.connection.rollback()
            cursor.close()
        else:
            message = "Please fill the required fields"
            flash(message, "warning")

    return render_template("business_product_create.html", message=message)


# This function is used to edit a product for the business
@app.route("/business_product_edit/<product_ID>", methods=["GET", "POST"])
def business_product_edit(product_ID):
    message = ""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_ID = %s", (product_ID,)
    )
    product = cursor.fetchone()

    if request.method == "POST":
        required_fields = ["title", "price", "amount", "category"]

        if all(field in request.form for field in required_fields):
            title = request.form["title"]
            price = request.form["price"]
            amount = request.form["amount"]
            category = request.form["category"]
            status = "not_sold"

            query = "UPDATE Product SET title = %s, price = %s, category = %s, product_status = %s"
            values = [title, price, category, status]

            optional_fields = [
                "product_description",
                "cover_picture",
                "proportions",
                "mass",
                "color",
                "product_date",
            ]

            for field in optional_fields:
                if field == "date" and field in request.form and request.form[field]:
                    query += f", {field} = %s"
                    date = datetime.strptime(request.form[field], "%Y-%m-%dT%H:%M")
                    values.append(date)
                elif field in request.form and request.form[field]:
                    query += f", {field} = %s"

                    if field != "cover_picture":
                        values.append(request.form[field])
                    else:
                        cover_picture = request.files["cover_picture"]
                        cover_picture_binary_data = cover_picture.read()
                        values.append(cover_picture_binary_data)

            query += " WHERE product_ID = %s"
            values.append(product_ID)

            try:
                cursor.execute(query, values)
                cursor.execute(
                    "UPDATE Owns SET amount = %s WHERE product_ID = %s",
                    (int(amount), product_ID),
                )
                mysql.connection.commit()
                flash("Product updated successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
                mysql.connection.rollback()
            cursor.close()
        else:
            message = "Please fill the required fields"
            flash(message, "warning")

    # Get the product information from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_ID = %s", (product_ID,)
    )
    product = cursor.fetchone()

    return render_template(
        "business_product_edit.html", product=product, message=message
    )


@app.route("/admin_main_page")
def admin_main_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all products that are not sold using the following query
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_status= %s",
        ("not_sold",),
    )
    product_table = cursor.fetchall()
    return render_template(
        "admin_main_page.html",
        product_table=product_table,
        is_in_session=session["loggedin"],
        username=session["username"],
    )


# TODO Explain and fix the function
@app.route("/balance", methods=["GET", "POST"])
def balance():
    message = ""
    if request.method == "POST":
        amount = request.form["amount"]
        if amount:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "UPDATE Customer SET balance = balance + %s WHERE user_ID = %s",
                (
                    amount,
                    session["user_ID"],
                ),
            )
            mysql.connection.commit()
            flash("Balance is updated successfully!", "success")
        else:
            message = "Please fill the required fields"
            flash(message, "warning")
    return render_template("balance.html", message=message)


@app.route("/balance_business", methods=["GET", "POST"])
def balance_business():
    message = ""
    if request.method == "POST":
        amount = request.form["amount"]
        if amount:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "UPDATE Business SET balance = balance + %s WHERE user_ID = %s",
                (
                    amount,
                    session["user_ID"],
                ),
            )
            mysql.connection.commit()
            flash("Balance is updated successfully!", "success")
        else:
            message = "Please fill the required fields"
            flash(message, "warning")
    return render_template("balance_business.html", message=message)


@app.route("/shopping_cart")
def shopping_cart():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all products from shopping cart
    cursor.execute(
        "SELECT product_ID, title, price, amount FROM Product NATURAL JOIN Puts_On_Cart NATURAL JOIN User  WHERE user_ID= %s",
        (session["user_ID"],),
    )
    cart = cursor.fetchall()

    return render_template("shopping_cart.html", cart=cart)


# Called when a user adds an item to their shopping cart
@app.route("/add_to_cart/<product_ID>/<amount>")
def add_to_cart(product_ID, amount):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If it is not already in the cart then insert, otherwise update the amount
    cursor.execute("SELECT amount FROM Owns WHERE product_ID = %s", (product_ID,))
    stock = cursor.fetchone()
    cursor.execute(
        "SELECT amount FROM Puts_On_Cart WHERE product_ID = %s AND user_ID = %s",
        (product_ID, session["user_ID"]),
    )
    amountInCart = cursor.fetchone()
    if amountInCart is None:
        if int(amount) <= stock["amount"]:
            cursor.execute(
                "INSERT INTO Puts_On_Cart (user_ID, product_ID, amount) VALUES (%s, %s, %s)",
                (session["user_ID"], product_ID, amount),
            )
            mysql.connection.commit()
        else:
            response = jsonify({"message": "Failure"})
            response.status_code = 500
            return response
    else:
        if int(amount) + amountInCart["amount"] <= stock["amount"]:
            cursor.execute(
                "INSERT INTO Puts_On_Cart (user_ID, product_ID, amount) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)",
                (session["user_ID"], product_ID, amount),
            )
            mysql.connection.commit()
        else:
            response = jsonify({"message": "Failure"})
            response.status_code = 500
            return response

    response = jsonify({"message": "Success"})
    response.status_code = 200
    return response


# Remove an item from the cart
@app.route("/remove_from_cart/<product_ID>")
def remove_from_cart(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "DELETE FROM Puts_On_Cart WHERE product_ID = %s AND user_ID = %s",
        (product_ID, session["user_ID"]),
    )
    mysql.connection.commit()
    return redirect(url_for("shopping_cart"))


# Checkout, add the items up and provide the "confirm purchase" order
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    # an item in cart has the following fields: product_ID, title, price, amount
    # sum up the total price
    total_price = 0
    list = request.get_json()
    cartlist = list
    for item in cartlist:
        total_price += float(item["price"]) * int(item["amount"])

    # Get existing addresses
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # We could come up with a view for the address
    cursor.execute(
        "SELECT country, city, state_code, zip_code, building, street, address_description FROM User WHERE user_ID = %s",
        (session["user_ID"],),
    )
    address = cursor.fetchone()
    response = {
        "redirect_url": url_for(
            "render_checkout",
            cart=json.dumps(cartlist),
            total_price=total_price,
            address=json.dumps(address),
        )
    }
    return jsonify(response)


@app.route("/render_checkout")
def render_checkout():
    cart = json.loads(request.args.get("cart"))
    total_price = request.args.get("total_price")
    address = json.loads(request.args.get("address"))
    return render_template(
        "checkout.html", cart=cart, total_price=total_price, address=address
    )


@app.route("/enteraddress", methods=["POST"])
def enteraddress():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    addressJSON = request.get_json()
    # addressJSON = json.loads(address)
    cursor.execute(
        "UPDATE User SET country = %s, city = %s, state_code = %s, zip_code = %s, building = %s, street = %s, address_description = %s WHERE user_ID = %s",
        (
            addressJSON["country"],
            addressJSON["city"],
            addressJSON["state"],
            addressJSON["zip"],
            addressJSON["building"],
            addressJSON["street"],
            addressJSON["address_description"],
            session["user_ID"],
        ),
    )
    mysql.connection.commit()
    response = jsonify({"message": "Success"})
    response.status_code = 200
    return response


@app.route("/confirm_purchase", methods=["POST"])
def confirm_purchase():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get the items inside the shopping cart
    cursor.execute(
        "SELECT product_ID, title, price, amount FROM Product NATURAL JOIN Puts_On_Cart NATURAL JOIN User  WHERE user_ID= %s",
        (session["user_ID"],),
    )
    cart = cursor.fetchall()

    # Get the balance of the customer
    cursor.execute(
        "SELECT balance FROM Customer WHERE user_ID = %s", (session["user_ID"],)
    )

    balanceDict = cursor.fetchone()
    balance = balanceDict["balance"]

    # Check the availability of each product in the cart, they might have gone out of stock
    available = []
    out_of_stock = []
    for item in cart:
        cursor.execute(
            "SELECT amount FROM Owns WHERE product_ID = %s", (item["product_ID"],)
        )
        amount = cursor.fetchone()
        item["product_amount"] = amount["amount"]
        if amount["amount"] >= item["amount"]:
            available.append(item)
        else:
            out_of_stock.append(item)

    # Check if the balance of our current user is enough for the items that are available
    insufficient_balance = False
    totalprice = 0
    for item in available:
        totalprice += item["price"] * item["amount"]
    if totalprice > balance:
        insufficient_balance = True

    # If the balance is enough, confirm purchase and create a purchase_info
    if not insufficient_balance:
        for item in available:
            total_price = item["price"] * item["amount"]
            cursor.execute(
                "INSERT INTO Purchase_Information(purchase_ID, purchase_status, total_price, purchase_date, user_ID , product_ID, amount) VALUES(%s, %s,%s,%s,%s,%s,%s)",
                (
                    get_next_ID_purchase_info(),
                    "purchased",
                    total_price,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    session["user_ID"],
                    item["product_ID"],
                    item["amount"],
                ),
            )

            # Reduce the amount from OWNS
            newamount = item["product_amount"] - item["amount"]
            cursor.execute(
                "UPDATE Owns SET amount = %s WHERE product_ID = %s",
                (newamount, item["product_ID"]),
            )
            mysql.connection.commit()

            # remove the item from the cart
            cursor.execute(
                "DELETE FROM Puts_On_Cart WHERE user_ID = %s AND product_ID = %s",
                (session["user_ID"], item["product_ID"]),
            )
            mysql.connection.commit()

            # update the balance of the business
            cursor.execute(
                "SELECT user_ID FROM Owns WHERE product_ID = %s", (item["product_ID"],)
            )

            business = cursor.fetchone()
            businessID = business["user_ID"]

            cursor.execute(
                "UPDATE Business SET balance = balance + %s WHERE user_ID = %s",
                (total_price, businessID),
            )
            mysql.connection.commit()

        # finally update the balance of the customer
        balance -= totalprice
        cursor.execute(
            "UPDATE Customer SET balance = %s WHERE user_ID = %s",
            (balance, session["user_ID"]),
        )
        mysql.connection.commit()
    # this page will show the purchased items and out of stock items if any and if the balance is sufficent
    # if the balance is insufficient it will show the out of stock items as well as a message saying that the user has insufficient balance
    # Store the purchase result in the session
    session["purchase_result"] = {
        "insufficient_balance": insufficient_balance,
        "available": available,
        "out_of_stock": out_of_stock,
        "balance": balance,
    }

    return redirect(url_for("purchase_summary"))


@app.route("/purchase_summary")
def purchase_summary():
    purchase_result = session.pop("purchase_result", None)
    if purchase_result is None:
        return redirect(url_for("customer_main_page"))

    return render_template(
        "purchase_screen.html",
        insufficient_balance=purchase_result["insufficient_balance"],
        available=purchase_result["available"],
        out_of_stock=purchase_result["out_of_stock"],
        balance=purchase_result["balance"],
    )


@app.route("/customer_active_orders", methods=["GET"])
def customer_active_orders():
    # Display according to their order status
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Purchase_Information WHERE user_ID = %s AND purchase_status = %s",
        (session["user_ID"], "purchased"),
    )
    purchaseinfo = cursor.fetchall()

    for info in purchaseinfo:
        cursor.execute(
            "SELECT * FROM Product WHERE product_ID = %s", (info["product_ID"],)
        )
        product = cursor.fetchone()
        info["title"] = product["title"]
        info["cover_picture"] = product["cover_picture"]

    past = False
    return render_template("customer_orders.html", purchaseinfo=purchaseinfo, past=past)


# Returns/refunds the active order
# The order status will be updated to returned
# The product amount will be updated
# The user balance will be updated
# The business balance will be updated
# Active order will be marked as returned and moved to past orders
# The user will be redirected to the active orders page
@app.route("/customer_order_return/<purchase_ID>", methods=["POST", "DELETE", "GET"])
def customer_order_return(purchase_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Purchase_Information WHERE purchase_ID = %s", (purchase_ID,)
    )
    purchase = cursor.fetchone()
    cursor.execute(
        "SELECT * FROM Product WHERE product_ID = %s", (purchase["product_ID"],)
    )
    product = cursor.fetchone()

    # Update the product amount
    cursor.execute(
        "UPDATE Owns SET amount = amount + %s WHERE product_ID = %s",
        (purchase["amount"], product["product_ID"]),
    )
    mysql.connection.commit()

    # Update the user balance
    cursor.execute(
        "SELECT balance FROM Customer WHERE user_ID = %s", (session["user_ID"],)
    )
    balance = cursor.fetchone()
    cursor.execute(
        "UPDATE Customer SET balance = balance + %s WHERE user_ID = %s",
        (purchase["total_price"], session["user_ID"]),
    )
    mysql.connection.commit()

    # Update the business balance
    cursor.execute(
        "SELECT user_ID FROM Owns WHERE product_ID = %s", (product["product_ID"],)
    )
    business = cursor.fetchone()
    cursor.execute(
        "UPDATE Business SET balance = balance - %s WHERE user_ID = %s",
        (purchase["total_price"], business["user_ID"]),
    )
    mysql.connection.commit()

    # Update the purchase status
    cursor.execute(
        "UPDATE Purchase_Information SET purchase_status = %s WHERE purchase_ID = %s",
        ("returned", purchase_ID),
    )
    mysql.connection.commit()

    # Send notification to the business
    cursor.execute(
        "INSERT INTO Notification (notification_title, notification_text, notification_date, user_ID, notification_ID) VALUES (%s, %s, %s, %s, %s)",
        (
            "Order Returned",
            f"Order with purchase ID {purchase_ID} has been returned",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            business["user_ID"],
            get_next_ID_notification(),
        ),
    )
    mysql.connection.commit()

    # Now redirect to the active orders page by fetching the active orders again
    # Display according to their order status
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Purchase_Information WHERE user_ID = %s AND purchase_status = %s",
        (session["user_ID"], "purchased"),
    )
    purchaseinfo = cursor.fetchall()

    for info in purchaseinfo:
        cursor.execute(
            "SELECT * FROM Product WHERE product_ID = %s", (info["product_ID"],)
        )
        product = cursor.fetchone()
        info["title"] = product["title"]
        info["cover_picture"] = product["cover_picture"]

    past = False

    return render_template("customer_orders.html", purchaseinfo=purchaseinfo, past=past)


@app.route("/customer_past_orders", methods=["GET"])
def customer_past_orders():
    # Display according to their order status
    # Display shipped orders
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Purchase_Information WHERE user_ID = %s AND purchase_status = %s",
        (session["user_ID"], "shipped"),
    )
    purchaseinfo = cursor.fetchall()

    # Display returned orders
    cursor.execute(
        "SELECT * FROM Purchase_Information WHERE user_ID = %s AND purchase_status = %s",
        (session["user_ID"], "returned"),
    )
    purchaseinfo += cursor.fetchall()

    for info in purchaseinfo:
        cursor.execute(
            "SELECT * FROM Product WHERE product_ID = %s", (info["product_ID"],)
        )
        product = cursor.fetchone()
        info["title"] = product["title"]
        info["cover_picture"] = product["cover_picture"]

    past = True
    return render_template("customer_orders.html", purchaseinfo=purchaseinfo, past=past)


# The orders received and shipped by the business
@app.route("/business_past_orders", methods=["GET"])
def business_past_orders():
    # Display according to their order status
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all products of the business
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE user_ID = %s",
        (session["user_ID"],),
    )
    products = cursor.fetchall()
    purchaseinfo = []
    for item in products:
        cursor.execute(
            "SELECT * FROM Purchase_Information WHERE product_ID = %s AND purchase_status = %s",
            (item["product_ID"], "shipped"),
        )
        purchase = cursor.fetchone()
        if purchase:
            purchase["title"] = item["title"]
            purchase["cover_picture"] = item["cover_picture"]
            purchaseinfo.append(purchase)

    return render_template(
        "business_past_orders.html",
        purchaseinfo=purchaseinfo,
    )


# The orders received by the business
@app.route("/business_active_orders", methods=["GET"])
def business_active_orders():
    # Display according to their order status
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all products of the business
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE user_ID = %s",
        (session["user_ID"],),
    )
    products = cursor.fetchall()
    purchaseinfo = []
    for item in products:
        cursor.execute(
            "SELECT * FROM Purchase_Information WHERE product_ID = %s AND purchase_status <> %s",
            (item["product_ID"], "shipped"),
        )
        purchase = cursor.fetchone()
        if purchase:
            purchase["title"] = item["title"]
            purchase["cover_picture"] = item["cover_picture"]
            purchaseinfo.append(purchase)

    return render_template("business_active_orders.html", purchaseinfo=purchaseinfo)


@app.route("/update_purchase_status/<newstatus>/<product_ID>", methods=["POST"])
def update_purchase_status(newstatus, product_ID, user_ID):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "UPDATE Purchase_Information SET purchase_status = %s WHERE product_ID = %s AND user_ID = %s",
        (newstatus, product_ID, user_ID),
    )
    mysql.connection.commit()
    # TODO send notification
    return redirect(url_for("business_active_orders"))


# Profile page for the customer
# This page will be used to show the customer details
# The customer details will be fetched from the database
# Link to this page will be provided in the customer_main_page.html
@app.route("/customer_profile")
def customer_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the customer details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Customer WHERE user_ID = %s",
        (session["user_ID"],),
    )
    customer = cursor.fetchone()
    return render_template("customer_profile.html", customer=customer)


# Edit profile page for the customer
# This page will be used to edit the customer details
# The customer details will be fetched from the database
# Link to this page will be provided in the customer_profile.html


@app.route("/customer_profile_edit", methods=["GET", "POST"])
def customer_profile_edit():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get the customer details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Customer WHERE user_ID = %s",
        (session["user_ID"],),
    )

    # Fetch the customer details
    customer = cursor.fetchone()

    # If the form is submitted, update the customer details in the database and show a message
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone_number = request.form["phone_number"]
        country = request.form["country"]
        city = request.form["city"]
        state_code = request.form["state_code"]
        zip_code = request.form["zip_code"]
        building = request.form["building"]
        street = request.form["street"]
        address_description = request.form["address_description"]

        # If an image is provided, read the binary data of the image
        if "picture" in request.files:
            picture = request.files["picture"]
            picture_binary_data = picture.read()
        else:
            picture_binary_data = None

        # If password field is not empty, hash the password
        if password:
            hashedpassword = generate_password_hash(password)
        else:
            hashedpassword = customer["password"]

        # Update the customer details in the database
        cursor.execute(
            "UPDATE User SET name = %s, email = %s, password = %s, phone_number = %s, country = %s, city = %s, state_code = %s, zip_code = %s, building = %s, street = %s, address_description = %s, picture = %s WHERE user_ID = %s",
            (
                name,
                email,
                hashedpassword,
                phone_number,
                country,
                city,
                state_code,
                zip_code,
                building,
                street,
                address_description,
                picture_binary_data,
                session["user_ID"],
            ),
        )
        mysql.connection.commit()  # Commit the changes to the database

        # Update the current details of the customer
        cursor.execute(
            "SELECT * FROM User NATURAL JOIN Customer WHERE user_ID = %s",
            (session["user_ID"],),
        )
        customer = cursor.fetchone()

        return render_template(
            "customer_profile.html",
            message="Profile updated successfully",
            customer=customer,
        )  # Show a message to the user that the profile is updated
    return render_template("customer_profile_edit.html", customer=customer)


# Delete profile page for the customer
# This page will be used to delete the customer details
# The customer details will be fetched from the database
# Link to this page will be provided in the customer_profile.html
@app.route("/customer_profile_delete", methods=["GET", "POST"])
def customer_profile_delete():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the customer details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Customer WHERE user_ID = %s",
        (session["user_ID"],),
    )
    customer = cursor.fetchone()
    if request.method == "POST":
        cursor.execute(
            "DELETE FROM User WHERE user_ID = %s",
            (session["user_ID"],),
        )
        mysql.connection.commit()

        # Redirect to the login page by clearing the session
        session.clear()

        return render_template("login.html", message="Account deleted successfully")

    return render_template("customer_profile_delete.html", customer=customer)


# Profile page for the business
# This page will be used to show the business details
# The business details will be fetched from the database
# Link to this page will be provided in the business_main_page.html
@app.route("/business_profile")
def business_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the business details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Business WHERE user_ID = %s",
        (session["user_ID"],),
    )
    business = cursor.fetchone()
    return render_template("business_profile.html", business=business)


# Edit profile page for the business
# This page will be used to edit the business details
# The business details will be fetched from the database
# Link to this page will be provided in the business_profile.html
@app.route("/business_profile_edit", methods=["GET", "POST"])
def business_profile_edit():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get the business details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Business WHERE user_ID = %s",
        (session["user_ID"],),
    )
    business = cursor.fetchone()

    # If the form is submitted, update the business details in the database and show a message
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone_number = request.form["phone_number"]
        country = request.form["country"]
        city = request.form["city"]
        state_code = request.form["state_code"]
        zip_code = request.form["zip_code"]
        building = request.form["building"]
        street = request.form["street"]
        address_description = request.form["address_description"]

        picture_binary_data = None
        # If an image is provided, read the binary data of the image
        if "picture" in request.files:
            picture = request.files["picture"]
            print(picture)
            picture_binary_data = picture.read()
            print(picture_binary_data)

        if password:
            # Hash the password
            hashedpassword = generate_password_hash(password)
        else:
            hashedpassword = business["password"]
        # Update the business details in the database
        cursor.execute(
            "UPDATE User SET name = %s, email = %s, password = %s, phone_number = %s, country = %s, city = %s, state_code = %s, zip_code = %s, building = %s, street = %s, address_description = %s, picture = %s WHERE user_ID = %s",
            (
                name,
                email,
                hashedpassword,
                phone_number,
                country,
                city,
                state_code,
                zip_code,
                building,
                street,
                address_description,
                picture_binary_data,
                session["user_ID"],
            ),
        )
        mysql.connection.commit()

        # Update the current details of the business
        cursor.execute(
            "SELECT * FROM User NATURAL JOIN Business WHERE user_ID = %s",
            (session["user_ID"],),
        )
        business = cursor.fetchone()

        return render_template(
            "business_profile.html",
            message="Profile updated successfully",
            business=business,
        )
    return render_template("business_profile_edit.html", business=business)


# Delete profile page for the business
# This page will be used to delete the business details
# The business details will be fetched from the database
# Link to this page will be provided in the business_profile.html
@app.route("/business_profile_delete", methods=["GET", "POST"])
def business_profile_delete():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the business details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Business WHERE user_ID = %s",
        (session["user_ID"],),
    )
    business = cursor.fetchone()

    #  Delete all products of the business
    cursor.execute(
        "DELETE FROM Owns WHERE user_ID = %s",
        (session["user_ID"],),
    )
    mysql.connection.commit()

    #  Delete the business
    if request.method == "POST":
        cursor.execute(
            "DELETE FROM User WHERE user_ID = %s",
            (session["user_ID"],),
        )
        mysql.connection.commit()

        # clear the session
        session.clear()

        return render_template("login.html", message="Account deleted successfully")

    return render_template("business_profile_delete.html", business=business)


# Profile page for the admin
# This page will be used to show the admin details
# The admin details will be fetched from the database
# Link to this page will be provided in the admin_main_page.html
@app.route("/admin_profile")
def admin_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the admin details from the database using the user_ID
    cursor.execute(
        "SELECT * FROM User NATURAL JOIN Admin WHERE user_ID = %s",
        (session["user_ID"],),
    )
    admin = cursor.fetchone()
    return render_template("admin_profile.html", admin=admin)


# This page will be used to show the customer product details and the customer product picture
# The customer product details will be fetched from the database
# Link to this page will be provided in the customer_main_page.html, link will be /customer_product/<product_ID>
# The product_ID will be passed to this page as a parameter


@app.route("/customer_product/<product_ID>/add_comment", methods=["POST"])
def add_comment(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    content = request.json.get("content")
    if not content:
        return jsonify({"success": False, "error": "Content is required"}), 400

    try:
        cursor.execute(
            "SELECT name FROM User WHERE user_ID = %s", (session["user_ID"],)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        username = user["name"]
        comment_ID = (
            get_next_ID_comment()
        )  # Ensure this function generates the next comment ID correctly
        cursor.execute(
            "INSERT INTO Comment (comment_ID, user_ID, product_ID, text) VALUES (%s, %s, %s, %s)",
            (comment_ID, session["user_ID"], product_ID, content),
        )
        mysql.connection.commit()
        return jsonify({"success": True, "username": username})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/delete_product/<product_ID>", methods=["DELETE"])
def delete_product(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Check if the product exists
        cursor.execute("SELECT * FROM Product WHERE product_ID = %s", (product_ID,))
        product = cursor.fetchone()

        if product:
            # Check if the user is authorized to delete the product (you need to implement this logic)
            # For example, you might check if the user is the owner of the product or has appropriate permissions

            # Delete the product
            cursor.execute("DELETE FROM Product WHERE product_ID = %s", (product_ID,))
            mysql.connection.commit()
            return jsonify({"success": True}), 200
        else:
            # Product not found
            return jsonify({"success": False, "error": "Product not found"}), 404
    except Exception as e:
        # Handle any database or other errors
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()


@app.route(
    "/customer_product/<product_ID>/delete_comment/<comment_ID>", methods=["DELETE"]
)
def delete_comment(product_ID, comment_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if the comment exists and belongs to the current user
    cursor.execute(
        "SELECT * FROM Comment WHERE comment_ID = %s AND user_ID = %s",
        (comment_ID, session["user_ID"]),
    )
    comment = cursor.fetchone()

    if comment:
        # Delete the comment
        cursor.execute("DELETE FROM Comment WHERE comment_ID = %s", (comment_ID,))
        mysql.connection.commit()
        return jsonify({"success": True}), 200
    else:
        return (
            jsonify({"success": False, "error": "Comment not found or unauthorized"}),
            404,
        )


@app.route("/customer_product/<product_ID>", methods=["GET", "POST"])
def customer_product(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the customer product details from the database using the product_ID
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_ID = %s", (product_ID,)
    )
    customer_product = cursor.fetchone()

    # Get the customer product picture from the database using the product_ID
    cursor.execute("SELECT * FROM Product_Picture WHERE product_ID = %s", (product_ID,))
    product_picture = cursor.fetchone()
    encoded_image = None
    if product_picture is not None:
        image_data = product_picture["picture"]
        encoded_image = base64.b64encode(image_data).decode("utf-8")

    # Get the comments for the product
    cursor.execute(
        "SELECT Comment.*, User.name as username FROM Comment JOIN User ON Comment.user_ID = User.user_ID WHERE product_ID = %s",
        (product_ID,),
    )
    comments = cursor.fetchall()

    # Render the template with the product details and comments
    return render_template(
        "customer_product.html",
        customer_product=customer_product,
        product_picture=encoded_image,
        comments=comments,
    )


import logging


@app.route("/customer_product/<product_ID>/add_report", methods=["POST"])
def add_report(product_ID):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get the report content from the request JSON
        report_content = request.json.get("content")

        # Ensure content is provided
        if not report_content:
            return jsonify({"success": False, "error": "Content is required"}), 400

        # Retrieve user_ID from the session
        user_ID = session.get("user_ID")

        if user_ID is None:
            return jsonify({"success": False, "error": "User session not found"}), 400

        # Get the user_ID of the seller associated with the product
        cursor.execute(
            "SELECT user_ID FROM Product NATURAL JOIN Owns WHERE product_ID = %s",
            (product_ID,),
        )
        seller_user = cursor.fetchone()

        if seller_user is None:
            return jsonify({"success": False, "error": "Seller user not found"}), 404

        seller_user_ID = seller_user["user_ID"]

        # Insert report into the database
        report_ID = (
            generate_report_id()
        )  # Assuming this function generates a unique report ID
        cursor.execute(
            "INSERT INTO Report (report_ID, report_date, report_description, product_ID, reported_user_ID, user_ID, report_status) "
            "VALUES (%s, NOW(), %s, %s, %s, %s, %s)",
            (
                report_ID,
                report_content,
                product_ID,
                seller_user_ID,
                user_ID,
                "Under Review",
            ),
        )
        # Commit the transaction
        mysql.connection.commit()
        cursor.close()
        return jsonify({"success": True}), 200

    except Exception as e:
        # Rollback the transaction in case of any error
        mysql.connection.rollback()
        logging.error(f"Error adding report: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# This page will be used to show the business product details and the business product picture
# The business product details will be fetched from the database
# Link to this page will be provided in the business_main_page.html, link will be /business_product/<product_ID>
# The product_ID will be passed to this page as a parameter
@app.route("/business_product/<product_ID>")
def business_product(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get the business product details from the database using the product_ID
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_ID = %s", (product_ID,)
    )
    business_product = cursor.fetchone()

    # Get the business product picture from the database using the product_ID
    cursor.execute("SELECT * FROM Product_Picture WHERE product_ID = %s", (product_ID,))
    product_picture = cursor.fetchone()
    encoded_image = None
    if product_picture is not None:
        image_data = product_picture["picture"]
        encoded_image = base64.b64encode(image_data).decode("utf-8")
    if product_picture:
        image_data = product_picture["picture"]
        encoded_image = base64.b64encode(image_data).decode("utf-8")

    # Get comments for the product
    cursor.execute(
        "SELECT Comment.*, User.name as username FROM Comment JOIN User JOIN Customer ON Comment.user_ID = User.user_ID AND Customer.user_ID = Comment.user_ID  WHERE product_ID = %s",
        (product_ID,),
    )
    comments = cursor.fetchall()

    # Get the business comments
    cursor.execute(
        "SELECT Comment.*, User.name as username FROM Comment JOIN User JOIN Business ON Comment.user_ID = User.user_ID AND Business.user_ID = Comment.user_ID  WHERE product_ID = %s",
        (product_ID,),
    )
    business_comments = cursor.fetchall()
    return render_template(
        "business_product.html",
        business_product=business_product,
        product_picture=encoded_image,
        comments=comments,
        business_comments=business_comments,
    )


# This page will be used to show the admin product details and the admin product picture
# The admin product details will be fetched from the database
# Link to this page will be provided in the admin_main_page.html, link will be /admin_product/<product_ID>
# The product_ID will be passed to this page as a parameter
@app.route("/admin_product/<product_ID>")
def admin_product(product_ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get the admin product details from the database using the product_ID
    cursor.execute(
        "SELECT * FROM Owns NATURAL JOIN Product WHERE product_ID = %s", (product_ID,)
    )
    admin_product = cursor.fetchone()
    # Get the admin product picture from the database using the product_ID
    cursor.execute("SELECT * FROM Product_Picture WHERE product_ID = %s", (product_ID,))
    product_picture = cursor.fetchone()
    return render_template(
        "admin_product.html",
        admin_product=admin_product,
        product_picture=product_picture,
    )


@app.route("/logout")
def logout():
    # Pop all the elements that are in local storage, and leave the system
    session.pop("role", None)
    session.pop("user_ID", None)
    session.pop("username", None)
    return redirect(url_for("login"))


# TODO: Explain and fix the function
@app.route("/tables")
def admin():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch data from the User table
    cursor.execute("SELECT * FROM User ORDER BY user_ID")
    users = cursor.fetchall()

    # Fetch data from the Customer table
    cursor.execute("SELECT * FROM Customer ORDER BY user_ID")
    customers = cursor.fetchall()

    # Fetch data from the Business table
    cursor.execute("SELECT * FROM Business ORDER BY user_ID")
    businesses = cursor.fetchall()

    # Fetch data from the Admin table
    cursor.execute("SELECT * FROM Admin ORDER BY user_ID")
    admins = cursor.fetchall()

    # Fetch data from the Product table
    cursor.execute("SELECT * FROM Product ORDER BY product_ID")
    products = cursor.fetchall()

    # Fetch data from the Product_Picture table
    cursor.execute("SELECT * FROM Product_Picture ORDER BY product_ID")
    product_pictures = cursor.fetchall()

    # Fetch data from the Owns table
    cursor.execute("SELECT * FROM Owns ORDER BY user_ID, product_ID")
    owns = cursor.fetchall()

    # Fetch data from the Wishes table
    cursor.execute("SELECT * FROM Wishes ORDER BY user_ID, product_ID")
    wishes = cursor.fetchall()

    # Fetch data from the Puts_On_Cart table
    cursor.execute("SELECT * FROM Puts_On_Cart ORDER BY user_ID, product_ID")
    puts_on_cart = cursor.fetchall()

    # Fetch data from the Purchase_Information table
    cursor.execute("SELECT * FROM Purchase_Information ORDER BY purchase_ID")
    purchase_info = cursor.fetchall()

    # Fetch data from the Return_Request_Information table
    cursor.execute("SELECT * FROM Return_Request_Information ORDER BY return_ID")
    return_requests = cursor.fetchall()

    # Fetch data from the Has_Return_Request table
    cursor.execute("SELECT * FROM Has_Return_Request ORDER BY return_ID, product_ID")
    has_return_request = cursor.fetchall()

    # Fetch data from the Report table
    cursor.execute("SELECT * FROM Report ORDER BY report_ID")
    reports = cursor.fetchall()

    # Fetch data from the Blacklists table
    cursor.execute("SELECT * FROM Blacklists ORDER BY user_ID, report_ID, admin_ID")
    blacklists = cursor.fetchall()

    # Pass the fetched data to the render_template function
    return render_template(
        "admin_tables.html",
        users=users,
        customers=customers,
        businesses=businesses,
        admins=admins,
        products=products,
        product_pictures=product_pictures,
        owns=owns,
        wishes=wishes,
        puts_on_cart=puts_on_cart,
        purchase_info=purchase_info,
        return_requests=return_requests,
        has_return_request=has_return_request,
        reports=reports,
        blacklists=blacklists,
    )


# TODO: Explain and fix the function
@app.route("/admin_user_report", methods=["GET", "POST"])
def admin_user_report():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        action = request.form.get("action")
        report_ID = request.form.get("report_ID")
        report_date = request.form.get("report_date")
        report_description = request.form.get("report_description")
        product_ID = request.form.get("product_ID")
        reported_user_ID = request.form.get("reported_user_ID")
        purchase_ID = request.form.get("purchase_ID")
        return_ID = request.form.get("return_ID")
        user_ID = request.form.get("user_ID")

        cursor = mysql.connection.cursor()

        if action == "ban":
            # "UPDATE User SET name = %s WHERE user_ID = %s",
            query = "UPDATE Report SET report_status = 'Resolved' WHERE reported_user_ID = %s"
            cursor.execute(query, (reported_user_ID,))
            query = "INSERT INTO Blacklists (user_ID, report_ID, admin_ID, reason_description) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                query,
                (
                    reported_user_ID,
                    report_ID,
                    session["user_ID"],
                    report_description,
                ),
            )
            mysql.connection.commit()
            return redirect(url_for("admin_user_report"))

        elif action == "dismiss":
            query = "UPDATE Report SET report_status = 'Resolved' WHERE report_ID = %s"
            cursor.execute(query, (report_ID,))
            mysql.connection.commit()
            return redirect(url_for("admin_user_report"))

        elif action == "delete":
            query = "DELETE FROM Report WHERE report_ID = %s"
            cursor.execute(query, (report_ID,))
            mysql.connection.commit()
            return redirect(url_for("admin_user_report"))

    cursor.execute(
        "SELECT * FROM Report WHERE report_status='Under Review' ORDER BY report_id"
    )
    reports = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM Report WHERE report_status='Resolved' ORDER BY report_id"
    )
    solved_reports = cursor.fetchall()

    return render_template(
        "admin_user_report.html", reports=reports, solved_reports=solved_reports
    )


# TODO: Explain and fix the function
@app.route("/admin_system_report", methods=["GET", "POST"])
def admin_system_report():
    return render_template("admin_system_report.html")


# TODO: Explain and fix the function
@app.route("/admin_blacklist", methods=["GET", "POST"])
def admin_blacklist():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    message = ""

    if request.method == "POST" and "user_id" in request.form:
        user_id = request.form["user_id"]
        query = "DELETE FROM Blacklists WHERE user_ID = %s"
        cursor.execute(query, (user_id,))
        mysql.connection.commit()
        message = "%s is removed from blacklist" % user_id
        # return redirect(url_for("admin_blacklist"))

    search_query = request.args.get("search_query", "")

    if search_query:
        query = """
        SELECT b.user_ID, u.name, b.report_ID, b.reason_description
        FROM Blacklists b
        INNER JOIN User u ON b.user_ID = u.user_ID
        WHERE b.user_ID LIKE %s OR u.name LIKE %s
        ORDER BY b.user_ID, b.report_ID, b.admin_ID
        """
        cursor.execute(query, ("%" + search_query + "%", "%" + search_query + "%"))
    else:
        # Perform a join between Blacklists and User tables without search condition
        query = """
        SELECT b.user_ID, u.name, b.report_ID, b.reason_description
        FROM Blacklists b
        INNER JOIN User u ON b.user_ID = u.user_ID
        ORDER BY b.user_ID, b.report_ID, b.admin_ID
        """
        cursor.execute(query)

    blacklist = cursor.fetchall()

    return render_template(
        "blacklist.html",
        blacklist=blacklist,
        search_query=search_query,
        message=message,
    )


# TODO: Explain and fix the function
# I think this is deprecated
@app.route("/admin_report", methods=["GET", "POST"])
def admin_report():
    if request.method == "POST":
        report_ID = report_ID = get_next_ID_report()
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(report_date)
        report_description = request.form["report_description"]
        product_ID = request.form["product_ID"]
        reported_user_ID = request.form[
            "reported_user_ID"
        ]  # TODO this field also should be autofilled like report_ID and report_date
        purchase_ID = request.form["purchase_ID"]
        return_ID = request.form["return_ID"]
        report_status = request.form["report_status"]
        user_ID = request.form["user_ID"]

        # Insert the new report into the database
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO Report (report_ID, report_date, report_description, product_ID, reported_user_ID, purchase_ID, return_ID, report_status, user_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                report_ID,
                report_date,
                report_description,
                product_ID,
                reported_user_ID,
                purchase_ID,
                return_ID,
                report_status,
                user_ID,
            ),
        )
        mysql.connection.commit()
        cursor.close()

        flash("Report created successfully!", "success")
        return redirect(url_for("admin_user_report"))

    # Fetch reports for GET request
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Report ORDER BY report_date")
    reports = cursor.fetchall()
    return render_template("admin_user_report.html", reports=reports)


# TODO: Explain and fix the function
def get_next_ID_report():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Report ORDER BY CONVERT(report_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return "1"  # Start from 1 if no records exist
    max_id = max_id["report_ID"]
    return str(int(max_id) + 1)


# Main function to run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
