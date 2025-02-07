import { useState, FormEvent, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import { createNewChatAPI } from "../../shared/services/ChatServices";

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
			<form onSubmit={handleSubmit}>
				<div>
					<ul>
						{errorMessages.map((errorMessage, index) => (
							<li key={index}>{errorMessage}</li>
						))}
					</ul>
				</div>

				<div>
					<input type="text" id="name" value={formState.name}
						onChange={e => setFormState(prevState => ({ ...prevState, name: e.target.value }))} />
					<label htmlFor="name">Name</label>
				</div>

				<div>
					<input type="text" id="user-view" value={formState.userView}
						onChange={e => setFormState(prevState => ({ ...prevState, userView: e.target.value }))} />
					<label htmlFor="user-view">User view</label>
				</div>

				<button type="submit" disabled={isSubmitting}>Submit</button>
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
