CREATE TABLE User
(
    userID              varchar(20)    not null,
    name                varchar(50)    not null,
    email               varchar(50)    not null,
    password            varchar(50)    not null,
    picture             varchar(100)   default null,
    phone_number        varchar(100)   default null,
    country             varchar(100)   default null,
    city                varchar(100)   default null,
    state               varchar(100)   default null,
    zip                 decimal(10, 0) default null,
    building            varchar(10)    default null,
    street              varchar(50)    default null,
    no                  varchar(20)    default null,
    addressDescription  varchar(50)    default null,
    primary key(userID),
    unique(email)
);

create table Customer
(
	userID varchar(20),
	balance numeric(20, 2),
	description varchar(50) default null,
    primary key(userID),
    foreign key (userID) references User(userID) on delete cascade on update cascade
);

create table Business
(
	userID varchar(20),
	rating numeric(10, 0)       default null,
	yearOfEstablishment date    default null,
	balance numeric(20, 2),
	logo varchar(50)            default null,
	description varchar(50)     default null,
	companyName varchar(20)     default null,
    primary key(userID),
    foreign key (userID) references User(userID) on delete cascade on update cascade
);

create table Admin
(
	userID varchar(20),
    primary key(userID),
    foreign key (userID) references User(userID) on delete cascade on update cascade
);


create table Product
(
    productID       varchar(20) not null,
    title           varchar(20) not null,
    price           numeric(20, 2) not null,
    description     varchar(50),
    status          varchar(20),
    proportions     varchar(20),
    mass            numeric(10,2),
    coverPicture    varchar(50),
    date            timestamp not null,
    color           varchar(20),
    category        varchar(20),
    primary key(productID)
);

create table ProductPicture
(
	productID varchar(20) not null,
    picture varchar(50),
    primary key(productID),
    foreign key (productID) references Product(productID) on delete cascade on update cascade
);

create table Owns
(
	userID varchar(20),
	productID varchar(20),
	amount numeric(20, 0) not null,
    primary key(userID, productID),
    foreign key (productID) references Product(productID) on delete cascade on update cascade,
    foreign key (userID) references Business(userID) on delete cascade on update cascade
);

create table Wishes
(
	userID varchar(20),
	productID varchar(20),
    primary key(userID, productID),
    foreign key (productID) references Product(productID) on delete cascade on update cascade,
    foreign key (userID) references Customer(userID) on delete cascade on update cascade
);

create table PutsOnCart
(
	userID varchar(20)      not null,
	productID varchar(20)   not null,
	amount numeric(20, 0)   not null,
	primary key(userID, productID),
	foreign key (productID) references Product(productID) on delete cascade on update cascade,
	foreign key (userID) references Customer(userID) on delete cascade on update cascade
);

create table PurchaseInformation
(
	purchaseID varchar(20)      not null,
	status varchar(20),
	totalPrice numeric(20,2)    not null,
	date timestamp              not null,
	userID varchar(20)          not null,
	primary key(purchaseID),
	foreign key (userID) references Customer(userID) on delete cascade on update cascade
);

create table ReturnRequestInformation
(
	returnID varchar(20)    not null,
	date timestamp          not null,
	reason varchar(20)      not null,
	status varchar(20),
	purchaseID varchar(20)  not null,
	primary key(returnID),
	foreign key (purchaseID) references PurchaseInformation(purchaseID) on delete cascade on update cascade
);

create table HasReturnRequest
(
    returnID varchar(20)    not null,
    productID varchar(20)   not null,
    amount numeric(20)      not null,
    primary key(returnID, productID),
    foreign key (productID) references Product(productID) on delete cascade on update cascade,
    foreign key (returnID) references ReturnRequestInformation(returnID) on delete cascade on update cascade
);


create table Report
(
	reportID varchar(20)        not null,
    date timestamp              not null,
    description varchar(50)     not null,
    productID varchar(20),
    reportedUserID varchar(20)  not null,
    purchaseID varchar(20),
    returnID varchar(20),
    status varchar(20)          not null,
    userID varchar(20)          not null,
    primary key(reportID),
    foreign key (productID) references Product(productID) on delete cascade on update cascade,
    foreign key (reportedUserID) references User(userID) on delete cascade on update cascade,
    foreign key (userID) references User(userID) on delete cascade on update cascade,
    foreign key (returnID) references ReturnRequestInformation(returnID) on delete cascade on update cascade,
    foreign key (purchaseID) references PurchaseInformation(purchaseID) on delete cascade on update cascade
);

create table Blacklists
(
	userID varchar(20),
	reportID varchar(20),
	adminID varchar(20),
	description varchar(50),
    primary key (userID, reportID, adminID),
    foreign key (userID) references User(userID) on delete cascade on update cascade,
    foreign key (adminID) references Admin(userID) on delete cascade on update cascade,
    foreign key (reportID) references Report(reportID) on delete cascade on update cascade
);

insert into User(userID, name, email, password) values ('0', 'admin', 'admin', 'admin');
insert into Admin(userID) values ( '0' );
insert into User(userID, name, email, password) values ('10', 'MCK', 'MCK', 'admin');
insert into Business(userID, balance) values ( '10', 4000 );
insert into Product(productID, title, price, status) values ('1', 'Murat1', 400, 'notSold'),
                                                            ('2', 'Murat2', 500, 'notSold'),
                                                            ('3', 'Murat3', 600, 'notSold');
insert into Owns(userID, productID, amount)  values ('10', '1', 5),
                                                    ('10', '2', 5),
                                                    ('10', '3', 5);



