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
        
        # Command: Update User
        # Usage: update_user <username> <field> <new_value>
        elif command == "update_user":
            if len(parts) == 4:
                if commands.update_user(parts[1], parts[2], parts[3]):
                    print(f"User '{parts[1]}' updated successfully.")
                else:
                    print("Failed to update user.")
            else:
                print("Usage: update_user <username> <field> <new_value>")

        # Command: Delete User
        # Usage: delete_user <username>
        elif command == "delete_user":
            if len(parts) == 2:
                if commands.delete_user(parts[1]):
                    print(f"User '{parts[1]}' deleted.")
                else:
                    print("Failed to delete user.")
            else:
                print("Usage: delete_user <username>")

        
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
                    category_lower = parts[1].strip().lower()
                    if commands.add_category(category_lower):
                        print(f"Category '{category_lower}' added")
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
        
                # Payment method management
                
        elif command == "add_expense":
            #add_expense(amount, category, payment_method, date, description, tags)
            if len(parts) >= 6:
                if commands.add_expense(parts[1], parts[2].strip().lower(), parts[3].strip().lower(), parts[4], parts[5], parts[6:]):
                    print("Expense added successfully.")
                else:
                    print("Failed to add the expense!")
                    print("Usage: add_expense <amount> <category> <payment_method> <date> <description> <list_of_tags (seperated by space)> ")
            else:
                print("Usage: add_expense <amount> <category> <payment_method> <date> <description> <list_of_tags (seperated by space)> ")

        # Input format: add_tag <tag_name>
        elif command == "add_tag":
            if len(parts) == 2:
                if commands.add_tag(parts[1]):
                    print(f"Tag '{parts[1]}' added.")
                else:
                    print("Failed to add tag. It may already exist.")
            else:
                print("Usage: add_tag <tag_name>")

        # Command: Delete Tag
        # Usage: delete_tag <tag_name>
        elif command == "delete_tag":
            if len(parts) == 2:
                if commands.delete_tag(parts[1]):
                    print(f"Tag '{parts[1]}' deleted.")
                else:
                    print(f"Failed to delete tag '{parts[1]}'.")
            else:
                print("Usage: delete_tag <tag_name>")

        # Input format: add_group <group_name> <description>
        elif command == "add_group":
            if len(parts) >= 3:
                group_name = parts[1]
                description = ' '.join(parts[2:])
                if commands.create_group(group_name, description):
                    print(f"Group '{group_name}' created.")
                else:
                    print("Failed to add group.")
            else:
                print("Usage: add_group <group_name> <description>")

        # Input format: add_group_expense <amount> <group_name> <category> <payment_method> <date> <description> <list_of_tags>
        elif command == "add_group_expense":
            if len(parts) >= 7:
                if commands.add_group_expense(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7:]):
                    print("Group expense added successfully.")
                else:
                    print("Failed to add group expense.")
            else:
                print("Usage: add_group_expense <amount> <group_name> <category> <payment_method> <date> <description> <list_of_tags>")
        
        # Command: Add User to Group
        # Usage: add_user_to_group <username> <group_name>
        elif command == "add_user_to_group":
            if len(parts) == 3:
                if commands.add_user_to_group(parts[1], parts[2]):
                    print(f"User '{parts[1]}' added to group '{parts[2]}'.")
                else:
                    print("Failed to add user to group.")
            else:
                print("Usage: add_user_to_group <username> <group_name>")

        
        
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
    
    Group commands: 
    add_group <group_name> <description>
    add_group_expense <amount> <group_name> <category> <payment_method> <date> <description> <list_of_tags>
    
          
    Import/Export:
    import_expenses <file.csv>
    export_csv <file.csv> sort-on <field>
    
    System:
    help
    exit
    """)

if __name__ == "__main__":
    main_cli()