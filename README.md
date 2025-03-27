# Expense Reporting Project - DBMS
 This is a DBMS project which deals with building a Expense reporting tool with a logic overview built in python and SQL as the backend

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project is a CLI tool designed to manage expense reporting with user authentication, expense management, and various reporting features. It uses SQLite as its database engine to keep things simple and self-contained.

## Project Structure

Below is an overview of the project structure along with a description of what each file/folder does:


- **README.md:**  
  Provides an overview, setup instructions, and documentation for the project.

- **requirements.txt:**  
  Lists Python dependencies. Since we use SQLite from the standard library, no external packages are needed at the moment. Future dependencies can be added here.

- **.gitignore:**  
  Ensures that unnecessary or sensitive files (e.g., compiled Python files, SQLite database file) are not committed to the repository.

- **config/config.py:**  
  Contains configuration settings (e.g., database type and SQLite file path). This centralizes configuration for easier modifications and environment-specific setups.

- **db/init_db.py:**  
  A script to initialize the database. It connects to SQLite, creates the necessary tables, and is used during the initial setup of the project.

- **db/schema.sql:**  
  An optional SQL script that can be used to set up database schemas manually or as part of a migration process.

- **app/__init__.py:**  
  Marks the `app` directory as a Python package, allowing for modular import and organization of code.

- **app/cli.py:**  
  Implements the command-line interface (CLI) loop. It reads user input and will eventually parse and delegate commands to appropriate functions.

- **app/commands.py:**  
  Contains stub implementations for various CLI commands (like login, add expense, etc.). These are the starting points for your business logic.

- **app/db.py:**  
  Provides functions to connect to the SQLite database and initialize it (e.g., create tables). This module abstracts the database operations.

- **main.py:**  
  The main entry point for the application. It starts the CLI and ties together the initialization and application logic.

## Setup and Installation

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   test - by kalash
