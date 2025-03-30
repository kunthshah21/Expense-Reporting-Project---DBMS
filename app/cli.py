# app/cli.py

from app import commands
import shlex

def main_cli():
    print("Welcome to the Expense Reporting CLI.")
    print("Type 'help' for a list of commands or 'exit' to quit.")
    
    while True:
        try:
            user_input = input(">> ").strip()
            if user_input.lower() == "exit":
                print("Exiting the CLI.")
                break
            elif user_input.lower() == "help":
                show_help()
            elif user_input:
                process_command(user_input)
        except Exception as e:
            print(f"Error: {e}")

def show_help():
    print("\nAvailable Commands:")
    print("------------------")
    print("user add <email> <role> <phone> - Add a new user")
    print("user list - List all users")
    print("category add <name> - Add a new category")
    print("category list - List all categories")
    print("payment add <method> - Add a new payment method")
    print("payment list - List all payment methods")
    print("tag add <name> - Add a new tag")
    print("tag list - List all tags")
    print("expense add <uid> <amount> <category_id> <payment_id> <date> <time> <description> - Add expense")
    print("expense list - List all expenses")
    print("expense update <id> <field> <value> - Update an expense")
    print("expense delete <id> - Delete an expense")
    print("exit - Exit the application")
    print("help - Show this help menu\n")

def process_command(cmd_str):
    try:
        # Parse the command into tokens
        tokens = shlex.split(cmd_str)
        if not tokens:
            return
            
        main_cmd = tokens[0].lower()
        
        if main_cmd == "user":
            if len(tokens) >= 2:
                if tokens[1] == "list":
                    commands.list_users()
                elif tokens[1] == "add" and len(tokens) >= 5:
                    commands.add_user(tokens[2], tokens[3], tokens[4])
                else:
                    print("Invalid user command format")
                    
        elif main_cmd == "category":
            if len(tokens) >= 2:
                if tokens[1] == "list":
                    commands.list_categories()
                elif tokens[1] == "add" and len(tokens) >= 3:
                    commands.add_category(tokens[2])
                else:
                    print("Invalid category command format")
                    
        elif main_cmd == "payment":
            if len(tokens) >= 2:
                if tokens[1] == "list":
                    commands.list_payment_methods()
                elif tokens[1] == "add" and len(tokens) >= 3:
                    commands.add_payment_method(tokens[2])
                else:
                    print("Invalid payment command format")
                    
        elif main_cmd == "tag":
            if len(tokens) >= 2:
                if tokens[1] == "list":
                    commands.list_tags()
                elif tokens[1] == "add" and len(tokens) >= 3:
                    commands.add_tag(tokens[2])
                else:
                    print("Invalid tag command format")
                    
        elif main_cmd == "expense":
            if len(tokens) >= 2:
                if tokens[1] == "list":
                    commands.list_expenses()
                elif tokens[1] == "add" and len(tokens) >= 8:
                    commands.add_expense(int(tokens[2]), float(tokens[3]), 
                                        int(tokens[4]), int(tokens[5]), 
                                        tokens[6], tokens[7], 
                                        " ".join(tokens[8:]) if len(tokens) > 8 else "")
                elif tokens[1] == "update" and len(tokens) >= 5:
                    commands.update_expense(int(tokens[2]), tokens[3], tokens[4])
                elif tokens[1] == "delete" and len(tokens) >= 3:
                    commands.delete_expense(int(tokens[2]))
                else:
                    print("Invalid expense command format")
        else:
            print(f"Unknown command: {main_cmd}")
                
    except Exception as e:
        print(f"Error processing command: {e}")
