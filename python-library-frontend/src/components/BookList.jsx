import React, { useEffect, useState} from "react";
import api from '../api/axios.js';

const BookList = () => {
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // useEffect roda assim que o componente aparece na tela
    useEffect(() => {
        const fetchBooks = async () => {
            try {
                // Chama a sua rota GET /api/books
                const response = await api.get('/books');
                setBooks(response.data.books); // Guarda os dados no estado
                setLoading(false);
            } catch (err) {
                console.error("Erro ao buscar livros: ", err);
                setError("Não foi possível carregar os livros");
                setLoading(false);
            }
        };

        fetchBooks();
    }, []);

    if (loading) return <p>Carregando Biblioteca...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div style={{ padding: '20px'}}>
            <h1>Acervo da Biblioteca</h1>

            {books.length === 0 ? (
                <p>Nenhum livro encontrado.</p>
            ) : (
            <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))'}}>
                {/* Mapeia cada livro para um 'Card' */}
                {books.map((book) => (
                    <div key={book.ISBN} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
                        <h3>{book.Title}</h3>
                        <p><strong>Autor:</strong> {book.Author}</p>
                        <p><strong>Editora:</strong> {book.Publisher}</p>
                        <p><strong>Idioma:</strong> {book.Language}</p>
                        <p><strong>ISBN:</strong> <small>{book.ISBN}</small></p>
                        {/* Se tiver nota, exibe, senão exibe "Sem avaliação" */}
                        <p>⭐ {book.Review ? book.Review : 'N/A'}</p>
                    </div>
                ))}
            </div>
            )}
        </div>
    )
}

export default BookList;