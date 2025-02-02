import { useEffect, useState } from "react";
import { Dataset } from "../../shared/types/Dataset";
import { getUserDatasetsAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";
import { Link } from "react-router-dom";
import DatasetItem from "./components/DatasetItem";

function Datasets() {
	const [datasets, setDatasets] = useState<Dataset[]>([]);
	const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
	const [isLoadingDatasets, setIsLoadingDatasets] = useState<boolean>(false);

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

	return (
		<>
			<h1>Datasets</h1>

			<small>The dataset means the set of uploaded files (1 or more), not just one uploaded file.</small>

			<div>
				<div>
					{isLoadingDatasets ? (<span>Loading datasets...</span>) : (
						<label>
							Select dataset...
							<select onChange={e => selectDataset(parseInt(e.target.value))}>
								{datasets.map((dataset, index) => (
									<option key={index} value={dataset.id}>
										<DatasetItem dataset={dataset} />
									</option>
								))}
							</select>
						</label>
					)}
				</div>
				<div>
					{selectedDataset === null ? (<div>No dataset is selected</div>) : (
						<div>
							Additional info: {selectedDataset.additionalInfo}<br />
							Encoding: {selectedDataset.encoding}<br />
							Separator: {selectedDataset.separator}<br />
							Dataset files:<br />
							<ul>{selectedDataset.datasetFiles.map((datasetFile, index) =>
								(<li key={index}>{datasetFile.name}</li>))}
							</ul>
							<Link to={`/chats/${selectedDataset.id}`}>Choose dataset</Link>
						</div>
					)}
				</div>
				<div>
					<Link to="/datasets/new">Add new dataset</Link>
				</div>
			</div>
		</>
	);

	function selectDataset(datasetId: number) {
		const dataset = datasets.find(d => d.id == datasetId);
		if (dataset) {
			setSelectedDataset(dataset);
		}
	}
}

export default Datasets;
