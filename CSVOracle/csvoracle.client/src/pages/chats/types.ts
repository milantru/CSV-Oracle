export type CorrelationExplanation = {
    column1Name: string;
    column2Name: string;
    correlationValue: string;
    explanation: string;
};

export type ColumnKnowledge = {
    name: string;
    description: string;
    missingValuesExplanation: string;
};

export type Row = {
    values: string[];
};

export type TableKnowledge = {
    name: string;
    description: string;
    rowEntityDescription: string;
    sampleHead: Row[];
    sampleTail: Row[];
    columnKnowledges: ColumnKnowledge[];
    correlationExplanations: CorrelationExplanation[];
};

export type DatasetKnowledge = {
    description: string;
    tableKnowledges: TableKnowledge[];
};
