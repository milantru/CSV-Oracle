import { useEffect, useState } from "react";
import { Dataset, DatasetStatus } from "../../shared/types/Dataset";
import { getUserDatasetsAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";
import { Link } from "react-router-dom";
import DatasetItem from "./components/DatasetItem";
import { useInterval } from "../../shared/hooks/useInterval";
import { FadeLoader } from "react-spinners";

function Datasets() {
	const [datasets, setDatasets] = useState<Dataset[]>([]);
	const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
	const [isLoadingDatasets, setIsLoadingDatasets] = useState<boolean>(false);
	const tips = [
		"The dataset means the set of uploaded files (1 or more), not just one uploaded file.",
		"Processing a dataset may take longer."
	];
	const [currentTipIndex, setCurrentTipIndex] = useState<number>(0);

	useEffect(() => {
		async function fetchData() {
			setIsLoadingDatasets(true);
			const { userDatasets, errorMessages } = await getUserDatasetsAPI()
			if (errorMessages.length > 0) {
				for (let i = 0; i < errorMessages.length; i++) {
					toast.warning(errorMessages[i]);
				}

				setIsLoadingDatasets(false);
				return;
			}

			setDatasets(userDatasets);
			setIsLoadingDatasets(false);
		}

		fetchData();
	}, []);

	useInterval(() => {
		const newTipIndex = (currentTipIndex + 1) % tips.length;
		setCurrentTipIndex(newTipIndex);
	}, 3000);

	return (
		<div className="w-75 mx-auto pt-3">
			<h1>Datasets</h1>

			<small className="border border-dark rounded py-1 px-2 my-3 d-block">
				<i className="bi bi-exclamation-circle"></i> {`(${currentTipIndex + 1}/${tips.length}) ${tips[currentTipIndex]}`}
			</small>

			<div>
				<div>
					<h4 className="my-3">Select dataset...</h4>
					<div className="d-flex w-90">
						<div className="d-flex flex-wrap overflow-auto border p-1" style={{ width: "100%", maxHeight: "15em" }}>
							{isLoadingDatasets ? (<div className="d-flex align-items-center p-4"><FadeLoader /></div>) : (<>
								{datasets.map((dataset, index) => (
									<DatasetItem key={index} dataset={dataset} onSelect={selectDataset}
										onStatusUpdate={status => updateDatasetStatus(dataset.id, status)} />
								))}
							</>)}
						</div>
						<div className="w-10 ml-auto">
							<Link to="/datasets/new" className="btn border rounded mx-4">
								<i className="bi bi-database-add fs-1 d-block"></i> Add new dataset
							</Link>
						</div>
					</div>
				</div>
				<div className="my-3">
					{selectedDataset === null ? (<div>No dataset selected</div>) : (
						<div className="border rounded p-3">
							Additional info: {selectedDataset.additionalInfo}<br />
							Encoding: {selectedDataset.encoding}<br />
							Separator: {selectedDataset.separator}<br />
							Dataset files:<br />
							<ul>{selectedDataset.datasetFiles.map((datasetFile, index) =>
								(<li key={index}>{datasetFile.name}</li>))}
							</ul>

							{selectedDataset.status == DatasetStatus.Processed &&
								<Link to={`/chats/${selectedDataset.id}`}>
									<span className="d-block w-50 mx-auto btn btn-success py-2">Choose dataset</span>
								</Link>
							}
						</div>
					)}
				</div>
			</div>
		</div>
	);

	function selectDataset(datasetId: number) {
		const dataset = datasets.find(d => d.id == datasetId);
		if (dataset) {
			setSelectedDataset(dataset);
		}
	}

	function updateDatasetStatus(datasetId: number, newStatus: DatasetStatus): void {
		setDatasets(prevState =>
			prevState.map(dataset =>
				dataset.id === datasetId ? { ...dataset, status: newStatus } : dataset
			)
		);

		if (selectedDataset?.id === datasetId) {
			setSelectedDataset({ ...selectedDataset, status: newStatus });
		}
	}
}

export default Datasets;
