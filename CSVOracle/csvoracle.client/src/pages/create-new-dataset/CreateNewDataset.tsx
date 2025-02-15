import { useState, FormEvent, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDatasetForProcessingAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";
import ErrorsDisplay from "../../shared/components/ErrorsDisplay";

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
			<h1 className="text-center mb-2">Create new dataset</h1>

			<form onSubmit={handleSubmit} className="mx-auto p-4 border rounded shadow" style={{ maxWidth: "720px" }}>
				<ErrorsDisplay errorMessages={errorMessages} />

				<div>
					<input type="file" className="form-control" multiple onChange={handleFilesChange} />
					{isUploading && (<>
						<label htmlFor="files" className="form-label">Uploading progress: </label>
						<progress id="files" value={uploadProgress} max="100">{uploadProgress}%</progress>
					</>)}
					<ul>
						{formState.files.map((file, index) => (
							<li key={index}><small>Filename: {file.name} ({(file.size / 1024).toFixed(2)} KB)</small></li>

						))}
					</ul>
				</div>

				<div className="form-outline">
					<label className="form-label" htmlFor="additional-info">Additional info</label>
					<textarea id="additional-info" className="form-control border" rows={3} value={formState.additionalInfo}
						onChange={e => setFormState(prevState => ({ ...prevState, additionalInfo: e.target.value }))}></textarea>
				</div>

				<div className="form-outline">
					<label className="form-label" htmlFor="separator">Separator</label>
					<input type="text" id="separator" className="form-control border" value={formState.separator}
						onChange={e => setFormState(prevState => ({ ...prevState, separator: e.target.value }))} />
				</div>

				<div className="form-outline">
					<label className="form-label" htmlFor="encoding">Encoding</label>
					<input type="text" id="encoding" className="form-control border" value={formState.encoding}
						onChange={e => setFormState(prevState => ({ ...prevState, encoding: e.target.value }))} />
				</div>

				<div className="text-center mt-3">
					<button type="submit" className="btn btn-primary" disabled={formState.files.length == 0 || isUploading}>Submit</button>
				</div>
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
