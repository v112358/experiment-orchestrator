"""
Reschedule Orchestrator - Move experiments to conflict-free dates

Uses the agent to find safe date ranges and move experiments.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from src.models.experiment import Experiment
from src.integrations.repository import ExperimentRepository
from src.agent.conflict_analyzer import ConflictAnalyzer


class RescheduleOrchestrator:
    """
    Handles rescheduling experiments to avoid conflicts.
    """
    
    def __init__(self):
        self.repo = ExperimentRepository()
        self.conflict_analyzer = ConflictAnalyzer()
    
    def list_experiments_for_rescheduling(self) -> List[Tuple[int, Experiment]]:
        """
        List all experiments with indices for user selection.
        
        Returns:
            List of (index, experiment) tuples
        """
        experiments = self.repo.load_all()
        return [(i, exp) for i, exp in enumerate(experiments, 1)]
    
    def find_safe_dates(
        self,
        duration_days: int,
        start_search_date: str = None,
        end_search_date: str = None,
        surface_id: str = None,
        metric_name: str = None,
    ) -> List[Tuple[str, str]]:
        """
        Find date ranges that are conflict-free for a given duration.
        
        Args:
            duration_days: How long the experiment needs to run
            start_search_date: Start looking from this date (default: today)
            end_search_date: Stop looking at this date (default: 90 days from now)
            surface_id: If specified, only check conflicts with this surface
            metric_name: If specified, only check conflicts with this metric
        
        Returns:
            List of (start_date, end_date) tuples representing available slots
        """
        
        if not start_search_date:
            start_search_date = datetime.now().strftime("%Y-%m-%d")
        if not end_search_date:
            end_date_obj = datetime.now() + timedelta(days=90)
            end_search_date = end_date_obj.strftime("%Y-%m-%d")
        
        # Get all existing experiments
        existing = self.repo.load_all()
        
        # If filtering by surface/metric, only check those experiments
        if surface_id or metric_name:
            existing = [
                e for e in existing
                if (surface_id is None or surface_id in e.surfaces) and
                   (metric_name is None or metric_name in e.metrics)
            ]
        
        # Find gaps in the schedule
        available_slots = []
        current_date = datetime.strptime(start_search_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_search_date, "%Y-%m-%d")
        
        while current_date < end_date:
            # Check if this date range is available
            potential_end = current_date + timedelta(days=duration_days - 1)
            
            # Check for overlaps
            has_conflict = False
            for exp in existing:
                exp_start = datetime.strptime(exp.start_date, "%Y-%m-%d")
                exp_end = datetime.strptime(exp.end_date, "%Y-%m-%d")
                
                # Check if there's an overlap
                if current_date <= exp_end and potential_end >= exp_start:
                    has_conflict = True
                    # Jump to after this experiment
                    current_date = exp_end + timedelta(days=1)
                    break
            
            if not has_conflict:
                available_slots.append((
                    current_date.strftime("%Y-%m-%d"),
                    potential_end.strftime("%Y-%m-%d")
                ))
                current_date = potential_end + timedelta(days=1)
        
        return available_slots
    
    def reschedule_experiment(
        self,
        experiment_id: str,
        new_start_date: str,
        new_duration_days: int,
        calendar_service=None,
    ) -> Tuple[bool, str, Optional[Experiment]]:
        """
        Reschedule an experiment to new dates.
        
        Args:
            experiment_id: ID of experiment to reschedule
            new_start_date: New start date (YYYY-MM-DD)
            new_duration_days: New duration in days
            calendar_service: Google Calendar service (for updating events)
        
        Returns:
            (success: bool, message: str, updated_experiment: Experiment or None)
        """
        
        try:
            # Get the experiment
            experiment = self.repo.get_by_id(experiment_id)
            if not experiment:
                return False, f"Experiment not found: {experiment_id}", None
            
            # Create a temporary copy with new dates for conflict checking
            old_dates = (experiment.start_date, experiment.end_date)
            experiment.start_date = new_start_date
            experiment.duration_days = new_duration_days
            experiment.end_date = experiment._calculate_end_date()
            
            # Get other experiments (all except this one)
            all_experiments = self.repo.load_all()
            other_experiments = [e for e in all_experiments if e.id != experiment_id]
            
            # Check for conflicts with new dates
            conflict_check = self.conflict_analyzer.analyze_conflicts(
                experiment,
                other_experiments
            )
            
            if conflict_check["has_conflicts"]:
                # Revert changes
                experiment.start_date, experiment.end_date = old_dates
                experiment.duration_days = (
                    datetime.strptime(experiment.end_date, "%Y-%m-%d") -
                    datetime.strptime(experiment.start_date, "%Y-%m-%d")
                ).days
                
                message = f"Cannot reschedule: {conflict_check['analysis']}\n\n"
                message += f"Recommendation: {conflict_check['recommendation']}"
                return False, message, None
            
            # No conflicts - save the updated experiment
            self.repo.save(experiment)
            
            # Update calendar event if service provided
            if calendar_service and experiment.calendar_event_id:
                try:
                    from src.calendar_helper import get_experiments_calendar_id
                    calendar_id = get_experiments_calendar_id(calendar_service)
                    
                    event_body = {
                        'summary': experiment.name,
                        'description': f'Duration: {new_duration_days} days (rescheduled)',
                        'start': {
                            'date': experiment.start_date,
                        },
                        'end': {
                            'date': experiment.end_date,
                        }
                    }
                    
                    calendar_service.events().update(
                        calendarId=calendar_id,
                        eventId=experiment.calendar_event_id,
                        body=event_body
                    ).execute()
                except Exception as e:
                    # Calendar update failed but experiment was saved
                    return True, f"Experiment rescheduled to {experiment.start_date} - {experiment.end_date}, but calendar update failed: {str(e)}", experiment
            
            message = f"✓ Rescheduled successfully!\n"
            message += f"  Old dates: {old_dates[0]} → {old_dates[1]}\n"
            message += f"  New dates: {experiment.start_date} → {experiment.end_date}\n"
            if conflict_check["analysis"]:
                message += f"  Note: {conflict_check['analysis']}"
            
            return True, message, experiment
            
        except Exception as e:
            return False, f"Error: {str(e)}", None
