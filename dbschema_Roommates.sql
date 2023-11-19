create database if not exists roommates;
use roommates;

create table flat(
flat_code char(10) not null primary key,
name varchar(100) not null
);

create table room(
room_id int not null primary key auto_increment,
name varchar(64) not null,
flat_code char(10) not null,
foreign key (flat_code) references flat(flat_code) on update cascade on delete cascade,
constraint unq_room_in_flat unique(name, flat_code)
);

create table user(
username varchar(64) not null primary key,
email_id varchar(255) not null unique,
phone char(10),
password text not null
);

create table flatmate (
username varchar(64) not null primary key,
flat_code char(10) not null,
room_id int,
join_date date not null,
foreign key (username) references user(username) on update cascade on delete cascade,
foreign key (flat_code) references flat(flat_code) on update cascade on delete cascade,
foreign key (room_id) references room(room_id) on update cascade on delete set null
);

create table belonging(
belonging_id int not null primary key auto_increment,
description varchar(255),
name varchar(255) not null,
flat_code char(10) not null,
foreign key (flat_code) references flat(flat_code) on update cascade on delete cascade,
constraint unq_flat_belonging unique(name, flat_code)
);

create table belonging_owner(
belonging_id int not null,
username varchar(64) not null,
foreign key (belonging_id) references belonging(belonging_id) on update cascade on delete cascade,
foreign key (username) references flatmate(username) on update cascade on delete cascade,
primary key (belonging_id, username)
);

create table payment(
payment_id int not null primary key auto_increment,
name varchar(255) not null,
amount_paid float not null,
payment_date date not null,
payment_type varchar(100) not null,
paid_by varchar(64) not null,
flat_code char(10) not null,
foreign key (flat_code) references flat(flat_code) on update cascade on delete cascade,
foreign key (paid_by) references user(username) on update cascade on delete cascade,
constraint unq_expense unique(name, payment_date, paid_by)
);

create table payment_affected_users(
payment_id int not null,
username varchar(64) not null,
is_paid boolean not null default false,
foreign key (payment_id) references payment(payment_id) on update cascade on delete cascade,
foreign key (username) references user(username) on update cascade on delete cascade
);

create table task(
task_id int not null primary key auto_increment,
task_name varchar(100) not null,
frequency enum('NO_REPEAT', 'DAILY', 'WEEKLY', 'MONTHLY') not null default 'WEEKLY',
current_assigned_to varchar(64),
task_date date,
flat_code char(10) not null,
foreign key (current_assigned_to) references flatmate(username) on update cascade on delete set null,
foreign key (flat_code) references flat(flat_code) on update cascade on delete cascade,
constraint unq_task unique(task_name, current_assigned_to)
);

-- write a trigger to populate current_assigned_to from task_order if a flatmate leaves
drop trigger if exists update_task_when_flatmate_leaves;
delimiter $
create trigger update_task_when_flatmate_leaves 
	after delete on flatmate
for each row
begin
declare task_not_found boolean default false;
        declare task_id_var int;
        declare next_user_var varchar(64);
		declare task_id_cur cursor for select task_id from task where current_assigned_to = old.username;
        declare exit handler for not found
			set task_not_found = true;
		open task_id_cur;
        while task_not_found = false do
			fetch task_id_cur into task_id_var;
            call next_flatmate_to_perform_task(task_id_var, next_user_var);
			update task
				set current_assigned_to = next_user_var where task_id = task_id_var;
		end while;
end $
delimiter ;

-- procedure to get next assigned person
drop procedure if exists next_flatmate_to_perform_task;
delimiter $
create procedure next_flatmate_to_perform_task(in task_id_p int, out username_out_p varchar(64))
begin
	declare cur_user_var varchar(64);
    declare seq_no_cur int;
    select current_assigned_to into cur_user_var from task where task_id = task_id_p;
    if cur_user_var is null then
		select username into username_out_p from task_order where task_id = task_id_p and seq_number = 1;
    else
		select seq_number into seq_no_cur from task_order where task_id = task_id_p and username = cur_user_var;
        select username into username_out_p from task_order where task_id = task_id_p and seq_number = seq_no_cur + 1;
        if username_out_p is null then
			select username into username_out_p from task_order where task_id = task_id_p and seq_number = 1;
		end if;
    end if;
end $
delimiter ;


create table task_order(
task_order_id int not null primary key auto_increment,
seq_number int not null,
username varchar(64) not null,
task_id int not null,
foreign key (task_id) references task(task_id) on update cascade on delete cascade,
foreign key (username) references flatmate(username) on update cascade on delete cascade,
constraint unq_task_sequence unique(task_id, username, seq_number)
);


-- write trigger to update sq no when a flatmate leaves
drop trigger if exists update_task_seq_on_flatmate_delete;
delimiter $
create trigger update_task_seq_on_flatmate_delete
	after delete on flatmate
for each row
	begin
		declare task_not_found boolean default false;
        declare sq_no_var int;
        declare task_id_var int;
		declare task_id_cur cursor for select task_id, seq_number from task_order where username = old.username;
        declare exit handler for not found
			set task_not_found = true;
		open task_id_cur;
        while task_not_found = false do
			fetch task_id_cur into task_id_var, sq_no_var;
			update task_order
				set seq_number = seq_number - 1 where task_id = task_id_var and seq_number > sq_no_var;
		end while;
	end $
delimiter ;


		

