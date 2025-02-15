import { useState, FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginAPI } from "../../shared/services/AuthServices";
import ErrorsDisplay from "../../shared/components/ErrorsDisplay";

type LoginFormState = {
	email: string;
	password: string;
};

function Login() {
	const [formState, setFormState] = useState<LoginFormState>({
		email: '',
		password: ''
	});
	const [errorMessages, setErrorMessages] = useState<string[]>([]);
	const navigate = useNavigate();

	return (
		<div className="container d-flex flex-column justify-content-center align-items-center min-vh-100">
			<h1 className="text-center display-3">CSV-Oracle</h1>

			<form className="w-100 text-center" style={{ maxWidth: "400px" }} onSubmit={handleSubmit}>
				<ErrorsDisplay errorMessages={errorMessages} />

				<div data-mdb-input-init className="form-outline mb-4">
					<input type="email" id="email" className="form-control border" value={formState.email}
						onChange={e => setFormState(prevState => ({ ...prevState, email: e.target.value }))} />
					<label className="form-label" htmlFor="email">Email</label>
				</div>

				<div data-mdb-input-init className="form-outline mb-4">
					<input type="password" id="password" className="form-control border" value={formState.password}
						onChange={e => setFormState(prevState => ({ ...prevState, password: e.target.value }))} />
					<label className={`form-label ${formState.email ? 'active' : ''}`} htmlFor="password">Password</label>
				</div>

				<button type="submit" className="btn btn-primary btn-block mb-4">Login</button>

				<div className="text-center">
					<Link to="/register">Create new account</Link>
				</div>
			</form>
		</div>
	);

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		const { email, password } = formState;

		const errMsgs = await loginAPI(email, password);
		if (errMsgs.length > 0) {
			setErrorMessages(errMsgs);
		} else {
			navigate("/");
		}
	}
}

export default Login;
