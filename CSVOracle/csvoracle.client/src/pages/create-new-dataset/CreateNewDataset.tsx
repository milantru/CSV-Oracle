import { useState, FormEvent, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDatasetForProcessingAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";
import ErrorsDisplay from "../../shared/components/ErrorsDisplay";

type DatasetFormState = {
	csvFiles: File[];
	schemaFile: File | null;
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

				<div className="mb-2">
					<label className="form-label" htmlFor="csv-files">CSV files</label>
					<input id="csv-files" className="form-control" type="file" accept=".csv" multiple onChange={handleCsvFilesChange} />
					{isUploading && (<>
						<label className="form-label" htmlFor="csv-files-progress">Uploading progress: </label>
						<progress id="csv-files-progress" value={uploadProgress} max="100">{uploadProgress}%</progress>
					</>)}
					{formState.csvFiles.length > 0 && (
						<ul>
							{formState.csvFiles.map((csvFile, index) => (
								<li key={index}><small>Filename: {csvFile.name} ({(csvFile.size / 1024).toFixed(2)} KB)</small></li>
							))}
						</ul>
					)}
				</div>

				<div className="mb-2">
					<label className="form-label" htmlFor="schema">CSV schema (CSVW)</label>
					<input id="schema" className="form-control" type="file" accept=".json" onChange={handleSchemaFileChange} />
				</div>

				<div className="form-outline mb-2">
					<label className="form-label" htmlFor="separator">Separator</label>
					<input type="text" id="separator" className="form-control border" value={formState.separator}
						onChange={e => setFormState(prevState => ({ ...prevState, separator: e.target.value }))} />
				</div>

				<div className="form-outline mb-2">
					<label className="form-label" htmlFor="encoding">Encoding</label>
					<input type="text" id="encoding" className="form-control border" value={formState.encoding}
						onChange={e => setFormState(prevState => ({ ...prevState, encoding: e.target.value }))} />
				</div>

				<div className="text-center mt-3">
					<button type="submit" className="btn btn-primary" disabled={formState.csvFiles.length == 0 || isUploading}>Submit</button>
				</div>
			</form>
		</>
	);

	function createInitialFormState() {
		const emptyFormState: DatasetFormState = {
			csvFiles: [],
			schemaFile: null,
			separator: ",",
			encoding: "utf-8",
		};

		return emptyFormState
	}

	function handleCsvFilesChange(e: ChangeEvent<HTMLInputElement>): void {
		setUploadProgress(0);

		const files = e.target.files;
		if (files) {
			setFormState({
				...formState,
				csvFiles: Array.from(files),
			});
		}
	}

	function handleSchemaFileChange(e: ChangeEvent<HTMLInputElement>) {
		const files = e.target.files;
		if (files && files[0]) {
			setFormState({
				...formState,
				schemaFile: files[0],
			});
		}
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		if (formState.csvFiles.length === 0) {
			setErrorMessages(["No files provided."]);
			return;
		}
		setErrorMessages([]);

		setIsUploading(true);

		const { errorMessages: errMsgs } = await uploadDatasetForProcessingAPI(
			formState.csvFiles,
			formState.schemaFile,
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
