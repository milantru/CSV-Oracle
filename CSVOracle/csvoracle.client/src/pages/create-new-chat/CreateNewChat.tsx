import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import BackButton from "../../shared/components/BackButton";
import ChatForm from "../../shared/components/ChatForm";

function CreateNewChat() {
	const { datasetId } = useParams();
	const navigate = useNavigate();

	useEffect(() => {
		if (!isNumber(datasetId) || datasetId === "0") {
			navigate("/not-found");
		}
	}, [])

	return (
		<>
			<h1 className="text-center py-4">Create new chat</h1>
			<div className="position-absolute top-0 start-0 m-3">
				<BackButton label="Back to chats" />
			</div>

			{datasetId && (
				<ChatForm datasetId={Number(datasetId)} />
			)}
		</>
	);
}

export default CreateNewChat;
