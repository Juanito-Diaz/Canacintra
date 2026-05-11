const mysql = require('mysql2/promise');
const pool = require('./db');

async function setup() {
    try {
        console.log('Iniciando configuración de base de datos...');

        const tempPool = mysql.createPool({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASS,
            waitForConnections: true,
            connectionLimit: 2
        });

        await tempPool.query(`CREATE DATABASE IF NOT EXISTS ${process.env.DB_NAME}`);
        await tempPool.end();

        // Tabla usuarios
        await pool.query(`
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                rol ENUM('admin', 'usuario') DEFAULT 'usuario'
            )
        `);
        console.log('Tabla usuarios lista.');

        // Tabla noticias
        await pool.query(`
            CREATE TABLE IF NOT EXISTS noticias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                contenido TEXT NOT NULL,
                imagen_url VARCHAR(255),
                fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);
        // Asegurarse de que las columnas existan si la tabla ya existía
        try {
            await pool.query('ALTER TABLE noticias ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(255)');
            await pool.query('ALTER TABLE noticias ADD COLUMN IF NOT EXISTS fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP');
        } catch (e) {
            // Algunos servidores MySQL antiguos no soportan ADD COLUMN IF NOT EXISTS
            console.log('Nota: No se pudo verificar/agregar columnas dinámicamente, asegúrate de que existan.');
        }
        console.log('Tabla noticias lista.');

        // Tabla comentarios
        await pool.query(`
            CREATE TABLE IF NOT EXISTS comentarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_noticia INT NOT NULL,
                id_usuario INT NOT NULL,
                texto TEXT NOT NULL,
                estado ENUM('pendiente', 'aprobado') DEFAULT 'pendiente',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_noticia) REFERENCES noticias(id) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        `);
        console.log('Tabla comentarios lista.');

        // Insertar algunas noticias de prueba para el carrusel
        const [rows] = await pool.query('SELECT COUNT(*) as count FROM noticias');
        if (rows[0].count === 0) {
            await pool.query(`
                INSERT INTO noticias (titulo, contenido, imagen_url) VALUES 
                ('Nueva Inversión en Sector Industrial', 'Canacintra anuncia nuevos proyectos...', 'https://picsum.photos/seed/noticia1/800/400'),
                ('Reunión Anual de Socios', 'Se discutieron los retos del 2024...', 'https://picsum.photos/seed/noticia2/800/400'),
                ('Innovación Tecnológica en Pymes', 'Nuevas herramientas para el crecimiento...', 'https://picsum.photos/seed/noticia3/800/400'),
                ('Convenio con Universidades', 'Alianza estratégica para el talento...', 'https://picsum.photos/seed/noticia4/800/400'),
                ('Expo Industria 2024', 'El evento más grande del sector...', 'https://picsum.photos/seed/noticia5/800/400'),
                ('Taller de Liderazgo', 'Desarrollando habilidades directivas...', 'https://picsum.photos/seed/noticia6/800/400')
            `);
            console.log('Noticias de prueba insertadas.');
        }

        // Insertar usuario admin inicial si no hay usuarios
        const [userRows] = await pool.query('SELECT COUNT(*) as count FROM usuarios');
        if (userRows[0].count === 0) {
            const bcrypt = require('bcryptjs');
            const hashedAdminPass = await bcrypt.hash('admin123', 10);
            await pool.query(
                'INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)',
                ['Admin Canacintra', 'admin@canacintra.com', hashedAdminPass, 'admin']
            );
            console.log('Usuario administrador inicial creado (admin@canacintra.com / admin123).');
        }

        console.log('Base de datos configurada correctamente.');
        process.exit(0);
    } catch (error) {
        console.error('Error configurando la base de datos:', error);
        process.exit(1);
    }
}

setup();
