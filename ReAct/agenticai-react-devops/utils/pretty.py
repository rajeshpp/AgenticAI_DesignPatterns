from rich import print


def print_thought(text: str):
    print(f"\n[bold purple]Thought:[/bold purple] {text}")


def print_action(action: str, action_input: str):
    print(f"[bold blue]Action:[/bold blue] {action}({action_input})")


def print_observation(obs):
    print(f"[green]Observation:[/green] {obs}")