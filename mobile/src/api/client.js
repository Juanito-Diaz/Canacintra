import axios from 'axios';

const client = axios.create({
    baseURL: 'http://localhost:3000', // Nota: En emulador Android usar 10.0.2.2 o la IP local si se prueba en físico
});

export default client;
