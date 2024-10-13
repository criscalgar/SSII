DROP DATABASE IF EXISTS pai_2; 
CREATE DATABASE pai_2;
USE pai_2;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_source VARCHAR(255),
    user_destination VARCHAR(255),
    message TEXT
);