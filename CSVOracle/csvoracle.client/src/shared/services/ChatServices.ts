import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { Chat } from "../types/Chat";

export const getDatasetChatsAPI = async (datasetId: number): Promise<{ chats: Chat[], errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { chats: [], errorMessages: ["Please log in."] };
	}

	try {
		const response = await axios.get<Chat[]>(apiBaseUrl + `/Chat/${datasetId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const chats = response.data;
		return { chats: chats, errorMessages: [] };
	} catch (error) {
		return { chats: [], errorMessages: getErrorMessages(error) };
	}
};

export const createNewChatAPI = async (chatName: string, userView: string, datasetId: string) => {
	const token = localStorage.getItem("token");
	if (!token) {
		return ["Please log in."];
	}

	const formData = new FormData();
	formData.append("name", chatName);
	formData.append("userView", userView);
	formData.append("datasetId", datasetId);

	try {
		await axios.post(apiBaseUrl + "/Chat", formData, {
			headers: {
				"Authorization": "bearer " + token,
				"Content-Type": "multipart/form-data"
			}
		});

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};
