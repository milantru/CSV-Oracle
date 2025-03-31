import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { Chat } from "../types/Chat";
import { DatasetKnowledge } from "../../pages/chats/types";

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
