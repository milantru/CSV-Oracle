import { DatasetFile } from "./DatasetFile";

export enum DatasetStatus {
	Created,
	Queued,
	Processing,
	Processed,
	Failed
};

export type Dataset = {
	id: number;
	status: DatasetStatus;
	separator: string | null; // char or null
	encoding: string | null;
	isSchemaProvided: boolean;
	datasetFiles: DatasetFile[];
};
