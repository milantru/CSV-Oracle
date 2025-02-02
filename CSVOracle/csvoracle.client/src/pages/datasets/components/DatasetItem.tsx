import { toast } from "react-toastify";
import { getUserDatasetStatusAPI } from "../../../shared/services/DatasetServices";
import { Dataset, DatasetStatus } from "../../../shared/types/Dataset";
import { useEffect, useState } from "react";
import { useVisibilityChange } from "../../../shared/hooks/useVisibilityChange";
import { useInterval } from "../../../shared/hooks/useInterval";

const POLLING_INTERVAL = 1000 * 5; // every 5 seconds

type Props = {
	dataset: Dataset;
};

function DatasetItem({ dataset }: Props) {
	const [datasetStatus, setDatasetStatus] = useState<DatasetStatus | null>(null);
	const [pollingInterval, setPollingInterval] = useState<number | null>(POLLING_INTERVAL);
	const isPageVisible = useVisibilityChange();
	const [isPollingDisabled, setIsPollingDisabled] = useState<boolean>(false);
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
			setDatasetStatus(status);
			setIsFetching(false);
		}

		if (isFetching) {
			return;
		}
		fetchData();
	}, pollingInterval);

	return (
		<li key={dataset.id}>Dataset with id {dataset.id} ({datasetStatus !== null ? getDatasetStatusLabel(datasetStatus) : "-"})</li>
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
}

export default DatasetItem;
