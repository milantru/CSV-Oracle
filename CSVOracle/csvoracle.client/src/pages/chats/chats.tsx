import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chat } from "../../shared/types/Chat";
import { generateAnswerAPI, getDatasetChatsAPI } from "../../shared/services/ChatServices";
import { toast } from "react-toastify";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";

function Chats() {
	const { datasetId } = useParams();
	const navigate = useNavigate();
	const [datasetChats, setDatasetChats] = useState<Chat[]>([]);
	const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
	const [isLoadingChats, setIsLoadingChats] = useState<boolean>(false);
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
	const [newMessage, setNewMessage] = useState<string>("");

	useEffect(() => {
		async function loadChats(datasetId: number) {
			setIsLoadingChats(true);
			const { chats, errorMessages } = await getDatasetChatsAPI(datasetId);
			if (errorMessages.length > 0) {
				for (let i = 0; i < errorMessages.length; i++) {
					toast.warn(errorMessages[i]);
				}
				setIsLoadingChats(false);
				return;
			}

			setDatasetChats(chats);
			setIsLoadingChats(false);
		}

		if (isNumber(datasetId)) {
			loadChats(parseInt(datasetId!));
		} else {
			navigate("/not-found");
		}
	}, []);

	return (
		<div>
			<aside>
				<div>
					<Link to="/datasets">Back to datasets</Link>
					<Link to={`/chats/${datasetId}/new`}>New dataset chat</Link>
				</div>
				<div>
					{isLoadingChats ? (<div>Loading chats...</div>) : (
						<div>{datasetChats.map((chat, index) => (
							<button key={index} onClick={() => selectChat(chat.id)}>{chat.name}</button>))}
						</div>
					)}
				</div>
			</aside>
			<div>
				{selectedChat && (<>
					<h1>{selectedChat.name}</h1>

					<ul>{selectedChat.messages.map((message, index) => (
						<li key={index}>{message}</li>
					))}
					</ul>

					<form onSubmit={handleSubmit}>
						<div>
							<input type="text" id="new-message" value={newMessage}
								onChange={e => setNewMessage(e.target.value)} />
							<label htmlFor="new-message">New message</label>
						</div>

						<button type="submit" disabled={isSubmitting}>Send</button>
					</form>

					<div>
						{selectedChat.currentDatasetKnowledgeJson}
					</div>
				</>)}
			</div>
		</div>
	);

	function selectChat(chatId: number) {
		const chat = datasetChats.find(c => c.id === chatId);
		if (chat) {
			setSelectedChat(chat);
		}
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		if (!selectedChat) {
			return;
		}
		
		setIsSubmitting(true);

		const { chat, errorMessages } = await generateAnswerAPI(newMessage, selectedChat.id);
		if (errorMessages.length > 0) {
			for (let i = 0; i < errorMessages.length; i++) {
				toast.warn(errorMessages[i]);
			}
			setNewMessage("");
			setIsSubmitting(false);
			return;
		}


		setNewMessage("");
		const updateChats = (chats: Chat[], chat: Chat) => {
			const updatedChats: Chat[] = [];

			for (let i = 0; i < chats.length; i++) {
				if (chats[i].id !== chat.id) {
					updatedChats.push(chats[i])
				} else {
					updatedChats.push(chat)
				}
			}

			return updatedChats;
		}
		setDatasetChats(prevState => updateChats(prevState, chat!));
		setSelectedChat(chat);
		setIsSubmitting(false);
	}
}

export default Chats;
