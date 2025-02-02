import { Routes, Route } from "react-router-dom";
import Chat from "../../pages/chat/chat";
import Datasets from "../../pages/datasets/Datasets";
import NotFound from "../../pages/not-found/NotFound";
import Register from "../../pages/register/Register";
import ProtectedRoute from "./ProtectedRoute";
import Login from "../../pages/login/Login";
import Profile from "../../pages/profile/Profile";
import CreateNewDataset from "../../pages/create-new-dataset/CreateNewDataset";

function CsvOracleRoutes() {
    return (
        <>
            <Routes>
                <Route path="/" element={<ProtectedRoute><Datasets /></ProtectedRoute>} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                <Route path="/datasets" element={<ProtectedRoute><Datasets /></ProtectedRoute>} />
                <Route path="/datasets/new" element={<ProtectedRoute><CreateNewDataset /></ProtectedRoute>} />
                <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </>
    );
}

export default CsvOracleRoutes;
