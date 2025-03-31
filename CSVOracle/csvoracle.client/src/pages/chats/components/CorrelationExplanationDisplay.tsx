import { CorrelationExplanation } from "../types";

type Props = {
    correlationExplanation: CorrelationExplanation;
};

function CorrelationExplanationDisplay({ correlationExplanation }: Props) {
    return (
        <>
            <div>
                <p><b>Correlation value: </b>{correlationExplanation.correlationValue}</p>
            </div>

            <div>
                <p><b>Correlation explanation: </b>{correlationExplanation.explanation}</p>
            </div>
        </>
    );
}

export default CorrelationExplanationDisplay;
