import { Link } from "react-router-dom";
import { useAuth } from "../auth/Auth";

function Panel() {
	const { logout, isLoggedIn } = useAuth();

	return (
		isLoggedIn() ? (
			<div>
				<Link to="/profile">Profile</Link>
				<button type="button" onClick={logout}>Log out</button>
			</div>
		) : (
			<></>
		)
	);
}

export default Panel;
