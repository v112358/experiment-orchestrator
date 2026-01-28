"""
CLI for rescheduling experiments

Allows users to list, view, and reschedule experiments.
"""

from src.agent.reschedule import RescheduleOrchestrator
from src.auth import get_authenticated_service
from datetime import datetime


def show_reschedule_menu():
    """Main menu for rescheduling experiments"""
    
    reschedule = RescheduleOrchestrator()
    
    while True:
        print("\n" + "="*60)
        print("RESCHEDULE EXPERIMENTS")
        print("="*60)
        print("\n1. List all experiments")
        print("2. Find safe dates for new experiment duration")
        print("3. Reschedule an experiment")
        print("4. Back to main menu")
        
        choice = input("\nWhat would you like to do? (1-4) ").strip()
        
        if choice == "1":
            show_all_experiments(reschedule)
        elif choice == "2":
            find_safe_dates_menu(reschedule)
        elif choice == "3":
            reschedule_menu(reschedule)
        elif choice == "4":
            break
        else:
            print("Invalid choice")


def show_all_experiments(reschedule: RescheduleOrchestrator):
    """Display all experiments with options"""
    
    experiments = reschedule.list_experiments_for_rescheduling()
    
    if not experiments:
        print("\nNo experiments scheduled.")
        return
    
    print("\n" + "="*60)
    print("ALL EXPERIMENTS")
    print("="*60 + "\n")
    
    for idx, exp in experiments:
        print(f"{idx}. {exp.name}")
        print(f"   Dates: {exp.start_date} → {exp.end_date} ({exp.duration_days} days)")
        print(f"   Surfaces: {', '.join(exp.surfaces)}")
        print(f"   Metrics: {', '.join(exp.metrics)}")
        print(f"   Status: {exp.status}")
        print()


def find_safe_dates_menu(reschedule: RescheduleOrchestrator):
    """Find safe date ranges for a hypothetical experiment"""
    
    print("\n" + "="*60)
    print("FIND SAFE DATES")
    print("="*60 + "\n")
    
    duration = input("Duration (days)? ").strip()
    try:
        duration = int(duration)
    except ValueError:
        print("Invalid duration")
        return
    
    start_date = input("Start searching from (YYYY-MM-DD, or press Enter for today)? ").strip()
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    safe_slots = reschedule.find_safe_dates(duration, start_search_date=start_date)
    
    if not safe_slots:
        print(f"\nNo available {duration}-day slots found in the next 90 days.")
        return
    
    print(f"\nFound {len(safe_slots)} available time slot(s):\n")
    
    for i, (start, end) in enumerate(safe_slots[:10], 1):  # Show first 10
        print(f"{i}. {start} → {end}")


def reschedule_menu(reschedule: RescheduleOrchestrator):
    """Reschedule a specific experiment"""
    
    print("\n" + "="*60)
    print("RESCHEDULE AN EXPERIMENT")
    print("="*60 + "\n")
    
    # Show experiments
    experiments = reschedule.list_experiments_for_rescheduling()
    if not experiments:
        print("No experiments to reschedule.")
        return
    
    for idx, exp in experiments:
        print(f"{idx}. {exp.name} ({exp.start_date} → {exp.end_date})")
    
    # Get selection
    choice = input("\nWhich experiment? (number) ").strip()
    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(experiments):
            print("Invalid choice")
            return
        
        selected_idx, selected_exp = experiments[choice_idx]
        
        print(f"\nRescheduling: {selected_exp.name}")
        print(f"Current dates: {selected_exp.start_date} → {selected_exp.end_date}")
        
        # Get new dates
        new_start = input("\nNew start date (YYYY-MM-DD)? ").strip()
        new_duration = input("New duration (days)? ").strip()
        
        try:
            new_duration = int(new_duration)
        except ValueError:
            print("Invalid duration")
            return
        
        # Reschedule
        print("\nChecking for conflicts...")
        
        # Get calendar service for updating events
        try:
            calendar_service = get_authenticated_service()
        except:
            calendar_service = None
        
        success, message, experiment = reschedule.reschedule_experiment(
            selected_exp.id,
            new_start,
            new_duration,
            calendar_service
        )
        
        print("\n" + "="*60)
        if success:
            print("SUCCESS!")
        else:
            print("COULD NOT RESCHEDULE")
        print("="*60)
        print(message)
        print("="*60 + "\n")
        
    except ValueError:
        print("Invalid input")
