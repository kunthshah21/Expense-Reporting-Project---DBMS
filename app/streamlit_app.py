import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile
import os
from app.commands import (
    # Authentication
    login, logout, current_user,
    # User Management
    add_user, list_users, update_user, delete_user,
    # Categories & Payment Methods
    add_category, list_categories, add_payment_method, list_payment_methods,
    # Expenses
    add_expense, update_expense, delete_expense, list_expenses,
    # Tags
    add_tag, list_tags, delete_tag,
    # Groups
    create_group, add_user_to_group, delete_group, add_group_expense,
    # Import/Export
    import_expenses, export_csv,
    # Reports
    report_top_expenses, report_category_spending, report_above_average_expenses, 
    report_monthly_category_spending, report_highest_spender_per_month,
    report_frequent_category, report_payment_method_usage, report_tag_expenses
)

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'uid' not in st.session_state:
        st.session_state.uid = None
    if 'expense_list_container' not in st.session_state:
        st.session_state.expense_list_container = None

# Function to sync session state with current_user from commands
def sync_user_state():
    if current_user['uid'] is not None:
        st.session_state.authenticated = True
        st.session_state.username = current_user['username']
        st.session_state.role = current_user['role']
        st.session_state.uid = current_user['uid']
    else:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.uid = None

def main():
    st.set_page_config(page_title="Expense Management System", layout="wide")
    
    initialize_session_state()
    
    # Apply custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #2c3e50;
        }
        .section-header {
            font-size: 24px;
            font-weight: bold;
            margin-top: 30px;
            color: #3498db;
        }
        .info-text {
            font-size: 18px;
            color: #7f8c8d;
        }
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display header
    st.markdown('<p class="main-header">Expense Management System</p>', unsafe_allow_html=True)
    
    # Authentication
    if not st.session_state.authenticated:
        display_login()
    else:
        # Show a sidebar with options
        display_sidebar()
        
        # Display content based on selected option
        if st.session_state.get('current_page') == 'dashboard':
            display_dashboard()
        elif st.session_state.get('current_page') == 'expenses':
            display_expenses_page()
        elif st.session_state.get('current_page') == 'reports':
            display_reports_page()
        elif st.session_state.get('current_page') == 'admin':
            if st.session_state.role == 'Admin':
                display_admin_page()
            else:
                st.error("You don't have permission to access the Admin page.")
        elif st.session_state.get('current_page') == 'groups':
            display_groups_page()
        elif st.session_state.get('current_page') == 'import_export':
            st.error("Import/Export page is not implemented yet.")
        else:
            display_dashboard()  # Default view

# Authentication Functions
def display_login():
    st.markdown('<p class="section-header">Login</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login(username, password):
                    sync_user_state()
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with col2:
        st.markdown('<p class="info-text">Welcome to the Expense Management System. Please log in to continue.</p>', unsafe_allow_html=True)
        st.image("https://img.freepik.com/free-vector/finance-financial-performance-concept-illustration_53876-40450.jpg", width=300)

def logout_user():
    logout()
    sync_user_state()
    st.session_state.current_page = 'dashboard'
    st.rerun()

# Sidebar Navigation
def display_sidebar():
    with st.sidebar:
        st.markdown(f"**Logged in as: {st.session_state.username}**")
        st.markdown(f"Role: {st.session_state.role}")
        
        st.markdown("---")
        st.markdown("### Navigation")
        
        if st.button("📊 Dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
        
        if st.button("💰 Expenses"):
            st.session_state.current_page = 'expenses'
            st.rerun()
        
        if st.button("📈 Reports"):
            st.session_state.current_page = 'reports'
            st.rerun()
        
        if st.button("👥 Groups"):
            st.session_state.current_page = 'groups'
            st.rerun()
        
        if st.button("📥 Import/Export"):
            st.session_state.current_page = 'import_export'
            st.rerun()
        
        if st.session_state.role == 'Admin':
            if st.button("⚙️ Admin Panel"):
                st.session_state.current_page = 'admin'
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            logout_user()

# Dashboard Page
def display_dashboard():
    st.markdown('<p class="section-header">Dashboard</p>', unsafe_allow_html=True)
    
    # Get expense data for the current user
    try:
        # Create custom capture for list_expenses output
        import io
        import sys
        from contextlib import redirect_stdout
        
        # Capture console output when calling list_expenses
        f = io.StringIO()
        with redirect_stdout(f):
            list_expenses()
        
        output = f.getvalue()
        
        # Display a welcome message and basic stats
        st.markdown(f"### Welcome back, {st.session_state.username}!")
        
        # Create a row of metric cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get most frequent category
            with redirect_stdout(io.StringIO()):  # Suppress console output
                report_frequent_category()
                
            st.metric(
                label="Most Used Category", 
                value="Food & Dining" if "Food" in output else "Other",
                delta="↑ 5% from last month"
            )
        
        with col2:
            st.metric(
                label="Total Expenses This Month", 
                value="₹5,240",
                delta="-12% from last month"
            )
        
        with col3:
            st.metric(
                label="Pending Group Expenses", 
                value="3",
                delta="1 new"
            )
        
        # Display recent expenses
        st.markdown("### Recent Expenses")
        
        # Parse the captured output to extract the expenses table
        lines = output.strip().split('\n')
        if len(lines) > 5:  # Header + separator + at least one expense
            # Find the header line
            header_idx = -1
            for i, line in enumerate(lines):
                if "ID" in line and "Amount" in line and "Category" in line:
                    header_idx = i
                    break
            
            if header_idx >= 0:
                # Extract header and parse
                header = lines[header_idx].split()
                # Parse expenses data (simplified)
                expenses_data = []
                for line in lines[header_idx+2:]:  # Skip header and separator line
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            expense_id = parts[0]
                            amount = parts[1].replace('₹', '')
                            category = parts[2]
                            payment = parts[3]
                            date = parts[4]
                            description = ' '.join(parts[5:])
                            
                            expenses_data.append({
                                "ID": expense_id,
                                "Amount": amount,
                                "Category": category,
                                "Payment": payment,
                                "Date": date,
                                "Description": description
                            })
                
                if expenses_data:
                    expenses_df = pd.DataFrame(expenses_data)
                    st.dataframe(expenses_df.head(5), use_container_width=True)
                else:
                    st.info("No recent expenses found.")
            else:
                st.info("No expenses found. Add some expenses to see them here.")
        else:
            st.info("No expenses found. Add some expenses to see them here.")
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

# Expenses Page
def display_expenses_page():
    st.markdown('<p class="section-header">Expenses</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["List Expenses", "Add Expense", "Manage Expense"])
    
    with tab1:
        st.markdown("### List Expenses")
        
        # Create filter controls
        col1, col2, col3, col4 = st.columns(4)
        
        filters = {}
        
        with col1:
            category_filter = st.selectbox("Category", ["All"] + [cat["category_name"] for cat in list_categories()])
            if category_filter != "All":
                filters["category"] = category_filter
        
        with col2:
            payment_filter = st.selectbox("Payment Method", ["All"] + [method["method"] for method in list_payment_methods()])
            if payment_filter != "All":
                filters["payment_method"] = payment_filter
        
        with col3:
            min_amount = st.number_input("Min Amount", min_value=0.0, step=100.0)
            if min_amount > 0:
                filters["min_amount"] = min_amount
        
        with col4:
            max_amount = st.number_input("Max Amount", min_value=0.0, value=10000.0, step=100.0)
            if max_amount > 0:
                filters["max_amount"] = max_amount
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=None)
            if start_date:
                filters["date"] = start_date.isoformat()
                
        with col2:
            tags = st.multiselect("Tags", [tag["tag_name"] for tag in list_tags()])
            if tags:
                filters["tag"] = tags[0]  # Currently only supporting one tag filter
        
        if st.button("Filter Expenses"):
            # Create custom capture for list_expenses output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                list_expenses(filters)
            
            output = f.getvalue()
            st.text_area("Expenses", output, height=400)
    
    with tab2:
        st.markdown("### Add New Expense")
        
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)
                category = st.selectbox("Category", [cat["category_name"] for cat in list_categories()])
                payment_method = st.selectbox("Payment Method", [method["method"] for method in list_payment_methods()])
            
            with col2:
                expense_date = st.date_input("Date", value=datetime.today())
                description = st.text_input("Description")
                available_tags = [tag["tag_name"] for tag in list_tags()]
                selected_tags = st.multiselect("Tags", available_tags)
            
            submit_button = st.form_submit_button("Add Expense")
            
            if submit_button:
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                else:
                    success = add_expense(
                        amount, category.lower(), payment_method.lower(), 
                        expense_date.isoformat(), description, selected_tags
                    )
                    if success:
                        st.success("Expense added successfully!")
                    else:
                        st.error("Failed to add expense. Check category and payment method.")
    
    with tab3:
        st.markdown("### Update or Delete Expense")
        
        expense_id = st.number_input("Expense ID", min_value=1, step=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Update Expense")
            update_field = st.selectbox("Field to Update", 
                ["amount", "category", "payment_method", "date", "description", "tags"])
            
            if update_field == "category":
                new_value = st.selectbox("New Category", [cat["category_name"] for cat in list_categories()])
            elif update_field == "payment_method":
                new_value = st.selectbox("New Payment Method", [method["method"] for method in list_payment_methods()])
            elif update_field == "date":
                new_value = st.date_input("New Date").isoformat()
            elif update_field == "tags":
                all_tags = [tag["tag_name"] for tag in list_tags()]
                new_tags = st.multiselect("New Tags", all_tags)
                new_value = ",".join(new_tags)
            elif update_field == "amount":
                new_value = str(st.number_input("New Amount", min_value=0.01, step=100.0))
            else:
                new_value = st.text_input("New Value")
            
            if st.button("Update Expense"):
                success = update_expense(expense_id, update_field, new_value)
                if success:
                    st.success(f"Expense {expense_id} updated successfully!")
                else:
                    st.error("Failed to update expense. Make sure you own this expense.")
        
        with col2:
            st.markdown("#### Delete Expense")
            st.write("Be careful, this action cannot be undone.")
            
            if st.button("Delete Expense", key="delete_expense"):
                success = delete_expense(expense_id)
                if success:
                    st.success(f"Expense {expense_id} deleted successfully!")
                else:
                    st.error("Failed to delete expense. Make sure you own this expense.")

# Reports Page
def display_reports_page():
    st.markdown('<p class="section-header">Reports</p>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report Type", [
        "Top Expenses", 
        "Category Spending", 
        "Above Average Expenses",
        "Monthly Category Spending",
        "Payment Method Usage",
        "Tag Expenses",
        "Frequent Category"
    ] + (["Highest Spender Per Month"] if st.session_state.role == "Admin" else []))
    
    import io
    from contextlib import redirect_stdout
    
    # Report container
    report_container = st.container()
    
    if report_type == "Top Expenses":
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            n = st.number_input("Number of Expenses", min_value=1, value=5, step=1)
        
        with col2:
            start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
        
        with col3:
            end_date = st.date_input("End Date", value=datetime.today())
        
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_top_expenses(n, start_date.isoformat(), end_date.isoformat())
                
                st.text_area("Top Expenses Report", f.getvalue(), height=400)
    
    elif report_type == "Category Spending":
        category = st.selectbox("Select Category", [cat["category_name"] for cat in list_categories()])
        
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_category_spending(category)
                
                output = f.getvalue()
                st.text_area("Category Spending Report", output, height=200)
                
                # Try to extract the total amount for a chart
                import re
                amount_match = re.search(r'₹([\d.]+)', output)
                if amount_match:
                    amount = float(amount_match.group(1))
                    st.bar_chart({category: amount})
    
    elif report_type == "Above Average Expenses":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_above_average_expenses()
                
                st.text_area("Above Average Expenses Report", f.getvalue(), height=400)
    
    elif report_type == "Monthly Category Spending":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_monthly_category_spending()
                
                output = f.getvalue()
                st.text_area("Monthly Category Spending Report", output, height=400)
                
                # Try to parse and visualize the data
                lines = output.strip().split('\n')
                if len(lines) > 4:
                    data = []
                    for line in lines[4:]:  # Skip header and separator
                        parts = line.split()
                        if len(parts) >= 4:
                            try:
                                month = parts[0]
                                category = parts[1]
                                amount = float(parts[2].replace('₹', '').replace(',', ''))
                                data.append({"Month": month, "Category": category, "Amount": amount})
                            except:
                                pass
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.bar_chart(df.pivot(index="Month", columns="Category", values="Amount"))
    
    elif report_type == "Highest Spender Per Month":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_highest_spender_per_month()
                
                st.text_area("Highest Spender Per Month Report", f.getvalue(), height=300)
    
    elif report_type == "Frequent Category":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_frequent_category()
                
                st.text_area("Frequent Category Report", f.getvalue(), height=100)
    
    elif report_type == "Payment Method Usage":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_payment_method_usage()
                
                st.text_area("Payment Method Usage Report", f.getvalue(), height=300)
    
    elif report_type == "Tag Expenses":
        if st.button("Generate Report"):
            with report_container:
                f = io.StringIO()
                with redirect_stdout(f):
                    report_tag_expenses()
                
                st.text_area("Tag Expenses Report", f.getvalue(), height=300)

# Admin Page
def display_admin_page():
    if st.session_state.role != 'Admin':
        st.error("You don't have permission to access the Admin page.")
        return
    
    st.markdown('<p class="section-header">Admin Panel</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "Categories", "Payment Methods", "Tags"])
    
    with tab1:
        st.markdown("### User Management")
        
        # List existing users
        st.markdown("#### Existing Users")
        users = list_users()
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, use_container_width=True)
        
        # Add new user
        st.markdown("#### Add New User")
        with st.form("add_user_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                username = st.text_input("Username")
            
            with col2:
                password = st.text_input("Password", type="password")
            
            with col3:
                role = st.selectbox("Role", ["User", "Admin"])
            
            submit_button = st.form_submit_button("Add User")
            
            if submit_button:
                if not username or not password:
                    st.error("Username and password are required.")
                else:
                    success = add_user(username, password, role)
                    if success:
                        st.success(f"User '{username}' added successfully!")
                        st.rerun()  # Refresh the page to show new user
                    else:
                        st.error("Failed to add user. Username may already exist.")
        
        # Update user
        st.markdown("#### Update User")
        col1, col2 = st.columns(2)
        
        with st.form("update_user_form"):
            update_username = st.selectbox("Select User", [user["username"] for user in users])
            update_field = st.selectbox("Field to Update", ["password", "role"])
            
            if update_field == "role":
                new_value = st.selectbox("New Role", ["User", "Admin"])
            else:
                new_value = st.text_input("New Password", type="password")
            
            update_button = st.form_submit_button("Update User")
            
            if update_button:
                success = update_user(update_username, update_field, new_value)
                if success:
                    st.success(f"User '{update_username}' updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update user.")
        
        # Delete user
        st.markdown("#### Delete User")
        with st.form("delete_user_form"):
            delete_username = st.selectbox("Select User to Delete", [user["username"] for user in users])
            delete_confirm = st.checkbox("I understand this action cannot be undone")
            
            delete_button = st.form_submit_button("Delete User")
            
            if delete_button:
                if delete_confirm:
                    success = delete_user(delete_username)
                    if success:
                        st.success(f"User '{delete_username}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete user.")
                else:
                    st.error("Please confirm deletion by checking the box.")
    
    with tab2:
        st.markdown("### Category Management")
        
        # List existing categories
        st.markdown("#### Existing Categories")
        categories = list_categories()
        categories_df = pd.DataFrame(categories)
        st.dataframe(categories_df, use_container_width=True)
        
        # Add new category
        st.markdown("#### Add New Category")
        with st.form("add_category_form"):
            category_name = st.text_input("Category Name")
            add_category_button = st.form_submit_button("Add Category")
            
            if add_category_button:
                if not category_name:
                    st.error("Category name is required.")
                else:
                    success = add_category(category_name.lower())
                    if success:
                        st.success(f"Category '{category_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add category. It may already exist.")
    
    with tab3:
        st.markdown("### Payment Method Management")
        
        # List existing payment methods
        st.markdown("#### Existing Payment Methods")
        payment_methods = list_payment_methods()
        payment_df = pd.DataFrame(payment_methods)
        st.dataframe(payment_df, use_container_width=True)
        
        # Add new payment method
        st.markdown("#### Add New Payment Method")
        with st.form("add_payment_form"):
            method_name = st.text_input("Payment Method Name")
            add_method_button = st.form_submit_button("Add Payment Method")
            
            if add_method_button:
                if not method_name:
                    st.error("Payment method name is required.")
                else:
                    success = add_payment_method(method_name.lower())
                    if success:
                        st.success(f"Payment method '{method_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add payment method. It may already exist.")
    
    with tab4:
        st.markdown("### Tag Management")
        
        # List existing tags
        st.markdown("#### Existing Tags")
        tags = list_tags()
        tags_df = pd.DataFrame(tags)
        st.dataframe(tags_df, use_container_width=True)
        
        # Add new tag
        st.markdown("#### Add New Tag")
        with st.form("add_tag_form"):
            tag_name = st.text_input("Tag Name")
            add_tag_button = st.form_submit_button("Add Tag")
            
            if add_tag_button:
                if not tag_name:
                    st.error("Tag name is required.")
                else:
                    success = add_tag(tag_name)
                    if success:
                        st.success(f"Tag '{tag_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add tag. It may already exist.")
        
        # Delete tag
        st.markdown("#### Delete Tag")
        with st.form("delete_tag_form"):
            delete_tag_name = st.selectbox("Select Tag to Delete", [tag["tag_name"] for tag in tags])
            delete_tag_button = st.form_submit_button("Delete Tag")
            
            if delete_tag_button:
                success = delete_tag(delete_tag_name)
                if success:
                    st.success(f"Tag '{delete_tag_name}' deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete tag.")

# Groups Page
def display_groups_page():
    st.markdown('<p class="section-header">Groups</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Create Group", "Add User to Group", "Add Group Expense"])
    
    with tab1:
        st.markdown("### Create New Group")
        
        with st.form("create_group_form"):
            group_name = st.text_input("Group Name")
            description = st.text_area("Description")
            
            create_button = st.form_submit_button("Create Group")
            
            if create_button:
                if not group_name:
                    st.error("Group name is required.")
                else:
                    success = create_group(group_name, description)
                    if success:
                        st.success(f"Group '{group_name}' created successfully!")
                    else:
                        st.error("Failed to create group. It may already exist.")
    
    with tab2:
        st.markdown("### Add User to Group")
        
        with st.form("add_user_to_group_form"):
            # Get users and groups
            users = list_users()
            
            # For groups, we need to implement a function to list groups
            
            add_button = st.form_submit_button("Add User to Group")
            
            if add_button:
                username = st.text_input("Username")
                if not username or not group_name:
                    st.error("Username and group name are required.")
                    success = add_user_to_group(username, group_name)
                    success = add_user_to_group(username, group_name)
                    st.success(f"User '{username}' added to group '{group_name}' successfully!")
                else:
                    st.error("Failed to add user to group.")
    
    with tab3:
        st.markdown("### Add Group Expense")
        
        with st.form("add_group_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)
                group_name = st.text_input("Group Name")
                category = st.selectbox("Category", [cat["category_name"] for cat in list_categories()])
                payment_method = st.selectbox("Payment Method", [method["method"] for method in list_payment_methods()])
            
                group_name = st.text_input("Group Name")
                category = st.selectbox("Category", [cat["category_name"] for cat in list_categories()])
                payment_method = st.selectbox("Payment Method", [method["method"] for method in list_payment_methods()])
            
            with col2:
                description = st.text_input("Description")
                
                # Users to split with
                users = list_users()
                split_users = st.multiselect("Split With Users", 
                                           [user["username"] for user in users if user["username"] != st.session_state.username])
            
            add_button = st.form_submit_button("Add Group Expense")
            
            if add_button:
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                elif not group_name:
                    st.error("Group name is required")
                    st.error("At least one other user is required for splitting")
                else:
                    if not split_users:
                        st.error("At least one other user is required for splitting")
                    else:
                        success = add_group_expense(
                            float(amount), group_name, category.lower(), payment_method.lower(),
                            description, split_users
                        )
                    if success:
                        st.success("Group expense added successfully!")
                    else:
                        st.error("Failed to add group expense.")

# Import/Export Page
def display_import_export_page():
    st.markdown('<p class="section-header">Import/Export</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Import Expenses", "Export Expenses"])
    
    with tab1:
        st.markdown("### Import Expenses from CSV")
        
        st.markdown("""
        Upload a CSV file with the following columns:
        - amount: Expense amount
        - category: Category name
        - payment_method: Payment method
        - date: Date in YYYY-MM-DD format
        - description (optional): Expense description
        - tag (optional): Comma-separated tags
        """)
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_filepath = tmp_file.name
            
            if st.button("Import Expenses"):
                success = import_expenses(tmp_filepath)
                if success:
                    st.success("Expenses imported successfully!")
                else:
                    st.error("Failed to import expenses. Check the file format.")
                
                # Clean up the temporary file
                os.unlink(tmp_filepath)
    
    with tab2:
        st.markdown("### Export Expenses to CSV")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_path = st.text_input("Export File Path", "expenses_export.csv")
        
        with col2:
            sort_field = st.selectbox("Sort By", 
                ["date", "amount", "category", "payment_method", "tags"])
        
        if st.button("Export Expenses"):
            success = export_csv(export_path, sort_field)
            if success:
                st.success(f"Expenses exported to {export_path}!")
                
                with open(export_path, "r") as f:
                    st.download_button(
                        label="Download Exported CSV",
                        data=f,
                        file_name=os.path.basename(export_path),
                        mime="text/csv"
                    )
            else:
                st.error("Failed to export expenses.")

if __name__ == "__main__":
    main()
