import { Link } from "react-router-dom";
import { useAuth } from "../auth/Auth";

function Panel() {
	const { logout, isLoggedIn } = useAuth();

	return (
		isLoggedIn() ? (
			// z-index is set to 1 because otherwise, on some pages, parts of panel are not clickable
			<div className="d-flex position-absolute end-0 mt-1 mr-3" style={{ zIndex: 1 }}>
				<Link to="/profile"><i className="bi bi-person-circle fs-2 d-block pt-1 mr-2"></i></Link>
				<div className="my-auto">
					<button type="button" className="btn btn-primary" onClick={logout}><i className="bi bi-door-closed"></i> Log out</button>
				</div>
			</div>
		) : (
			<></>
		)
	);
}

export default Panel;
