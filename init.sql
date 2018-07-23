
CREATE DATABASE IF NOT EXISTS vm_db;
USE vm_db;
create table if not exists vm_reservations (
                vm_id varchar(40) not null unique,
                ip_address varchar(30) not null unique,
                vm_status varchar(20) not null unique,
                primary key(vm_id));