"""
Main Script - Experiment Orchestrator v0.2

This is the script you run to schedule experiments.

The agent will:
1. Ask for experiment details
2. Check for conflicts with existing experiments
3. Analyze interaction effects using AI
4. Create the calendar event
5. Store the experiment for future reference

How to use:
    python main.py
    
Then answer the prompts about your experiment.
"""

from src.agent.orchestrator import ExperimentOrchestratorAgent
from src.knowledge.product_config import SURFACES, SCREENS, METRICS
from src.cli.reschedule_cli import show_reschedule_menu
from datetime import datetime


def validate_date(date_string):
    """Check if user entered a valid date format"""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def show_available_surfaces():
    """Show user available product surfaces"""
    print("\nAvailable surfaces:")
    for surface_id, surface in SURFACES.items():
        print(f"  • {surface_id}: {surface.name} - {surface.description}")


def show_available_metrics():
    """Show user available metrics"""
    print("\nAvailable metrics:")
    for metric_id, metric in METRICS.items():
        print(f"  • {metric_id}: {metric.name}")


def get_user_input():
    """
    Ask the user for comprehensive experiment details.
    """
    
    print("\n" + "="*60)
    print("EXPERIMENT ORCHESTRATOR - AI-Powered Scheduling")
    print("="*60 + "\n")
    
    # Experiment name
    name = input("Experiment name? ").strip()
    if not name:
        raise ValueError("Experiment name cannot be empty")
    
    # Description
    description = input("What are you testing? (brief description) ").strip()
    if not description:
        description = name
    
    # Hypothesis
    hypothesis = input("What's your hypothesis? (expected outcome) ").strip()
    if not hypothesis:
        hypothesis = "TBD"
    
    # Show available surfaces
    show_available_surfaces()
    surfaces_input = input("\nWhich surfaces does this affect? (comma-separated, e.g., 'homepage,checkout') ").strip()
    surfaces = [s.strip() for s in surfaces_input.split(",")]
    
    # Map surfaces to their main screens automatically
    # For simplicity, use the first screen of each surface
    from src.knowledge.product_config import SURFACES
    screens = []
    for surface_id in surfaces:
        surface = SURFACES.get(surface_id)
        if surface and surface.screens:
            screens.append(surface.screens[0])  # Use first screen of the surface
    
    # Show available metrics
    show_available_metrics()
    metrics_input = input("\nWhich metrics will you measure? (comma-separated) ").strip()
    metrics = [m.strip() for m in metrics_input.split(",")]
    
    # Start date
    while True:
        start_date = input("\nStart date (YYYY-MM-DD)? ").strip()
        if validate_date(start_date):
            break
        print("Invalid format. Please use YYYY-MM-DD (e.g., 2026-02-01)")
    
    # Duration
    while True:
        try:
            duration_days = int(input("Duration (days)? ").strip())
            if duration_days > 0:
                break
            print("Duration must be greater than 0")
        except ValueError:
            print("Please enter a number")
    
    return {
        'name': name,
        'description': description,
        'hypothesis': hypothesis,
        'surfaces': surfaces,
        'screens': screens,
        'metrics': metrics,
        'start_date': start_date,
        'duration_days': duration_days,
    }


def main():
    """
    Main function that orchestrates the whole process.
    """
    
    try:
        # Show menu
        print("\n" + "="*60)
        print("EXPERIMENT ORCHESTRATOR - v0.3")
        print("="*60)
        print("\n1. Schedule new experiment")
        print("2. Reschedule/move experiments")
        print("3. Exit")
        
        choice = input("\nWhat would you like to do? (1-3) ").strip()
        
        if choice == "1":
            schedule_new_experiment()
        elif choice == "2":
            show_reschedule_menu()
        elif choice == "3":
            print("\nGoodbye!")
            return
        else:
            print("Invalid choice")
            return
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        raise


def schedule_new_experiment():
    """Schedule a new experiment (old workflow)"""
    
    try:
        # Step 1: Get user input
        print("\nLet's schedule an experiment!\n")
        user_input = get_user_input()
        
        # Step 2: Initialize agent
        print("\nInitializing Experiment Orchestrator Agent...")
        agent = ExperimentOrchestratorAgent()
        
        # Step 3: Schedule the experiment
        print("\nAnalyzing experiment and checking for conflicts...")
        success, message, experiment = agent.schedule_experiment(
            name=user_input['name'],
            description=user_input['description'],
            hypothesis=user_input['hypothesis'],
            surfaces=user_input['surfaces'],
            screens=user_input['screens'],
            metrics=user_input['metrics'],
            start_date=user_input['start_date'],
            duration_days=user_input['duration_days'],
        )
        
        # Step 4: Show result and handle conflict
        print("\n" + "="*60)
        if success:
            print("SUCCESS!")
            print("="*60)
            print(f"✓ {experiment.name}")
            print(f"  Start: {experiment.start_date}")
            print(f"  End: {experiment.end_date}")
            print(f"  Duration: {experiment.duration_days} days")
            print(f"  Calendar Event ID: {experiment.calendar_event_id}")
            print(f"  Repo ID: {experiment.id}")
            print(f"\n  Surfaces: {', '.join(experiment.surfaces)}")
            print(f"  Metrics: {', '.join(experiment.metrics)}")
        else:
            print("CONFLICT DETECTED")
            print("="*60)
            print(message)
            print("="*60)
            
            # Offer to find safe dates
            offer = input("\nWould you like me to find safe dates? (yes/no) ").strip().lower()
            if offer in ['yes', 'y']:
                print("\nSearching for available time slots...")
                
                from src.agent.reschedule import RescheduleOrchestrator
                reschedule = RescheduleOrchestrator()
                
                # Find safe slots for same duration
                safe_slots = reschedule.find_safe_dates(
                    user_input['duration_days'],
                    start_search_date=user_input['start_date']
                )
                
                if not safe_slots:
                    print("No available slots found.")
                else:
                    print(f"\nFound {len(safe_slots)} available time slot(s):\n")
                    for i, (start, end) in enumerate(safe_slots[:5], 1):  # Show first 5
                        print(f"{i}. {start} → {end}")
                    
                    choice = input("\nWhich slot? (number, or 0 to skip) ").strip()
                    try:
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(safe_slots[:5]):
                            new_start, new_end = safe_slots[choice_idx]
                            
                            print(f"\nRescheduling to {new_start}...")
                            
                            # Try scheduling again with new dates
                            success, message, experiment = agent.schedule_experiment(
                                name=user_input['name'],
                                description=user_input['description'],
                                hypothesis=user_input['hypothesis'],
                                surfaces=user_input['surfaces'],
                                screens=user_input['screens'],
                                metrics=user_input['metrics'],
                                start_date=new_start,
                                duration_days=user_input['duration_days'],
                            )
                            
                            print("\n" + "="*60)
                            if success:
                                print("SUCCESS!")
                                print("="*60)
                                print(f"✓ {experiment.name}")
                                print(f"  Start: {experiment.start_date}")
                                print(f"  End: {experiment.end_date}")
                                print(f"  Duration: {experiment.duration_days} days")
                            else:
                                print("STILL HAS CONFLICTS")
                                print("="*60)
                                print(message)
                    except (ValueError, IndexError):
                        pass
        
        print("="*60 + "\n")
        
        # Show all scheduled experiments
        print("\nAll scheduled experiments:")
        print(agent.get_experiment_status())
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        raise


if __name__ == '__main__':
    main()
