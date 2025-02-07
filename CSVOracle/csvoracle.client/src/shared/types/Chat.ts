export type Chat = {
	id: number;
	name: string;
	userView: string | null;
	messages: string[];
	currentDatasetKnowledgeJson: string;
};
