from app import commands
import shlex
from datetime import datetime

# Add a helper function to check login status
def check_login():
    if not commands.current_user or not commands.current_user.get('uid'):
        print("You must be logged in to use this command.")
        return False
    return True

# Modify the main_cli function's loop:


def main_cli():
    print("Expense Management System")
    print("Type 'help' for commands\n")

    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
            if cmd.lower() == 'exit':
                print("Exiting...")
                break
            process_command(cmd)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except SystemExit:
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
            if not check_login():
                return
                
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
            if not check_login():
                return
                
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
            if not check_login():
                return
                
            if len(parts) == 2:
                if commands.delete_user(parts[1]):
                    print(f"User '{parts[1]}' deleted.")
                else:
                    print("Failed to delete user.")
            else:
                print("Usage: delete_user <username>")

        elif command == "list_users":
            if not check_login():
                return
                
            if commands.current_user.get('role') == 'Admin':
                users = commands.list_users()
                for user in users:
                    print(
                        f"ID: {user['uid']} | User: {user['username']} | Role: {user['role']}")
            else:
                print("Permission denied")

        # Category management
        elif command == "add_category":
            if not check_login():
                return
                
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
            if not check_login():
                return
                
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

                # In process_command() function:
        elif command == "add_expense":
            if not check_login():
                return
                
            if len(parts) >= 6:
                try:
                    amount = float(parts[1])
                    if amount <= 0:
                        raise ValueError
                    category = parts[2].strip().lower()
                    payment_method = parts[3].strip().lower()
                    date = datetime.strptime(parts[4], '%Y-%m-%d').date()
                    description = parts[5]
                    tags = []

                    if len(parts) > 6:
                        tags = [tag.strip() for tag in parts[6].split(",")]

                    if commands.add_expense(amount, category, payment_method,
                                            date.isoformat(), description, tags):
                        print("Expense added successfully.")
                    else:
                        print("Failed to add expense. Check category/payment method.")
                except ValueError:
                    print(
                        "Invalid amount/date format. Use positive numbers and YYYY-MM-DD")
            else:
                print(
                    "Usage: add_expense <amount> <category> <payment_method> <YYYY-MM-DD> <description> [tags]")

                # In process_command() for list_expenses:
        elif command == "list_expenses":
            if not commands.current_user or not commands.current_user.get('uid'):
                print("Please login first")
                return
            
            filters = {}
            for arg in parts[1:]:
                if arg.startswith("--"):
                    key_value = arg[2:].split("=", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        # Handle amount range special case
                        if key == "amount":
                            if '-' in value:
                                min_val, max_val = value.split('-', 1)
                                filters['min_amount'] = min_val
                                filters['max_amount'] = max_val
                            else:
                                print("Invalid amount format. Use min-max")
                                return
                        else:
                            filters[key.replace("-", "_")] = value
            commands.list_expenses(filters)

        # Replace current update_expense handler with:
        elif command == "update_expense":
            if not check_login(): return
            
            if len(parts) == 4:
                try:
                    expense_id = int(parts[1])
                    field = parts[2].lower()
                    new_value = parts[3]
                    
                    if field == 'tags':  # Special handling for tags
                        new_value = new_value.split(',')
                    
                    if commands.update_expense(expense_id, field, new_value):
                        print(f"Expense {expense_id} updated")
                    else:
                        print("Update failed. Check if you own this expense.")
                except ValueError:
                    print("Error: Expense ID must be a number")
            else:
                print("Usage: update_expense <ID> <field> <new_value>")
                print("Fields: amount, date, description, category, payment_method, tags")

                # Replace current delete_expense handler with:
        elif command == "delete_expense":
            if not check_login(): return
            
            if len(parts) == 2:
                try:
                    if commands.delete_expense(int(parts[1])):
                        print("Expense deleted")
                    else:
                        print("Delete failed. Check if you own this expense.")
                except ValueError:
                    print("Error: Expense ID must be a number")
            else:
                print("Usage: delete_expense <ID>")

        # Input format: add_tag <tag_name>
        elif command == "add_tag":
            if not check_login():
                return
                
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
            if not check_login():
                return
                
            if len(parts) == 2:
                if commands.delete_tag(parts[1]):
                    print(f"Tag '{parts[1]}' deleted.")
                else:
                    print(f"Failed to delete tag '{parts[1]}'.")
            else:
                print("Usage: delete_tag <tag_name>")

        # Input format: add_group <group_name> <description>
        elif command == "add_group":
            if not check_login():
                return
                
            if len(parts) >= 3:
                group_name = parts[1]
                description = ' '.join(parts[2:])
                if commands.create_group(group_name, description):
                    print(f"Group '{group_name}' created.")
                else:
                    print("Failed to add group.")
            else:
                print("Usage: add_group <group_name> <description>")

        # add group expense
        elif command == "add_group_expense":
            if not check_login():
                return
                
            if len(parts) >= 7:
                # Extract required parameters
                amount = parts[1]
                group_name = parts[2]
                category = parts[3]
                payment_method = parts[4]
                date = parts[5]
                description = parts[6]

                # Handle tags and split users
                tags = []
                split_usernames = []

                if "|" in parts[7]:  # Check if both lists are provided
                    tag_part, user_part = parts[7].split("|", 1)
                    tags = [tag.strip()
                            for tag in tag_part.split(",") if tag.strip()]
                    split_usernames = [
                        user.strip() for user in user_part.split(",") if user.strip()]
                else:
                    tags = [tag.strip() for tag in parts[7].split(
                        ",") if tag.strip()]  # Only tags provided

                # Call the function with parsed arguments
                if commands.add_group_expense(amount, group_name, category, payment_method, date, description, tags, split_usernames):
                    print("Group expense added successfully.")
                else:
                    print("Failed to add group expense.")
            else:
                print("Usage: add_group_expense <amount> <group_name> <category> <payment_method> <date> <description> <comma-separated-tags> | <comma-separated-usernames>")

        # Command: Add User to Group
        # Usage: add_user_to_group <username> <group_name>
        elif command == "add_user_to_group":
            if not check_login():
                return
                
            if len(parts) == 3:
                if commands.add_user_to_group(parts[1], parts[2]):
                    print(f"User '{parts[1]}' added to group '{parts[2]}'.")
                else:
                    print("Failed to add user to group.")
            else:
                print("Usage: add_user_to_group <username> <group_name>")

        # In the 'process_command' function, add these elif blocks:

                # In process_command() function:
        elif command == "import_expenses":
            if not check_login():
                return
                
            if len(parts) == 2:
                if commands.import_expenses(parts[1]):
                    print("Import completed")
            else:
                print("Usage: import_expenses <file_path>")

        elif command == "export_csv":
            if not check_login():
                return
                
            if len(parts) >= 4 and parts[-2] == "sort-on":
                file_path = ' '.join(parts[1:-2]).rstrip(',')
                sort_field = parts[-1]
                if commands.export_csv(file_path, sort_field):
                    print(f"Exported to {file_path}")
            else:
                print("Usage: export_csv <file_path>, sort-on <field_name>")

        elif command == "list_categories":
            if not check_login():
                return
                
            categories = commands.list_categories()
            print("Categories:")
            for idx, cat in enumerate(categories, 1):
                print(f"{idx}. {cat['category_name']}")

        elif command == "list_payment_methods":
            if not check_login():
                return
                
            methods = commands.list_payment_methods()
            print("Payment Methods:")
            for idx, method in enumerate(methods, 1):
                print(f"{idx}. {method['method']}")

                # In process_command() function:
        elif command == "report":
            if not check_login():
                return
                
            if len(parts) < 2:
                print("Invalid report command")
                return

            subcmd = parts[1].lower()

            try:
                if subcmd == "top_expenses":
                    if len(parts) >= 5 and parts[2].isdigit() and parts[3] == "date-range":
                        n = int(parts[2])
                        # Join the remaining parts to handle dates that might contain spaces
                        date_range = ' '.join(parts[4:]).split(" to ")
                        if len(date_range) == 2:
                            start_date = date_range[0].strip()
                            end_date = date_range[1].strip()
                            commands.report_top_expenses(
                                n, start_date, end_date)
                        else:
                            print(
                                "Invalid date range format. Use 'date-range <start_date> to <end_date>'")
                    else:
                        print(
                            "Usage: report top_expenses <N> date-range <start_date> to <end_date>")

                elif subcmd == "category_spending":
                    if len(parts) == 3:
                        commands.report_category_spending(parts[2])
                    else:
                        print("Usage: report category_spending <category>")

                elif subcmd == "above_average_expenses":
                    commands.report_above_average_expenses()

                elif subcmd == "monthly_category_spending":
                    commands.report_monthly_category_spending()

                elif subcmd == "highest_spender_per_month":
                    # Check admin role using commands module's current_user
                    if not commands.current_user or commands.current_user.get('role') != 'Admin':
                        print("This report is only available for admins")
                    else:
                        commands.report_highest_spender_per_month()

                elif subcmd == "frequent_category":
                    commands.report_frequent_category()

                elif subcmd == "payment_method_usage":
                    commands.report_payment_method_usage()
                
                elif subcmd == "tag_expenses":
                    commands.report_tag_expenses()

                else:
                    print("Invalid report type")

            except ValueError:
                print(
                    "Invalid arguments. N must be a number and date format should be YYYY-MM-DD")
            except Exception as e:
                print(f"Report error: {str(e)}")

        elif command == "exit":
            print("Exiting...")
            raise SystemExit
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
    add_group_expense add_group_expense <amount> <group_name> <category> <payment_method> <date> <description> <comma-separated-tags> | <comma-separated-usernames>
    
          
    Import/Export:
    import_expenses <file.csv>
    export_csv <file.csv> sort-on <field>
    
    System:
    help
    exit
    """)


if __name__ == "__main__":
    main_cli()
