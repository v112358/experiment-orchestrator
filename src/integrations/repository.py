"""
Repository - Read and write experiments to disk

Stores experiments in experiments.json so they persist and the agent can learn from them.
"""

import json
import os
from typing import List, Optional
from src.models.experiment import Experiment


class ExperimentRepository:
    """
    Manages reading and writing experiments to a JSON file.
    Think of it as the agent's memory of past experiments.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.experiments_file = os.path.join(data_dir, "experiments.json")
        os.makedirs(data_dir, exist_ok=True)
    
    def load_all(self) -> List[Experiment]:
        """
        Load all experiments from disk.
        
        Returns:
            List of Experiment objects
        """
        if not os.path.exists(self.experiments_file):
            return []
        
        try:
            with open(self.experiments_file, 'r') as f:
                data = json.load(f)
            return [Experiment.from_dict(exp) for exp in data]
        except (json.JSONDecodeError, IOError):
            return []
    
    def save(self, experiment: Experiment) -> None:
        """
        Save a single experiment to disk (adds or updates).
        
        Args:
            experiment: Experiment object to save
        """
        experiments = self.load_all()
        
        # Check if experiment already exists (update) or new (add)
        existing_idx = next(
            (i for i, e in enumerate(experiments) if e.id == experiment.id),
            None
        )
        
        if existing_idx is not None:
            experiments[existing_idx] = experiment
        else:
            experiments.append(experiment)
        
        self._write_all(experiments)
    
    def save_all(self, experiments: List[Experiment]) -> None:
        """Save multiple experiments at once"""
        self._write_all(experiments)
    
    def get_by_id(self, exp_id: str) -> Optional[Experiment]:
        """Get a specific experiment by ID"""
        experiments = self.load_all()
        return next((e for e in experiments if e.id == exp_id), None)
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Experiment]:
        """
        Get experiments that overlap with a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            List of overlapping experiments
        """
        experiments = self.load_all()
        
        overlapping = []
        for exp in experiments:
            # Check if dates overlap
            if exp.start_date <= end_date and exp.end_date >= start_date:
                overlapping.append(exp)
        
        return overlapping
    
    def get_by_surface(self, surface_id: str) -> List[Experiment]:
        """Get all experiments that touch a specific surface"""
        experiments = self.load_all()
        return [e for e in experiments if surface_id in e.surfaces]
    
    def get_by_metric(self, metric_name: str) -> List[Experiment]:
        """Get all experiments that measure a specific metric"""
        experiments = self.load_all()
        return [e for e in experiments if metric_name in e.metrics]
    
    def delete(self, exp_id: str) -> bool:
        """Delete an experiment by ID"""
        experiments = self.load_all()
        original_count = len(experiments)
        experiments = [e for e in experiments if e.id != exp_id]
        
        if len(experiments) < original_count:
            self._write_all(experiments)
            return True
        return False
    
    def _write_all(self, experiments: List[Experiment]) -> None:
        """Internal: write all experiments to disk"""
        with open(self.experiments_file, 'w') as f:
            json.dump(
                [e.to_dict() for e in experiments],
                f,
                indent=2
            )
