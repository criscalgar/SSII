DROP DATABASE IF EXISTS pai_1; 
CREATE DATABASE pai_1;
USE pai_1;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    clave VARCHAR(60) NOT NULL
);

CREATE TABLE transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emisor_nombre VARCHAR(50) NOT NULL,
    destinatario_nombre VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (emisor_nombre) REFERENCES usuarios(nombre_usuario) ON DELETE CASCADE,
    FOREIGN KEY (destinatario_nombre) REFERENCES usuarios(nombre_usuario) ON DELETE CASCADE
);