from typing import List
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class SSLState(BaseModel):
    domain: str
    dns_access: bool = False
    renewal_method: str = "none"
    logs: List[str] = Field(default_factory=list)

class CheckDnsAccessNode(Node[SSLState]):
    def exec(self) -> None:
        self.state.logs.append(f"Checking DNS access for {self.state.domain}")
        if self.state.dns_access:
            self.result = "automatic"
        else:
            self.result = "manual"

class HttpChallengeNode(Node[SSLState]):
    def exec(self) -> None:
        self.state.logs.append("Performing HTTP-01 challenge for SSL renewal")
        self.state.renewal_method = "http-01"

class DnsChallengeNode(Node[SSLState]):
    def exec(self) -> None:
        self.state.logs.append("DNS access not available. Manual DNS challenge required.")
        self.state.renewal_method = "dns-01-manual"

class SSLRenewalFlow(StateFlow[SSLState]):
    def setup_graph(self) -> None:
        self.add_node("check_dns", CheckDnsAccessNode())
        self.add_node("http_challenge", HttpChallengeNode())
        self.add_node("dns_challenge", DnsChallengeNode())

        self.add_edge(START, "check_dns")
        self.add_conditional_edges("check_dns", {
            "automatic": "http_challenge",
            "manual": "dns_challenge"
        })
        self.add_edge("http_challenge", END)
        self.add_edge("dns_challenge", END)

if __name__ == "__main__":
    flow = SSLRenewalFlow()
    # Case: Automatic renewal
    state = flow.run(SSLState(domain="example.com", dns_access=True))
    print(f"Domain: {state.domain}, Method: {state.renewal_method}, Logs: {state.logs[-1]}")
