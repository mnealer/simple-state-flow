from typing import List
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class HealthState(BaseModel):
    service_name: str
    status: str = "unknown"
    health_result: str = "healthy"
    logs: List[str] = Field(default_factory=list)

class HealthCheckNode(Node[HealthState]):
    def exec(self) -> None:
        self.state.logs.append(f"Checking health for {self.state.service_name}")
        self.result = self.state.health_result

class LogStatusNode(Node[HealthState]):
    def exec(self) -> None:
        self.state.logs.append("Service is healthy")
        self.state.status = "ok"

class RestartServiceNode(Node[HealthState]):
    def exec(self) -> None:
        self.state.logs.append("Service unresponsive. Restarting service...")
        self.state.status = "restarted"

class ReplaceInstanceNode(Node[HealthState]):
    def exec(self) -> None:
        self.state.logs.append("Critical failure. Replacing instance...")
        self.state.status = "replaced"

class HealthCheckFlow(StateFlow[HealthState]):
    def setup_graph(self) -> None:
        self.add_node("check", HealthCheckNode())
        self.add_node("log", LogStatusNode())
        self.add_node("restart", RestartServiceNode())
        self.add_node("replace", ReplaceInstanceNode())

        self.add_edge(START, "check")
        self.add_conditional_edges("check", {
            "healthy": "log",
            "unresponsive": "restart",
            "critical_failure": "replace"
        })
        self.add_edge("log", END)
        self.add_edge("restart", END)
        self.add_edge("replace", END)

if __name__ == "__main__":
    flow = HealthCheckFlow()
    # Case: Unresponsive
    state = flow.run(HealthState(service_name="api-server", health_result="unresponsive"))
    print(f"Service: {state.service_name}, Status: {state.status}, Logs: {state.logs[-1]}")
