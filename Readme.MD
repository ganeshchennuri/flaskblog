# Blog using Flask-MySQL

## DATABASE Queries

- CREATE DATABASE flskblog_db;

- USE flskblog_db;

- CREATE TABLE users (userid int AUTO_INCREMENT UNIQUE, first_name varchar(20), last_name varchar(20), username varchar(20) UNIQUE, email varchar(30) UNIQUE, password varchar(100), PRIMARY KEY (userid));

- CREATE TABLE blog (blogid int AUTO_INCREMENT PRIMARY KEY, title varchar(100), author varchar(40), body varchar(1000));   