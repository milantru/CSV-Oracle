import { useState, useEffect } from "react";

type Props = {
	datasetKnowledgeJson: string;
};

type CorrelationExplanation = {
    column1Name: string;
    column2Name: string;
    correlationValue: string;
    explanation: string;
};

type ColumnKnowledge = {
    name: string;
    description: string;
    missingValuesExplanation: string;
    correlationExplanations: CorrelationExplanation[];
};

type TableKnowledge = {
    name: string;
    description: string;
    rowEntityDescription: string;
    columnKnowledges: ColumnKnowledge[];
};

type DatasetKnowledge = {
    description: string;
    tableKnowledges: TableKnowledge[];
};

function DatasetKnowledgeDisplay({ datasetKnowledgeJson }: Props) {
    const [datasetKnowledge, setDatasetKnowledge] = useState<DatasetKnowledge | null>(null);

    useEffect(() => {
        try {
            const parsedDatasetKnowledge: DatasetKnowledge = JSON.parse(datasetKnowledgeJson);
            setDatasetKnowledge(parsedDatasetKnowledge);
        } catch {
            setDatasetKnowledge(null);
        }
    }, [datasetKnowledgeJson]);

    if (!datasetKnowledge) { // This should never happen, but defensive programming...
        return <div>Error: Invalid dataset knowledge JSON.</div>;
    }

    return (
        <div>
            <h1>Current dataset knowledge</h1>

            <h2>Dataset description</h2>
            <p>{datasetKnowledge.description}</p>

            {datasetKnowledge.tableKnowledges.map(tableKnowledge => (<>
                <h2>{tableKnowledge.name}</h2>

                <p>{tableKnowledge.description}</p><br />
                {tableKnowledge.rowEntityDescription &&
                    (<><b>Row entity: </b><p>{tableKnowledge.rowEntityDescription}</p></>)}
                {tableKnowledge.columnKnowledges.map(columnKnowledge => (<>
                    <h3>{columnKnowledge.name}</h3>

                    <p>{columnKnowledge.description}</p><br />
                    {columnKnowledge.missingValuesExplanation &&
                        (<><b>Explanation why are the values missing: </b><p>{columnKnowledge.missingValuesExplanation}</p></>)}
                    {columnKnowledge.correlationExplanations.map(correlationExplanation => (<>
                        <h4>{correlationExplanation.column1Name} X {correlationExplanation.column2Name} (corr. value: {correlationExplanation.correlationValue})</h4>

                        {correlationExplanation.explanation ?
                            (<><b>Correlation explanation: </b><p>{correlationExplanation.explanation}</p></>)
                            : (<>-</>)
                        }
                    </>))}
                </>))}
            </>))}
            
        </div>
    );
}

export default DatasetKnowledgeDisplay;
