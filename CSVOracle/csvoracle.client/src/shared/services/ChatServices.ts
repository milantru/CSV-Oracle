import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { Chat } from "../types/Chat";
import { DatasetKnowledge } from "../../pages/chats/types";

/**
 * Retrieves all chats associated with a specific dataset.
 * @param datasetId - The ID of the dataset.
 * @returns An object with a list of chats and error messages if any.
 */
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

/**
 * Retrieves a chat by the provided id.
 * @param chatId - The ID of the requested chat.
 * @returns A chat and empty array, or null and error messages if any.
 */
export const getChatAPI = async (chatId: number): Promise<{ chat: Chat | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { chat: null, errorMessages: ["Please log in."] };
	}

	try {
		const response = await axios.get<Chat>(apiBaseUrl + `/Chat/chat/${chatId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const chat = response.data;
		return { chat: chat, errorMessages: [] };
	} catch (error) {
		return { chat: null, errorMessages: getErrorMessages(error) };
	}
};

/**
 * Retrieves dataset knowledge for a specific chat by chat ID.
 * @param chatId - The ID of the chat.
 * @returns A dataset knowledge object and empty array, or null and error messages if any.
 */
export const getDatasetKnowledgeAPI = async (chatId: number): Promise<{ datasetKnowledge: DatasetKnowledge | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { datasetKnowledge: null, errorMessages: ["Please log in."] };
	}

	try {
		const response = await axios.get<DatasetKnowledge>(apiBaseUrl + `/Chat/dataset-knowledge/${chatId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const datasetKnowledge = response.data;
		return { datasetKnowledge: datasetKnowledge, errorMessages: [] };
	} catch (error) {
		return { datasetKnowledge: null, errorMessages: getErrorMessages(error) };
	}
};

/**
 * Creates a new chat with the provided name and user view, related to the dataset specified by the dataset ID.
 * @param chatName - The name of the chat.
 * @param userView - The user view.
 * @param datasetId - The ID of the dataset to which chat should relate to.
 * @returns An array of error messages if creation fails; otherwise, an empty array.
 */
export const createNewChatAPI = async (chatName: string, userView: string, datasetId: number) => {
	const token = localStorage.getItem("token");
	if (!token) {
		return ["Please log in."];
	}

	const formData = new FormData();
	formData.append("name", chatName);
	formData.append("userView", userView);
	formData.append("datasetId", datasetId.toString());

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

/**
 * Updates the existing chat.
 * @param chat - The updated chat.
 * @returns An array of error messages if the update fails; otherwise, an empty array.
 */
export const updateChatAPI = async (chat: Chat) => {
	const token = localStorage.getItem("token");

	try {
		await axios.put<string>(apiBaseUrl + "/Chat", {
			...chat
		}, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};

/**
 * Sends a message to generate an answer to it, in a specific chat.
 * @param message - The message to send.
 * @param chatId - The chat ID.
 * @returns An object containing the updated chat or null if failed, plus error messages.
 */
export const generateAnswerAPI = async (message: string, chatId: number)
	: Promise<{ chat: Chat | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { chat: null, errorMessages: ["Please log in."] };
	}

	const formData = new FormData();
	formData.append("newMessage", message);
	formData.append("chatId", chatId.toString());

	try {
		const response = await axios.post<Chat>(apiBaseUrl + "/Chat/generate-answer", formData, {
			headers: {
				"Authorization": "bearer " + token,
				"Content-Type": "multipart/form-data"
			}
		});

		const chat = response.data as Chat;
		return { chat: chat, errorMessages: [] };
	} catch (error) {
		return { chat: null, errorMessages: getErrorMessages(error) };
	}
};

/**
 * Deletes a chat identified by the given chat ID.
 * @param chatId - The ID of the chat to delete.
 * @returns An array with error messages if deletion fails; otherwise, an empty array.
 */
export const deleteChatAPI = async (chatId: number): Promise<string[]> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return ["Please log in."];
	}

	try {
		await axios.delete(apiBaseUrl + `/Chat/${chatId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};
