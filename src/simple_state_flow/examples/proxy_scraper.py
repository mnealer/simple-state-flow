from typing import List, Dict, Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class ScrapingState(BaseModel):
    url: str
    proxies: List[str]
    current_proxy: Optional[str] = None
    data: Optional[Dict] = None
    attempts: int = 0
    max_attempts: int = 3
    is_blocked: bool = False

class GetProxyNode(Node[ScrapingState]):
    def exec(self) -> None:
        if not self.state.proxies:
            self.result = "no_proxies"
            return
        
        self.state.current_proxy = self.state.proxies.pop(0)
        self.state.attempts += 1
        self.result = "success"

class FetchPageNode(Node[ScrapingState]):
    def exec(self) -> None:
        print(f"Fetching {self.state.url} with proxy {self.state.current_proxy}")
        
        # Mock responses based on attempts for simulation
        if self.state.attempts == 1:
            self.result = "blocked"
        elif self.state.attempts == 2:
            self.result = "timeout"
        else:
            self.result = "success"
            self.state.data = {"title": "Sample Scraped Title", "content": "..."}

class RotateProxyNode(Node[ScrapingState]):
    def exec(self) -> None:
        print("Rotating proxy due to blockage")
        self.state.is_blocked = True

class RetryFetchNode(Node[ScrapingState]):
    def exec(self) -> None:
        print(f"Retrying fetch (Attempt {self.state.attempts}/{self.state.max_attempts})")

class ErrorAlertNode(Node[ScrapingState]):
    def exec(self) -> None:
        print(f"Alert: Scraping failed for {self.state.url}")

class ScraperFlow(StateFlow[ScrapingState]):
    def setup_graph(self) -> None:
        self.add_node("get_proxy", GetProxyNode())
        self.add_node("fetch", FetchPageNode())
        self.add_node("rotate", RotateProxyNode())
        self.add_node("retry", RetryFetchNode())
        self.add_node("alert", ErrorAlertNode())

        self.add_edge(START, "get_proxy")
        
        self.add_conditional_edges("get_proxy", {
            "success": "fetch",
            "no_proxies": "alert"
        })

        self.add_conditional_edges("fetch", {
            "success": END,
            "blocked": "rotate",
            "timeout": "retry"
        })

        self.add_edge("rotate", "get_proxy")
        self.add_edge("retry", "get_proxy")
        self.add_edge("alert", END)

if __name__ == "__main__":
    scraper = ScraperFlow()
    initial_proxies = ["proxy1", "proxy2", "proxy3"]
    final_state = scraper.run(ScrapingState(url="https://example.com", proxies=initial_proxies))
    print(f"Scraping result: {final_state.data is not None}")
