from app import commands
import shlex
from datetime import datetime

def main_cli():
    print("Expense Management System")
    print("Type 'help' for commands\n")
    
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
            process_command(cmd)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def process_command(cmd):
    parts = shlex.split(cmd)
    if not parts:
        return
    
    command = parts[0].lower()
    
    try:
        if command == "help":
            show_help()
        
        # Authentication
        elif command == "login":
            if len(parts) == 3:
                if commands.login(parts[1], parts[2]):
                    print("Login successful")
                else:
                    print("Invalid credentials")
            else:
                print("Usage: login <username> <password>")
        
        elif command == "logout":
            commands.logout()
            print("Logged out")
        
        # User management
        elif command == "add_user":
            if len(parts) == 4:
                if commands.add_user(parts[1], parts[2], parts[3]):
                    print("User added")
                else:
                    print("Failed to add user")
            else:
                print("Usage: add_user <username> <password> <role>")
        
        elif command == "list_users":
            if commands.current_user.get('role') == 'Admin':
                users = commands.list_users()
                for user in users:
                    print(f"ID: {user['uid']} | User: {user['username']} | Role: {user['role']}")
            else:
                print("Permission denied")
        
        # Category management
        elif command == "add_category":
            if len(parts) == 2:
                if commands.current_user.get('role') == 'Admin':
                    if commands.add_category(parts[1]):
                        print(f"Category '{parts[1]}' added")
                    else:
                        print("Failed to add category")
                else:
                    print("Permission denied. Only admins can add categories.")
            else:
                print("Usage: add_category <name>")
        
        # Payment method management
        elif command == "add_payment_method":
            if len(parts) == 2:
                if commands.current_user.get('role') == 'Admin':
                    if commands.add_payment_method(parts[1]):
                        print(f"Payment method '{parts[1]}' added")
                    else:
                        print("Failed to add payment method")
                else:
                    print("Permission denied. Only admins can add payment methods.")
            else:
                print("Usage: add_payment_method <name>")
        
        # [Rest of your existing command handlers...]
        
        else:
            print("Invalid command")

    except Exception as e:
        print(f"Error: {str(e)}")

def show_help():
    print("""
    Available Commands:
    ------------------
    Authentication:
    login <username> <password>
    logout
    
    User Management (Admin only):
    add_user <username> <password> <role>
    list_users
    
    Category Management (Admin only):
    add_category <name>
    list_categories
    
    Payment Methods (Admin only):
    add_payment_method <name>
    list_payment_methods
    
    Expense Management:
    add_expense <amount> <category> <payment_method> <date> <description> <tag>
    update_expense <id> <field> <value>
    delete_expense <id>
    list_expenses [--category=] [--date=] [--min-amount=] [--max-amount=] [--payment=] [--tag=]
    
    Import/Export:
    import_expenses <file.csv>
    export_csv <file.csv> sort-on <field>
    
    System:
    help
    exit
    """)

if __name__ == "__main__":
    main_cli()