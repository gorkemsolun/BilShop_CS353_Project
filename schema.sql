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
	userID varchar(20) not null,
	productID varchar(20) not null,
	amount numeric(20, 0) not null,
	primary key(userID, productID),
	foreign key (productID) references Product(productID) on delete cascade on update cascade,
	foreign key (userID) references Customer(userID) on delete cascade on update cascade
);

insert into User(userID, name, email, password) values (0, 'admin', 'admin', 'admin');
insert into Admin(userID) values ( 0 );



