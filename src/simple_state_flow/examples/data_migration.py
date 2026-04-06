from typing import List
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class MigrationState(BaseModel):
    source_count: int
    has_existing_data: bool = False
    migrated_count: int = 0
    status: str = "pending"
    logs: List[str] = Field(default_factory=list)

class CheckExistingDataNode(Node[MigrationState]):
    def exec(self) -> None:
        self.state.logs.append("Checking destination for existing data")
        if self.state.has_existing_data:
            self.result = "exists"
        else:
            self.result = "empty"

class MergeRecordsNode(Node[MigrationState]):
    def exec(self) -> None:
        self.state.logs.append("Merging records into existing data")
        self.state.migrated_count = self.state.source_count
        self.state.status = "merged"

class BulkInsertNode(Node[MigrationState]):
    def exec(self) -> None:
        self.state.logs.append("Performing bulk insert into empty destination")
        self.state.migrated_count = self.state.source_count
        self.state.status = "inserted"

class DataMigrationFlow(StateFlow[MigrationState]):
    def setup_graph(self) -> None:
        self.add_node("check", CheckExistingDataNode())
        self.add_node("merge", MergeRecordsNode())
        self.add_node("bulk_insert", BulkInsertNode())

        self.add_edge(START, "check")
        self.add_conditional_edges("check", {
            "exists": "merge",
            "empty": "bulk_insert"
        })
        self.add_edge("merge", END)
        self.add_edge("bulk_insert", END)

if __name__ == "__main__":
    flow = DataMigrationFlow()
    # Case 1: Empty destination
    state1 = flow.run(MigrationState(source_count=100, has_existing_data=False))
    print(f"Migration 1: {state1.status}, Count: {state1.migrated_count}")
    
    # Case 2: Existing data
    state2 = flow.run(MigrationState(source_count=50, has_existing_data=True))
    print(f"Migration 2: {state2.status}, Count: {state2.migrated_count}")
