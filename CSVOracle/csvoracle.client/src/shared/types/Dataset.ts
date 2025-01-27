import { DatasetFile } from "./DatasetFile";

export enum DatasetStatus {
	Created,
	Queued,
	Processing,
	Processed
};

export type Dataset = {
	id: number;
	separator: string | null; // char or null
	encoding: string | null;
	additionalInfo: string | null;
	datasetFiles: DatasetFile[];
};
