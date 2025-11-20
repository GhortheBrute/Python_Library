import { BrowserRouter as Router, Routes, Route} from "react-router-dom";
import BookList from "./components/BookList";

function App() {
    return (
        <Router>
            <div className="App">
                {/* Aqui você poderia colocar um Menu/Navbar */}

                <Routes>
                    {/* Rota principal, (Home) mostra a lista de livros */}
                    <Route path="/" element={<BookList />} />

                    {/* Futuras rotas: */}
                    {/* <Route path='/clientes' element={<ClientList/>}/> */}
                </Routes>
            </div>
        </Router>
    )
}

export default App;