import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getDatasetKnowledgeAPI } from "../../shared/services/ChatServices";
import { toast } from "react-toastify";
import { isNumber } from "../../shared/helperFunctions/TypeChecker";
import DatasetKnowledgeDisplay from "../chats/components/DatasetKnowledgeDisplay";
import { DatasetKnowledge as DatasetKnowledgeType } from "../chats/types";

function DatasetKnowledge() {
    const { chatId } = useParams();
    const navigate = useNavigate();
    const [datasetKnowledge, setDatasetKnowledge] = useState<DatasetKnowledgeType | null>(null);

    useEffect(() => {
        async function loadChat(chatId: number) {
            const { datasetKnowledge: datasetKnowledgeTmp, errorMessages } = await getDatasetKnowledgeAPI(chatId);
            if (errorMessages.length > 0) {
                for (let i = 0; i < errorMessages.length; i++) {
                    toast.warn(errorMessages[i]);
                }
                return;
            }

            setDatasetKnowledge(datasetKnowledgeTmp);
        }

        if (isNumber(chatId)) {
            loadChat(parseInt(chatId!));
        } else {
            navigate("/not-found");
        }
    }, []);

    return (<>
        {datasetKnowledge && (
            <DatasetKnowledgeDisplay datasetKnowledge={datasetKnowledge} />
        )}
    </>);
}

export default DatasetKnowledge;
