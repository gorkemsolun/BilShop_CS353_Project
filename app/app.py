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

app = Flask(__name__, static_folder="static")

app.secret_key = "abcdefgh"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "cs353projectDB"

mysql = MySQL(app)


# Adding people with manual insertions can result in an error,
# It needs to be checked whether entry has been placed in sql.
def get_next_id():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM User ORDER BY CONVERT(user_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return str(1)  # Start from 1 if no records exist
    max_id = max_id["user_ID"]
    return str(int(max_id) + 1)


def get_next_id_product():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Product ORDER BY CONVERT(product_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return str(1)  # Start from 1 if no records exist
    max_id = max_id["product_ID"]
    return str(int(max_id) + 1)


def get_next_id_comment():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch the current maximum ID from the table
    cursor.execute(
        "SELECT * FROM Comment ORDER BY CONVERT(comment_ID, UNSIGNED INTEGER) DESC"
    )
    max_id = cursor.fetchone()
    if max_id is None:
        return str(1)  # Start from 1 if no records exist
    max_id = max_id["comment_ID"]
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


# Login page elements and given checks for login
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    # Checking whether the user logged in the system, redirect to the correct page using user roles
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
        # Getting the user with the provided name
        cursor.execute(
            "SELECT * FROM User WHERE name = % s AND password = % s",
            (
                username,
                password,
            ),
        )
        user_w_name = cursor.fetchone()
        # Getting the user with the provided name
        cursor.execute(
            "SELECT * FROM User WHERE email = % s AND password = % s",
            (
                username,
                password,
            ),
        )
        user_w_email = cursor.fetchone()
        # Assigning user to the default choice of providing name
        user = user_w_name
        # If name is empty assign it to user with provided email, noting that user can still be empty
        if user_w_name is None:
            user = user_w_email
        # Checking whether user is empty
        if user:
            # Check whether the user is blacklisted
            cursor.execute(
                "SELECT * FROM Blacklists WHERE user_ID = % s", (user["user_ID"],)
            )
            isBlacklisted = cursor.fetchone()
            if isBlacklisted:
                message = "Sorry, you are blacklisted."
            else:
                # Check whether the user_ID exists in the Customer table, noting that user_ID are same in business and user
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "SELECT * FROM Customer WHERE user_ID = % s", (user["user_ID"],)
                )
                customer = cursor.fetchone()
                if customer:
                    # user_ID are same in customer and user
                    session["role"] = "customer"
                    session["loggedin"] = True
                    session["user_ID"] = user["user_ID"]
                    session["username"] = user["name"]
                    return redirect(url_for("customer_main_page"))
                else:
                    # Check whether the user_ID exists in the Business table, noting that user_ID are same in business and user
                    cursor.execute(
                        "SELECT * FROM Business WHERE user_ID = % s", (user["user_ID"],)
                    )
                    business = cursor.fetchone()
                    # If business exists assign session information to local storage
                    if business:
                        session["role"] = "business"
                        session["loggedin"] = True
                        session["user_ID"] = user["user_ID"]
                        session["username"] = user["name"]
                        return redirect(url_for("business_main_page"))
                    # Assign admin session information to local storage
                    else:
                        session["role"] = "admin"
                        session["loggedin"] = True
                        session["user_ID"] = user["user_ID"]
                        session["username"] = user["name"]
                        return redirect(url_for("admin_main_page"))
        # user not found
        else:
            message = "Please enter correct email / username and password !"
    return render_template("login.html", message=message)


# Customer and Business registers through this
# No admin registration
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check whether the given field, username, exists in the db
        cursor.execute("SELECT * FROM User WHERE name = % s", (username,))
        account = cursor.fetchone()
        # Check whether the given field, email, exists in the db
        cursor.execute("SELECT * FROM User WHERE email = % s", (email,))
        account_email = cursor.fetchone()
        if account:
            message = "Username already exists."
        elif account_email:
            message = "Email address is already registered."
        elif not username or not password or not email:
            message = "Please fill out the form!"
        else:
            # The chosen role in HTML is requested by request.form.get('role') function
            role = request.form.get("role")
            # Get a new id which is unique
            new_id = get_next_id()
            # Insert the user with a new ID, given password, name and email
            cursor.execute(
                "INSERT INTO User (password, name, email, user_ID) VALUES (% s, % s, %s, %s)",
                (
                    password,
                    username,
                    email,
                    new_id,
                ),
            )
            mysql.connection.commit()
            # For the chosen role insert to balance default value 0 and user_ID Customer table
            if role == "customer":
                cursor.execute(
                    "INSERT INTO Customer (balance, user_ID) VALUES (% s, % s)",
                    (
                        0,
                        new_id,
                    ),
                )
                mysql.connection.commit()
            # For the chosen role insert the balance default value 0 and user_ID to Business table
            elif role == "business":
                cursor.execute(
                    "INSERT INTO Business (balance, user_ID) VALUES (% s, % s)",
                    (
                        0,
                        new_id,
                    ),
                )
                mysql.connection.commit()
            mysql.connection.commit()
            message = "User successfully created!"
    elif request.method == "POST":
        message = "Please fill all the fields!"
    return render_template("register.html", message=message)


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
    page = request.args.get("page", default=1, type=int)
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
            productID = get_next_id_product()
            status = "not_sold"

            query = "INSERT INTO Product (product_ID, title, price, category, product_status"
            values = [productID, title, price, category, status]

            optional_fields = [
                "product_description",
                "coverPicture",
                "proportions",
                "mass",
                "color",
                "date",
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

                    # If the field is not coverPicture, add it to the query as a string
                    if field != "coverPicture":
                        values.append(request.form[field])

                    # If the field is coverPicture, add it to the query as binary data
                    else:
                        cover_picture = request.files["coverPicture"]
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
                    (session["user_ID"], productID, int(amount)),
                )
                cursor.execute(
                    "INSERT INTO Product_Picture(product_ID, picture) VALUES (%s, %s)",
                    (productID, picture_binary_data),
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


# TODO main page admin reports etc
# TODO write description of this function/page
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


# TODO notifications page
@app.route("/notifications")
def notifications():
    return render_template("notifications.html")


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


# TODO Explain and fix the function
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


# TODO shopping-cart page
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
    cartlist = json.loads(list)
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
    customer = cursor.fetchone()
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
        cursor.execute(
            "UPDATE User SET name = %s, email = %s, password = %s, phone_number = %s, country = %s, city = %s, state_code = %s, zip_code = %s, building = %s, street = %s, address_description = %s WHERE user_ID = %s",
            (
                name,
                email,
                password,
                phone_number,
                country,
                city,
                state_code,
                zip_code,
                building,
                street,
                address_description,
                session["user_ID"],
            ),
        )
        mysql.connection.commit()
        return redirect(url_for("customer_profile"))
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

        return redirect(url_for("login"))
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
        cursor.execute(
            "UPDATE User SET name = %s, email = %s, password = %s, phone_number = %s, country = %s, city = %s, state_code = %s, zip_code = %s, building = %s, street = %s, address_description = %s WHERE user_ID = %s",
            (
                name,
                email,
                password,
                phone_number,
                country,
                city,
                state_code,
                zip_code,
                building,
                street,
                address_description,
                session["user_ID"],
            ),
        )
        mysql.connection.commit()
        return redirect(url_for("business_profile"))
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
        
        return redirect(url_for("login"))

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
            get_next_id_comment()
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


# TODO admin product page
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
        "test_tables.html",
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
        if action == "ban":
            reported_user_ID = request.form.get("reported_user_ID")
            # TODO : ADJUST QUERY
            query = "INSERT INTO Blacklist (user_ID) VALUES (%s)"
            cursor.execute(query, (reported_user_ID,))
            mysql.connection.commit()
        elif action == "dismiss":
            report_ID = request.form.get("report_ID")
            # TODO : ADJUST QUERY
            query = "UPDATE Reports SET status = 'dismissed' WHERE report_ID = %s"
            cursor.execute(query, (report_ID,))
            mysql.connection.commit()

    cursor.execute("SELECT * FROM Report ORDER BY report_date")
    reports = cursor.fetchall()

    return render_template("admin_user_report.html", reports=reports)


# TODO: Explain and fix the function
@app.route("/admin_system_report", methods=["GET", "POST"])
def admin_system_report():
    return render_template("admin_system_report.html")


# TODO: Explain and fix the function
@app.route("/admin_blacklist", methods=["GET", "POST"])
def admin_blacklist():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST" and "user_id" in request.form:
        user_id = request.form["user_id"]
        # Add code here to remove the user with the specified user_id from the blacklist
        # For demonstration purposes, let's assume we are just printing the user_id to console

        # TODO : WRITE REMOVE BLACKLIST AND REPORT QUERY

        # Redirect back to the same page after processing the removal
        return redirect(url_for("admin_blacklist"))

    search_query = request.args.get("search_query", "")

    if search_query:
        # Perform a join between Blacklists and User tables with search condition
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
        "blacklist.html", blacklist=blacklist, search_query=search_query
    )


# TODO: Explain and fix the function
@app.route("/admin_report", methods=["GET", "POST"])
def admin_report():
    if request.method == "POST":
        report_ID = report_ID = get_next_id_report()
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
def get_next_id_report():
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


# Main function to run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
