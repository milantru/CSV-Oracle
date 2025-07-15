import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "../auth/Auth";
import { User } from "../types/User";
import { getCurrentlyLoggedInUserAPI, updateUserAPI } from "../services/UserServices";
import { toast } from "react-toastify";
import { registerAPI } from "../services/AuthServices";
import { useNavigate } from "react-router-dom";
import ErrorsDisplay from "./ErrorsDisplay";
import { FadeLoader } from "react-spinners";

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
		<div className="d-flex flex-column w-100">
			<div className="mx-auto"><FadeLoader /></div>
			<div className="mt-2 mx-auto">Loading...</div>
		</div>
	) : (
		<form onSubmit={handleSubmit} className="mx-auto p-4 border rounded shadow" style={{ maxWidth: "500px" }}>
			<ErrorsDisplay errorMessages={errorMessages} />

			<div className="form-outline">
				<label className="form-label " htmlFor="email">Email</label>
				<input type="email" id="email" className="form-control border" value={formState.email}
					onChange={e => setFormState(prevState => ({ ...prevState, email: e.target.value }))} />
			</div>

			{isLoggedIn() && (
				<div className="form-outline">
					<label className="form-label  mt-3" htmlFor="old-password">Old password</label>
					<input type="password" id="old-password" className="form-control border" value={formState.oldPassword}
						onChange={e => setFormState(prevState => ({ ...prevState, oldPassword: e.target.value }))} />
				</div>
			)}

			<div className="form-outline">
				<label className="form-label  mt-3" htmlFor="password">{isLoggedIn() ? "New password" : "Password"}</label>
				<input type="password" id="password" className="form-control border" value={formState.password}
					onChange={e => setFormState(prevState => ({ ...prevState, password: e.target.value }))} />
			</div>

			<div className="form-outline">
				<label className="form-label mt-3" htmlFor="repeated-password">{isLoggedIn() ? "Confirm new password" : "Confirm password"}</label>
				<input type="password" id="repeated-password" className="form-control border" value={formState.repeatedPassword}
					onChange={e => setFormState(prevState => ({ ...prevState, repeatedPassword: e.target.value }))} />
			</div>

			<div className="text-center mt-3">
				<button type="submit" className="btn btn-primary">{isLoggedIn() ? "Save" : "Register"}</button>
			</div>
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
