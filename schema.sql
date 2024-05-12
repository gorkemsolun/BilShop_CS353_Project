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
        state varchar(100) default null,
        zip decimal(10, 0) default null,
        building varchar(10) default null,
        street varchar(50) default null,
        no varchar(20) default null,
        address_description varchar(50) default null,
        primary key (user_ID),
        unique (email)
    );

create table
    Customer (
        user_ID varchar(20),
        balance numeric(20, 2),
        description varchar(50) default null,
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
        description varchar(50) default null,
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
        description varchar(50),
        status varchar(20),
        proportions varchar(20),
        mass numeric(10, 2),
        cover_picture varchar(50),
        date timestamp not null,
        color varchar(20),
        category varchar(20),
        primary key (product_ID)
    );

create table
    Product_Picture (
        product_ID varchar(20) not null,
        picture varchar(50),
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
        status varchar(20),
        total_price numeric(20, 2) not null,
        date timestamp not null,
        user_ID varchar(20) not null,
        primary key (purchase_ID),
        foreign key (user_ID) references Customer (user_ID) on delete cascade on update cascade
    );

create table
    Return_Request_Information (
        return_ID varchar(20) not null,
        date timestamp not null,
        reason varchar(20) not null,
        status varchar(20),
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
        date timestamp not null,
        description varchar(50) not null,
        product_ID varchar(20),
        reported_user_ID varchar(20) not null,
        purchase_ID varchar(20),
        return_ID varchar(20),
        status varchar(20) not null,
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
        description varchar(50),
        primary key (user_ID, report_ID, admin_ID),
        foreign key (user_ID) references User (user_ID) on delete cascade on update cascade,
        foreign key (admin_ID) references Admin (user_ID) on delete cascade on update cascade,
        foreign key (report_ID) references Report (report_ID) on delete cascade on update cascade
    );

insert into
    User (user_ID, name, email, password)
values
    ('0', 'admin', 'admin', 'admin');

insert into
    Admin (user_ID)
values
    ('0');

insert into
    User (user_ID, name, email, password)
values
    ('10', 'MCK', 'MCK', 'admin');

insert into
    Business (user_ID, balance)
values
    ('10', 4000);

insert into
    Product (product_ID, title, price, status, category)
values
    ('1', 'Murat1', 400, 'not_sold', 'Jewelry'),
    ('2', 'Murat2', 500, 'not_sold', 'Sculpture'),
    ('3', 'Murat3', 600, 'not_sold', 'Furniture'),
    ('4', 'Murat4', 100, 'not_sold', 'Accessories'),
    ('5', 'Murat5', 300, 'not_sold', 'Painting');

insert into
    Owns (user_ID, product_ID, amount)
values
    ('10', '1', 5),
    ('10', '2', 5),
    ('10', '3', 5),
    ('10', '4', 5),
    ('10', '5', 5);