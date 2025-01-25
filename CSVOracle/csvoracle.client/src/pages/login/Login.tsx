import { useState, FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginAPI } from "../../shared/services/AuthServices";

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
		<>
			<h1>CSV-Oracle</h1>

			<form onSubmit={handleSubmit}>
				<div>
					<ul>
						{errorMessages.map((message, index) => (
							<li key={index}>{message}</li>
						))}
					</ul>
				</div>

				<div>
					<input type="email" id="email" value={formState.email}
						onChange={e => setFormState(prevState => ({ ...prevState, email: e.target.value }))} />
					<label htmlFor="email">Email</label>
				</div>

				<div>
					<input type="password" id="password" value={formState.password}
						onChange={e => setFormState(prevState => ({ ...prevState, password: e.target.value }))} />
					<label htmlFor="password">Password</label>
				</div>

				<button type="submit">Login</button>

				<div className="text-center">
					<Link to="/register">Create new account</Link>
				</div>
			</form>
		</>
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
