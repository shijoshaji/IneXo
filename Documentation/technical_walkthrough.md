# Technical Walkthrough: IneX̂ō

This document provides a comprehensive technical explanation of the **IneX̂ō** application. It is designed to help improve understanding of "what the code does" line-by-line and how different components connect.

---

## 1. Overview & Architecture

**IneX̂ō** is a personal finance management application built using:

- **Streamlit (`app.py`)**: The frontend framework that handles the User Interface (UI) and interactivity.
- **Python (Backend)**: Handles logic and data processing.
- **SQLite (`finance.db`)**: A local relational database to store users, transactions, and categories.
- **Plotly**: Used for generating interactive charts (Pie charts, etc.).

### **File Structure Logic**

1.  **`run_finance_tracker.bat`**: The **Start Button**. This script sets up the environment and launches the app.
2.  **`app.py`**: The **Brain & Face**. It defines how the app looks and reacts to user clicks.
3.  **`database.py`**: The **Memory**. It handles saving, retrieving, and updating data in the database file.
4.  **`finance_utils.py`**: The **Translator**. Converts numbers to words (e.g., "Five Hundred") and formats currency symbols dynamically.
5.  **`requirements.txt`**: The **Toolbox**. Lists all external Python libraries needed.

---

## 2. Step 1: Running the Application (`run_finance_tracker.bat`)

When you double-click this file, the following happens:

1.  **`call venv\Scripts\activate`**: This command "wakes up" the isolated Python environment (`venv`) where all your specific tools (Streamlit, Pandas) are installed. This ensures the app doesn't conflict with other Python programs on your computer.
2.  **`streamlit run app.py`**: This launches the web server.
3.  **`start /B powershell ... inexo_auto_backup_db.ps1`**: Concurrently, a background job starts to watch your database and automatically backup changes to Git every 15 minutes.

---

## 3. Step 2: The Database Layer (`database.py`)

This file is the **backend foundation**. It doesn't show anything on the screen; it simply answers questions from `app.py` (e.g., "Give me all transactions") or follows commands (e.g., "Save this expense").

### **Key Components:**

1.  **Connection (`get_connection`)**:
    - Opens a tunnel to `finance.db`. If the file doesn't exist, SQLite creates it automatically.
2.  **Initialization (`init_db`)**:

    - **What it does**: This runs every time the app starts. It checks if tables like `users`, `transactions`, and `categories` exist.
    - **Migrations**: You'll see blocks of code checking `PRAGMA table_info`. This is "self-healing" code. If you add a new feature (like "Loans") that needs a new column, this code detects it's missing and adds it automatically without deleting your old data.

3.  **The Tables (The Data Structure)**:

    - **`users`**: Stores login info (`username`, `password` hash).
    - **`categories`**: Stores buckets for money (e.g., "Food", "Salary"). Has flags like `is_loan` to trigger special behaviors.
    - **`transactions`**: The main ledger. Every row is one money movement. It links to `users` (who made it) and includes fields for Loans (`loan_emi`, `loan_tenure`) and Credit Cards (`is_credit_card_payment`).
    - **`recurring_items`**: A planning table. Stores your expected monthly income/expenses. Used to calculate "Projected Savings" on the Dashboard.

4.  **Crucial Functions**:
    - **`get_summary`**: The math engine. It sums up Income, Expenses, Investments, etc. **Important Logic**: It calculates "Net Savings" by subtracting expenses from income but _excludes_ generic debt entries (borrowing isn't income) and credit card _bill payments_ (to avoid double-counting if you tracked the individual swipes).
    - **`get_portfolio_status`**: Calculates your "Net Worth". It differentiates between **Assets** (Cash, Investments) and **Liabilities** (Loans, Friends Debt).

---

## 4. Step 3: The User Interface (`app.py`)

This is the file users interact with. Streamlit runs this script from top to bottom every time you click a button (updates the interaction).

### **A. Setup & Configuration (Lines 1-56)**

- **Imports**: Brings in `database` (our `database.py` file) so the UI can talk to the DB.
- **`st.set_page_config`**: Sets the browser tab title and icon (💰).
- **Custom CSS**: The `<style>` block makes the "Metric Cards" look colorful (gradients) and prettifies headers.
- **`db.init_db()`**: The very first imperative logical step. Ensures the database is ready before drawing any UI.
- **`st.session_state`**: This is the app's "Short-term Memory". It remembers:
  - **Identity**: `user_id`, `username`, `is_admin`.
  - **Preferences**: `currency` (INR/USD), `currency_symbol` (₹/$).
  - **UI State**: `edit_recurring_id` (which item is being edited).

### **B. Authentication (Lines 57-103)**

- **The `if` Logic**:
  - If `st.session_state.user_id` is `None` (empty), it shows the **Login Screen**.
  - If a user logs in successfully, it saves their ID into `session_state` and `st.rerun()`s the app.
- **Rerun**: When the app reruns with `user_id` set, it skips the Login block and goes straight to the **Main App**.

### **C. The Sidebar & Navigation**

- **`st.sidebar.radio`**: Creates the menu (Dashboard, Portfolio, Add Transaction, etc.). The value usually stored in variable `page` decides which "screen" is shown next.

### **D. The Screens (Page Logic)**

#### **1. 📊 Dashboard**

- **Date Filters**: Users pick `From` and `To` dates.
- **Data Fetching**: It calls `db.get_summary(user_id, start, end)`.
- **Metric Cards**: Displays the raw numbers (Income, Expenses) returned by the database.
- **Charts**: Uses `plotly.express` to draw Pie Charts. It asks `db.get_category_breakdown` for the data slices.

#### **2. ➕ Add Transaction**

- **The Form**: Built using `st.columns` to layout Date, Type, Category, Amount side-by-side.
- **Dynamic Logic**:
  - **Loans**: If you pick "Debt" type AND a "Loan" category, the code dynamically reveals extra fields (Interest Rate, Tenure, Lender).
  - **Credit Cards**: If "Expense", it shows a checkbox "Paid via Credit Card". This flag tells the database this expense shouldn't be subtracted from your "Cash in Hand" immediately.
- **Submission**: When you click "Add", it bundles all inputs and sends them to `db.add_transaction`.

#### **3. 📋 View Transactions**

- **Interactive Table**: Uses `st.dataframe` with `on_select="rerun"`. This allows you to click a row to "select" it.
- **Edit Mode**: If a row is selected, a new Form appears below key populated with that row's data. This allows "Update" or "Delete" actions.

#### **4. 💸 Debt Views**

- **Tabs**: Splits into "Friends Debt" and "Loans".
- **Friends Logic**: Shows who owes you or who you owe. Has a "Repay" popover that records a partial payment.
- **Loans Logic**:
  - Calculates "Active Loans" by checking if `is_repaid == 0`.
  - Displays an "EMI Card" for each loan with a progress bar.
  - **Pay EMI**: A special button that records an "Expense" (Category: EMI) and links it to the Loan (via `linked_id`). This ensures your bank balance goes down, and the loan outstanding amount reduces simultaneously.

#### **5. 🔄 Recurring Items**

- **The List**: Displays items grouped by type (Income, Expense) in collapsible Accordions (`st.expander`).
- **Edit Logic**:
  - Clicking "Edit" (✏️) sets `session_state.edit_recurring_id`.
  - The page reloads (`st.rerun()`) and detects this ID.
  - It renders an **Edit Form** at the top and hides the "Add New" form to reduce clutter.
  - Saving updates the DB and clears the ID to return to normal view.

---

## 5. Summary of Connections

1.  **User Action**: User clicks "Add Transaction" in `app.py`.
2.  **Frontend Processing**: `app.py` gathers the inputs (Date: Today, Amount: 500, Cat: Food).
3.  **Backend Call**: `app.py` calls `db.add_transaction(...)`.
4.  **Database Action**: `database.py` receives the data, writes a SQL `INSERT` command, and saves it to `finance.db`.
5.  **Feedback**: `app.py` sees the success, sets `session_state.transaction_added = True`, and refreshes to show a "Success Badge".

This separation ensures that if you want to change the _color_ of the button, you edit `app.py`. If you want to change how _savings_ are calculated, you edit `database.py`.
