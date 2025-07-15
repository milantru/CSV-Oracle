import { useNavigate } from "react-router-dom";

type Props = {
	label?: string;
	toSpecificUrl?: string;
	classes?: string;
};

function ErrorsDisplay({ label = "Back", toSpecificUrl = undefined, classes = "" }: Props) {
	const navigate = useNavigate();

	return (
		<button onClick={navigateToPreviousPage} className={`btn btn-primary ${classes}`}>
			<i className="bi bi-arrow-left"></i> {label}
		</button>
	);

	function navigateToPreviousPage() {
		if (!toSpecificUrl) {
			navigate(-1);
		} else {
			navigate(toSpecificUrl);
		}
	}
}

export default ErrorsDisplay;
