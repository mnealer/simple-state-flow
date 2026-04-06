from typing import Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class BackupState(BaseModel):
    db_name: str
    backup_path: Optional[str] = None
    is_valid: bool = False
    error: Optional[str] = None

class CreateBackupNode(Node[BackupState]):
    def exec(self) -> None:
        self.state.backup_path = f"/backups/{self.state.db_name}.sql"
        print(f"Created backup at {self.state.backup_path}")

class VerifyBackupNode(Node[BackupState]):
    def exec(self) -> None:
        # Mocking corruption if db_name contains "bad"
        if "bad" in self.state.db_name:
            self.result = "corrupt"
            self.state.error = "Integrity check failed"
        else:
            self.result = "valid"
            self.state.is_valid = True

class StoreInS3Node(Node[BackupState]):
    def exec(self) -> None:
        print(f"Uploading {self.state.backup_path} to S3 bucket")

class AlertDBANode(Node[BackupState]):
    def exec(self) -> None:
        print(f"CRITICAL: Backup corruption for {self.state.db_name}. Reason: {self.state.error}")

class BackupFlow(StateFlow[BackupState]):
    def setup_graph(self) -> None:
        self.add_node("backup", CreateBackupNode())
        self.add_node("verify", VerifyBackupNode())
        self.add_node("s3", StoreInS3Node())
        self.add_node("alert", AlertDBANode())

        self.add_edge(START, "backup")
        self.add_edge("backup", "verify")
        
        self.add_conditional_edges("verify", {
            "valid": "s3",
            "corrupt": "alert"
        })
        
        self.add_edge("s3", END)
        self.add_edge("alert", END)

if __name__ == "__main__":
    backup = BackupFlow()
    state = backup.run(BackupState(db_name="bad_database"))
    print(f"Backup valid: {state.is_valid}, Error: {state.error}")
