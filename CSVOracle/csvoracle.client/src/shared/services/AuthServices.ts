import axios from "axios";
import { User } from "../types/User";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";

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
