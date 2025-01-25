import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { User } from "../types/User";

export const getCurrentlyLoggedInUserAPI = async (): Promise<{ user: User | null, errorMessages: string[] }>  => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { user: null, errorMessages: [] };
	}

	try {
		const response = await axios.get<User>(apiBaseUrl + "/User", {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const user = response.data;
		return { user: user, errorMessages: [] };
	} catch (error) {
		return { user: null, errorMessages: getErrorMessages(error) };
	}
};

export const updateUserAPI = async (user: User, oldPassword: string, newPassword: string) => {
	const token = localStorage.getItem("token");

	try {
		const response = await axios.put<string>(apiBaseUrl + "/User", {
			...user,
			oldPassword: oldPassword,
			newPassword: newPassword,
		}, {
			headers: {
				Authorization: "bearer " + token
			}
		});
		
		const newToken = response.data;
		localStorage.setItem("token", newToken);

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};
