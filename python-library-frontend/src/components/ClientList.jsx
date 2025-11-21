import React, { useEffect, useState} from "react";
import api from "../api/axios.js"
import { useNavigate } from "react-router-dom";

const ClientList = () => {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    // Função para buscar clientes
    const fetchClients = async () => {
        try {
            const response = await api.get("/clients");
            setClients(response.data.clients);
            setLoading(false);
        } catch (err) {
            console.error("Erro ao buscar clientes: ", err);
            setError("Erro ao carregar a lista de clientes.");
            setLoading(false);
        }
    };
    useEffect(() => {
        fetchClients();
    }, []);

    if (loading) return <p style={{ padding: '20px' }}>Carregando clientes...</p>;
    if (error) return <p style={{ padding: '20px', color: 'red' }}>{error}</p>;

    return (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>Clientes Cadastrados</h1>
                <button
                    onClick={() => navigate('/clientes/novo')}
                    style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '5px', marginLeft: '1rem' }}
                >
                    + Novo Cliente
                </button>
            </div>


            {clients.length === 0 ? (
                <p>Nenhum cliente encontrado.</p>
            ) : (
                <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
                    {clients.map((client) => (
                        <div key={client.idClient} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', position: 'relative' }}>
                            {/* Tag para identificar o tipo*/}
                            <span style={{
                                position: 'absolute', top: '10px', right: '10px',
                                background: client.Type === 'PF' ? '#007bff' : '#6f42c1',
                                color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px'
                            }}>
                                {client.Type}
                            </span>

                            {/* Nome Principal */}
                            <h3>{client.Name}</h3>

                            {/* Substituído para PJ (Nome Fantasia) */}
                            {client.Type === 'PJ' && client.FantasyName && (
                                <p style={{ fontStyle: 'italic', color: '#666' }}>{client.FantasyName}</p>
                            )}

                            <div style={{ marginTop: '10px', fontSize: '14px' }}>
                                <p><strong>Documento:</strong> {client.Type === 'PF' ? client.CPF : client.CNPJ}</p>
                                <p><strong>Email:</strong> {client.Email}</p>
                                <p><strong>Telefone:</strong> {client.Phone || 'N/A'}</p>

                                {/* Endereço formatado*/}
                                <p style={{ marginTop: '10px', borderTop: '1px solid #eee', paddingTop: '5px'}}>
                                    <strong>Endereço:</strong><br />
                                    {client.Address.Road}, {client.Address.Number || 'N/A'} <br />
                                    {client.Address.Neighbourhood} - {client.Address.City}/{client.Address.State}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default ClientList;