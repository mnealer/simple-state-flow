from typing import List
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class IoTState(BaseModel):
    device_id: str
    battery_level: int
    firmware_version: str = "1.0.0"
    update_status: str = "none"
    logs: List[str] = Field(default_factory=list)

class CheckBatteryNode(Node[IoTState]):
    def exec(self) -> None:
        self.state.logs.append(f"Checking battery for {self.state.device_id}: {self.state.battery_level}%")
        if self.state.battery_level > 20:
            self.result = "sufficient"
        else:
            self.result = "low"

class StartFirmwareUpdateNode(Node[IoTState]):
    def exec(self) -> None:
        self.state.logs.append("Starting firmware update...")
        self.state.firmware_version = "1.1.0"
        self.state.update_status = "completed"

class WaitUntilChargedNode(Node[IoTState]):
    def exec(self) -> None:
        self.state.logs.append("Battery low. Waiting until charged.")
        self.state.update_status = "deferred"

class IoTFirmwareFlow(StateFlow[IoTState]):
    def setup_graph(self) -> None:
        self.add_node("check_battery", CheckBatteryNode())
        self.add_node("update", StartFirmwareUpdateNode())
        self.add_node("wait", WaitUntilChargedNode())

        self.add_edge(START, "check_battery")
        self.add_conditional_edges("check_battery", {
            "sufficient": "update",
            "low": "wait"
        })
        self.add_edge("update", END)
        self.add_edge("wait", END)

if __name__ == "__main__":
    flow = IoTFirmwareFlow()
    # Case: Low battery
    state = flow.run(IoTState(device_id="iot-001", battery_level=15))
    print(f"Device: {state.device_id}, Update: {state.update_status}, Logs: {state.logs[-1]}")
