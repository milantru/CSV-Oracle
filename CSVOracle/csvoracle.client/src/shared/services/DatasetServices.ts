import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { Dataset, DatasetStatus } from "../types/Dataset";

export const getUserDatasetsAPI = async (): Promise<{userDatasets: Dataset[], errorMessages: string[]}> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { userDatasets: [], errorMessages: ["Please log in."] };
	}

	try {
		const response = await axios.get<Dataset[]>(apiBaseUrl + "/Dataset", {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const datasets = response.data;
		return { userDatasets: datasets, errorMessages: [] };
	} catch (error) {
		return { userDatasets: [], errorMessages: getErrorMessages(error) };
	}
};

export const getUserDatasetStatusAPI = async (datasetId: number): Promise<{ status: DatasetStatus | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { status: null, errorMessages: ["Please log in."] };
	}
	
	try {
		const response = await axios.get<DatasetStatus>(apiBaseUrl + `/Dataset/status/${datasetId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		const status = response.data;
		return { status: status, errorMessages: [] };
	} catch (error) {
		return { status: null, errorMessages: getErrorMessages(error) };
	}
};

export const uploadDatasetForProcessingAPI = async (
	files: File[],
	additionalInfo: string | null,
	separator: string | null,
	encoding: string | null,
	setUploadProgress: React.Dispatch<React.SetStateAction<number>>)
	: Promise<{ uploadedDatasetId: number | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { uploadedDatasetId: null, errorMessages: ["Please log in."] };
	}
	if (files.length === 0) {
		return { uploadedDatasetId: null, errorMessages: ["No files provided."] };
	}

	const formData = new FormData();
	for (let i = 0; i < files.length; i++) {
		formData.append("files", files[i]);
	}
	if (additionalInfo) formData.append("metadata.additionalInfo", additionalInfo);
	if (separator) formData.append("metadata.separator", separator);
	if (encoding) formData.append("metadata.encoding", encoding);

	try {
		const response = await axios.post<number>(apiBaseUrl + "/Dataset", formData, {
			headers: {
				"Authorization": "bearer " + token,
				"Content-Type": "multipart/form-data"
			},
			onUploadProgress: (progressEvent) => {
				const progress = progressEvent.total ? Math.round((progressEvent.loaded * 100) / progressEvent.total) : 0;
				setUploadProgress(progress);
			}
		});

		const datasetId = response.data;
		return { uploadedDatasetId: datasetId, errorMessages: [] };;
	}
	catch (error) {
		return { uploadedDatasetId: null, errorMessages: getErrorMessages(error) };
	}
};
