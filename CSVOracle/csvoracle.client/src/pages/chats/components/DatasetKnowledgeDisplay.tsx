import { DatasetKnowledge } from "../types";
import TableKnowledgeDisplay from "./TableKnowledgeDisplay";
import { Tabs, TabList, Tab, TabPanel } from "react-tabs";
import 'react-tabs/style/react-tabs.css';

type Props = {
    datasetKnowledge: DatasetKnowledge;
};

function DatasetKnowledgeDisplay({ datasetKnowledge }: Props) {
    return (
        <div className="p-3">
            <h1 className="py-2">Current dataset knowledge</h1>

            <div className="py-2">
                <p><b>Dataset description:</b> {datasetKnowledge.description}</p>
            </div>

            <Tabs>
                <TabList>
                    {datasetKnowledge.tableKnowledges.map((tableKnowledge, idx) =>
                        <Tab key={idx}>{tableKnowledge.name}</Tab>)}
                </TabList>
                {datasetKnowledge.tableKnowledges.map((tableKnowledge, idx) =>
                    <TabPanel key={idx}><TableKnowledgeDisplay tableKnowledge={tableKnowledge} /></TabPanel>)}
            </Tabs>
        </div>
    );
}

export default DatasetKnowledgeDisplay;
