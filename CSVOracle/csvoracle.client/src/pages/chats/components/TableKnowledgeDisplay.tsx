import 'react-tabs/style/react-tabs.css';
import { ColumnKnowledge, CorrelationExplanation, TableKnowledge } from "../types";
import { useEffect, useState } from 'react';
import CorrelationExplanationDisplay from './CorrelationExplanationDisplay';

type Props = {
    tableKnowledge: TableKnowledge;
};

function TableKnowledgeDisplay({ tableKnowledge }: Props) {
    const columnColorWhenSelected = "#5b5b5b";
    const columnColorWhenHovered = "#777"; // This color is also used for highlighting columns correlated with the selected column
    // Max 2 columns can be selected
    const [selectedColumnIndices, setSelectedColumnIndices] = useState<number[]>([]);
    // When 2 columns are selected, the correlation explanation is selected
    const [selectedCorrelationExplanation, setSelectedCorrelationExplanation] = useState<CorrelationExplanation | null>(null);

    useEffect(() => {
        if (selectedColumnIndices.length < 2) {
            setSelectedCorrelationExplanation(null);
            return;
        }

        const col1Name = tableKnowledge.columnKnowledges[selectedColumnIndices[0]].name;
        const col2Name = tableKnowledge.columnKnowledges[selectedColumnIndices[1]].name;

        const corrExpl = tableKnowledge.correlationExplanations.find(x =>
            (x.column1Name === col1Name && x.column2Name === col2Name)
            || (x.column1Name === col2Name && x.column2Name === col1Name));
        if (!corrExpl) {
            // This should never happen, but defensive programming...
            return;
        }

        setSelectedCorrelationExplanation(corrExpl);
    }, [selectedColumnIndices]);

    return (
        <>
            <table className="table table-striped table-sm table-responsive">
                <thead className="thead-dark">
                    <tr>
                        {tableKnowledge.columnKnowledges.map((ck, idx) => (
                            <th key={idx}
                                title={getTableInfoString(ck)}
                                onClick={e => handleColumnSelection(e, idx)}
                                style={{
                                    transition: "background-color 0.2s ease",
                                    cursor: "pointer",
                                    boxShadow: isCorrelatedWithSelectedColumn(idx) ? `inset 0 0 4px 4px ${columnColorWhenHovered}` : ""
                                }}
                                onMouseEnter={e => handleOnMouseEnter(e, idx)}
                                onMouseLeave={e => handleOnMouseLeave(e, idx)}>
                                {ck.name}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody title={`Row entity: ${tableKnowledge.rowEntityDescription}`}>
                    {tableKnowledge.sampleHead.slice(0, 3).map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {row.values.map((value, colIndex) => (
                                <td key={colIndex}>{value}</td>
                            ))}
                        </tr>
                    ))}
                    <tr>
                        {tableKnowledge.columnKnowledges.map(ck => (
                            <td key={ck.name}>...</td>
                        ))}
                    </tr>
                    {tableKnowledge.sampleTail.slice(0, 3).map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {row.values.map((value, colIndex) => (
                                <td key={colIndex}>{value}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>

            <div className="pt-3">
                <p><b>Table description:</b> {tableKnowledge.description}</p>
            </div>

            <div>
                {selectedColumnIndices.length === 1 && (<small>Choose one more column to see correlation info.</small>)}
                {selectedColumnIndices.length === 2 && !selectedCorrelationExplanation && (<small>No correlation.</small>)}
                {selectedCorrelationExplanation &&
                    (<CorrelationExplanationDisplay correlationExplanation={selectedCorrelationExplanation} />)}
            </div>
        </>
    );

    function getTableInfoString(columnKnowledge: ColumnKnowledge) {
        let infoString = "";

        const description = columnKnowledge.description;
        infoString += description

        if (columnKnowledge.missingValuesExplanation) {
            infoString += "It seems this column has missing values. A possible reason is:\n";
            infoString += columnKnowledge.missingValuesExplanation;
        }

        return infoString;
    }

    function handleColumnSelection(event: React.MouseEvent<HTMLTableCellElement>, columnIndex: number): void {
        if (selectedColumnIndices.some(x => x === columnIndex)) {
            // Unselect column if already selected
            setSelectedColumnIndices(prevState => prevState.filter(idx => idx !== columnIndex));
            event.currentTarget.style.backgroundColor = "";
            return;
        }

        if (selectedColumnIndices.length === 2) {
            // If 2 already selected and trying to select third, do nothing
            return;
        }

        // Add to selected columns
        setSelectedColumnIndices(prevState => [...prevState, columnIndex]);
        event.currentTarget.style.backgroundColor = columnColorWhenSelected;
    }

    function handleOnMouseEnter(event: React.MouseEvent<HTMLTableCellElement>, columnIndex: number) {
        if (selectedColumnIndices.length === 2 || selectedColumnIndices.includes(columnIndex)) {
            return;
        }

        event.currentTarget.style.backgroundColor = columnColorWhenHovered;
    }

    function handleOnMouseLeave(event: React.MouseEvent<HTMLTableCellElement>, columnIndex: number) {
        if (selectedColumnIndices.length === 2 || selectedColumnIndices.includes(columnIndex)) {
            return;
        }

        event.currentTarget.style.backgroundColor = "";
    }

    function isCorrelatedWithSelectedColumn(columnKnowledgeIdx: number) {
        if (selectedColumnIndices.length !== 1) {
            return false;
        }

        const selectedColumnKnowledge = tableKnowledge.columnKnowledges[selectedColumnIndices[0]];
        const columnKnowledgeToTest = tableKnowledge.columnKnowledges[columnKnowledgeIdx];

        /* The column, even though it is correlated with itself, won't be found, therefore false will be returned,
         * but for our usecase it is OK. */
        const result = tableKnowledge.correlationExplanations.find(ce =>
            (ce.column1Name === selectedColumnKnowledge.name && ce.column2Name === columnKnowledgeToTest.name)
            || (ce.column1Name === columnKnowledgeToTest.name && ce.column2Name === selectedColumnKnowledge.name));

        return result !== undefined;
    }
}

export default TableKnowledgeDisplay;
