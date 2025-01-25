import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "../auth/Auth";
import { User } from "../types/User";
import { getCurrentlyLoggedInUserAPI, updateUserAPI } from "../services/UserServices";
import { toast } from "react-toastify";
import { registerAPI } from "../services/AuthServices";
import { useNavigate } from "react-router-dom";

type UserFormState = User & {
	oldPassword: string;
	password: string;
	repeatedPassword: string;
};

function UserForm() {
	const [formState, setFormState] = useState<UserFormState>(null!);
	const [errorMessages, setErrorMessages] = useState<string[]>([]);
	const { isLoggedIn } = useAuth();
	const navigate = useNavigate();

	useEffect(() => {
		async function fetchData() {
			const { user: currentlyLoggedInUser, errorMessages: errMsgs } = await getCurrentlyLoggedInUserAPI();
			if (errMsgs.length > 0) {
				setErrorMessages(errMsgs);
				return;
			}

			if (currentlyLoggedInUser === null) {
				setFormState(createEmptyFormState());
			} else {
				const newFormState = {
					...currentlyLoggedInUser,
					oldPassword: "",
					password: "",
					repeatedPassword: "",
				}
				setFormState(newFormState);
			}
			setErrorMessages([]);
		}

		fetchData();
	}, [])

	return formState === null ? (
		<div>Loading...</div>
	) : (
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

			{isLoggedIn() && (
				<div>
					<input type="password" id="old-password" value={formState.oldPassword}
						onChange={e => setFormState(prevState => ({ ...prevState, oldPassword: e.target.value }))} />
					<label htmlFor="old-password">Old password</label>
				</div>
			)}

			<div>
				<input type="password" id="password" value={formState.password}
					onChange={e => setFormState(prevState => ({ ...prevState, password: e.target.value }))} />
				<label htmlFor="password">{isLoggedIn() ? "New password" : "Password"}</label>
			</div>

			<div>
				<input type="password" id="repeated-password" value={formState.repeatedPassword}
					onChange={e => setFormState(prevState => ({ ...prevState, repeatedPassword: e.target.value }))} />
				<label htmlFor="repeated-password">{isLoggedIn() ? "Confirm new password" : "Confirm password"}</label>
			</div>

			<button type="submit">{isLoggedIn() ? "Save" : "Register"}</button>
		</form>
	);

	function createEmptyFormState() {
		const emptyFormState: UserFormState = {
			id: 0,
			email: "",
			oldPassword: "",
			password: "",
			repeatedPassword: "",
		};

		return emptyFormState
	}

	async function updateExistingUser(user: User, oldPassword: string, password: string) {
		const errMsgs = await updateUserAPI(user, oldPassword, password);
		if (errMsgs.length > 0) {
			setErrorMessages(errMsgs);
			return
		}
		setErrorMessages([]);

		setFormState(prevState => ({
			...prevState,
			oldPassword: "",
			password: "",
			repeatedPassword: ""
		}));

		toast.success("Profile saved successfully!");
	}

	async function registerNewUser(user: User, password: string) {
		const errMsgs = await registerAPI(user, password);
		if (errMsgs.length > 0) {
			setErrorMessages(errMsgs);
			return
		}
		setErrorMessages([]);

		toast.success("Registration successful!")
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		const { id, email, oldPassword, password, repeatedPassword } = formState;

		if (password !== repeatedPassword) {
			setFormState(prevState => ({
				...prevState,
				password: "",
				repeatedPassword: ""
			}));

			setErrorMessages(["Passwords do not match"]);
			return;
		}
		setErrorMessages([]);

		const user: User = { id, email };
		if (isLoggedIn()) {
			await updateExistingUser(user, oldPassword, password);
		} else {
			await registerNewUser(user, password);

			navigate("/login");
		}
	}
}

export default UserForm;