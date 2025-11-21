import { BrowserRouter as Router, Routes, Route} from "react-router-dom";
import BookList from "./components/BookList";
import Navbar from "./components/Navbar";
import ClientList from "./components/ClientList.jsx";
import ClientForm from "./components/ClientForm.jsx";
import LoanForm from "./components/LoanForm.jsx";

function App() {
    return (
        <Router>
            <div className="App">
                <Navbar />

                <Routes>
                    {/* Rota principal, (Home) mostra a lista de livros */}
                    <Route path="/" element={<BookList />} />
                    <Route path='/clientes' element={<ClientList />} />
                    <Route path='/clientes/novo' element={<ClientForm />} />
                    <Route path='/emprestimos' element={<LoanForm />}/>
                    {/* Futuras rotas: */}

                    <Route path='/relatorios' element={<h2>Página de Relatórios (Em construção)</h2>}/>
                </Routes>
            </div>
        </Router>
    )
}

export default App;