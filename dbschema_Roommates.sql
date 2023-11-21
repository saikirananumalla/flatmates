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

drop procedure if exists update_flatmate_room;
delimiter $
create procedure update_flatmate_room(username_p varchar(64), room_name_p varchar(64))
begin
	declare flat_code_var char(10);
    declare room_id_var int;
    select flat_code into flat_code_var from flatmate where username = username_p;
    if flat_code_var is null then
		signal sqlstate '45000' set message_text = 'user is not registered in any flat';
	else
		select room_id into room_id_var from room where flat_code = flat_code_var and name = room_name_p;
        if room_id_var is null then
			signal sqlstate '45000' set message_text = 'no such room in the flat';
		else
			update flatmate set room_id = room_id_var where username = username_p;
		end if;
	end if;
end $
delimiter ;


drop procedure if exists get_flatmate;
delimiter $
create procedure get_flatmate(username_p varchar(64))
begin
	select username, flatmate.flat_code, room.name, join_date from flatmate left join room on flatmate.room_id = room.room_id where username = username_p;
end $
delimiter ;

drop procedure if exists get_flatmates_by_flat_code;
delimiter $
create procedure get_flatmates_by_flat_code(flat_code_p varchar(64))
begin
	select username, flatmate.flat_code, room.name, join_date from flatmate left join room on flatmate.room_id = room.room_id where flatmate.flat_code = flat_code_p;
end $
delimiter ;


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

drop procedure if exists get_belonging;
delimiter $
create procedure get_belonging(name_p varchar(255), flat_code_p char(10))
begin
    select belonging.*, group_concat(username) from belonging left join belonging_owner on belonging.belonging_id = belonging_owner.belonging_id
		where flat_code = flat_code_p and name = name_p group by belonging_id, description, name, flat_code;
end $
delimiter ;


drop procedure if exists get_belonging_by_flat;
delimiter $
create procedure get_belonging_by_flat(flat_code_p char(10))
begin
    select belonging.*, group_concat(username) from belonging left join belonging_owner on belonging.belonging_id = belonging_owner.belonging_id
		where flat_code = flat_code_p group by belonging_id, description, name, flat_code;
end $
delimiter ;


drop procedure if exists insert_belonging;
delimiter $
create procedure insert_belonging(description_p varchar(255), name_p varchar(255), flat_code_p char(10))
begin
	insert into belonging(description, name, flat_code) values (description_p, name_p, flat_code_p);
    select belonging_id from belonging where name = name_p and flat_code = flat_code_p;
end $
delimiter ;

drop procedure if exists update_belonging;
delimiter $
create procedure update_belonging(belonging_id_p int, description_p varchar(255), name_p varchar(255))
begin
	declare bid int;
    select belonging_id into bid from belonging where belonging_id = belonging_id_p;
    if bid is null then
		signal sqlstate '45000' set message_text = 'belonging_id does not exist';
	end if;
	update belonging set description = description_p, name = name_p where belonging_id = belonging_id_p;
    select * from belonging where belonging_id = belonging_id_p;
end $
delimiter ;

drop procedure if exists add_belonging_owner;
delimiter $
create procedure add_belonging_owner(belonging_id_p int, username_p varchar(64))
begin
	declare flat_c1 char(10);
    declare flat_c2 char(10);
    
    select distinct flat_code into flat_c1 from belonging where belonging_id = belonging_id;
    select distinct flat_code into flat_c2 from flatmate where username = username_p;
    
    if flat_c1 is null or flat_c2 is null or flat_c1 != flat_c2 then
		signal sqlstate '45000' set message_text = 'invalid request the belonging and user are not of same flat';
    end if;
    insert into belonging_owner values (belonging_id_p, username_p);
end $
delimiter ;


drop procedure if exists drop_belonging_owners;
delimiter $
create procedure drop_belonging_owners(belonging_id_p int)
begin
	delete from belonging_owner where belonging_id = belonging_id_p;
end $
delimiter ;



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
foreign key (username) references user(username) on update cascade on delete cascade,
primary key (payment_id, username)
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

create table task_order(
                           task_order_id int not null primary key auto_increment,
                           seq_number int not null,
                           username varchar(64) not null,
                           task_id int not null,
                           foreign key (task_id) references task(task_id) on update cascade on delete cascade,
                           foreign key (username) references flatmate(username) on update cascade on delete cascade,
                           constraint unq_task_sequence unique(task_id, username, seq_number)
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

drop procedure if exists get_all_task_details_by_task_id;
delimiter //
create procedure get_all_task_details_by_task_id(in task_id_p int)
begin
	select * from task inner join task_order on task.task_id=task_order.task_id where task.task_id=task_id_p;
end //
delimiter ;

drop procedure if exists check_if_user_belongs_to_flat;
delimiter //
create procedure check_if_user_belongs_to_flat(in flat_code_p varchar(255), in username_p varchar(255))
begin
    declare username_var varchar(255) default null;
    select username into username_var from flatmate where flatmate.flat_code=flat_code_p and username=username_p;
    if username_var is not null then
        select 1;
    else
        select 0;
    end if;
end //
delimiter ;
