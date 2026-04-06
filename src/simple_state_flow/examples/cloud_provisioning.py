from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class CloudState(BaseModel):
    instance_type: str
    region: str
    status: str = "pending"
    instance_id: Optional[str] = None
    quota_exceeded: bool = False
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)

class RequestInstanceNode(Node[CloudState]):
    def exec(self) -> None:
        self.state.logs.append(f"Requesting {self.state.instance_type} in {self.state.region}")
        if self.state.quota_exceeded:
            self.result = "quota_exceeded"
        elif self.state.instance_type == "unsupported":
            self.result = "error"
            self.state.error = "Unsupported instance type"
        else:
            self.result = "success"
            self.state.instance_id = "i-1234567890abcdef0"

class ConfigureInstanceNode(Node[CloudState]):
    def exec(self) -> None:
        self.state.logs.append(f"Configuring instance {self.state.instance_id}")
        self.state.status = "running"

class RequestQuotaIncreaseNode(Node[CloudState]):
    def exec(self) -> None:
        self.state.logs.append("Requesting quota increase")
        self.state.status = "quota_pending"

class CleanupResourcesNode(Node[CloudState]):
    def exec(self) -> None:
        self.state.logs.append(f"Cleaning up resources after error: {self.state.error}")
        self.state.status = "failed"

class CloudProvisioningFlow(StateFlow[CloudState]):
    def setup_graph(self) -> None:
        self.add_node("request", RequestInstanceNode())
        self.add_node("configure", ConfigureInstanceNode())
        self.add_node("increase_quota", RequestQuotaIncreaseNode())
        self.add_node("cleanup", CleanupResourcesNode())

        self.add_edge(START, "request")
        self.add_conditional_edges("request", {
            "success": "configure",
            "quota_exceeded": "increase_quota",
            "error": "cleanup"
        })
        self.add_edge("configure", END)
        self.add_edge("increase_quota", END)
        self.add_edge("cleanup", END)

if __name__ == "__main__":
    flow = CloudProvisioningFlow()
    # Case: Success
    state1 = flow.run(CloudState(instance_type="t2.micro", region="us-east-1"))
    print(f"Provisioning 1: {state1.status}, ID: {state1.instance_id}")
    
    # Case: Quota Exceeded
    state2 = flow.run(CloudState(instance_type="p3.16xlarge", region="us-east-1", quota_exceeded=True))
    print(f"Provisioning 2: {state2.status}, Logs: {state2.logs[-1]}")
