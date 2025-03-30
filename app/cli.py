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
        if cmd_type == 'help':
            show_help()
        elif cmd_type == 'login' and len(parts) == 3:
            commands.login(parts[1], parts[2])
        elif cmd_type == 'logout':
            commands.logout()
        elif cmd_type == 'add_user':
            if len(parts) == 4:
                commands.add_user(parts[1], parts[2], parts[3])
            elif len(parts) == 6:
                commands.add_user(parts[1], parts[2], parts[3], parts[4], parts[5])
            else:
                print("Invalid command format. Use 'add_user <username> <password> <role> [email] [phone]'")
        elif cmd_type == 'add_expense' and len(parts) >= 6:
            # Updated to work with timestamp instead of date
            tags = parts[6] if len(parts) > 6 else ''
            commands.add_expense(float(parts[1]), parts[2], parts[3], parts[4], parts[5], tags)
        elif cmd_type == 'list_users':
            commands.list_users()
        elif cmd_type == 'create_group' and len(parts) >= 2:
            description = parts[2] if len(parts) > 2 else None
            commands.create_group(parts[1], description)
        elif cmd_type == 'add_user_to_group' and len(parts) == 3:
            commands.add_user_to_group(parts[1], parts[2])
        elif cmd_type == 'add_group_expense' and len(parts) >= 7:
            # Format: add_group_expense <group_name> <amount> <category> <payment> <timestamp> <desc> [splits]
            splits = parts[7] if len(parts) > 7 else None
            commands.add_group_expense(parts[1], float(parts[2]), parts[3], parts[4], parts[5], parts[6], splits)
        elif cmd_type == 'report_category' and len(parts) == 2:
            commands.report_category_spending(parts[1])
        else:
            print("Invalid command. Use 'help' to see available commands.")
    except Exception as e:
        print(f"Error: {e}")

def show_help():
    print("""
    Commands:
    - login <username> <password>
    - logout
    - add_user <username> <password> <role> [email] [phone]
    - add_expense <amount> <category> <payment> <timestamp> <desc> [tags]
    - list_users
    - create_group <name> [description]
    - add_user_to_group <username> <group_name>
    - add_group_expense <group_name> <amount> <category> <payment> <timestamp> <desc> [splits]
    - report_category <category>
    - exit
    
    Note: For group expense splits, use format "user1:amount1,user2:amount2"
    """)

if __name__ == "__main__":
    main_cli()