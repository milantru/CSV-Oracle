import axios from "axios";
import { apiBaseUrl } from "../Constants";
import { getErrorMessages } from "../helperFunctions/ErrorHandler";
import { Dataset, DatasetStatus } from "../types/Dataset";

/**
 * Retrieves all datasets belonging to the currently logged-in user.
 * @returns An object containing the user's datasets (empty in case of error) and error messages if any.
 */
export const getUserDatasetsAPI = async (): Promise<{ userDatasets: Dataset[], errorMessages: string[] }> => {
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

/**
 * Fetches the status of a specific dataset by its ID.
 * @param datasetId - The ID of the dataset.
 * @returns An object containing the dataset status (null in case of error) and error messages if any.
 */
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

/**
 * Uploads CSV files for processing, with optional schema, separator, and encoding.
 * Reports upload progress through the provided callback.
 * @param csvFiles - Array of CSV files to upload.
 * @param schemaFile - Optional schema file.
 * @param separator - Optional CSV separator, e.g. ",".
 * @param encoding - Optional file encoding, e.g. "utf-8".
 * @param setUploadProgress - Callback to update upload progress percentage.
 * @returns An object containing the uploaded dataset ID (null in case of error) and error messages if any.
 */
export const uploadDatasetForProcessingAPI = async (
	csvFiles: File[],
	schemaFile: File | null,
	separator: string | null,
	encoding: string | null,
	setUploadProgress: React.Dispatch<React.SetStateAction<number>>)
	: Promise<{ uploadedDatasetId: number | null, errorMessages: string[] }> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return { uploadedDatasetId: null, errorMessages: ["Please log in."] };
	}
	if (csvFiles.length === 0) {
		return { uploadedDatasetId: null, errorMessages: ["No csv files provided."] };
	}

	const formData = new FormData();
	for (let i = 0; i < csvFiles.length; i++) {
		formData.append("csvFiles", csvFiles[i]);
	}
	if (schemaFile) formData.append("schemaFile", schemaFile);
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
		return { uploadedDatasetId: datasetId, errorMessages: [] };
	}
	catch (error) {
		return { uploadedDatasetId: null, errorMessages: getErrorMessages(error) };
	}
};

/**
 * Deletes a dataset by ID.
 * @param datasetId - The ID of the dataset to delete.
 * @returns An array with error messages if deletion fails; otherwise, an empty array.
 */
export const deleteDatasetAPI = async (datasetId: number): Promise<string[]> => {
	const token = localStorage.getItem("token");
	if (!token) {
		return ["Please log in."];
	}

	try {
		await axios.delete(apiBaseUrl + `/Dataset/${datasetId}`, {
			headers: {
				Authorization: "bearer " + token
			}
		});

		return [];
	} catch (error) {
		return getErrorMessages(error);
	}
};
