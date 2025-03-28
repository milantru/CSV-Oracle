import { BrowserRouter as Router } from "react-router-dom";
import { AuthProvider } from "./shared/auth/Auth";
import { ToastContainer } from "react-toastify";
import CsvOracleRoutes from "./shared/routes/CsvOracleRoutes";
import Panel from "./shared/components/Panel";

function App() {
	return (
		<>
			<Router>
				<AuthProvider>
					<div className="position-relative">
						<Panel />
						<CsvOracleRoutes />
						<ToastContainer />
					</div>
				</AuthProvider>
			</Router>
		</>
	);
}

export default App;
