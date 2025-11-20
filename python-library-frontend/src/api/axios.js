import axios from "axios";

// Cria uma instância de Axios com o endereço de seu Flask
const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api/',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;