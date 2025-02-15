import { Link } from "react-router-dom";

function NotFound() {
	return (
		<div className="pt-4 ml-4">
			<h1>Not Found</h1>

			<p>The page you are trying to load does not exist.</p>

			<Link to="/" className="btn btn-primary">Return home</Link>
		</div>
	);
}

export default NotFound;
