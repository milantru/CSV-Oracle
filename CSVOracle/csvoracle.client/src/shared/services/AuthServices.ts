import axios from "axios";
import { User } from "../types/User";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";

/**
 * Registers a new user with the provided user details and password.
 * @param user - The user information to register.
 * @param password - The user's password.
 * @returns An array of error messages if registration fails; otherwise, an empty array.
 */
export const registerAPI = async (user: User, password: string) => {
	try {
		await axios.post(apiBaseUrl + "/Auth/register", {
			...user,
			password: password
		});

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};

/**
 * Logs in a user using email and password, stores the received token locally.
 * @param email - The user's email address.
 * @param password - The user's password.
 * @returns An array of error messages if login fails; otherwise, an empty array.
 */
export const loginAPI = async (email: string, password: string) => {
	try {
		const response = await axios.post<string>(apiBaseUrl + "/Auth/login", {
			email: email,
			password: password
		});

		const token = response.data;
		localStorage.setItem("token", token);

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};
