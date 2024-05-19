CREATE TABLE
    User (
        user_ID varchar(20) not null,
        name varchar(50) not null,
        email varchar(50) not null,
        password varchar(500) not null,
        picture varchar(100) default null,
        phone_number varchar(100) default null,
        country varchar(100) default null,
        city varchar(100) default null,
        state_code varchar(100) default null,
        zip_code varchar(20) default null,
        building varchar(10) default null,
        street varchar(50) default null,
        address_description varchar(50) default null,
        primary key (user_ID),
        unique (email)
    );

CREATE TABLE
    Customer (
        user_ID varchar(20),
        balance numeric(20, 2),
        customer_description varchar(50) default null,
        primary key (user_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Business (
        user_ID varchar(20),
        rating numeric(10, 0) default null,
        establishment_year date default null,
        balance numeric(20, 2),
        logo varchar(50) default null,
        business_description varchar(50) default null,
        company_name varchar(20) default null,
        primary key (user_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Admin (
        user_ID varchar(20),
        primary key (user_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Product (
        product_ID varchar(20) not null,
        title varchar(20) not null,
        price numeric(20, 2) not null,
        product_description varchar(50),
        product_status varchar(20),
        proportions varchar(20),
        mass numeric(10, 2),
        cover_picture varchar(50),
        product_date timestamp not null,
        color varchar(20),
        category varchar(20),
        primary key (product_ID)
    );

CREATE TABLE
    Product_Picture (
        product_ID varchar(20) not null,
        picture BLOB,
        primary key (product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Owns (
        user_ID varchar(20),
        product_ID varchar(20),
        amount numeric(20, 0) not null,
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Business (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Wishes (
        user_ID varchar(20),
        product_ID varchar(20),
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Puts_On_Cart (
        user_ID varchar(20) not null,
        product_ID varchar(20) not null,
        amount numeric(20, 0) not null,
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Purchase_Information (
        purchase_ID varchar(20) not null,
        purchase_status varchar(20),
        total_price numeric(20, 2) not null,
        purchase_date timestamp not null,
        user_ID varchar(20) not null,
        product_ID varchar(20) not null,
        amount numeric(20, 0) not null,
        primary key (purchase_ID),
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade,
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Return_Request_Information (
        return_ID varchar(20) not null,
        return_request_date timestamp not null,
        reason varchar(20) not null,
        return_request_status varchar(20),
        purchase_ID varchar(20) not null,
        primary key (return_ID),
        foreign key (purchase_ID) references Purchase_Information (purchase_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Has_Return_Request (
        return_ID varchar(20) not null,
        product_ID varchar(20) not null,
        amount numeric(20) not null,
        primary key (return_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (return_ID) references Return_Request_Information (return_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Report (
        report_ID varchar(20) not null,
        report_date timestamp not null,
        report_description varchar(50) not null,
        product_ID varchar(20),
        reported_user_ID varchar(20) not null,
        purchase_ID varchar(20),
        return_ID varchar(20),
        report_status varchar(20) not null,
        user_ID varchar(20) not null,
        primary key (report_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (reported_user_ID) references User (user_ID) on delete cascade on update cascade,
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade,
        foreign key (return_ID) references Return_Request_Information (return_ID) on delete cascade on update cascade,
        foreign key (purchase_ID) references Purchase_Information (purchase_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Blacklists (
        user_ID varchar(20),
        report_ID varchar(20),
        admin_ID varchar(20),
        reason_description varchar(50),
        primary key (user_ID, report_ID, admin_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade,
        foreign key (admin_ID) references Admin (user_ID) on delete cascade on update cascade,
        foreign key (report_ID) references Report (report_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Comment (
        comment_ID varchar(20) not null,
        user_ID varchar(20) not null,
        product_ID varchar(20) not null,
        text varchar(50) not null,
        primary key (comment_ID, user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

CREATE TABLE
    Notification (
        notification_ID varchar(20) not null,
        notification_image varchar(50) default null,
        notification_title varchar(50) not null,
        user_ID varchar(20) not null,
        notification_text varchar(100) not null,
        notification_date timestamp not null,
        primary key (notification_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

-- Inserting data into User table
INSERT INTO
    User (
        user_ID,
        name,
        email,
        password,
        picture,
        phone_number,
        country,
        city,
        state_code,
        zip_code,
        building,
        street,
        address_description
    )
VALUES
    (
        '0',
        'admin',
        'admin',
        'admin',
        NULL,
        '123-456-7890',
        'USA',
        'New York',
        'NY',
        10001,
        '10',
        'Broadway',
        'Near Central Park'
    ),
    (
        '1',
        'John Doe',
        'john.doe@example.com',
        'password123',
        NULL,
        '123-456-7890',
        'USA',
        'New York',
        'NY',
        10001,
        '10',
        'Broadway',
        'Near Central Park'
    ),
    (
        '2',
        'Jane Smith',
        'jane.smith@example.com',
        'password123',
        NULL,
        '123-456-7891',
        'USA',
        'Los Angeles',
        'CA',
        90001,
        '20',
        'Hollywood Blvd',
        'Close to Dolby Theatre'
    ),
    (
        '3',
        'Alice Johnson',
        'alice.johnson@example.com',
        'password123',
        NULL,
        '123-456-7892',
        'USA',
        'Chicago',
        'IL',
        60601,
        '30',
        'Lake Shore Dr',
        'Near Millennium Park'
    ),
    (
        '4',
        'Bob Brown',
        'bob.brown@example.com',
        'password123',
        NULL,
        '123-456-7893',
        'USA',
        'Houston',
        'TX',
        77001,
        '40',
        'Main St',
        'Near Discovery Green'
    ),
    (
        '5',
        'Charlie Davis',
        'charlie.davis@example.com',
        'password123',
        NULL,
        '123-456-7894',
        'USA',
        'Phoenix',
        'AZ',
        85001,
        '50',
        'Van Buren St',
        'Close to Roosevelt Row'
    ),
    (
        '6',
        'Diana Evans',
        'diana.evans@example.com',
        'password123',
        NULL,
        '123-456-7895',
        'USA',
        'Philadelphia',
        'PA',
        19101,
        '60',
        'Market St',
        'Near Liberty Bell'
    ),
    (
        '7',
        'Ethan Garcia',
        'ethan.garcia@example.com',
        'password123',
        NULL,
        '123-456-7896',
        'USA',
        'San Antonio',
        'TX',
        78201,
        '70',
        'Commerce St',
        'Near The Alamo'
    ),
    (
        '8',
        'Fiona Harris',
        'fiona.harris@example.com',
        'password123',
        NULL,
        '123-456-7897',
        'USA',
        'San Diego',
        'CA',
        92101,
        '80',
        'Harbor Dr',
        'Close to Gaslamp Quarter'
    ),
    (
        '9',
        'George Martinez',
        'george.martinez@example.com',
        'password123',
        NULL,
        '123-456-7898',
        'USA',
        'Dallas',
        'TX',
        75201,
        '90',
        'Elm St',
        'Near Dealey Plaza'
    ),
    (
        '10',
        'Hannah Lopez',
        'hannah.lopez@example.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    ),
    (
        '11',
        'Placeholder1',
        'temp1@gmail.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    ),
    (
        '12',
        'Placeholder2',
        'temp1@gmai2.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    ),
    (
        '13',
        'Placeholder3',
        'temp1@gmai3.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    ),
    (
        '14',
        'Placeholder4',
        'temp1@gmai4.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    ),
    (
        '15',
        'Placeholder5',
        'temp1@gmai5.com',
        'password123',
        NULL,
        '123-456-7899',
        'USA',
        'San Jose',
        'CA',
        95101,
        '100',
        'Santa Clara St',
        'Near SAP Center'
    );

-- Inserting data into Customer table
INSERT INTO
    Customer (user_ID, balance, customer_description)
VALUES
    ('1', 150.00, 'Frequent buyer'),
    ('2', 200.00, 'Loyal customer'),
    ('3', 300.00, 'New customer'),
    ('4', 500.00, 'VIP customer'),
    ('5', 50.00, 'Occasional buyer'),
    ('6', 100.00, 'Regular customer'),
    ('7', 250.00, 'Frequent buyer'),
    ('8', 400.00, 'High-value customer'),
    ('9', 150.00, 'New customer'),
    ('10', 75.00, 'Occasional buyer');

-- Inserting data into Business table
INSERT INTO
    Business (
        user_ID,
        rating,
        establishment_year,
        balance,
        logo,
        business_description,
        company_name
    )
VALUES
    (
        '11',
        4.9,
        '2005-09-30',
        20000.00,
        NULL,
        'Gourmet coffee shop',
        'Bean Palace'
    ),
    (
        '12',
        4.7,
        '2012-03-22',
        12000.00,
        NULL,
        'Handmade jewelry store',
        'Gem Craft'
    ),
    (
        '13',
        4.6,
        '2018-11-11',
        18000.00,
        NULL,
        'Home decor shop',
        'Cozy Homes'
    ),
    (
        '14',
        4.5,
        '2016-07-07',
        16000.00,
        NULL,
        'Organic grocery store',
        'Green Mart'
    ),
    (
        '15',
        4.3,
        '2020-01-01',
        22000.00,
        NULL,
        'Pet supplies store',
        'Pet Haven'
    );

-- Inserting data into Admin table
INSERT INTO
    Admin (user_ID)
VALUES
    ('0');

-- Inserting data into Product table
INSERT INTO
    Product (
        product_ID,
        title,
        price,
        product_description,
        product_status,
        proportions,
        mass,
        cover_picture,
        product_date,
        color,
        category
    )
VALUES
    (
        '1',
        'Laptop',
        999.99,
        'High performance laptop',
        'Available',
        '14x9x0.7',
        2.5,
        'laptop.jpg',
        '2024-05-10 10:00:00',
        'Silver',
        'Electronics'
    ),
    (
        '2',
        'T-Shirt',
        19.99,
        '100% cotton t-shirt',
        'Available',
        'M',
        0.2,
        'tshirt.jpg',
        '2024-05-11 11:00:00',
        'Blue',
        'Clothing'
    ),
    (
        '3',
        'Smartphone',
        599.99,
        'Latest model smartphone',
        'Available',
        '6x3x0.3',
        0.3,
        'smartphone.jpg',
        '2024-05-14 14:00:00',
        'Black',
        'Electronics'
    ),
    (
        '4',
        'Jeans',
        49.99,
        'Comfort fit jeans',
        'Available',
        'L',
        0.5,
        'jeans.jpg',
        '2024-05-15 15:00:00',
        'Blue',
        'Clothing'
    ),
    (
        '5',
        'Headphones',
        199.99,
        'Noise-cancelling headphones',
        'Available',
        '7x7x3',
        0.6,
        'headphones.jpg',
        '2024-05-16 16:00:00',
        'Black',
        'Electronics'
    ),
    (
        '6',
        'Sneakers',
        89.99,
        'Running sneakers',
        'Available',
        '10',
        0.8,
        'sneakers.jpg',
        '2024-05-17 17:00:00',
        'White',
        'Footwear'
    ),
    (
        '7',
        'Watch',
        299.99,
        'Smartwatch with multiple features',
        'Available',
        'Adjustable',
        0.2,
        'watch.jpg',
        '2024-05-18 18:00:00',
        'Silver',
        'Accessories'
    );

-- Inserting data into Owns table
INSERT INTO
    Owns (user_ID, product_ID, amount)
VALUES
    ('11', '3', 30),
    ('12', '4', 60),
    ('13', '5', 40),
    ('14', '6', 80),
    ('15', '7', 20);

-- Inserting data into Wishes table
INSERT INTO
    Wishes (user_ID, product_ID)
VALUES
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7');

-- Inserting data into Puts_On_Cart table
INSERT INTO
    Puts_On_Cart (user_ID, product_ID, amount)
VALUES
    ('1', '1', 1),
    ('2', '2', 2),
    ('3', '3', 1),
    ('4', '4', 2),
    ('5', '5', 1),
    ('6', '6', 2),
    ('7', '7', 1);

-- Inserting data into Purchase_Information table
INSERT INTO
    Purchase_Information (
        purchase_ID,
        purchase_status,
        total_price,
        purchase_date,
        user_ID,
        product_ID,
        amount
    )
VALUES
    (
        '1',
        'Completed',
        999.99,
        '2024-05-12 12:00:00',
        '1',
        '1',
        2
    ),
    (
        '2',
        'Completed',
        39.98,
        '2024-05-13 13:00:00',
        '2',
        '2',
        2
    ),
    (
        '3',
        'Completed',
        599.99,
        '2024-05-18 18:00:00',
        '3',
        '3',
        2
    ),
    (
        '4',
        'Completed',
        99.98,
        '2024-05-19 19:00:00',
        '4',
        '4',
        2
    ),
    (
        '5',
        'Completed',
        199.99,
        '2024-05-20 20:00:00',
        '5',
        '5',
        2
    ),
    (
        '6',
        'Completed',
        179.98,
        '2024-05-21 21:00:00',
        '6',
        '6',
        2
    ),
    (
        '7',
        'Completed',
        299.99,
        '2024-05-22 22:00:00',
        '7',
        '7',
        2
    );

-- Inserting data into Return_Request_Information table
INSERT INTO
    Return_Request_Information (
        return_ID,
        return_request_date,
        reason,
        return_request_status,
        purchase_ID
    )
VALUES
    (
        '1',
        '2024-05-14 14:00:00',
        'Defective product',
        'Pending',
        '1'
    ),
    (
        '2',
        '2024-05-15 15:00:00',
        'Wrong size',
        'Approved',
        '2'
    ),
    (
        '3',
        '2024-05-23 23:00:00',
        'Not as described',
        'Pending',
        '3'
    ),
    (
        '4',
        '2024-05-24 22:00:00',
        'Quality issues',
        'Pending',
        '4'
    ),
    (
        '5',
        '2024-05-25 21:00:00',
        'Defective product',
        'Pending',
        '5'
    );

-- Inserting data into Has_Return_Request table
INSERT INTO
    Has_Return_Request (return_ID, product_ID, amount)
VALUES
    ('1', '1', 1),
    ('2', '2', 1),
    ('3', '3', 1),
    ('4', '4', 2),
    ('5', '5', 1);

-- Inserting data into Report table
INSERT INTO
    Report (
        report_ID,
        report_date,
        report_description,
        product_ID,
        reported_user_ID,
        purchase_ID,
        return_ID,
        report_status,
        user_ID
    )
VALUES
    (
        '1',
        '2024-05-16 16:00:00',
        'Product not as described',
        '1',
        '3',
        '1',
        '1',
        'Under Review',
        '1'
    ),
    (
        '2',
        '2024-05-17 17:00:00',
        'Late delivery',
        '2',
        '4',
        '2',
        '2',
        'Resolved',
        '2'
    ),
    (
        '3',
        '2024-05-26 21:00:00',
        'Late delivery',
        '3',
        '11',
        '3',
        '3',
        'Under Review',
        '3'
    ),
    (
        '4',
        '2024-05-27 20:00:00',
        'Damaged product',
        '4',
        '12',
        '4',
        '4',
        'Resolved',
        '4'
    );

-- Inserting data into Blacklists table
INSERT INTO
    Blacklists (user_ID, report_ID, admin_ID, reason_description)
VALUES
    (
        '3',
        '1',
        '0',
        'Multiple complaints about product quality'
    ),
    ('4', '2', '0', 'Repeated issues with delivery'),
    (
        '11',
        '3',
        '0',
        'Multiple complaints about delivery issues'
    ),
    (
        '12',
        '4',
        '0',
        'Repeated complaints about product quality'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '1',
        'order_confirmation.png',
        'Order Confirmation',
        '1',
        'Your order #12345 has been confirmed.',
        '2024-05-10 10:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '2',
        'shipping.png',
        'Shipping Update',
        '1',
        'Your order #12345 has been shipped.',
        '2024-05-11 11:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '3',
        'delivery.png',
        'Delivery Update',
        '1',
        'Your order #12345 has been delivered.',
        '2024-05-12 12:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '4',
        'return_request.png',
        'Return Request',
        '1',
        'Your return request for order #12345 has been received.',
        '2024-05-14 14:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '5',
        'return_approved.png',
        'Return Approved',
        '1',
        'Your return request for order #12345 has been approved.',
        '2024-05-15 15:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '6',
        'refund_processed.png',
        'Refund Processed',
        '1',
        'Your refund for order #12345 has been processed.',
        '2024-05-16 16:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '7',
        'new_product.png',
        'New Product Available',
        '1',
        'Check out our new product: High Performance Laptop.',
        '2024-05-17 17:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '8',
        'promotion.png',
        'Special Promotion',
        '1',
        'Get 20% off on your next purchase with code SAVE20.',
        '2024-05-18 18:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '9',
        'balance_update.png',
        'Account Balance Updated',
        '1',
        'Your account balance has been updated to $150.00.',
        '2024-05-19 19:00:00'
    );

INSERT INTO
    Notification (
        notification_ID,
        notification_image,
        notification_title,
        user_ID,
        notification_text,
        notification_date
    )
VALUES
    (
        '10',
        'wishlist.png',
        'Wishlist Product Available',
        '1',
        'A product from your wishlist is now available: High Performance Laptop.',
        '2024-05-20 20:00:00'
    );