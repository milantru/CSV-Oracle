type Props = {
    errorMessages: string[];
};

function ErrorsDisplay({ errorMessages }: Props) {
	return (
		<div className={`border border-danger rounded mb-2 p-1 ${errorMessages.length > 0 ? "" : "d-none"}`}>
			<ul className="p-0 m-0" style={{ listStyleType: "none" }}>
				{errorMessages.map((message, index) => (
					<li key={index}><small>{message}</small></li>
				))}
			</ul>
		</div>
	);
}

export default ErrorsDisplay;
