drop database if exists starter_test;
drop database if exists starter_development;
drop user if exists starter;

create user starter with encrypted password 'starter';
create database starter_development;
create database starter_test;
grant all privileges on database starter_development to starter;
grant all privileges on database starter_test to starter;
\c starter_development
grant create on schema public to starter;
\c starter_test
grant create on schema public to starter;
