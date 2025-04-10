import { toast } from "react-toastify";
import { deleteDatasetAPI, getUserDatasetStatusAPI } from "../../../shared/services/DatasetServices";
import { Dataset, DatasetStatus } from "../../../shared/types/Dataset";
import { useEffect, useState } from "react";
import { useVisibilityChange } from "../../../shared/hooks/useVisibilityChange";
import { useInterval } from "../../../shared/hooks/useInterval";
import 'bootstrap-icons/font/bootstrap-icons.css';
import { BeatLoader } from "react-spinners";
import { toastError } from "../../../shared/helperFunctions/ErrorHandler";

const POLLING_INTERVAL = 1000 * 2; // every 2 seconds

type Props = {
	dataset: Dataset;
	isSelected: boolean;
	onSelect: (datasetId: number) => void;
	onStatusUpdate: (status: DatasetStatus) => void;
	onDelete: (datasetId: number) => void;
};

function DatasetItem({ dataset, isSelected, onSelect, onStatusUpdate, onDelete }: Props) {
	const [pollingInterval, setPollingInterval] = useState<number | null>(POLLING_INTERVAL);
	const isPageVisible = useVisibilityChange();
	const [isPollingDisabled, setIsPollingDisabled] = useState<boolean>(dataset.status === DatasetStatus.Processed);
	const [isFetching, setIsFetching] = useState<boolean>(false);

	useEffect(() => {
		if (isPageVisible && !isPollingDisabled) {
			setPollingInterval(POLLING_INTERVAL);
		} else {
			setPollingInterval(null);
		}
	}, [isPageVisible, isPollingDisabled]);

	useInterval(() => {
		async function fetchData() {
			setIsFetching(true);
			const status = await getDatasetStatus(dataset.id);
			if (status === null) {
				setIsPollingDisabled(true);
				return;
			}

			if (status == DatasetStatus.Processed) {
				// Dataset is processed, its state won't change, so polling is not required anymore
				setIsPollingDisabled(true);
			}

			if (status !== dataset.status) {
				onStatusUpdate(status);
			}
			setIsFetching(false);
		}

		if (isFetching) {
			return;
		}
		fetchData();
	}, pollingInterval);

	return (
		<button
			type="button"
			className={`text-center m-2 px-4 py-3 border rounded-circle d-flex flex-column
				align-items-center justify-content-end position-relative ${isSelected ? "border-primary bg-light" : ""}`}
			style={{
				backgroundColor: "transparent",
				border: "1px solid #ccc",
				padding: "1rem",
				cursor: "pointer",
				transition: "all 0.15s ease-in-out",
				overflow: "visible",
				boxShadow: "none",
				outline: "none"
			}}
			title={getDatasetStatusLabel(dataset.status)}
			onClick={() => onSelect(dataset.id)}>
			<span
				className="position-absolute translate-middle badge rounded-pill bg-danger"
				style={{ cursor: "pointer", zIndex: 1, top: 15, right: -12, fontSize: "1rem" }}
				onClick={(e) => {
					e.stopPropagation(); // prevent triggering onSelect
					deleteDataset(dataset.id);
				}}>
				&times;
			</span>
			<div className="d-flex flex-column align-items-center">
				{getStatusIcon(dataset.status)}
				<small>Dataset #{dataset.id}</small>
			</div>
		</button>
	);

	async function getDatasetStatus(datasetId: number) {
		const { status, errorMessages: errMsgs } = await getUserDatasetStatusAPI(datasetId)
		if (errMsgs.length > 0) {
			for (let i = 0; i < errMsgs.length; i++) {
				toast.warning(errMsgs[i]);
			}
			return null;
		}

		return status!;
	}

	function getDatasetStatusLabel(status: DatasetStatus) {
		let statusLabel;

		switch (status) {
			case DatasetStatus.Created: {
				//statusMessage = "Created";
				statusLabel = DatasetStatus[DatasetStatus.Created];
				break;
			}
			case DatasetStatus.Queued: {
				//statusMessage = "Queued";
				statusLabel = DatasetStatus[DatasetStatus.Queued];
				break;
			}
			case DatasetStatus.Processing: {
				//statusMessage = "Processing";
				statusLabel = DatasetStatus[DatasetStatus.Processing];
				break;
			}
			case DatasetStatus.Processed: {
				//statusMessage = "Processed";
				statusLabel = DatasetStatus[DatasetStatus.Processed];
				break;
			}
			default: {
				throw new Error("Unknown status");
			}
		}

		return statusLabel;
	}

	function getStatusIcon(datasetStatus: DatasetStatus) {
		switch (datasetStatus) {
			case DatasetStatus.Created:
			case DatasetStatus.Queued:
			case DatasetStatus.Processing:
				return <BeatLoader className="pb-2 py-4" />;
			case DatasetStatus.Processed:
				return <i className="bi bi-database fs-1 d-block"></i>;
			default:
				throw new Error("Unknown dataset status.");
		}
	}

	async function deleteDataset(datasetId: number) {
		const { errorMessages } = await deleteDatasetAPI(datasetId);
		if (errorMessages.length > 0) {
			for (const errMsg of errorMessages) {
				toastError(errMsg);
			}
			return;
		}

		onDelete(datasetId);
	}
}

export default DatasetItem;
