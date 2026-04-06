from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class FileImportState(BaseModel):
    file_path: str
    file_type: Optional[str] = None
    data: List[dict] = Field(default_factory=list)
    status: str = "pending"
    logs: List[str] = Field(default_factory=list)

class DetectFileTypeNode(Node[FileImportState]):
    def exec(self) -> None:
        self.state.logs.append(f"Detecting file type for {self.state.file_path}")
        if self.state.file_path.endswith(".csv"):
            self.state.file_type = "csv"
            self.result = "csv"
        elif self.state.file_path.endswith(".json"):
            self.state.file_type = "json"
            self.result = "json"
        elif self.state.file_path.endswith(".xml"):
            self.state.file_type = "xml"
            self.result = "xml"
        else:
            self.state.status = "error"
            self.state.logs.append("Unsupported file type")
            self.result = "unsupported"

class CSVParserNode(Node[FileImportState]):
    def exec(self) -> None:
        self.state.logs.append("Parsing CSV file")
        self.state.data = [{"row": 1, "content": "csv_data"}]
        self.state.status = "success"

class JSONParserNode(Node[FileImportState]):
    def exec(self) -> None:
        self.state.logs.append("Parsing JSON file")
        self.state.data = [{"id": 1, "content": "json_data"}]
        self.state.status = "success"

class XMLParserNode(Node[FileImportState]):
    def exec(self) -> None:
        self.state.logs.append("Parsing XML file")
        self.state.data = [{"tag": "root", "content": "xml_data"}]
        self.state.status = "success"

class FileImportFlow(StateFlow[FileImportState]):
    def setup_graph(self) -> None:
        self.add_node("detect", DetectFileTypeNode())
        self.add_node("csv_parser", CSVParserNode())
        self.add_node("json_parser", JSONParserNode())
        self.add_node("xml_parser", XMLParserNode())

        self.add_edge(START, "detect")
        self.add_conditional_edges("detect", {
            "csv": "csv_parser",
            "json": "json_parser",
            "xml": "xml_parser",
            "unsupported": END
        })
        self.add_edge("csv_parser", END)
        self.add_edge("json_parser", END)
        self.add_edge("xml_parser", END)

if __name__ == "__main__":
    flow = FileImportFlow()
    state = flow.run(FileImportState(file_path="data.json"))
    print(f"Status: {state.status}, Type: {state.file_type}, Logs: {state.logs}")
