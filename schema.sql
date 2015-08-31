drop table if exists users;
create table if not exists users (
    id integer primary key autoincrement,
    name text not null,
    note text,
    binary text not null
);
drop table if exists log;
create table if not exists log (
    id integer primary key autoincrement,
    date text not null,
    name text,
    binary text not null,
    status boolean not null
);
