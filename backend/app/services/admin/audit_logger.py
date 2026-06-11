from datetime import datetime, timezone
from uuid import uuid4


class AuditLogger:
    def __init__(self, repository):
        self.repository = repository

    def log(self, actor_id, action, details=None):
        self.repository.save(
            {
                "_id": str(uuid4()),
                "actor_id": actor_id,
                "action": action,
                "details": details or {},
                "created_at": datetime.now(timezone.utc),
            }
        )
