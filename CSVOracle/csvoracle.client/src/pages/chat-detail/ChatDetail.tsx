import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import BackButton from "../../shared/components/BackButton";
import ChatForm from "../../shared/components/ChatForm";
import { Chat } from "../../shared/types/Chat";
import { getChatAPI } from "../../shared/services/ChatServices";
import { toast } from "react-toastify/unstyled";

function ChatDetail() {
	const { datasetId, chatId } = useParams();
	const navigate = useNavigate();
	const [chat, setChat] = useState<Chat | null>(null);

	useEffect(() => {
		async function init() {
			const { chat: chatTmp, errorMessages } = await getChatAPI(Number(chatId));
			if (errorMessages.length > 0) {
				for (const errMsg of errorMessages) {
					toast.warn(errMsg);
				}
				return;
			}

			setChat(chatTmp);
		}

		if (!isNumber(chatId) || !isNumber(datasetId) || datasetId === "0") {
			navigate("/not-found");
			return;
		}

		init();
	}, [])

	return (
		<>
			<h1 className="text-center py-4">Chat detail</h1>
			<div className="position-absolute top-0 start-0 m-3">
				<BackButton label="Back to chats" />
			</div>

			{chat && datasetId && (
				<ChatForm datasetId={Number(datasetId)} existingChat={chat} />
			)}
		</>
	);
}

export default ChatDetail;
