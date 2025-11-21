import React, { useState} from "react";
import api from "../api/axios.js";
import { useNavigate } from "react-router-dom";

const ClientForm = () => {
    const navigate = useNavigate(); // Para redirecionar após salvar
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);

    // Estado inicial do formulário
    const [formData, setFormData] = useState({
        Type: 'PF', // Padrão é pessoa Física
        Email: '',
        Phone: '',
        // Campos de endereço
        Address: {
            Road: '',
            Number: '',
            Neighbourhood: '',
            City: '',
            State: '',
            ZipCode: '',
            Complement: ''
        },
        // Campos específicos PF
        CPF: '',
        FName: '',
        MName: '',
        LName: '',
        Birthdate: '',
        // Campos específicos PJ
        CNPJ: '',
        Name: '',
        FantasyName: ''
    });

    // Função genérica para atualizar campos
    const handleChange = (e) => {
        const { name, value } = e.target;

        // Se for campo endereço, atualiza o objeto aninhado
        if (name.startsWith('addr_')) {
            const field = name.replace('addr_', '');
            setFormData(prev => ({
                ...prev,
                Address: { ...prev.Address, [field]: value }
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    // Envio do Formulário
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Envia para a API (POST /api/clients)
            await api.post('/clients', formData);
            alert('Cliente cadastrado com sucesso!');
            navigate('/clientes'); // Volta para a lista de clientes
        } catch (err) {
            console.log(err);
            // Tenta pegar a mensagem de erro da API ou uma genérica
            setError(err.response?.data?.error || "Erro ao salvar cliente");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '8px'  }}>
            <h2>Novo Cliente</h2>

            {error && <p style={{ color: '#f00', marginBottom: '10px' }}>{error}</p>}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>

                {/* Seleção de Tipo */}
                <div>
                    <label>Tipo de Pessoa:</label>
                    <select name="Type" value={formData.Type} onChange={handleChange} style={{ marginLeft: '10px', padding: '5px' }}>
                        <option value="PF">Pessoa Física</option>
                        <option value="PJ">Pessoa Jurídica</option>
                    </select>
                </div>

                {/* Dados de Contato (Comuns */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <input name="Email" placeholder="example@email.com" value={formData.Email} onChange={handleChange} required type="email"/>
                    <input name="Phone" placeholder="4191234567" value={formData.Phone} onChange={handleChange} required type="tel"/>
                </div>

                <hr />

                {/* --- CAMPOS CONDICIONAIS (PF vs PJ) --- */}

                {formData.Type === 'PF' ? (
                    <>
                        <h3>Dados Pessoais</h3>
                        <input name="CPF" placeholder="CPF (Somente números)" value={formData.CPF} onChange={handleChange} required type="number"/>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                            <input name="FName" placeholder="Primeiro Nome" value={formData.FName} onChange={handleChange} required type="text"/>
                            <input name="MName" placeholder="Nome(s) do meio" value={formData.MName} onChange={handleChange} type="text"/>
                            <input name="LName" placeholder="Último Nome" value={formData.LName} onChange={handleChange} required type="text"/>
                        </div>
                        <label>Data de Nascimento:
                            <input type="date" name="Birthdate" value={formData.Birthdate} onChange={handleChange} required style={{ marginLeft: '10px', padding: '5px' }}/>
                        </label>
                    </>
                ) : (
                    <>
                        <h3>Dados da Empresa</h3>
                        <input name="CNPJ" placeholder="CPNJ" value={formData.CNPJ} onChange={handleChange} required type="number"/>
                        <input name="Name" placeholder="Razão Social" value={formData.Name} onChange={handleChange} required type="text"/>
                        <input name="FantasyName" placeholder="Nome Fantasia" value={formData.FantasyName} onChange={handleChange} type="text"/>
                    </>
                )}

                <hr />

                {/* Endereço (Objeto Aninhado) */}
                <h3>Endereço</h3>
                <div style={{ display: 'grid', gap: '10px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '10px' }}>
                        <input name="addr_Road" placeholder="Rua/Logradouro" value={formData.Address.Road} onChange={handleChange} required type="text"/>
                        <input name="addr_Number" placeholder="Número" value={formData.Address.Number} onChange={handleChange} type="text"/>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
                        <input name="addr_Neighbourhood" placeholder="Bairro" value={formData.Address.Neighbourhood} onChange={handleChange} required type="text"/>
                        <input name="addr_Complement" placeholder="Complemento" value={formData.Address.Complement} onChange={handleChange} type="text"/>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '10px'}}>
                        <input name="addr_City" placeholder="Cidade" value={formData.Address.City} onChange={handleChange} required type="text"/>
                        <input name="addr_State" placeholder="Estado" value={formData.Address.State} onChange={handleChange} required type="text"/>
                        <input name="addr_ZipCode" placeholder="CEP" value={formData.Address.ZipCode} onChange={handleChange} required type="number"/>
                    </div>
                </div>

                <button type="submit" disabled={loading} style={{ marginTop: '20px', padding: '10px', backgroundColor: '#007bff', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer'}}>
                    {loading ? 'Salvando...' : 'Cadastrar Cliente'}
                </button>

            </form>
        </div>
    );
};

export default ClientForm;