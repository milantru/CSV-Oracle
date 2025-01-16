import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home/Home";
import Datasets from "./pages/datasets/Datasets";
import Chat from "./pages/chat/chat";
import NotFound from "./pages/not-found/NotFound";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/datasets" element={<Datasets />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </Router>
    );
}

export default App;