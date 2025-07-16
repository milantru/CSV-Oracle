import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ClipLoader } from "react-spinners";
import { createNewChatAPI, updateChatAPI } from "../services/ChatServices";
import ErrorsDisplay from "./ErrorsDisplay";
import { Chat } from "../types/Chat";

type ChatFormProps = {
	datasetId: number;
	existingChat?: Chat;
};

function ChatForm({ datasetId, existingChat = undefined }: ChatFormProps) {
	const [chatState, setChatState] = useState<Chat>(!existingChat
		? createEmptyChat()
		: { ...existingChat, userView: existingChat.userView ?? "" }
	);
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
	const [errorMessages, setErrorMessages] = useState<string[]>([]);
	const navigate = useNavigate();

	return (
		<form onSubmit={handleSubmit} className="mx-auto p-4 border rounded shadow" style={{ maxWidth: "720px" }}>
			<ErrorsDisplay errorMessages={errorMessages} />

			<div className="form-outline mb-2">
				<label className="form-label" htmlFor="name">Name</label>
				<input type="text" id="name" className="form-control border" value={chatState.name}
					onChange={e => setChatState(prevState => ({ ...prevState, name: e.target.value }))} />
			</div>

			{chatState.id !== 0 ? (
				<div>
					User view: {chatState.userView?.length ? chatState.userView : <em>Not provided</em>}
				</div>
			) : (
				<div className="form-outline">
					<label className="form-label" htmlFor="user-view">
						User view (optional) <i className="bi bi-question-circle align-middle"
							title="Description of how the user views or intends to use the data. This can help the assistant provide more relevant responses."></i>
					</label>
					<input type="text" id="user-view" className="form-control border" value={chatState.userView!}
						onChange={e => setChatState(prevState => ({ ...prevState, userView: e.target.value }))} />
				</div>
			)}

			<div className="text-center mt-3">
				{/* Min width and min height is set here so the button does not change its size when switching between text and animation. */}
				<button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ minWidth: "94px", minHeight: "39px" }}>
					{isSubmitting ? <ClipLoader size="15px" color="#fff" /> : "Submit"}
				</button>

				{chatState.id === 0 && chatState.userView && (
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
	);

	function createEmptyChat() {
		const newChat: Chat = {
			id: 0,
			name: "",
			userView: "",
			messages: [],
			currentDatasetKnowledgeJson: ""
		};

		return newChat
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		setIsSubmitting(true);

		const errMsgs = chatState.id === 0
			? await createNewChatAPI(chatState.name, chatState.userView!, datasetId)
			: await updateChatAPI(chatState);

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

export default ChatForm;
