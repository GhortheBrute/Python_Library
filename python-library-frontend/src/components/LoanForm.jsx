import React, { useState, useEffect} from "react";
import api from "../api/axios.js";
import { useNavigate } from "react-router-dom";
import './LoanForm.css';

const LoanForm = () => {
    const navigate = useNavigate();
    
    // Estados para armazenar as litas que vêm da API
    const [clients, setClients] = useState([]);
    const [books, setBooks] = useState([]);
    
    // Estado do formulário
    const [selectedClient, setSelectedClient] = useState('');
    const [selectedBook, setSelectedBook] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Busca de dados iniciais
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fazemos as duas requisições em paralelo para ser mais rápido
                const [clientsRes, booksRes] = await Promise.all([
                    api.get('/clients'),
                    api.get('/physicalBooks')
                ]);
                
                setClients(clientsRes.data.clients);
                
                // Filtramos no front apenas os livros DISPONÍVEIS
                // (O ideal seria ter um filtro na API, mas por enquanto fazemos aqui
                // Nota: A API retorna 'physical_books' no plural no JSON
                const availableBooks = booksRes.data.physical_books || [];
                setBooks(availableBooks);
                
                setLoading(false);
            } catch (err) {
                console.error('Erro ao carregar os dados: ', err);
                setError('Erro ao carregar listas. Verifique se o servidor está rodando.');
                setLoading(false);
            }
        };
        
        fetchData();
    }, []);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!selectedClient || !selectedBook) {
            alert("Selecione um cliente e um livro.")
            return;
        }
        
        try{
            const payload = {
                idClient: parseInt(selectedClient),
                idPhysicalBook: parseInt(selectedBook),
                BorroTimeSolicited: 14 // Padrão de 2 semanas
            };
            
            await api.post('/loans', payload);
            
            alert("Empréstimo realizado com sucesso!");
            navigate("/"); // Volta para a Home
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.error || "Erro ao realizar empréstimo.";
            alert(msg);
        }
    };
    
    if (loading) return <p className="loading">Carregando formulário...</p>;
    if (error) return <p className="error">{error}</p>;
    
    return (
        <div className="loan-form">
            <h2>Novo Empréstimo</h2>

            <form className="loan-form__form" onSubmit={handleSubmit} >

                {/* Seleção de Cliente */}
                <div>
                    <label className="loan-form__selection">Cliente:</label>
                    <select
                        value={selectedClient}
                        onChange={(e) => setSelectedClient(e.target.value)}
                        className="loan-form__select"
                        required
                    >
                        <option value="">-- Selecione um Cliente --</option>
                        {clients.map((client) => (
                            <option key={client.idClient} value={client.idClient}>
                                {client.Name} (ID:{client.idClient})
                            </option>
                        ))}
                    </select>
                </div>

                {/* Seleção de Livro Físico */}
                <div>
                    <label className="loan-form__selection">Exemplar (Livro Físico):</label>
                    <select
                        value={selectedBook}
                        onChange={(e) => setSelectedBook(e.target.value)}
                        className="loan-form__select"
                        required
                    >
                        <option value="">-- Selecione um Livro --</option>
                        {books.map((book) => (
                            <option key={book.idPhysicalBook} value={book.idPhysicalBook}>
                                {book.Title} (Cópia ID:{book.idPhysicalBook}) - {book.BranchName}
                            </option>
                        ))}
                    </select>
                    <small className="loan-form__note">Apenas livros disponíveis são mostrados.</small>
                </div>

                <button className="loan-form__submit" type="submit">
                    Confirmar Empréstimo
                </button>

            </form>
        </div>
    );
};

export default LoanForm;