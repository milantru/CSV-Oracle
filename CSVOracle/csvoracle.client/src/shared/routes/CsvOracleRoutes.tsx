import { Routes, Route } from "react-router-dom";
import Datasets from "../../pages/datasets/Datasets";
import NotFound from "../../pages/not-found/NotFound";
import Register from "../../pages/register/Register";
import ProtectedRoute from "./ProtectedRoute";
import Login from "../../pages/login/Login";
import Profile from "../../pages/profile/Profile";
import CreateNewDataset from "../../pages/create-new-dataset/CreateNewDataset";
import Chats from "../../pages/chats/chats";
import CreateNewChat from "../../pages/create-new-chat/CreateNewChat";

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
                <Route path="/chats/:datasetId" element={<ProtectedRoute><Chats /></ProtectedRoute>} />
                <Route path="/chats/:datasetId/new" element={<ProtectedRoute><CreateNewChat /></ProtectedRoute>} />
                <Route path="not-found" element={<NotFound />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </>
    );
}

export default CsvOracleRoutes;
