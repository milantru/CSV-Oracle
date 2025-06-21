import { useState, FormEvent, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import { createNewChatAPI } from "../../shared/services/ChatServices";
import ErrorsDisplay from "../../shared/components/ErrorsDisplay";

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

			<form onSubmit={handleSubmit} className="mx-auto p-4 border rounded shadow" style={{ maxWidth: "720px" }}>
				<ErrorsDisplay errorMessages={errorMessages} />

				<div className="form-outline">
					<label className="form-label" htmlFor="name">Name</label>
					<input type="text" id="name" className="form-control border" value={formState.name}
						onChange={e => setFormState(prevState => ({ ...prevState, name: e.target.value }))} />
				</div>

				<div className="form-outline">
					<label className="form-label" htmlFor="user-view">User view (optional)</label>
					<input type="text" id="user-view" className="form-control border" value={formState.userView}
						onChange={e => setFormState(prevState => ({ ...prevState, userView: e.target.value }))} />
				</div>

				<div className="text-center mt-3">
					<button type="submit" className="btn btn-primary" disabled={isSubmitting}>Submit</button>
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

		const errMsgs = await createNewChatAPI(
			formState.name, formState.userView, datasetId!
		)

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
