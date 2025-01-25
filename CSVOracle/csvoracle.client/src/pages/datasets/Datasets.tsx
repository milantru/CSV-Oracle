import { useEffect, useState } from "react";
import { Dataset } from "../../shared/types/Dataset";
import { getUserDatasetsAPI } from "../../shared/services/DatasetServices";
import { toast } from "react-toastify";
import { Link } from "react-router-dom";

function Datasets() {
	const [datasets, setDatasets] = useState<Dataset[]>([]);

	useEffect(() => {
		async function fetchData() {
			const { userDatasets, errorMessages } = await getUserDatasetsAPI()
			if (errorMessages.length > 0) {
				for (let i = 0; i < errorMessages.length; i++) {
					toast.warning(errorMessages[i]);
				}

				return;
			}

			setDatasets(userDatasets);
		}

		fetchData();
	}, []);

	return (
		<>
			<h1>Datasets</h1>

			<small>The dataset means the set of uploaded files (1 or more), not just one uploaded file.</small>
			<h2>Select dataset...</h2>

			<div>
				<div>
					<ul>
						{datasets.map((dataset, index) => (
							<li key={index}>Dataset with id {dataset.id}</li>
						))}
					</ul>
				</div>
				<div>
					<div>
						TODO: Dataset info
					</div>
				</div>
				<div>
					<Link to="/datasets/new">Add new dataset</Link>
				</div>
			</div>
		</>
	);
}

export default Datasets;
