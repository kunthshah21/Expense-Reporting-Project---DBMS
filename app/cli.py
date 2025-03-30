# app/cli.py
from app import commands
import shlex

def main_cli():
    print("Expense CLI. Type 'help' for commands.")
    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd.lower() == 'exit':
            break
        process_command(cmd)

def process_command(cmd):
    parts = shlex.split(cmd)
    if not parts:
        return
    cmd_type = parts[0].lower()
    
    try:
        if cmd_type == 'login' and len(parts) == 3:
            commands.login(parts[1], parts[2])
        elif cmd_type == 'logout':
            commands.logout()
        elif cmd_type == 'add_user' and len(parts) == 4:
            commands.add_user(parts[1], parts[2], parts[3])
        elif cmd_type == 'add_expense' and len(parts) >= 6:
            tags = parts[5] if len(parts) > 5 else ''
            commands.add_expense(float(parts[1]), parts[2], parts[3], parts[4], parts[5], tags)
        # Add other command handlers
        else:
            print("Invalid command. Use 'help'.")
    except Exception as e:
        print(f"Error: {e}")

def show_help():
    print("""
    Commands:
    - login <username> <password>
    - logout
    - add_user <username> <password> <role> (Admin only)
    - add_expense <amount> <category> <payment> <date> <desc> [tags]
    - exit
    """)

if __name__ == "__main__":
    main_cli()