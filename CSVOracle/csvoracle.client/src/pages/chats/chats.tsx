import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Chat } from "../../shared/types/Chat";
import { deleteChatAPI, generateAnswerAPI, getDatasetChatsAPI } from "../../shared/services/ChatServices";
import { toast } from "react-toastify";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import { PropagateLoader, SyncLoader } from "react-spinners";
import DatasetKnowledgeDisplay from "./components/DatasetKnowledgeDisplay";
import { DatasetKnowledge } from "./types";

function Chats() {
	const { datasetId } = useParams();
	const navigate = useNavigate();
	const [datasetChats, setDatasetChats] = useState<Chat[]>([]);
	const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
	const [isLoadingChats, setIsLoadingChats] = useState<boolean>(false);
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
	const [newMessage, setNewMessage] = useState<string>("");
	const [showDataset, setShowDataset] = useState(false);
	const chatMessages = useRef<HTMLDivElement | null>(null);

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

	useEffect(() => {
		scrollChatMessagesToBottom();
	}, [selectedChat?.messages]);

	return (
		<div className="d-flex position-relative" style={{ width: "100vw", height: "100vh" }}>
			{/* Side bar with chats and buttons */}
			<aside className="w-25 position-absolute d-flex flex-column border" style={{ height: "100%" }}>
				<div className="text-center">
					<Link to="/datasets" className="btn btn-primary my-2 mr-2">Back to datasets</Link>
					<Link to={`/chats/${datasetId}/new`} className="btn btn-primary my-2">New dataset chat</Link>
				</div>
				<div className="overflow-auto border border-top" style={{ flexGrow: 1 }}>
					{isLoadingChats ? (
						<div className="d-flex justify-content-center align-items-center" style={{ height: "32px" }}>
							<PropagateLoader />
						</div>
					) : (
						<div>{datasetChats.map((chat, index) => (
							<button key={index}
								className="btn border-bottom rounded-0 w-100 position-relative"
								style={{
									borderRadius: "",
									boxShadow: "none",
									backgroundColor: chat.id === selectedChat?.id ? "#cecece" : ""
								}}
								onClick={() => selectChat(chat.id)}>
								<span>{chat.name}</span>
								<span
									className="position-absolute text-danger"
									style={{
										cursor: "pointer",
										zIndex: 1,
										fontSize: "1.75rem",
										top: "50%",
										right: "1rem",
										transform: "translateY(-50%)", // vertically center
									}}
									onClick={e => {
										e.stopPropagation(); // prevent triggering button's onClick
										deleteChat(chat.id);
									}}>
									&times;
								</span>
							</button>))}
						</div>
					)}
				</div>
			</aside>
			<div className="w-75 position-absolute end-0 d-flex flex-column" style={{ height: "100%" }}>
				{selectedChat && (<>
					{/* Chat window */}
					<h1 className="m-3 d-block">{selectedChat.name}</h1>

					<div className="position-absolute" style={{ top: "75px", right: "0", bottom: "0", left: "0" }}>
						<div className="position-relative d-flex flex-column" style={{ height: showDataset ? "50%" : "100%" }}>
							{/* Chat messages */}
							<div ref={chatMessages} className="overflow-auto">
								{selectedChat.messages.map((message, index) => (
									<div key={index} className={`d-flex ${index % 2 ? "justify-content-end" : "justify-content-start"}`}>
										<div className={`border rounded m-2 p-2 w-75 ${index % 2 ? "bg-secondary" : "bg-light"}`}>
											{message === "..." ? <SyncLoader size={4} speedMultiplier={0.5} /> : message}
										</div>
									</div>
								))}
							</div>

							{/* Message input */}
							<form onSubmit={handleSubmit} className="p-2 border-top bg-white mt-auto">
								<div className="d-flex w-75 m-auto">
									<div className="d-flex align-items-center">
										<button
											type="button"
											className="rounded-circle border border-dark px-2"
											style={{ fontSize: "20px" }}
											title={`${showDataset ? "Hide" : "Show"} current dataset knowledge`}
											onClick={() => setShowDataset(!showDataset)}>
											{showDataset
												? <i className="bi bi-eye-slash"></i>
												: <i className="bi bi-eye"></i>}
										</button>
									</div>

									<textarea
										className="form-control mx-2"
										rows={3}
										placeholder="Type your message here..."
										value={newMessage}
										onChange={e => setNewMessage(e.target.value)}></textarea>

									<div className="d-flex align-items-center">
										<button type="submit" className="btn btn-primary" disabled={isSubmitting}>Send</button>
									</div>
								</div>
							</form>
						</div>

						{/* Dataset knowledge */}
						{showDataset && (
							<div className="overflow-auto h-50 position-relative border-top">
								<DatasetKnowledgeDisplay datasetKnowledge={parseDatasetKnowledge(selectedChat.currentDatasetKnowledgeJson)} />
								<Link
									className="position-absolute rounded-circle border border-dark text-black px-2"
									style={{ top: "20px", right: "24px", fontSize: "20px" }}
									title="Open dataset knowledge in a new separate tab"
									to={`/dataset-knowledge/${selectedChat.id}`}
									target="_blank"
									rel="noopener noreferrer">
									<i className="bi bi-arrows-fullscreen"></i>
								</Link>
							</div>
						)}
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

	async function deleteChat(chatId: number) {
		const { errorMessages: errMsgs } = await deleteChatAPI(chatId);
		if (errMsgs.length > 0) {
			for (const errMsg of errMsgs) {
				toast.warn(errMsg);
			}
			return;
		}

		setDatasetChats(prevState => prevState.filter(c => c.id !== chatId));

		if (selectedChat?.id === chatId) {
			setSelectedChat(null);
		}
	}

	function updateChats(updatedChat: Chat): void {
		setDatasetChats(prevState =>
			prevState.map(chat =>
				chat.id === updatedChat.id ? updatedChat : chat
			)
		);
	}

	async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
		e.preventDefault();

		if (!selectedChat) {
			return;
		}

		setIsSubmitting(true);

		/* We store the new message to the temporary variable and resetting newMessage state
		 * because we want the textarea to be empty while generating answer. But at the same time we also want to display
		 * newMessage and "..." to show that the message was sent and to simulate that the chat is typing.. */
		const tmp = newMessage;
		setNewMessage("");
		const newMessages = [...selectedChat.messages, tmp, "..."];
		setSelectedChat({ ...selectedChat, messages: newMessages });
		const { chat, errorMessages } = await generateAnswerAPI(tmp, selectedChat.id);
		if (errorMessages.length > 0) {
			for (let i = 0; i < errorMessages.length; i++) {
				toast.warn(errorMessages[i]);
			}
			setNewMessage("");
			setSelectedChat({
				...selectedChat,
				/* Remove the last 2 messages both to show the original message failed 
				 * and also to imitate that the assistant is not typing anymore */
				messages: newMessages.slice(0, -2)
			});
			setIsSubmitting(false);
			return;
		}

		setNewMessage("");
		updateChats(chat!);
		setSelectedChat(chat);
		setIsSubmitting(false);
	}

	function scrollChatMessagesToBottom() {
		if (chatMessages.current) {
			chatMessages.current.scrollTo({
				top: chatMessages.current.scrollHeight,
				behavior: "instant"
			});
		}
	}

	function parseDatasetKnowledge(datasetKnowledgeJson: string) {
		const parsedDatasetKnowledge: DatasetKnowledge = JSON.parse(datasetKnowledgeJson);
		return parsedDatasetKnowledge;
	}
}

export default Chats;
