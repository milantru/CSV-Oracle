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
	const [showDataset, setShowDataset] = useState(false);

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
		<div className="d-flex" style={{ height: "100vh", width: "98vw" }}>
			<aside className="w-25">
				<div className="mb-2">
					<Link to="/datasets" className="btn btn-primary m-2">Back to datasets</Link>
					<Link to={`/chats/${datasetId}/new`} className="btn btn-primary m-2">New dataset chat</Link>
				</div>
				<div className="border overflow-auto" style={{height: "100vh"}}>
					{isLoadingChats ? (<div>Loading chats...</div>) : (
						<div>{datasetChats.map((chat, index) => (
							<button key={index} className="btn border w-100" onClick={() => selectChat(chat.id)}>{chat.name}</button>))}
						</div>
					)}
				</div>
			</aside>
			<div className="w-75">
				{selectedChat && (<>
					<div>
							<h1 className="m-3">{selectedChat.name}</h1>

							<div className="flex-grow-1 overflow-auto" style={{ maxHeight: "400px" }}>
								{selectedChat.messages.slice(1).map((message, index) => (
									<div key={index} className={`d-flex ${index % 2 ? 'justify-content-end' : 'justify-content-start'}`}>
										<div className={`border rounded m-2 p-2 w-75 ${index % 2 ? 'bg-secondary' : 'bg-light'}`}>
											{message}
										</div>
									</div>
								))}
							</div>

							<form onSubmit={handleSubmit} className="p-2 border-top bg-white">
								<div className="d-flex w-75 m-auto">
									<textarea className="form-control me-2" rows={3} placeholder="Type your message here..." value={newMessage}
										onChange={e => setNewMessage(e.target.value)}></textarea>

									<div className="d-flex align-items-center">
										<button type="submit" className="btn btn-primary" disabled={isSubmitting}>Send</button>
									</div>
								</div>
							</form>
					</div>
					<div className="position-relative">
						<div className={showDataset ? 'd-block' : 'd-none'}>
							{selectedChat.currentDatasetKnowledgeJson}
						</div>

						<button type="button" className="btn btn-secondary position-absolute end-0 mx-4" style={{ top: "-20px" }}
							onClick={() => setShowDataset(!showDataset)}>
							{showDataset ? "Hide Dataset" : "Show Dataset"}
						</button>
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
