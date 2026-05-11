const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('./db');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretkey';

// Middleware de Autenticación
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.status(401).json({ error: 'Token no proporcionado' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Token inválido' });
        req.user = user;
        next();
    });
};

// Middleware para Admin
const isAdmin = (req, res, next) => {
    if (req.user.rol !== 'admin') {
        return res.status(403).json({ error: 'Acceso denegado. Se requiere rol admin.' });
    }
    next();
};

// --- AUTENTICACIÓN ---

app.post('/register', async (req, res) => {
    const { nombre, email, password, rol } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const [result] = await pool.query(
            'INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)',
            [nombre, email, hashedPassword, rol || 'usuario']
        );
        res.status(201).json({ message: 'Usuario registrado', id: result.insertId });
    } catch (error) {
        res.status(500).json({ error: 'Error al registrar usuario. Email posiblemente ya existe.' });
    }
});

app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        const [users] = await pool.query('SELECT * FROM usuarios WHERE email = ?', [email]);
        if (users.length === 0) return res.status(400).json({ error: 'Usuario no encontrado' });

        const user = users[0];
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(400).json({ error: 'Contraseña incorrecta' });

        const token = jwt.sign({ id: user.id, rol: user.rol, nombre: user.nombre }, JWT_SECRET, { expiresIn: '1h' });
        res.json({ token, user: { id: user.id, nombre: user.nombre, email: user.email, rol: user.rol } });
    } catch (error) {
        res.status(500).json({ error: 'Error en el login' });
    }
});

// --- NOTICIAS ---

app.get('/noticias/recientes', async (req, res) => {
    try {
        const [noticias] = await pool.query(
            'SELECT * FROM noticias ORDER BY fecha_publicacion DESC LIMIT 5'
        );
        res.json(noticias);
    } catch (error) {
        res.status(500).json({ error: 'Error al obtener noticias' });
    }
});

app.get('/noticias', async (req, res) => {
    try {
        const [noticias] = await pool.query('SELECT * FROM noticias ORDER BY fecha_publicacion DESC');
        res.json(noticias);
    } catch (error) {
        res.status(500).json({ error: 'Error al obtener noticias' });
    }
});

// --- COMENTARIOS ---

// POST: Enviar comentario (Pendiente)
app.post('/comentarios', authenticateToken, async (req, res) => {
    const { id_noticia, texto } = req.body;
    const id_usuario = req.user.id;
    try {
        const [result] = await pool.query(
            'INSERT INTO comentarios (id_noticia, id_usuario, texto, estado) VALUES (?, ?, ?, "pendiente")',
            [id_noticia, id_usuario, texto]
        );
        res.status(201).json({ message: 'Comentario enviado y pendiente de aprobación', id: result.insertId });
    } catch (error) {
        res.status(500).json({ error: 'Error al enviar comentario' });
    }
});

// GET: Comentarios aprobados de una noticia
app.get('/comentarios/:id_noticia', async (req, res) => {
    const { id_noticia } = req.params;
    try {
        const [comentarios] = await pool.query(
            `SELECT c.*, u.nombre as usuario_nombre 
             FROM comentarios c 
             JOIN usuarios u ON c.id_usuario = u.id 
             WHERE c.id_noticia = ? AND c.estado = 'aprobado' 
             ORDER BY c.fecha_creacion DESC`,
            [id_noticia]
        );
        res.json(comentarios);
    } catch (error) {
        res.status(500).json({ error: 'Error al obtener comentarios' });
    }
});

// GET: Comentarios pendientes (Admin)
app.get('/admin/comentarios/pendientes', authenticateToken, isAdmin, async (req, res) => {
    try {
        const [comentarios] = await pool.query(
            `SELECT c.*, u.nombre as usuario_nombre, n.titulo as noticia_titulo 
             FROM comentarios c 
             JOIN usuarios u ON c.id_usuario = u.id 
             JOIN noticias n ON c.id_noticia = n.id 
             WHERE c.estado = 'pendiente' 
             ORDER BY c.fecha_creacion ASC`
        );
        res.json(comentarios);
    } catch (error) {
        res.status(500).json({ error: 'Error al obtener comentarios pendientes' });
    }
});

// PATCH: Aprobar comentario (Admin)
app.patch('/comentarios/aprobar/:id', authenticateToken, isAdmin, async (req, res) => {
    const { id } = req.params;
    try {
        await pool.query('UPDATE comentarios SET estado = "aprobado" WHERE id = ?', [id]);
        res.json({ message: 'Comentario aprobado' });
    } catch (error) {
        res.status(500).json({ error: 'Error al aprobar comentario' });
    }
});

// DELETE: Eliminar comentario (Admin)
app.delete('/comentarios/:id', authenticateToken, isAdmin, async (req, res) => {
    const { id } = req.params;
    try {
        await pool.query('DELETE FROM comentarios WHERE id = ?', [id]);
        res.json({ message: 'Comentario eliminado' });
    } catch (error) {
        res.status(500).json({ error: 'Error al eliminar comentario' });
    }
});

app.listen(PORT, () => {
    console.log(`Servidor backend corriendo en http://localhost:${PORT}`);
});
