"""
Experiment Model - Data structure for an experiment

Stores all info about an experiment: what it tests, when it runs,
what surfaces/metrics it touches, and results.
"""

from datetime import datetime
from typing import List, Optional


class Experiment:
    """
    Represents a product experiment.
    
    Attributes:
        id: Unique identifier (auto-generated)
        name: Experiment name
        description: What the experiment tests and why
        hypothesis: Expected outcome
        surfaces: Which product surfaces this experiment touches
        screens: Which specific screens it affects
        metrics: Which metrics it measures
        start_date: When experiment starts (YYYY-MM-DD format)
        duration_days: How long it runs
        end_date: Calculated from start_date + duration_days
        created_at: When this record was created
        calendar_event_id: Google Calendar event ID (if created)
        status: "planned", "running", "completed"
        results: Results summary (optional)
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        hypothesis: str,
        surfaces: List[str],
        screens: List[str],
        metrics: List[str],
        start_date: str,
        duration_days: int,
        id: Optional[str] = None,
        calendar_event_id: Optional[str] = None,
        status: str = "planned",
        results: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        self.name = name
        self.id = id or self._generate_id()
        self.description = description
        self.hypothesis = hypothesis
        self.surfaces = surfaces
        self.screens = screens
        self.metrics = metrics
        self.start_date = start_date
        self.duration_days = duration_days
        self.end_date = self._calculate_end_date()
        self.created_at = created_at or datetime.now().isoformat()
        self.calendar_event_id = calendar_event_id
        self.status = status
        self.results = results
    
    def _generate_id(self) -> str:
        """Generate a unique ID based on name and timestamp"""
        import hashlib
        import time
        content = f"{self.name}-{time.time()}".encode()
        return hashlib.md5(content).hexdigest()[:8]
    
    def _calculate_end_date(self) -> str:
        """Calculate end date from start date and duration"""
        from datetime import datetime, timedelta
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = start + timedelta(days=self.duration_days)
        return end.strftime("%Y-%m-%d")
    
    def to_dict(self) -> dict:
        """Convert to dictionary (for JSON storage)"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "hypothesis": self.hypothesis,
            "surfaces": self.surfaces,
            "screens": self.screens,
            "metrics": self.metrics,
            "start_date": self.start_date,
            "duration_days": self.duration_days,
            "end_date": self.end_date,
            "created_at": self.created_at,
            "calendar_event_id": self.calendar_event_id,
            "status": self.status,
            "results": self.results,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Experiment":
        """Create Experiment from dictionary (for JSON loading)"""
        return Experiment(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            hypothesis=data.get("hypothesis"),
            surfaces=data.get("surfaces", []),
            screens=data.get("screens", []),
            metrics=data.get("metrics", []),
            start_date=data.get("start_date"),
            duration_days=data.get("duration_days"),
            calendar_event_id=data.get("calendar_event_id"),
            status=data.get("status", "planned"),
            results=data.get("results"),
            created_at=data.get("created_at"),
        )
    
    def __repr__(self) -> str:
        return f"Experiment(name='{self.name}', {self.start_date} - {self.end_date}, surfaces={self.surfaces})"
