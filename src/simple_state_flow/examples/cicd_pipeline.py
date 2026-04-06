from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class CICDState(BaseModel):
    branch: str
    test_result: str = "pass"
    deployment_status: str = "pending"
    logs: List[str] = Field(default_factory=list)

class RunTestsNode(Node[CICDState]):
    def exec(self) -> None:
        self.state.logs.append(f"Running tests for branch {self.state.branch}")
        self.result = self.state.test_result

class DeployToProdNode(Node[CICDState]):
    def exec(self) -> None:
        self.state.logs.append("All tests passed. Deploying to production...")
        self.state.deployment_status = "deployed_to_prod"

class NotifyDevNode(Node[CICDState]):
    def exec(self) -> None:
        self.state.logs.append("Unit tests failed. Notifying developer...")
        self.state.deployment_status = "failed_unit_tests"

class RollbackStagingNode(Node[CICDState]):
    def exec(self) -> None:
        self.state.logs.append("Integration tests failed. Rolling back staging...")
        self.state.deployment_status = "rolled_back_staging"

class CICDFlow(StateFlow[CICDState]):
    def setup_graph(self) -> None:
        self.add_node("run_tests", RunTestsNode())
        self.add_node("deploy", DeployToProdNode())
        self.add_node("notify", NotifyDevNode())
        self.add_node("rollback", RollbackStagingNode())

        self.add_edge(START, "run_tests")
        self.add_conditional_edges("run_tests", {
            "pass": "deploy",
            "fail_unit": "notify",
            "fail_integration": "rollback"
        })
        self.add_edge("deploy", END)
        self.add_edge("notify", END)
        self.add_edge("rollback", END)

if __name__ == "__main__":
    flow = CICDFlow()
    # Case: Integration failure
    state = flow.run(CICDState(branch="main", test_result="fail_integration"))
    print(f"Deployment Status: {state.deployment_status}, Last Log: {state.logs[-1]}")
