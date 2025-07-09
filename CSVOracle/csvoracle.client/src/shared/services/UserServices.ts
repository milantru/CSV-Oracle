import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { User } from "../types/User";

/**
 * Retrieves the currently logged-in user's details.
 * @returns An object containing the user data (null if not logged in or on error) and error messages if any.
 */
export const getCurrentlyLoggedInUserAPI = async (): Promise<{ user: User | null, errorMessages: string[] }> => {
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

/**
 * Updates the user's information and password.
 * Stores a new token if update is successful.
 * @param user - The updated user information.
 * @param oldPassword - The current password.
 * @param newPassword - The new password.
 * @returns An array of error messages if the update fails; otherwise, an empty array.
 */
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
