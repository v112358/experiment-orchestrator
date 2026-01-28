"""
Experiment Orchestrator Agent - The brain of the system

This agent:
1. Takes experiment info from the user
2. Reads the repository of past experiments
3. Checks the calendar for conflicts
4. Uses Gemini to analyze interaction effects
5. Makes a recommendation
6. Creates the calendar event
7. Stores the experiment in the repository
"""

from typing import List, Optional, Tuple
from datetime import datetime

from src.models.experiment import Experiment
from src.integrations.repository import ExperimentRepository
from src.auth import get_authenticated_service
from src.calendar_helper import create_experiment_event as create_calendar_event, get_experiments_calendar_id
from src.agent.conflict_analyzer import ConflictAnalyzer
from src.knowledge.product_config import get_surface, get_screen, get_metric


class ExperimentOrchestratorAgent:
    """
    Main agent for scheduling experiments.
    
    Workflow:
    1. User provides experiment details
    2. Agent validates inputs
    3. Agent checks for conflicts
    4. Agent gets user approval
    5. Agent creates calendar event and saves to repo
    """
    
    def __init__(self):
        self.repo = ExperimentRepository()
        self.conflict_analyzer = ConflictAnalyzer()
        self.calendar_service = None
    
    def schedule_experiment(
        self,
        name: str,
        description: str,
        hypothesis: str,
        surfaces: List[str],
        screens: List[str],
        metrics: List[str],
        start_date: str,
        duration_days: int,
        auto_approve: bool = False,
    ) -> Tuple[bool, str, Optional[Experiment]]:
        """
        Main function to schedule an experiment.
        
        Args:
            name: Experiment name
            description: What does it test?
            hypothesis: What's the expected outcome?
            surfaces: Which product surfaces affected (e.g., ["homepage", "checkout"])
            screens: Which specific screens affected
            metrics: Which metrics measured
            start_date: Start date (YYYY-MM-DD)
            duration_days: How long it runs
            auto_approve: Skip conflict confirmation if safe
        
        Returns:
            (success: bool, message: str, experiment: Experiment or None)
        """
        
        try:
            # Step 1: Validate inputs
            validation_error = self._validate_inputs(
                name, surfaces, screens, metrics, start_date, duration_days
            )
            if validation_error:
                return False, validation_error, None
            
            # Step 2: Create experiment object
            experiment = Experiment(
                name=name,
                description=description,
                hypothesis=hypothesis,
                surfaces=surfaces,
                screens=screens,
                metrics=metrics,
                start_date=start_date,
                duration_days=duration_days,
            )
            
            # Step 3: Check for conflicts
            conflict_check = self._check_conflicts(experiment)
            
            if conflict_check["has_conflicts"]:
                message = self._format_conflict_message(experiment, conflict_check)
                return False, message, None
            
            # Step 4: Create calendar event
            calendar_event_id = self._create_calendar_event(experiment)
            experiment.calendar_event_id = calendar_event_id
            
            # Step 5: Save to repository
            self.repo.save(experiment)
            
            # Success!
            message = f"✓ Experiment scheduled!\n"
            message += f"  Event ID: {calendar_event_id}\n"
            if conflict_check["analysis"]:
                message += f"  Note: {conflict_check['analysis']}"
            
            return True, message, experiment
            
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def _validate_inputs(
        self,
        name: str,
        surfaces: List[str],
        screens: List[str],
        metrics: List[str],
        start_date: str,
        duration_days: int,
    ) -> Optional[str]:
        """Validate all inputs before proceeding"""
        
        if not name or not name.strip():
            return "Experiment name cannot be empty"
        
        if not surfaces or len(surfaces) == 0:
            return "Must specify at least one product surface"
        
        # Validate surfaces exist
        for surface_id in surfaces:
            surface = get_surface(surface_id)
            if surface is None:
                return f"Unknown surface: {surface_id}. Available: homepage, product_page, checkout, email"
        
        # Validate screens exist (only if explicitly provided and not empty)
        for screen_id in screens:
            if screen_id and get_screen(screen_id) is None:
                return f"Unknown screen: {screen_id}"
        
        # Validate metrics exist
        for metric_name in metrics:
            if not get_metric(metric_name):
                return f"Unknown metric: {metric_name}. Available: click_through_rate, conversion_rate, aov, cart_abandonment, bounce_rate, pageviews, open_rate, email_click_rate, reviews_helpful"
        
        # Validate date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD (e.g., 2026-02-01)"
        
        if duration_days <= 0:
            return "Duration must be greater than 0 days"
        
        return None
    
    def _check_conflicts(self, experiment: Experiment) -> dict:
        """Check if experiment conflicts with existing ones"""
        
        # Find experiments that overlap in time
        overlapping = self.repo.get_by_date_range(
            experiment.start_date,
            experiment.end_date
        )
        
        if not overlapping:
            return {
                "has_conflicts": False,
                "analysis": "",
                "recommendation": "",
                "confidence": 1.0,
                "problematic_experiments": [],
            }
        
        # Use AI to analyze conflicts
        analysis = self.conflict_analyzer.analyze_conflicts(
            experiment,
            overlapping
        )
        
        return analysis
    
    def _create_calendar_event(self, experiment: Experiment) -> str:
        """Create event in Google Calendar"""
        
        if not self.calendar_service:
            self.calendar_service = get_authenticated_service()
        
        event_id = create_calendar_event(
            self.calendar_service,
            experiment.name,
            experiment.start_date,
            experiment.duration_days,
        )
        
        return event_id
    
    def _format_conflict_message(self, experiment: Experiment, conflict_check: dict) -> str:
        """Format a human-readable conflict message"""
        
        message = f"⚠ Cannot schedule: {experiment.name}\n\n"
        message += f"Reason: {conflict_check['analysis']}\n\n"
        message += f"Recommendation: {conflict_check['recommendation']}\n\n"
        message += f"Confidence: {int(conflict_check['confidence'] * 100)}%"
        
        return message
    
    def get_experiment_status(self) -> str:
        """Get summary of all scheduled experiments"""
        experiments = self.repo.load_all()
        
        if not experiments:
            return "No experiments scheduled."
        
        status = f"Total experiments: {len(experiments)}\n\n"
        
        for exp in sorted(experiments, key=lambda e: e.start_date):
            status += f"• {exp.name}\n"
            status += f"  {exp.start_date} → {exp.end_date} ({exp.duration_days} days)\n"
            status += f"  Surfaces: {', '.join(exp.surfaces)}\n"
            status += f"  Metrics: {', '.join(exp.metrics)}\n\n"
        
        return status
