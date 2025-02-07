import { useState, useEffect, FormEvent, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDatasetForProcessingAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";

type DatasetFormState = {
	files: File[];
	additionalInfo: string;
	separator: string; // char
	encoding: string;
};

function CreateNewDataset() {
	const [formState, setFormState] = useState<DatasetFormState>(createInitialFormState());
	const [isUploading, setIsUploading] = useState<boolean>(false);
	const [errorMessages, setErrorMessages] = useState<string[]>([]);
	const [uploadProgress, setUploadProgress] = useState<number>(0);
	const navigate = useNavigate();

	return (
		<>
			<form onSubmit={handleSubmit}>
				<div>
					<ul>
						{errorMessages.map((errorMessage, index) => (
							<li key={index}>{errorMessage}</li>
						))}
					</ul>
				</div>

				<div>
					<input type="file" multiple onChange={handleFilesChange} />
					<label htmlFor="files">Downloading progress:</label>
					<progress id="files" value={uploadProgress} max="100">{uploadProgress}%</progress>
					<ul>
						{formState.files.map((file, index) => (
							<li key={index}>Filename: {file.name} ({(file.size / 1024).toFixed(2)} KB)</li>

						))}
					</ul>
				</div>

				<div>
					<input type="text" id="additional-info" value={formState.additionalInfo}
						onChange={e => setFormState(prevState => ({ ...prevState, additionalInfo: e.target.value }))} />
					<label htmlFor="additional-info">Additional info</label>
				</div>

				<div>
					<input type="text" id="separator" value={formState.separator}
						onChange={e => setFormState(prevState => ({ ...prevState, separator: e.target.value }))} />
					<label htmlFor="separator">Separator</label>
				</div>

				<div>
					<input type="text" id="encoding" value={formState.encoding}
						onChange={e => setFormState(prevState => ({ ...prevState, encoding: e.target.value }))} />
					<label htmlFor="encoding">Encoding</label>
				</div>

				{formState.files.length > 0 && !isUploading && (
					<button type="submit">Submit</button>
				)}
			</form>
		</>
	);

	function createInitialFormState() {
		const emptyFormState: DatasetFormState = {
			files: [],
			additionalInfo: "",
			separator: ",",
			encoding: "utf-8",
		};

		return emptyFormState
	}

	function handleFilesChange(e: ChangeEvent<HTMLInputElement>): void {
		setUploadProgress(0);

		const files = e.target.files;
		if (files) {
			setFormState({
				...formState,
				files: Array.from(files),
			});
		}
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		if (formState.files.length === 0) {
			setErrorMessages(["No files provided."]);
			return;
		}
		setErrorMessages([]);

		setIsUploading(true);

		const { errorMessages: errMsgs } = await uploadDatasetForProcessingAPI(
			formState.files,
			formState.additionalInfo,
			formState.separator,
			formState.encoding,
			setUploadProgress
		)

		if (errMsgs.length > 0) {
			setErrorMessages(errMsgs);
			setUploadProgress(0);
			setIsUploading(false);
			return;
		}

		setUploadProgress(100);
		setIsUploading(false);

		toast.success("Files uploaded successfully!");
		navigate("/datasets");
	}
}

export default CreateNewDataset;
