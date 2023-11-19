create dao roommates;
use roommates;

create table flat(
flat_id int not null primary key auto_increment,
name varchar(64) not null 
);

create table room(
room_id int not null primary key auto_increment,
name varchar(64) not null,
flat_id int not null,
foreign key (flat_id) references flat(flat_id) on update cascade on delete cascade,
constraint unq_room_in_flat unique(name, flat_id)
);

create table user(
username varchar(64) not null primary key,
email_id varchar(255),
phone char(10),
password varchar(255) not null
);

create table flatmate (
username varchar(64) not null primary key,
flat_id int not null,
room_id int,
join_date date not null,
foreign key (username) references user(username) on update cascade on delete cascade,
foreign key (flat_id) references flat(flat_id) on update cascade on delete cascade,
foreign key (room_id) references room(room_id) on update cascade on delete set null
);

create table expense(
expense_id int not null primary key auto_increment,
name varchar(255) not null,
amount_paid float not null,
expense_date date not null,
paid_by varchar(64) not null,
foreign key (paid_by) references flatmate(username) on update cascade on delete cascade,
constraint unq_expense unique(name, expense_date, paid_by)
);

create table task(
task_id int not null primary key auto_increment,
task_name varchar(100) not null,
frequency enum('NO_REPEAT', 'DAILY', 'WEEKLY', 'MONTHLY') not null default 'WEEKLY',
assigned_to varchar(64) not null,
foreign key (assigned_to) references flatmate(username) on update cascade on delete cascade,
constraint unq_task unique(task_name, assigned_to)
);

create table rotation_sequence(
rotation_seq_id int not null primary key auto_increment,
seq_number int not null,
username varchar(64) not null,
task_id int not null,
foreign key (task_id) references task(task_id) on update cascade on delete cascade,
foreign key (username) references flatmate(username) on update cascade on delete cascade,
constraint unq_task_sequence unique(task_id, username, seq_number)
);

