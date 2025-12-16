#!/usr/bin/env python3
"""
Todo Console Application
Main entry point for the application.
"""

# Note: This application should be run from the project root using:
# python -m src.main
# This allows for proper relative imports from the src package.

import questionary
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import print as rprint
from rich.panel import Panel

from .tasks import create_task, get_all_tasks_formatted, format_tasks_list, update_task, delete_task, toggle_completion
from .validation import validate_task_title, validate_task_description, validate_task_id, validate_menu_choice, validate_confirmation, is_valid_confirmation_for_deletion

console = Console()


def display_menu():
    """Display the main menu options."""
    console.print("\n")
    console.print(Panel("[bold bright_cyan]TODO APPLICATION[/bold bright_cyan]",
                        border_style="bright_cyan", expand=False))
    console.print("\n[bright_white]Choose an option:[/bright_white]")

    menu_options = [
        ("1.", "[bold green]+ Add Task[/bold green]"),
        ("2.", "[bold blue]V View All Tasks[/bold blue]"),
        ("3.", "[bold yellow]U Update Task[/bold yellow]"),
        ("4.", "[bold red]D Delete Task[/bold red]"),
        ("5.", "[bold magenta]C Mark Task Complete/Incomplete[/bold magenta]"),
        ("6.", "[bold bright_white]X Exit[/bold bright_white]")
    ]

    for key, description in menu_options:
        console.print(f"  {key} {description}")


def get_user_choice():
    """Get and validate user menu choice."""
    try:
        choice = questionary.select(
            "Choose an option:",
            choices=[
                {"name": "+ Add Task", "value": 1},
                {"name": "V View All Tasks", "value": 2},
                {"name": "U Update Task", "value": 3},
                {"name": "D Delete Task", "value": 4},
                {"name": "C Mark Task Complete/Incomplete", "value": 5},
                {"name": "X Exit", "value": 6}
            ],
            qmark=">>",
            pointer=">"
        ).ask()

        if choice is None:  # User cancelled
            console.print("\n[bold red]Goodbye![/bold red]")
            exit(0)

        return choice
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Goodbye![/bold red]")
        exit(0)
    except EOFError:
        console.print("\n\n[bold red]Goodbye![/bold red]")
        exit(0)


def add_task_flow():
    """Handle the add task flow."""
    try:
        console.print(Panel("[bold yellow]ADD NEW TASK[/bold yellow]", border_style="yellow"))

        title = questionary.text(
            "Enter task title (1-200 characters):",
            qmark=">>",
            validate=lambda text: len(text) >= 1 and len(text) <= 200
        ).ask()

        if title is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        title = title.strip()

        description = questionary.text(
            "Enter task description (optional, max 1000 characters):",
            default="",
            qmark=">>"
        ).ask()

        if description is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        task = create_task(title, description)
        console.print(f"\n[bold green]Success![/bold green] [green]Task added successfully![/green]")
        console.print(f"ID: [bold]{task['id']}[/bold] | Title: [bold]{task['title']}[/bold]")
    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except EOFError:
        console.print("\n[yellow]Operation cancelled.[/yellow]")


def view_tasks_flow():
    """Handle the view tasks flow."""
    try:
        tasks = get_all_tasks_formatted()

        if not tasks:
            console.print(Panel("[yellow]No tasks found. Add your first task![/yellow]",
                              title="[bold bright_yellow]TASKS[/bold bright_yellow]",
                              border_style="yellow"))
            return

        # Create a more visually appealing table
        table = Table(
            title="[bold bright_blue]ALL TASKS[/bold bright_blue]",
            show_header=True,
            header_style="bold blue",
            border_style="bright_blue",
            title_justify="left",
            show_lines=True
        )
        table.add_column("[bold]ID[/bold]", style="dim", width=6, justify="center")
        table.add_column("[bold]Title[/bold]", min_width=25)
        table.add_column("[bold]Status[/bold]", justify="center", width=12)
        table.add_column("[bold]Created[/bold]", min_width=20)

        for task in tasks:
            status = "[bold green]COMPLETED[/bold green]" if task["completed"] else "[bold red]PENDING[/bold red]"
            # Convert ISO format to readable format
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
                created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = task["created_at"]

            # Add color coding based on completion status
            title_style = "strikethrough" if task["completed"] else "normal"
            table.add_row(
                f"[bold]{task['id']}[/bold]",
                f"[{title_style}]{task['title']}[/{title_style}]",
                status,
                f"[italic]{created_at}[/italic]"
            )

        console.print(f"\n[bold bright_cyan]Total: {len(tasks)} task{'s' if len(tasks) != 1 else ''}[/bold bright_cyan]")
        console.print(table)

        # Show summary statistics
        completed_count = sum(1 for task in tasks if task["completed"])
        pending_count = len(tasks) - completed_count
        console.print(f"\n[green]COMPLETED: {completed_count}[/green] | [red]PENDING: {pending_count}[/red]")

    except Exception as e:
        console.print(f"\n[bold red]Error viewing tasks:[/bold red] {e}")


def update_task_flow():
    """Handle the update task flow."""
    try:
        console.print(Panel("[bold yellow]UPDATE TASK[/bold yellow]", border_style="yellow"))

        task_id_str = questionary.text(
            "Enter task ID to update:",
            qmark=">>",
            validate=lambda text: text.isdigit() and int(text) > 0
        ).ask()

        if task_id_str is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Validate task ID
        is_valid, error_msg = validate_task_id(task_id_str)
        if not is_valid:
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}")
            return

        task_id = int(task_id_str)

        # Check if task exists by trying to get it
        from .storage import get_task_by_id
        task = get_task_by_id(task_id)
        if not task:
            console.print(f"\n[bold red]Error:[/bold red] Task with ID {task_id} does not exist")
            return

        console.print(f"\n[bold cyan]Current Task:[/bold cyan]")
        status = "[green]COMPLETED[/green]" if task["completed"] else "[red]PENDING[/red]"
        console.print(f"  ID: [bold]{task['id']}[/bold] | Title: [bold]{task['title']}[/bold] | Status: {status}")

        # Get new title (keep current if empty)
        new_title = questionary.text(
            f"Enter new title (current: '{task['title']}'), or press Enter to keep current:",
            default=task['title'],
            qmark=">>"
        ).ask()

        if new_title is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Get new description (keep current if empty)
        new_description = questionary.text(
            f"Enter new description (current: '{task['description']}'), or press Enter to keep current:",
            default=task['description'],
            qmark=">>"
        ).ask()

        if new_description is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Update the task
        success = update_task(task_id, new_title, new_description)

        if success:
            console.print(f"\n[bold green]Success![/bold green] [green]Task {task_id} updated successfully![/green]")
            console.print(f"  New Title: [bold]{new_title}[/bold]")
            console.print(f"  New Description: [italic]{new_description}[/italic]")
        else:
            console.print(f"\n[bold red]Error:[/bold red] Task with ID {task_id} does not exist")

    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except EOFError:
        console.print("\n[yellow]Operation cancelled.[/yellow]")


def delete_task_flow():
    """Handle the delete task flow."""
    try:
        console.print(Panel("[bold red]DELETE TASK[/bold red]", border_style="red"))

        task_id_str = questionary.text(
            "Enter task ID to delete:",
            qmark=">>",
            validate=lambda text: text.isdigit() and int(text) > 0
        ).ask()

        if task_id_str is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Validate task ID
        is_valid, error_msg = validate_task_id(task_id_str)
        if not is_valid:
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}")
            return

        task_id = int(task_id_str)

        # Check if task exists
        from .storage import get_task_by_id
        task = get_task_by_id(task_id)
        if not task:
            console.print(f"\n[bold red]Error:[/bold red] Task with ID {task_id} does not exist")
            return

        console.print(f"\n[bold cyan]Task to delete:[/bold cyan]")
        status = "[green]COMPLETED[/green]" if task["completed"] else "[red]PENDING[/red]"
        console.print(f"  ID: [bold]{task['id']}[/bold] | Title: [bold]{task['title']}[/bold] | Status: {status}")

        # Confirm deletion with better styling
        confirm = questionary.confirm(
            f"Are you sure you want to delete task '{task['title']}' (ID: {task_id})?",
            qmark=">>",
            default=False
        ).ask()

        if confirm is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        if confirm:
            success = delete_task(task_id)
            if success:
                console.print(f"\n[bold green]Success![/bold green] [green]Task {task_id} deleted successfully![/green]")
            else:
                console.print(f"\n[bold red]Error:[/bold red] Task with ID {task_id} does not exist")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")

    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except EOFError:
        console.print("\n[yellow]Operation cancelled.[/yellow]")


def toggle_completion_flow():
    """Handle the toggle completion flow."""
    try:
        console.print(Panel("[bold magenta]TOGGLE TASK COMPLETION[/bold magenta]", border_style="magenta"))

        task_id_str = questionary.text(
            "Enter task ID to toggle completion:",
            qmark=">>",
            validate=lambda text: text.isdigit() and int(text) > 0
        ).ask()

        if task_id_str is None:  # User cancelled
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Validate task ID
        is_valid, error_msg = validate_task_id(task_id_str)
        if not is_valid:
            console.print(f"\n[bold red]Error:[/bold red] {error_msg}")
            return

        task_id = int(task_id_str)

        # Check if task exists
        from .storage import get_task_by_id
        task = get_task_by_id(task_id)
        if not task:
            console.print(f"\n[bold red]Error:[/bold red] Task with ID {task_id} does not exist")
            return

        console.print(f"\n[bold cyan]Current Task:[/bold cyan]")
        current_status = "[green]COMPLETED[/green]" if task["completed"] else "[red]PENDING[/red]"
        console.print(f"  ID: [bold]{task['id']}[/bold] | Title: [bold]{task['title']}[/bold] | Status: {current_status}")

        # Toggle completion status
        success = toggle_completion(task_id)

        if success:
            action = "marked as completed" if task["completed"] == False else "marked as pending"
            console.print(f"\n[bold green]Success![/bold green] [green]Task {task_id} {action}![/green]")

            # Show updated status
            updated_task = get_task_by_id(task_id)
            updated_status = "[green]COMPLETED[/green]" if updated_task["completed"] else "[red]PENDING[/red]"
            console.print(f"  New Status: {updated_status}")
        else:
            console.print(f"\n[bold red]Error:[/bold red] Could not toggle completion status for task with ID {task_id}")

    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
    except EOFError:
        console.print("\n[yellow]Operation cancelled.[/yellow]")


def main():
    """Main application loop."""
    console.print(Panel(
        "[bold bright_cyan]WELCOME TO THE TODO CONSOLE APPLICATION[/bold bright_cyan]\n"
        "[italic bright_white]Your productivity companion for managing tasks efficiently[/italic bright_white]",
        border_style="bright_cyan",
        expand=False
    ))

    while True:
        display_menu()  # Show the improved menu
        choice = get_user_choice()

        if choice == 1:
            add_task_flow()
        elif choice == 2:
            view_tasks_flow()
        elif choice == 3:
            update_task_flow()
        elif choice == 4:
            delete_task_flow()
        elif choice == 5:
            toggle_completion_flow()
        elif choice == 6:
            console.print("\n[bold green]Thank you for using the Todo Application. Goodbye![/bold green]")
            console.print(Panel("[italic bright_white]Come back soon to manage your tasks![/italic bright_white]",
                              border_style="green"))
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


if __name__ == "__main__":
    main()