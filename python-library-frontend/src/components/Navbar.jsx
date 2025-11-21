import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
    const navStyle = {
        backgroundColor: '#33',
        padding: '10px 20px',
        marginBottom: '20px',
        display: 'flex',
        gap: '20px',
        alignItems: 'center',
    };

    const linkStyle = {
        color: 'white',
        textDecoration: 'none',
        fontSize: '18px',
        fontWeight: 'bold',
    };

    return (
        <nav style={navStyle}>
            <div style={{ color: '#fff', fontSize: '24px', marginRight: 'auto' }}>
                📚 Biblioteca Python
            </div>

            <Link to="/" style={linkStyle}>Livros</Link>
            <Link to="/clientes" style={linkStyle}>Clientes</Link>
            <Link to="/emprestimos" style={linkStyle}>Empréstimos</Link>
            <Link to="/relatorios" style={linkStyle}>Relatórios</Link>
        </nav>
    );
};

export default Navbar;