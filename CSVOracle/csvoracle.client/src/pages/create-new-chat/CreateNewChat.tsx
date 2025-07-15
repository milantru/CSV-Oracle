import { useState, FormEvent, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import { createNewChatAPI } from "../../shared/services/ChatServices";
import ErrorsDisplay from "../../shared/components/ErrorsDisplay";
import BackButton from "../../shared/components/BackButton";
import { ClipLoader } from "react-spinners";

type ChatFormState = {
	name: string;
	userView: string;
};

function CreateNewChat() {
	const { datasetId } = useParams();
	const [formState, setFormState] = useState<ChatFormState>(createInitialFormState());
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
	const [errorMessages, setErrorMessages] = useState<string[]>([]);
	const navigate = useNavigate();

	useEffect(() => {
		if (!isNumber(datasetId)) {
			navigate("/not-found");
		}
	}, [])

	return (
		<>
			<h1 className="text-center py-4">Create new chat</h1>
			<div className="position-absolute top-0 start-0 m-3">
				<BackButton label="Back to chats" />
			</div>

			<form onSubmit={handleSubmit} className="mx-auto p-4 border rounded shadow" style={{ maxWidth: "720px" }}>
				<ErrorsDisplay errorMessages={errorMessages} />

				<div className="form-outline mb-2">
					<label className="form-label" htmlFor="name">Name</label>
					<input type="text" id="name" className="form-control border" value={formState.name}
						onChange={e => setFormState(prevState => ({ ...prevState, name: e.target.value }))} />
				</div>

				<div className="form-outline">
					<label className="form-label" htmlFor="user-view">
						User view (optional) <i className="bi bi-question-circle align-middle"
							title="Description of how the user views or intends to use the data. This can help the assistant provide more relevant responses."></i>
					</label>
					<input type="text" id="user-view" className="form-control border" value={formState.userView}
						onChange={e => setFormState(prevState => ({ ...prevState, userView: e.target.value }))} />
				</div>

				<div className="text-center mt-3">
					{/* Min width and min height is set here so the button does not change its size when switching between text and animation. */}
					<button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ minWidth: "94px", minHeight: "39px" }}>
						{isSubmitting ? <ClipLoader size="15" color="#fff" /> : "Submit"}
					</button>

					{formState.userView && (
						<div className="mt-3">
							<div className="d-flex flex-nowrap mt-1 py-2 px-4 border rounded border-warning">
								<div className="my-auto mr-3"><i className="bi bi-exclamation-circle text-warning mr-1 fs-4"></i></div>
								User view may prolong chat creation as the assistant will try to react to it.
								However, this can help the assistant better address your needs.
							</div>
						</div>
					)}
				</div>
			</form>
		</>
	);

	function createInitialFormState() {
		const emptyFormState: ChatFormState = {
			name: "",
			userView: ""
		};

		return emptyFormState
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		setIsSubmitting(true);

		const errMsgs = await createNewChatAPI(formState.name, formState.userView, datasetId!)

		if (errMsgs.length > 0) {
			setErrorMessages(errMsgs);
			setIsSubmitting(false);
			return;
		}

		setErrorMessages([]);
		setIsSubmitting(false);
		navigate(`/chats/${datasetId}`);
	}
}

export default CreateNewChat;
