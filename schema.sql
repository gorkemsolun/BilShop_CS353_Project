CREATE TABLE
    User (
        user_ID varchar(20) not null,
        name varchar(50) not null,
        email varchar(50) not null,
        password varchar(50) not null,
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

create table
    Customer (
        user_ID varchar(20),
        balance numeric(20, 2),
        customer_description varchar(50) default null,
        primary key (user_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

create table
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

create table
    Admin (
        user_ID varchar(20),
        primary key (user_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade
    );

create table
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

create table
    Product_Picture (
        product_ID varchar(20) not null,
        picture BLOB,
        primary key (product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade
    );

create table
    Owns (
        user_ID varchar(20),
        product_ID varchar(20),
        amount numeric(20, 0) not null,
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Business (user_ID) on delete cascade on update cascade
    );

create table
    Wishes (
        user_ID varchar(20),
        product_ID varchar(20),
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

create table
    Puts_On_Cart (
        user_ID varchar(20) not null,
        product_ID varchar(20) not null,
        amount numeric(20, 0) not null,
        primary key (user_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

create table
    Purchase_Information (
        purchase_ID varchar(20) not null,
        purchase_status varchar(20),
        total_price numeric(20, 2) not null,
        purchase_date timestamp not null,
        user_ID varchar(20) not null,
        primary key (purchase_ID),
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

create table
    Return_Request_Information (
        return_ID varchar(20) not null,
        return_request_date timestamp not null,
        reason varchar(20) not null,
        return_request_status varchar(20),
        purchase_ID varchar(20) not null,
        primary key (return_ID),
        foreign key (purchase_ID) references Purchase_Information (purchase_ID) on delete cascade on update cascade
    );

create table
    Has_Return_Request (
        return_ID varchar(20) not null,
        product_ID varchar(20) not null,
        amount numeric(20) not null,
        primary key (return_ID, product_ID),
        foreign key (product_ID) references Product (product_ID) on delete cascade on update cascade,
        foreign key (return_ID) references Return_Request_Information (return_ID) on delete cascade on update cascade
    );

create table
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

create table
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

-- Inserting data into User table
INSERT INTO User (user_ID, name, email, password, picture, phone_number, country, city, state_code, zip_code, building, street, address_description)
VALUES 
('U001', 'John Doe', 'john.doe@example.com', 'password123', NULL, '123-456-7890', 'USA', 'New York', 'NY', 10001, '10', 'Broadway', 'Near Central Park'),
('U002', 'Jane Smith', 'jane.smith@example.com', 'password123', NULL, '123-456-7891', 'USA', 'Los Angeles', 'CA', 90001, '20', 'Hollywood Blvd', 'Close to Dolby Theatre'),
('U003', 'Alice Johnson', 'alice.johnson@example.com', 'password123', NULL, '123-456-7892', 'USA', 'Chicago', 'IL', 60601, '30', 'Lake Shore Dr', 'Near Millennium Park'),
('U004', 'Bob Brown', 'bob.brown@example.com', 'password123', NULL, '123-456-7893', 'USA', 'Houston', 'TX', 77001, '40', 'Main St', 'Near Discovery Green'),
('U005', 'Charlie Davis', 'charlie.davis@example.com', 'password123', NULL, '123-456-7894', 'USA', 'Phoenix', 'AZ', 85001, '50', 'Van Buren St', 'Close to Roosevelt Row'),
('U006', 'Diana Evans', 'diana.evans@example.com', 'password123', NULL, '123-456-7895', 'USA', 'Philadelphia', 'PA', 19101, '60', 'Market St', 'Near Liberty Bell'),
('U007', 'Ethan Garcia', 'ethan.garcia@example.com', 'password123', NULL, '123-456-7896', 'USA', 'San Antonio', 'TX', 78201, '70', 'Commerce St', 'Near The Alamo'),
('U008', 'Fiona Harris', 'fiona.harris@example.com', 'password123', NULL, '123-456-7897', 'USA', 'San Diego', 'CA', 92101, '80', 'Harbor Dr', 'Close to Gaslamp Quarter'),
('U009', 'George Martinez', 'george.martinez@example.com', 'password123', NULL, '123-456-7898', 'USA', 'Dallas', 'TX', 75201, '90', 'Elm St', 'Near Dealey Plaza'),
('U010', 'Hannah Lopez', 'hannah.lopez@example.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center'),
('U011', 'Placeholder1', 'temp1@gmail.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center'),
('U012', 'Placeholder2', 'temp1@gmai2.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center'),
('U013', 'Placeholder3', 'temp1@gmai3.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center'),
('U014', 'Placeholder4', 'temp1@gmai4.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center'),
('U015', 'Placeholder5', 'temp1@gmai5.com', 'password123', NULL, '123-456-7899', 'USA', 'San Jose', 'CA', 95101, '100', 'Santa Clara St', 'Near SAP Center');

-- Inserting data into Customer table
INSERT INTO Customer (user_ID, balance, customer_description)
VALUES 
('U001', 150.00, 'Frequent buyer'),
('U002', 200.00, 'Loyal customer'),
('U003', 300.00, 'New customer'),
('U004', 500.00, 'VIP customer'),
('U005', 50.00, 'Occasional buyer'),
('U006', 100.00, 'Regular customer'),
('U007', 250.00, 'Frequent buyer'),
('U008', 400.00, 'High-value customer'),
('U009', 150.00, 'New customer'),
('U010', 75.00, 'Occasional buyer');

-- Inserting data into Business table
INSERT INTO Business (user_ID, rating, establishment_year, balance, logo, business_description, company_name)
VALUES 
('U011', 4.9, '2005-09-30', 20000.00, NULL, 'Gourmet coffee shop', 'Bean Palace'),
('U012', 4.7, '2012-03-22', 12000.00, NULL, 'Handmade jewelry store', 'Gem Craft'),
('U013', 4.6, '2018-11-11', 18000.00, NULL, 'Home decor shop', 'Cozy Homes'),
('U014', 4.5, '2016-07-07', 16000.00, NULL, 'Organic grocery store', 'Green Mart'),
('U015', 4.3, '2020-01-01', 22000.00, NULL, 'Pet supplies store', 'Pet Haven');

-- Inserting data into Admin table
INSERT INTO Admin (user_ID)
VALUES 
('U005'),
('U006'),
('U007'),
('U008');

-- Inserting data into Product table
INSERT INTO Product (product_ID, title, price, product_description, product_status, proportions, mass, cover_picture, product_date, color, category)
VALUES 
('P001', 'Laptop', 999.99, 'High performance laptop', 'Available', '14x9x0.7', 2.5, 'laptop.jpg', '2024-05-10 10:00:00', 'Silver', 'Electronics'),
('P002', 'T-Shirt', 19.99, '100% cotton t-shirt', 'Available', 'M', 0.2, 'tshirt.jpg', '2024-05-11 11:00:00', 'Blue', 'Clothing'),
('P003', 'Smartphone', 599.99, 'Latest model smartphone', 'Available', '6x3x0.3', 0.3, 'smartphone.jpg', '2024-05-14 14:00:00', 'Black', 'Electronics'),
('P004', 'Jeans', 49.99, 'Comfort fit jeans', 'Available', 'L', 0.5, 'jeans.jpg', '2024-05-15 15:00:00', 'Blue', 'Clothing'),
('P005', 'Headphones', 199.99, 'Noise-cancelling headphones', 'Available', '7x7x3', 0.6, 'headphones.jpg', '2024-05-16 16:00:00', 'Black', 'Electronics'),
('P006', 'Sneakers', 89.99, 'Running sneakers', 'Available', '10', 0.8, 'sneakers.jpg', '2024-05-17 17:00:00', 'White', 'Footwear'),
('P007', 'Watch', 299.99, 'Smartwatch with multiple features', 'Available', 'Adjustable', 0.2, 'watch.jpg', '2024-05-18 18:00:00', 'Silver', 'Accessories');

-- Inserting data into Product_Picture table
INSERT INTO Product_Picture (product_ID, picture)
VALUES 
('P001', LOAD_FILE('path/to/laptop.jpg')),
('P002', LOAD_FILE('path/to/tshirt.jpg')),
('P003', LOAD_FILE('path/to/smartphone.jpg')),
('P004', LOAD_FILE('path/to/jeans.jpg')),
('P005', LOAD_FILE('path/to/headphones.jpg')),
('P006', LOAD_FILE('path/to/sneakers.jpg')),
('P007', LOAD_FILE('path/to/watch.jpg'));

-- Inserting data into Owns table
INSERT INTO Owns (user_ID, product_ID, amount)
VALUES 
('U011', 'P003', 30),
('U012', 'P004', 60),
('U013', 'P005', 40),
('U014', 'P006', 80),
('U015', 'P007', 20);

-- Inserting data into Wishes table
INSERT INTO Wishes (user_ID, product_ID)
VALUES 
('U001', 'P001'),
('U002', 'P002'),
('U003', 'P003'),
('U004', 'P004'),
('U005', 'P005'),
('U006', 'P006'),
('U007', 'P007');

-- Inserting data into Puts_On_Cart table
INSERT INTO Puts_On_Cart (user_ID, product_ID, amount)
VALUES 
('U001', 'P001', 1),
('U002', 'P002', 2),
('U003', 'P003', 1),
('U004', 'P004', 2),
('U005', 'P005', 1),
('U006', 'P006', 2),
('U007', 'P007', 1);

-- Inserting data into Purchase_Information table
INSERT INTO Purchase_Information (purchase_ID, purchase_status, total_price, purchase_date, user_ID)
VALUES 
('PUR001', 'Completed', 999.99, '2024-05-12 12:00:00', 'U001'),
('PUR002', 'Completed', 39.98, '2024-05-13 13:00:00', 'U002'),
('PUR003', 'Completed', 599.99, '2024-05-18 18:00:00', 'U003'),
('PUR004', 'Completed', 99.98, '2024-05-19 19:00:00', 'U004'),
('PUR005', 'Completed', 199.99, '2024-05-20 20:00:00', 'U005'),
('PUR006', 'Completed', 179.98, '2024-05-21 21:00:00', 'U006'),
('PUR007', 'Completed', 299.99, '2024-05-22 22:00:00', 'U007');

-- Inserting data into Return_Request_Information table
INSERT INTO Return_Request_Information (return_ID, return_request_date, reason, return_request_status, purchase_ID)
VALUES 
('RET001', '2024-05-14 14:00:00', 'Defective product', 'Pending', 'PUR001'),
('RET002', '2024-05-15 15:00:00', 'Wrong size', 'Approved', 'PUR002'),
('RET003', '2024-05-23 23:00:00', 'Not as described', 'Pending', 'PUR003'),
('RET004', '2024-05-24 22:00:00', 'Quality issues', 'Pending', 'PUR004'),
('RET005', '2024-05-25 21:00:00', 'Defective product', 'Pending', 'PUR005');

-- Inserting data into Has_Return_Request table
INSERT INTO Has_Return_Request (return_ID, product_ID, amount)
VALUES 
('RET001', 'P001', 1),
('RET002', 'P002', 1),
('RET003', 'P003', 1),
('RET004', 'P004', 2),
('RET005', 'P005', 1);

-- Inserting data into Report table
INSERT INTO Report (report_ID, report_date, report_description, product_ID, reported_user_ID, purchase_ID, return_ID, report_status, user_ID)
VALUES 
('REP001', '2024-05-16 16:00:00', 'Product not as described', 'P001', 'U003', 'PUR001', 'RET001', 'Under Review', 'U001'),
('REP002', '2024-05-17 17:00:00', 'Late delivery', 'P002', 'U004', 'PUR002', 'RET002', 'Resolved', 'U002'),
('REP003', '2024-05-26 21:00:00', 'Late delivery', 'P003', 'U011', 'PUR003', 'RET003', 'Under Review', 'U003'),
('REP004', '2024-05-27 20:00:00', 'Damaged product', 'P004', 'U012', 'PUR004', 'RET004', 'Resolved', 'U004');

-- Inserting data into Blacklists table
INSERT INTO Blacklists (user_ID, report_ID, admin_ID, reason_description)
VALUES 
('U003', 'REP001', 'U005', 'Multiple complaints about product quality'),
('U004', 'REP002', 'U006', 'Repeated issues with delivery'),
('U011', 'REP003', 'U007', 'Multiple complaints about delivery issues'),
('U012', 'REP004', 'U008', 'Repeated complaints about product quality');


