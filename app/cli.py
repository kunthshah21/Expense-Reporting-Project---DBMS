# app/cli.py

from app import commands

def main_cli():
    print("Welcome to the Expense Reporting CLI.")
    print("Type 'exit' to quit.")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() == "exit":
            print("Exiting the CLI.")
            break
        # For now, simply print out the received command.
        print(f"Received command: {user_input}")
        # In the future, parse the input and dispatch to functions in commands.py
