# Functional Walkthrough: IneX̂ō

This document explains the features and functional flows of the **IneX̂ō** personal finance application.

## 1. 📊 Dashboard
The central hub of the application.
- **Date Range**: Select custom "From" and "To" dates to filter all data.
- **KPI Metrics**: View Total Income, Regular Expenses (excluding debt repayments), Investments, Credit Card Bills, and Debt Repayments.
- **Net Savings**: Calculated as `Income - Expenses (incl. Repayments) - Investments - CC Bills - Cash/Bank Vehicle Spend`. 
- **Projections**: Shows "Projected Monthly Savings" based on your **Recurring Items**.

## 2. ➕ Add Transaction
The primary input form for money movement.
- **Types**: Income, Expense, Investment, Credit Card, Debt, Vehicle, Banking, Subscriptions.
- **Smart Features**:
    - **Loans**: Select "Debt" type and a "Loan" category to input lender, interest rate, and tenure. It auto-calculates EMI.
    - **Credit Card**: Check "Paid via Credit Card" for expenses. These don't deduct from your cash balance immediately.
    - **Self Expense**: Mark personal expenses to track them separately from shared/family expenses.

## 3. 💼 Portfolio
Your Net Worth Statement.
- **Assets**: Cash + Investments.
- **Liabilities**: Loans Outstanding + Friends Debt.
- **Net Worth**: Assets - Liabilities.

## 4. 💸 Debt Views
Dedicated module for liability management.
- **Friends Debt**: Track informal borrowing/lending.
- **Loans**: 
    - View active loans with progress bars (Paid vs Total).
    - **Pay EMI**: Click the button to record an EMI payment. This updates your expense ledger and reduces the loan balance automatically.

## 5. 🔄 Recurring Items
Budget planning tool.
- Add fixed monthly income (Salary) and expenses (Rent, Netflix).
- These figures feed into the Dashboard to show "Expected Savings" vs "Actual Savings".

## 6. 📈 Analytics
Deep dive into your financial habits.
- **Views**: Current Month, Quarterly, YTD, or Custom Range.
- **Tabs**:
    - **Income & Expense**: Breakdown by category.
    - **Credit Card**: Spending patterns by category.
    - **Vehicle**: Fuel, Service, Insurance costs.
    - **Forecast**: Simple projection of future trends (if enough data exists).

## 7. 🏷️ Categories
Customize your ledger.
- Add new categories for any transaction type.
- Enable "Track as Loan" for Debt categories to unlock Loan/EMI features.

## 8. ⚙️ Settings (Admin)
- **User Management**: Admin (`shijo`) can manage other users.
- **Password Resets**: Approve/Reject password reset requests from other users.
