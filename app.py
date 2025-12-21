from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import database as db
import finance_utils as utils

# Page config
st.set_page_config(
    page_title="IneX̂ō - Track. Save. Thrive.",
    page_icon="assets/icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    /* Login Card Styling */
    [data-testid="stForm"] {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        padding: 2rem;
        border-radius: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stForm"] input {
        background-color: #161621;
        color: white;
        border: 1px solid #3f3f5f;
        border-radius: 8px;
    }
    [data-testid="stForm"] button {
        # background: linear-gradient(90deg, #3a86ff, #0056b3);
        background: linear-gradient(90deg, #6C9E82, #68AD97);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(58, 134, 255, 0.4);
        transition: all 0.3s ease;
    }
    [data-testid="stForm"] button:hover {
        transform: translateY(-2px);
        # box-shadow: 0 6px 20px rgba(58, 134, 255, 0.6);
        box-shadow: 0 6px 20px rgba(237, 221, 83, 1);
    }
    [data-testid="stForm"] label {
        color: #e0e0e0 !important;
    }
    [data-testid="stForm"] .stMarkdown p {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
db.init_db()

# Automatic Backup on Startup
if 'backup_status' not in st.session_state:
    st.session_state.backup_status = db.perform_backup()

if "CRITICAL" in st.session_state.backup_status:
    st.sidebar.error("🚨 DATABASE CORRUPTION DETECTED! Backup aborted. Contact support.")

# Session State for Authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = 0
    st.session_state.currency = 'INR'
    st.session_state.currency_symbol = '₹'

# ========== LOGIN SCREEN ==========
if st.session_state.user_id is None:
    import base64
    def get_img_as_base64(file):
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # st.caption("Track. Save. Thrive.")
        with st.form("login_form"):
            try:
                icon_b64 = get_img_as_base64("assets/logo-inexo-banner.png")
                st.markdown(f'<div class="main-header"><img src="data:image/png;base64,{icon_b64}" width="auto" height="130" style="vertical-align: middle; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 0.2px solid #ffa600;"></div>', unsafe_allow_html=True)
            except:
                 st.markdown('<div class="main-header">💰 IneX̂ō Login</div>', unsafe_allow_html=True)
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            st.session_state.show_forgot_pass = True

            # resetPassword = st.form_submit_button("Forgot Password?")
            
            # if resetPassword:                
            #     st.rerun()
            
            if submitted:
                user = db.verify_user(username, password)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.is_admin = user['is_admin']
                    st.session_state.currency = user.get('currency', 'INR')
                    st.session_state.currency_symbol = utils.CURRENCIES.get(st.session_state.currency, utils.CURRENCIES['INR'])['symbol']
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            
            # Forgot Password Link
            # st.markdown("---")
            # if st.form_submit_button("Forgot Password?", type="secondary"):
            #     st.session_state.show_forgot_pass = True
        
        if st.session_state.get('show_forgot_pass', False):
             with st.popover("🔑 Reset Password Request", use_container_width=True):
                 st.write("Enter your username to request a password reset.")
                 with st.form("forgot_pass_form"):
                     fp_username = st.text_input("Username")
                     if st.form_submit_button("Submit Request"):
                         if db.request_password_reset(fp_username):
                             st.success("Request sent! Admin will review it.")
                             st.session_state.show_forgot_pass = False
                         else:
                             st.error("User not found or request already pending.")
        
        if db.user_exists('shijo'):
            st.info("**Default Login:** Username: `shijo` | Password: `admin123`")
    
    st.stop()

# ========== MAIN APP ==========

# Sidebar navigation
st.sidebar.image("assets/logo-inexo-banner.png")

# Hidden Developer Signature (Easter Egg)
# Listens for 'shijo', 'author', 'credits' sequence
import streamlit.components.v1 as components
components.html(
    """
    <script>  
    const _t = ['cGVuaWVs'].map(s => window.atob(s));
    let buffer = "";    
    window.parent.document.addEventListener('keydown', function(event) {        
        const target = event.target;
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable) {
            return;
        }
        if (event.key.length === 1) {
            if (window.sigTimeout) clearTimeout(window.sigTimeout);
            window.sigTimeout = setTimeout(() => {
                buffer = "";
            }, 2000); 
            buffer += event.key.toLowerCase();
            if (buffer.length > 20) buffer = buffer.slice(-20);            
            for (let seq of _t) {
                if (buffer.endsWith(seq)) {
                    const _h = "SW5lWMO0IC0gQ3JlYXRlZCBieSBTaGlqbyBTaGFqaQ==";
                    let msg = "";
                    try {
                        msg = decodeURIComponent(escape(window.atob(_h)));
                    } catch(e) { }                    
                    if (window.parent.document.getElementById('inexo-sig-toast')) return;                    
                    const toast = window.parent.document.createElement('div');
                    toast.id = 'inexo-sig-toast';
                    toast.style.position = 'fixed';
                    toast.style.top = '20px';
                    toast.style.right = '20px';
                    toast.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    toast.style.color = 'white';
                    toast.style.padding = '15px 25px';
                    toast.style.borderRadius = '10px';
                    toast.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
                    toast.style.fontFamily = 'sans-serif';
                    toast.style.zIndex = '999999';
                    toast.style.transition = 'opacity 0.5s ease';
                    toast.innerHTML = `👨‍💻 ${msg}`;                    
                    window.parent.document.body.appendChild(toast);                    
                    setTimeout(() => {
                        toast.style.opacity = '0';
                        setTimeout(() => toast.remove(), 500);
                    }, 4000);                    
                    buffer = "";
                }
            }
        }
    });
    </script>
    """,
    height=0,
    width=0
)
# st.sidebar.caption("IneX̂ō - Track. Save. Thrive.")
# st.sidebar.info("Track your income, expenses, investments, and more!")
# st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "💼 Portfolio", "➕ Add Transaction", "🔄 Recurring Items", "📋 View Transactions", "💸 Debt Views", "🏷️ Categories", "📈 Analytics", "👤 Profile", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = 0
    st.session_state.currency = 'INR'
    st.session_state.currency_symbol = '₹'
    st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 0px; color: gray;">
        🎯<small>App created by <a href="https://bio.link/shijoshaji" target="_blank" style="color: aqua; text-decoration: none;">Shijo Shaji</a></small>
    </div>
    """,
    unsafe_allow_html=True
)

# Get current user ID
user_id = st.session_state.user_id
currency = st.session_state.get('currency', 'INR')
symbol = st.session_state.get('currency_symbol', '₹')

# ========== DASHBOARD PAGE ==========
if page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("To", datetime.now())
    
    # Get summary
    summary = db.get_summary(user_id, str(start_date), str(end_date))
    
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💵 Income", utils.format_currency(summary['total_income'], currency))
    
    with col2:
        combined_expenses = summary['total_expense'] + summary['total_banking']
        debt_repaid = summary.get('total_debt_repayment', 0)
        regular_expenses = summary['total_expense'] - debt_repaid
        help_text = f"Regular: {utils.format_currency(regular_expenses, currency)} | Banking: {utils.format_currency(summary['total_banking'], currency)} | Debt Repaid: {utils.format_currency(debt_repaid, currency)}"
        st.metric("💸 Expenses", utils.format_currency(combined_expenses, currency), help=help_text)
    
    with col3:
        st.metric("📈 Investments", utils.format_currency(summary['total_investment'], currency))
    
    with col4:
        st.metric("💳 Credit Cards", utils.format_currency(summary['total_credit_card'], currency))
    
    with col5:
        st.metric("📉 Debt Repaid", utils.format_currency(summary.get('total_debt_repayment', 0), currency))
    
    # Net Savings & Vehicle Tracking
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        savings_rate = (summary['net_savings'] / summary['total_income'] * 100) if summary['total_income'] > 0 else 0
        savings_help = f"Income ({utils.format_currency(summary['total_income'], currency)}) - Expenses (incl. Debt Repay) ({utils.format_currency(combined_expenses, currency)}) - Investments ({utils.format_currency(summary['total_investment'], currency)}) - CC Bills ({utils.format_currency(summary['total_credit_card'], currency)}) - Vehicle (Cash)"
        st.metric("💰 Net Savings", utils.format_currency(summary['net_savings'], currency), 
                 delta=f"{savings_rate:.1f}%", help=savings_help)
    with c2:
        st.metric("🚗 Vehicle (Tracking)", utils.format_currency(summary['total_vehicle'], currency), help="Total Spend (Cash + CC). Note: Only Cash/Bank spend is deducted from Net Savings.")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Income Breakdown")
        income_data = db.get_category_breakdown(user_id, 'Income', str(start_date), str(end_date))
        if not income_data.empty:
            import plotly.express as px
            fig = px.pie(income_data, values='total', names='category', 
                        title='Income by Category',
                        color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No income data for this period")
    
    with col2:
        st.subheader("Expense Breakdown")
        expense_data = db.get_category_breakdown(user_id, 'Expense', str(start_date), str(end_date))
        if not expense_data.empty:
            fig = px.pie(expense_data, values='total', names='category',
                        title='Expenses by Category',
                        color_discrete_sequence=px.colors.sequential.Reds_r)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data for this period")
    
    # Monthly Projections (Recurring)
    st.subheader("🔮 Projected Monthly Savings")
    
    rec_items = db.get_recurring_items(user_id)
    if not rec_items.empty:
        rec_items = rec_items[rec_items['is_active'] == 1]
        
        # Valid Income
        rec_income = rec_items[rec_items['type'] == 'Income']['amount'].sum()
        
        # All other types are considered Outflows for projection purposes
        rec_expense_df = rec_items[rec_items['type'] != 'Income']
        rec_total_outflow = rec_expense_df['amount'].sum()
        
        proj_savings = rec_income - rec_total_outflow
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Expected Income", utils.format_currency(rec_income, currency))
        c2.metric("Expected Outflows", utils.format_currency(rec_total_outflow, currency), help="Includes Expenses, Investments, EMIs, Bills, etc.")
        c3.metric("Projected Savings", utils.format_currency(proj_savings, currency), delta="Monthly Net")
        
        with st.expander("View Breakdown"):
             b1, b2 = st.columns(2)
             with b1:
                 st.write("**Income Sources**")
                 st.dataframe(rec_items[rec_items['type']=='Income'][['name', 'amount']], hide_index=True)
             with b2:
                 st.write("**Obligations**")
                 st.dataframe(rec_expense_df[['type', 'name', 'amount']].sort_values(by='type'), hide_index=True)
                 
    else:
        st.info("Add items in 'Recurring Items' page to see monthly projections here.")

# ========== RECURRING ITEMS PAGE ==========
elif page == "🔄 Recurring Items":
    st.markdown('<div class="main-header">🔄 Recurring Items Manager</div>', unsafe_allow_html=True)
    st.info("Plan your monthly budget by adding expected recurring income and expenses. This data is used for Dashboard projections.")
    
    # Initialize session state for editing
    if 'edit_recurring_id' not in st.session_state:
        st.session_state.edit_recurring_id = None

    # Edit Form Container
    if st.session_state.edit_recurring_id:
        with st.container():
            st.subheader("✏️ Edit Recurring Item")
            # Fetch item details
            edit_item = db.get_recurring_items(user_id)
            edit_item = edit_item[edit_item['id'] == st.session_state.edit_recurring_id]
            
            if not edit_item.empty:
                row = edit_item.iloc[0]
                with st.form(f"edit_rec_form_{row['id']}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                         e_type = st.selectbox("Type", ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"], 
                                             index=["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"].index(row['type']),
                                             key=f"e_type_{row['id']}")
                    with c2:
                         # Fetch categories for selected type (simplified: fetch all or just use current if not changing, but let's allow change)
                         e_cats = db.get_categories(user_id, e_type)
                         cat_list = e_cats['name'].tolist() if not e_cats.empty else [row['category']]
                         e_cat = st.selectbox("Category", cat_list, index=cat_list.index(row['category']) if row['category'] in cat_list else 0, key=f"e_cat_{row['id']}")
                    with c3:
                         e_name = st.text_input("Item Name", value=row['name'], key=f"e_name_{row['id']}")
                    
                    c4, c5 = st.columns(2)
                    with c4:
                         e_amount = st.number_input(f"Amount ({symbol})", min_value=0.0, value=float(row['amount']), step=100.0, key=f"e_amt_{row['id']}")
                         if e_amount > 0:
                             st.caption(f"**{utils.number_to_words(e_amount, currency)}**")
                    with c5:
                         e_active = st.checkbox("Active?", value=bool(row['is_active']), key=f"e_act_{row['id']}")
                    
                    b1, b2 = st.columns([1, 1])
                    with b1:
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                             if db.update_recurring_item(int(row['id']), int(user_id), e_name, e_type, e_cat, float(e_amount), 1 if e_active else 0):
                                 st.session_state.edit_recurring_id = None
                                 st.success("Updated!")
                                 st.rerun()
                             else:
                                 st.error("Update failed. Please try again.")
                    with b2:
                        if st.form_submit_button("❌ Cancel"):
                             st.session_state.edit_recurring_id = None
                             st.rerun()
            else:
                st.error("Item not found.")
                st.session_state.edit_recurring_id = None
                st.rerun()
        st.divider()

    # Define types for sorting and selection
    all_types = ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"]

    # Add form in expanader - Hide if editing
    if not st.session_state.edit_recurring_id:
        with st.expander("➕ Add New Recurring Item", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                r_type = st.selectbox("Type", all_types)
            with c2:
                r_cats = db.get_categories(user_id, r_type)
                r_cat = st.selectbox("Category", r_cats['name'].tolist() if not r_cats.empty else ["General"])
            with c3:
                # Auto-fill name based on Category + Type
                # Using dynamic key to force update when Type/Cat changes
                default_name = f"{r_cat} - {r_type}"
                r_name = st.text_input("Item Name", value=default_name, key=f"r_name_{r_type}_{r_cat}")
            
            c4, c5 = st.columns(2)
            with c4:
                r_amount = st.number_input(f"Est. Monthly Amount ({symbol})", min_value=0.0, step=100.0)
                if r_amount > 0:
                    st.caption(f"**{utils.number_to_words(r_amount, currency)}**")
            with c5:
                r_active = st.checkbox("Active?", value=True, help="Uncheck to hide from projections without deleting")
            
            if st.button("Add Item", type="primary"):
                if r_name and r_amount > 0:
                    db.add_recurring_item(user_id, r_name, r_type, r_cat, r_amount, 1 if r_active else 0)
                    st.success("Added!")
                    st.rerun()
                else:
                    st.error("Name and Amount required")

    # List Items
    items = db.get_recurring_items(user_id)
    if not items.empty:
        st.subheader("Your Recurring Plan")
        
        # Group by Type - Dynamic
        # Get unique types present in items, sorted by custom order if possible, or just standard
        present_types = items['type'].unique().tolist()
        # Sort based on standard order
        present_types.sort(key=lambda x: all_types.index(x) if x in all_types else 99)
        
        for r_type in present_types:
            type_items = items[items['type'] == r_type]
            if not type_items.empty:
                with st.expander(f"{r_type}", expanded=False):
                    for _, row in type_items.iterrows():
                        with st.container():
                            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1, ])
                            with col1:
                                st.write(f"**{row['name']}**")
                                # st.caption(row['category'])
                                
                            with col2:
                                st.write(f"**{utils.format_currency(row['amount'], currency)}**")
                            with col3:
                                 status = "✅ Active" if row['is_active'] else "❌ Inactive"
                                 st.write(status)
                            with col4:
                                # Simple Toggle Active Button
                                btn_label = "Deactivate" if row['is_active'] else "Activate"
                                if st.button(btn_label, key=f"toggle_{row['id']}"):
                                    new_status = 0 if row['is_active'] else 1
                                    db.update_recurring_item(row['id'], user_id, row['name'], row['type'], row['category'], row['amount'], new_status)
                                    st.rerun()
                            with col5:
                                if st.button("✏️", key=f"edit_rec_{row['id']}"):
                                    st.session_state.edit_recurring_id = row['id']
                                    st.rerun()
                                if st.button("🗑️", key=f"del_rec_{row['id']}"):
                                     db.delete_recurring_item(row['id'], user_id)
                                     st.rerun()
                            st.divider()
    else:
        st.info("No recurring items added yet.")

# ========== ADD TRANSACTION PAGE ==========
elif page == "➕ Add Transaction":
    st.markdown('<div class="main-header">➕ Add Transaction</div>', unsafe_allow_html=True)
    
    # Show success message if transaction was just added
    if 'transaction_added' in st.session_state and st.session_state.transaction_added:
        st.success(f"✅ Transaction added successfully! (ID: {st.session_state.last_transaction_id})")
        st.balloons()
        st.session_state.transaction_added = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        trans_date = st.date_input("Date", datetime.now())
        trans_type = st.selectbox("Type", ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"])
    
    with col2:
        categories = db.get_categories(user_id, trans_type)
        if not categories.empty:
            category = st.selectbox("Category", categories['name'].tolist())
        else:
            category = st.text_input("Category (No categories found, enter manually)")
        
        amount = st.number_input(f"Amount ({symbol})", min_value=0.0, step=100.0)
        if amount > 0:
            st.caption(f"**{utils.number_to_words(amount, currency)}**")
        
        is_cc_payment = False
        if trans_type in ["Expense", "Subscriptions", "Vehicle"]:
            is_cc_payment = st.checkbox("Paid via Credit Card", help="Check this if you paid using a credit card. This will be excluded from total expenses to avoid double counting when you pay the bill.")
            
        is_reinvestment = False
        if trans_type == "Investment":
            is_reinvestment = st.checkbox("🔄 Reinvestment / Rollover", help="Check this if you are reinvesting matured funds (e.g., RD -> FD). This will be EXCLUDED from your Net Savings and Total Investment on Dashboard to prevent double counting.")
            
        is_self_expense = False
        if trans_type == "Expense":
             is_self_expense = st.checkbox("👤 Self / Personal Expense", help="Check this if this is a personal expense just for you (not shared).")
    
    if trans_type == "Debt" and category == "Friends":
        st.info("ℹ️ **Note:** This transaction will be tracked in 'Friends Debt' and excluded from your main savings calculations.")
    
    # Loan Details Section
    loan_rate = None
    loan_tenure = None
    loan_emi = None
    loan_lender = None
    loan_end_date = None

    if trans_type == "Debt" and not categories.empty:
         selected_cat_row = categories[categories['name'] == category]
         if not selected_cat_row.empty and selected_cat_row.iloc[0].get('is_loan', 0) == 1:
             st.markdown("---")
             st.subheader("🏦 Loan Details")
             l1, l2, l3 = st.columns(3)
             with l1:
                 loan_lender = st.text_input("Lender / Bank Name")
             with l2:
                 loan_rate = st.number_input("Interest Rate (% p.a.)", min_value=0.1, value=10.0, step=0.1, format="%.2f")
             with l3:
                 loan_tenure = st.number_input("Tenure (Months)", min_value=1, value=12, step=1)
             
             if amount > 0 and loan_rate > 0 and loan_tenure > 0:
                 # EMI Calculation
                 p = amount
                 r = loan_rate / 12 / 100
                 n = loan_tenure
                 
                 emi = p * r * ((1 + r)**n) / (((1 + r)**n) - 1)
                 
                 loan_emi = emi
                 total_pay = emi * n
                 total_int = total_pay - p
                 
                 loan_end_date = trans_date + timedelta(days=int(30.44 * loan_tenure))
                 
                 st.info(f"💰 **Monthly EMI:** {utils.format_currency(emi, currency)} | **Total Interest:** {utils.format_currency(total_int, currency)} | **End Date:** ~{loan_end_date.strftime('%d-%b-%Y')}")
             else:
                 st.warning("Enter Amount, Rate and Tenure to see EMI")
                 st.info("Date must be Loan Start date, Amount will be total loan amount - once added tracations always gp to debt views to update EMI")
    
    description = st.text_area("Description (Optional)")
    account = st.text_input("Account (Optional)")
    
    if st.button("➕ Add Transaction", width='stretch', type="primary"):
        if amount > 0:
            trans_id = db.add_transaction(
                user_id=user_id,
                date=str(trans_date),
                trans_type=trans_type,
                category=category,
                amount=amount,
                description=description if description else None,
                account=account if account else None,
                is_credit_card_payment=1 if is_cc_payment else 0,
                loan_interest_rate=loan_rate,
                loan_tenure_months=loan_tenure,
                loan_emi=loan_emi,
                loan_start_date=str(trans_date) if loan_tenure else None,
                loan_end_date=str(loan_end_date) if loan_end_date else None,
                loan_lender_bank=loan_lender,
                is_reinvestment=1 if is_reinvestment else 0,
                is_self=1 if is_self_expense else 0
            )
            st.session_state.transaction_added = True
            st.session_state.last_transaction_id = trans_id
            st.rerun()
        else:
            st.error("Amount must be greater than 0")

# ========== VIEW TRANSACTIONS PAGE ==========
elif page == "📋 View Transactions":
    st.markdown('<div class="main-header">📋 View Transactions</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_start = st.date_input("From", datetime.now() - timedelta(days=30))
    
    with col2:
        filter_end = st.date_input("To", datetime.now())
    
    with col3:
        filter_type = st.selectbox("Type", ["All", "Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking"])
    
    with col4:
        if filter_type == "All":
            all_categories = db.get_categories(user_id)
        else:
            all_categories = db.get_categories(user_id, filter_type)
            
        filter_category = st.selectbox("Category", ["All"] + all_categories['name'].tolist() if not all_categories.empty else ["All"])
    
    # Get transactions
    transactions = db.get_transactions(
        user_id=user_id,
        start_date=str(filter_start),
        end_date=str(filter_end),
        trans_type=filter_type if filter_type != "All" else None,
        category=filter_category if filter_category != "All" else None
    )
    
    if not transactions.empty:
        st.write(f"**Total: {len(transactions)} transactions | Sum: ₹{transactions['amount'].sum():,.0f}**")
        st.caption("Select a row to edit or delete.")
        st.markdown("---")
        
        # Create a container for the edit form at the top
        edit_container = st.container()

        transactions['date'] = pd.to_datetime(transactions['date']).dt.date
        
        # Display DataFrame with selection enabled
        event = st.dataframe(
            transactions,
            column_config={
                "id": None,
                "user_id": None,
                "date": st.column_config.DateColumn("Date", format="DD-MM-YYYY"),
                "type": "Type",
                "category": "Category",
                "amount": st.column_config.NumberColumn(f"Amount ({symbol})", format=f"{symbol}%d"),
                "description": "Description",
                "account": "Account",
                "is_credit_card_payment": st.column_config.CheckboxColumn("CC Paid"),
                "is_reinvestment": st.column_config.CheckboxColumn("Reinvest"),
                "created_at": None,
                "linked_id": None,
                "is_repaid": None,
                "created_at": None,
                "linked_id": None,
                "is_repaid": None,
                "subcategory": None,
                "paid_amount": None,
                "is_self": st.column_config.CheckboxColumn("Self?")
            },
            hide_index=True,
            width=None,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        if len(event.selection.rows) > 0:
            selected_index = event.selection.rows[0]
            selected_row = transactions.iloc[selected_index]
            
            with edit_container:
                st.subheader(f"✏️ Edit Transaction: {selected_row['description'] or 'Untitled'}")
                st.info(f"Editing Transaction ID: {selected_row['id']} | Date: {selected_row['date']}")
                
                with st.form(f"edit_trans_{selected_row['id']}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        e_date = st.date_input("Date", selected_row['date'])
                    with c2:
                        e_type = st.selectbox("Type", ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"], 
                                            index=["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"].index(selected_row['type']) if selected_row['type'] in ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"] else 0)
                    with c3:
                        # Refresh categories based on type selection if needed, but for simplicity show all or valid ones
                        # Ideally this should be dynamic, but in a form, we might need rerun to update options.
                        # For now keep simple: Show all categories or just the current one if not found.
                        # A better UX: If Type changes, Category list should update. But that requires st.rerun inside form which is not allowed.
                        # So we use standard selectbox. If user wants to change type AND category, they might need two steps or we accept mismatch.
                        # Let's fetch all categories for now to allow flexible edits.
                        current_cats = db.get_categories(user_id, e_type)
                        cat_options = current_cats['name'].tolist() if not current_cats.empty else [selected_row['category']]
                        e_cat = st.selectbox("Category", cat_options, index=cat_options.index(selected_row['category']) if selected_row['category'] in cat_options else 0)
                    
                    c4, c5 = st.columns(2)
                    with c4:
                        e_amount = st.number_input("Amount", min_value=0.0, value=float(selected_row['amount']))
                        if e_amount > 0:
                            st.caption(f"**{utils.number_to_words(e_amount, currency)}**")
                    with c5:
                        e_account = st.text_input("Account", value=selected_row['account'] or "")
                    
                    e_desc = st.text_area("Description", value=selected_row['description'] or "")
                    
                    c6, c7 = st.columns(2)
                    with c6:
                        e_is_cc = st.checkbox("Paid via Credit Card", value=bool(selected_row.get('is_credit_card_payment', 0)))
                    with c7:
                        e_is_reinvest = st.checkbox("Reinvestment", value=bool(selected_row.get('is_reinvestment', 0)))
                        if e_type == "Expense":
                            e_is_self = st.checkbox("Self / Personal Expense", value=bool(selected_row.get('is_self', 0)))
                        else:
                            e_is_self = 0
                    
                    e_loan_interest = None
                    e_loan_tenure = None
                    e_loan_emi = None
                    e_loan_lender = None
                    
                    if e_type == "Debt":
                        st.markdown("#### 🏦 Loan Details")
                        ld1, ld2 = st.columns(2)
                        with ld1:
                            e_loan_lender = st.text_input("Lender Bank", value=selected_row['loan_lender_bank'] or "")
                            e_loan_interest = st.number_input("Interest Rate (%)", min_value=0.0, value=float(selected_row['loan_interest_rate'] or 0.0), step=0.1)
                        with ld2:
                            e_loan_tenure = st.number_input("Tenure (Months)", min_value=0, value=int(selected_row['loan_tenure_months'] or 0))
                            e_loan_emi = st.number_input(f"EMI Amount ({symbol})", min_value=0.0, value=float(selected_row['loan_emi'] or 0.0))
                            if e_loan_emi > 0:
                                st.caption(f"EMI: {utils.number_to_words(e_loan_emi, currency)}")

                    col_update, col_delete = st.columns([1, 1])
                    with col_update:
                        if st.form_submit_button("💾 Update Transaction", type="primary"):
                            if st.session_state.username == 'demouser':
                                 st.error("Demo User cannot edit data.")
                            else:
                                db.update_transaction(
                                    user_id=user_id,
                                    trans_id=int(selected_row['id']),
                                    date=str(e_date),
                                    trans_type=e_type,
                                    category=e_cat,
                                    amount=e_amount,
                                    description=e_desc,
                                    account=e_account,
                                    is_credit_card_payment=1 if e_is_cc else 0,
                                    is_reinvestment=1 if e_is_reinvest else 0,
                                    loan_interest_rate=e_loan_interest,
                                    loan_tenure_months=e_loan_tenure,
                                    loan_emi=e_loan_emi,
                                    loan_lender_bank=e_loan_lender,
                                    is_self=1 if e_is_self else 0
                                )
                                st.success("Transaction updated!")
                                st.rerun()
                    
                    with col_delete:
                        if st.form_submit_button("🗑️ Delete Transaction", type="secondary"):
                             if st.session_state.username == 'demouser':
                                 st.error("Demo User cannot delete data.")
                             else:
                                 db.delete_transaction(user_id, int(selected_row['id']))
                                 st.error("Transaction deleted!")
                                 st.rerun()
                st.divider()
    else:
        st.info("No transactions found for the selected filters")

# ========== CATEGORIES PAGE ==========
elif page == "🏷️ Categories":
    st.markdown('<div class="main-header">🏷️ Categories</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add New Category"):
        with st.form("add_category_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_cat_name = st.text_input("Category Name")
            
            with col2:
                new_cat_type = st.selectbox("Type", ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"])
                
                is_loan_cat = False
                if new_cat_type == "Debt":
                    is_loan_cat = st.checkbox("Track as Loan", help="Enable this to track Loan details like EMI, Interest Rate, etc.")
            
            if st.form_submit_button("Add Category"):
                if new_cat_name:
                    cat_id = db.add_category(user_id, new_cat_name, new_cat_type, is_loan=1 if is_loan_cat else 0)
                    if cat_id:
                        st.success(f"✅ Category '{new_cat_name}' added!")
                        st.rerun()
                    else:
                        st.error("Category already exists!")
                else:
                    st.error("Please enter a category name")
    
    categories = db.get_categories(user_id)
    
    if not categories.empty:
        if 'edit_cat_id' not in st.session_state:
            st.session_state.edit_cat_id = None
            
        cat_types = ["Income", "Expense", "Investment", "Credit Card", "Debt", "Vehicle", "Banking", "Subscriptions"]
        tabs = st.tabs([f"{t}" for t in cat_types])
        
        for i, cat_type in enumerate(cat_types):
            with tabs[i]:
                type_cats = categories[categories['type'] == cat_type]
                if not type_cats.empty:
                    st.subheader(f"{cat_type} Categories ({len(type_cats)})")
                    
                    for _, row in type_cats.iterrows():
                        cat_id = row['id']
                        
                        if st.session_state.edit_cat_id == cat_id:
                            with st.container():
                                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                                with col1:
                                    edit_name = st.text_input("Name", value=row['name'], key=f"cat_name_{cat_id}", label_visibility="collapsed")
                                with col2:
                                    edit_type = st.selectbox("Type", cat_types, 
                                                           index=cat_types.index(row['type']) if row['type'] in cat_types else 0,
                                                           key=f"cat_type_{cat_id}", label_visibility="collapsed")
                                    
                                    edit_is_loan = 0
                                    if edit_type == "Debt":
                                        # Default to current value if column exists, else 0. 
                                        # Note: dataframe row might not have is_loan if we didn't refresh app/db connection or if using cached data.
                                        # But db.get_categories should fetch all columns.
                                        current_is_loan = row.get('is_loan', 0)
                                        is_loan_checked = st.checkbox("Track as Loan", value=bool(current_is_loan), key=f"is_loan_{cat_id}")
                                        edit_is_loan = 1 if is_loan_checked else 0
                                        
                                with col3:
                                    if st.button("💾", key=f"save_cat_{cat_id}", help="Save"):
                                        if db.update_category(user_id, cat_id, edit_name, edit_type, is_loan=edit_is_loan):
                                            st.session_state.edit_cat_id = None
                                            st.success("Updated!")
                                            st.rerun()
                                        else:
                                            st.error("Error/Duplicate")
                                with col4:
                                    if st.button("❌", key=f"cancel_cat_{cat_id}", help="Cancel"):
                                        st.session_state.edit_cat_id = None
                                        st.rerun()
                        else:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                if row.get('is_loan', 0) == 1:
                                    st.write(f"• {row['name']} (Loan)")
                                else:
                                    st.write(f"• {row['name']}")
                            with col2:
                                if str(row['name']).strip() == 'Friends':
                                    st.markdown("🔒 **Protected**", help="System-managed category for Friends Debt tracking and cannot be edited or deleted.")
                                else:
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        if st.button("✏️", key=f"edit_cat_btn_{cat_id}", help="Edit"):
                                            st.session_state.edit_cat_id = cat_id
                                            st.rerun()
                                    with c2:
                                        if st.button("🗑️", key=f"del_cat_btn_{cat_id}", help="Delete"):
                                            db.delete_category(user_id, cat_id)
                                            st.success("Deleted!")
                                            st.rerun()
                else:
                    st.info(f"No {cat_type} categories found")
    else:
        st.info("No categories found")

# ========== DEBT VIEWS PAGE ==========
elif page == "💸 Debt Views":
    st.markdown('<div class="main-header">💸 Debt Views</div>', unsafe_allow_html=True)
    st.info("Track money you owe. Use 'Repay' to record partial or full payments.")

    tab_friends, tab_loans = st.tabs(["🤝 Friends Debt", "🏦 Loans"])

    with tab_friends:
        # Get all friends debts
        debts = db.get_friends_debts(user_id)
        
        if not debts.empty:
            # Calculate remaining amount for each debt
            debts['paid_amount'] = debts['paid_amount'].fillna(0)
            debts['remaining'] = debts['amount'] - debts['paid_amount']
            
            unpaid = debts[debts['is_repaid'] == 0]
            repaid = debts[debts['is_repaid'] == 1]
            
            total_outstanding = unpaid['remaining'].sum()
            
            # KPI Card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                <h2 style="margin:0; font-size: 1.2rem;">Total Outstanding (Friends)</h2>
                <h1 style="margin:0; font-size: 3rem;">{utils.format_currency(total_outstanding, currency)}</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Active Debts Accordion
            with st.expander("📝 Active Debts", expanded=True):
                if not unpaid.empty:
                    for _, row in unpaid.iterrows():
                        with st.container():
                            c1, c2, c3, c4 = st.columns([2, 3, 2, 3])
                            with c1:
                                st.write(f"📅 **{row['date']}**")
                            with c2:
                                st.write(f"**{row['description']}**")
                                st.caption(f"Account: {row['account'] or 'None'}")
                            with c3:
                                st.write(f"Total: ₹{row['amount']:,.0f}")
                                if row['paid_amount'] > 0:
                                    st.write(f"Paid: ₹{row['paid_amount']:,.0f}")
                                st.write(f"**Left: ₹{row['remaining']:,.0f}**")
                            with c4:
                                # Repay Logic
                                with st.popover("💸 Repay"):
                                    with st.form(f"repay_form_{row['id']}"):
                                        repay_amt = st.number_input("Amount", min_value=1.0, max_value=float(row['remaining']), value=float(row['remaining']), key=f"amt_{row['id']}")
                                        if repay_amt > 0:
                                            st.caption(f"{utils.number_to_words(repay_amt, currency)}")
                                        pay_date = st.date_input("Date", datetime.now(), label_visibility="collapsed", key=f"date_{row['id']}")
                                        pay_account = st.text_input("From Account", value="Cash", key=f"acc_{row['id']}")
                                        
                                        if st.form_submit_button("Confirm Payment"):
                                            if db.repay_debt(user_id, row['id'], repay_amt, pay_account, str(pay_date)):
                                                st.success("Payment Recorded!")
                                                st.rerun()
                                            else:
                                                st.error("Error recording payment")
                            
                            # Progress bar
                            if row['amount'] > 0:
                                progress = min(1.0, row['paid_amount'] / row['amount'])
                                st.progress(progress)
                            st.markdown("---")
                else:
                    st.success("🎉 You don't owe anyone money right now!")
            
            # Recent Repayments Accordion
            with st.expander("📜 Recent Repayments / History", expanded=False):
                if not repaid.empty:
                    # Sort repaid by date descending (though likely already sorted coming from DB, usually safe to re-sort or rely on query)
                    # Let's show table for overview
                    st.dataframe(repaid[['date', 'description', 'amount', 'paid_amount']], width='stretch', hide_index=True)
                    
                    st.subheader("Recent Repayments (Undo Actions)")
                    st.caption("You can undo repayments made within the last 48 hours.")
                    
                    # Need to fetch linked repayment transaction date to verify 48h limit
                    # We iterate through recent ones
                    conn_check = db.get_connection()
                    
                    for _, row in repaid.head(10).iterrows(): # Check last 10
                         # Fetch the LAST repayment transaction for this debt
                        repay_trans = pd.read_sql_query(
                            "SELECT id, date, amount FROM transactions WHERE linked_id = ? AND type = 'Expense' ORDER BY date DESC LIMIT 1", 
                            conn_check, params=[row['id']]
                        )
                        
                        can_undo = False
                        repay_date_str = "Unknown"
                        
                        if not repay_trans.empty:
                            last_pay_date = pd.to_datetime(repay_trans.iloc[0]['date']).date()
                            time_diff = (datetime.now().date() - last_pay_date).days
                            repay_date_str = last_pay_date.strftime('%d-%b-%Y')
                            if time_diff <= 2:
                                can_undo = True
                        
                        c1, c2, c3 = st.columns([3, 2, 2])
                        c1.write(f"{row['date']} - {row['description']}")
                        c2.write(f"Paid: ₹{row['amount']:,.0f}")
                        
                        with c3:
                            if can_undo:
                                if st.button("↩️ Undo", key=f"undo_{row['id']}"):
                                    # 1. Delete the linked Expense transaction(s)
                                    db.delete_transaction_by_link(user_id, row['id'])
                                    
                                    # 2. Reset paid_amount to 0 and mark as unpaid
                                    db.update_transaction(user_id, row['id'], paid_amount=0.0)
                                    db.toggle_transaction_repaid(user_id, row['id'])
                                    
                                    st.success("Repayment undone!")
                                    st.rerun()
                            else:
                                st.caption(f"Closed: {repay_date_str}")
                                
                    conn_check.close()

                else:
                    st.info("No repaid debts yet.")
        else:
             st.info("No debt records found.")

    with tab_loans:
        # Get all transactions that are Debts AND belong to Loan Categories
        all_debts = db.get_transactions(user_id, trans_type='Debt')
        
        # Get loan categories
        all_cats = db.get_categories(user_id)
        if not all_cats.empty and 'is_loan' in all_cats.columns:
            loan_cat_names = all_cats[all_cats['is_loan'] == 1]['name'].tolist()
        else:
            loan_cat_names = []
            
        loans = all_debts[all_debts['category'].isin(loan_cat_names)]
        
        if not loans.empty:
            loans['paid_amount'] = loans['paid_amount'].fillna(0)
            sub_active_tab, sub_closed_tab = st.tabs(["🏦 Active Loans", "🏁 Closed Loans"])

            active_loans = loans[loans['is_repaid'] == 0]
            closed_loans = loans[loans['is_repaid'] == 1]

            with sub_active_tab:
                # Calculate total outstanding
                total_loan_outstanding = 0
                for _, r in active_loans.iterrows():
                    if r['loan_emi'] and r['loan_tenure_months']:
                        total_payable = r['loan_emi'] * r['loan_tenure_months']
                        paid = r['paid_amount'] or 0
                        total_loan_outstanding += (total_payable - paid)
                    else:
                        total_loan_outstanding += (r['amount'] - (r['paid_amount'] or 0))
                
                # KPI Card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                    <h2 style="margin:0; font-size: 1.2rem;">Total Active Loans Amount</h2>
                    <h1 style="margin:0; font-size: 3rem;">{utils.format_currency(total_loan_outstanding, currency)}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                if not active_loans.empty:
                    loan_tabs = st.tabs([f"{row['category']}" for _, row in active_loans.iterrows()])
                    
                    for i, (index, row) in enumerate(active_loans.iterrows()):
                        with loan_tabs[i]:
                            # Calculations
                            principal = row['amount']
                            roi = row['loan_interest_rate'] or 0.0
                            tenure_months = row['loan_tenure_months'] or 1
                            emi = row['loan_emi'] or 0.0
                            
                            if emi > 0:
                                total_payable = emi * tenure_months
                                total_interest = total_payable - principal
                                
                                amount_paid_so_far = row['paid_amount'] or 0.0
                                balance_left = total_payable - amount_paid_so_far
                                
                                months_paid = amount_paid_so_far / emi if emi else 0
                                months_left = max(0, tenure_months - months_paid)
                            else:
                                total_payable = principal
                                total_interest = 0
                                amount_paid_so_far = row['paid_amount'] or 0.0
                                balance_left = principal - amount_paid_so_far
                                months_paid = 0
                                months_left = 0
                            
                            # Header Info
                            start_d = row['loan_start_date'] or "N/A"
                            end_d = row['loan_end_date'] or "N/A"
                            st.caption(f"Bank: {row['loan_lender_bank'] or 'N/A'} | ROI: {roi}% | Tenure: {tenure_months}m | Start: {start_d} | End: {end_d}")
                            
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Total Payable", f"₹{total_payable:,.0f}", help=f"Principal: ₹{principal:,.0f} + Interest: ₹{total_interest:,.0f}")
                            m2.metric("EMI", f"₹{emi:,.0f}")
                            m3.metric("Balance Left", f"₹{balance_left:,.0f}", delta=f"-₹{amount_paid_so_far:,.0f} Paid", delta_color="inverse")
                            
                            st.divider()
                            
                            d1, d2, d3, d4 = st.columns(4)
                            d1.metric("Principal", f"₹{principal:,.0f}")
                            d2.metric("Interest", f"₹{total_interest:,.0f}")
                            d3.metric("Months Paid", f"{months_paid:.1f}")
                            d4.metric("Months Left", f"{months_left:.1f}")
                            
                            st.divider()
                            
                            if total_payable > 0:
                                prog = min(1.0, amount_paid_so_far / total_payable)
                                st.progress(prog, text=f"Repayment Progress: {prog*100:.1f}%")
                            
                            c1, c2 = st.columns([1, 3])
                            with c1:
                                with st.popover("💸 Pay EMI"):
                                    st.write(f"Record EMI Payment")
                                    with st.form(f"pay_emi_{row['id']}"):
                                        p_amt = st.number_input("Amount", value=float(emi) if emi else 0.0, step=100.0)
                                        if p_amt > 0:
                                            st.caption(f"{utils.number_to_words(p_amt, currency)}")
                                        p_date = st.date_input("Date", datetime.now())
                                        p_acc = st.text_input("From Account", value="Bank Account")
                                        
                                        if st.form_submit_button("Confirm Payment"):
                                            db.add_transaction(
                                                user_id=user_id,
                                                date=str(p_date),
                                                trans_type="Expense",
                                                category="EMI", 
                                                subcategory="Loan Repayment",
                                                amount=p_amt,
                                                description=f"EMI for {row['category']} ({row['loan_lender_bank']})",
                                                account=p_acc,
                                                linked_id=row['id']
                                            )
                                            new_paid = amount_paid_so_far + p_amt
                                            is_done = 1 if new_paid >= (total_payable - 10) else 0 
                                            
                                            db.update_transaction(user_id, row['id'], paid_amount=new_paid)
                                            if is_done:
                                                db.toggle_transaction_repaid(user_id, row['id'])
                                                
                                            st.success("EMI Paid!")
                                            st.rerun()
                            
                            st.divider()
                            with st.expander("📜 Repayment History"):
                                conn_hist = db.get_connection()
                                hist_df = pd.read_sql_query("SELECT date, amount, description, account FROM transactions WHERE linked_id = ? ORDER BY date DESC", conn_hist, params=[row['id']])
                                conn_hist.close()
                                if not hist_df.empty:
                                    st.dataframe(hist_df, width=1000, hide_index=True)
                                else:
                                    st.info("No repayments recorded yet.")
                else:
                    st.info("No active loans to display.")

            with sub_closed_tab:
                if not closed_loans.empty:
                    # Year filter
                    closed_years = []
                    conn_dates = db.get_connection()
                    
                    # We need to find closure year for each loan. 
                    # Optimization: For now just fetch all repayment dates and map them.
                    # Or simpler: Just user Current Year default and a number input
                    
                    c1, c2 = st.columns(2)
                    with c1:
                         sel_year = st.number_input("Filter by Closure Year", min_value=2000, max_value=2100, value=datetime.now().year)

                    # Filter logic: Check if max repayment date year == sel_year
                    filtered_closed_loans = []
                    
                    for _, row in closed_loans.iterrows():
                        last_pymt = pd.read_sql_query("SELECT date FROM transactions WHERE linked_id = ? ORDER BY date DESC LIMIT 1", conn_dates, params=[row['id']])
                        if not last_pymt.empty:
                            close_date = pd.to_datetime(last_pymt.iloc[0]['date']).date()
                            if close_date.year == sel_year:
                                row['close_date'] = close_date
                                filtered_closed_loans.append(row)
                        else:
                            # If no repayments found (maybe manually closed?), check created date? Or just ignore?
                            # Let's include if created date year matches as fallback
                            pass
                    
                    conn_dates.close() # Close after loop
                    
                    if filtered_closed_loans:
                        df_closed = pd.DataFrame(filtered_closed_loans)
                        
                        st.success(f"Found {len(df_closed)} closed loans in {sel_year}")
                        
                        for _, row in df_closed.iterrows():
                            with st.container():
                                st.subheader(f"✅ {row['category']} ({row['loan_lender_bank']})")
                                c1, c2, c3, c4 = st.columns(4)
                                c1.caption(f"Closed on: {row['close_date'].strftime('%d-%b-%Y')}")
                                c2.caption(f"Principal: ₹{row['amount']:,.0f}")
                                c3.caption(f"Total Paid: ₹{row['paid_amount']:,.0f}")
                                c4.caption(f"Tenure: {row['loan_tenure_months']}m")
                                st.markdown("---")
                    else:
                        st.info(f"No loans closed in {sel_year}")
                else:
                    st.info("No closed loans found yet.")
                    
        else:
            st.info("No active or closed loans found. Create a Debt transaction with a Loan Category to see it here.")
            st.caption("Tip: Go to Categories, edit a Debt category and check 'Track as Loan'.")

# ========== PROFILE PAGE ==========
elif page == "👤 Profile":
    st.markdown('<div class="main-header">👤 Profile</div>', unsafe_allow_html=True)
    
    st.subheader(f"User: {st.session_state.username}")
    # st.info(f"User ID: {user_id} | Admin: {'Yes' if st.session_state.is_admin else 'No'}")
    
    st.markdown("---")
    
    st.subheader("🌍 Currency Settings")
    c1, c2 = st.columns([1, 2])
    with c1:
        # Currency Selector
        curr_options = list(utils.CURRENCIES.keys())
        # Display as Code - Symbol
        format_func = lambda x: f"{x} - {utils.CURRENCIES[x]['symbol']}"
        
        current_idx = curr_options.index(currency) if currency in curr_options else 0
        new_currency = st.selectbox("Preferred Currency", curr_options, index=current_idx, format_func=format_func)
        
        if new_currency != currency:
            if db.update_user_currency(user_id, new_currency):
                st.session_state.currency = new_currency
                st.session_state.currency_symbol = utils.CURRENCIES[new_currency]['symbol']
                st.success(f"Currency updated to {new_currency}!")
                st.rerun()
            else:
                st.error("Failed to update currency.")
                
    st.markdown("---")
    
    # Change Password Section
    st.subheader("🔐 Change Password")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            if not old_password or not new_password or not confirm_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                if db.update_user_password(user_id, old_password, new_password):
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Current password is incorrect")

# ========== ANALYTICS PAGE ==========
elif page == "📈 Analytics":
    st.markdown('<div class="main-header">📈 Analytics</div>', unsafe_allow_html=True)
    
    st.subheader("Quick Views")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📅 Current Month", width='stretch'):
            st.session_state.view_type = "current_month"
    
    with col2:
        if st.button("⏮️ Previous Month", width='stretch'):
            st.session_state.view_type = "previous_month"
    
    with col3:
        if st.button("📊 Quarterly", width='stretch'):
            st.session_state.view_type = "quarterly"
    
    with col4:
        if st.button("📆 Year to Date", width='stretch'):
            st.session_state.view_type = "ytd"
    
    with col5:
        if st.button("🔧 Custom", width='stretch'):
            st.session_state.view_type = "custom"
    
    if 'view_type' not in st.session_state:
        st.session_state.view_type = "current_month"
    
    today = datetime.now().date()
    
    if st.session_state.view_type == "current_month":
        analytics_start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        analytics_end = next_month - timedelta(days=next_month.day)
        view_label = "Current Month"
    
    elif st.session_state.view_type == "previous_month":
        first_day_current = today.replace(day=1)
        analytics_end = first_day_current - timedelta(days=1)
        analytics_start = analytics_end.replace(day=1)
        view_label = "Previous Month"
    
    elif st.session_state.view_type == "quarterly":
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            q_year = st.number_input("Year", min_value=2000, max_value=2100, value=today.year, key="q_year_select")
        with c2:
            q_select = st.selectbox("Quarter", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"], key="q_select_box")
        
        q_map = {"Q1 (Jan-Mar)": 1, "Q2 (Apr-Jun)": 2, "Q3 (Jul-Sep)": 3, "Q4 (Oct-Dec)": 4}
        q_num = q_map[q_select]
        
        analytics_start = datetime(q_year, 3 * q_num - 2, 1).date()
        if q_num == 4:
            analytics_end = datetime(q_year, 12, 31).date()
        else:
            analytics_end = (datetime(q_year, 3 * q_num + 1, 1) - timedelta(days=1)).date()
            
        view_label = f"{q_select} {q_year}"
    
    elif st.session_state.view_type == "ytd":
        analytics_start = datetime(today.year, 1, 1).date()
        analytics_end = today
        view_label = "Year to Date"
    
    else:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            analytics_start = st.date_input("From", today - timedelta(days=180), key="analytics_start")
        with col2:
            analytics_end = st.date_input("To", today, key="analytics_end")
        view_label = "Custom Range"
    
    st.info(f"**{view_label}**: {analytics_start.strftime('%d %b %Y')} to {analytics_end.strftime('%d %b %Y')}")
    
    st.markdown("---")
    
    summary = db.get_summary(user_id, str(analytics_start), str(analytics_end))
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["📊 Overview", "💰 Income & Expense", "📈 Invest & Debt", "💳 Credit Card", "🚗 Vehicle Tracking", "⚖️ Comparison", "🔮 Forecast", "📺 Subscriptions", "🏠 Rent", "👤 Self Expenses"])
    
    with tab1:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💵 Income", utils.format_currency(summary['total_income'], currency))
        
        with col2:
            combined_expenses = summary['total_expense'] + summary['total_banking']
            help_text = f"Regular: {utils.format_currency(summary['total_expense'], currency)} | Banking: {utils.format_currency(summary['total_banking'], currency)}"
            st.metric("💸 Expenses", utils.format_currency(combined_expenses, currency), help=help_text)
        
        with col3:
            st.metric("📈 Investments", utils.format_currency(summary['total_investment'], currency))
            
        with col4:
            st.metric("💳 Credit Card", utils.format_currency(summary['total_credit_card'], currency))
        
        with col5:
            savings_rate = (summary['net_savings'] / summary['total_income'] * 100) if summary['total_income'] > 0 else 0
            st.metric("💰 Savings", f"₹{summary['net_savings']:,.0f}", delta=f"{savings_rate:.1f}%")
        
        st.markdown("---")
        
        st.subheader("Monthly Trend")
        trend_data = db.get_monthly_trend(user_id, str(analytics_start), str(analytics_end))
        
        if not trend_data.empty:
            pivot = trend_data.pivot(index='month', columns='type', values='total').fillna(0)
            
            fig = go.Figure()
            
            for col in pivot.columns:
                color_map = {
                    'Income': '#2ecc71',
                    'Expense': '#e74c3c',
                    'Investment': '#3498db',
                    'Credit Card': '#e67e22',
                    'Debt': '#c0392b',
                    'Vehicle': '#7f8c8d',
                    'Banking': '#9b59b6'
                }
                fig.add_trace(go.Scatter(
                    x=pivot.index,
                    y=pivot[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=color_map.get(col, '#95a5a6'), width=3),
                    marker=dict(size=8)
                ))
            
            fig.update_layout(
                title=f'Monthly Trend - {view_label}',
                xaxis_title='Month',
                yaxis_title='Amount (₹)',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for the selected period")

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Expenses")
            expense_breakdown = db.get_category_breakdown(user_id, 'Expense', str(analytics_start), str(analytics_end))
            if not expense_breakdown.empty:
                fig = px.bar(expense_breakdown.head(10), x='category', y='total',
                            title='Top 10 Expense Categories',
                            color='total',
                            color_continuous_scale='Reds')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data")
        
        with col2:
            st.subheader("Income Sources")
            income_breakdown = db.get_category_breakdown(user_id, 'Income', str(analytics_start), str(analytics_end))
            if not income_breakdown.empty:
                fig = px.pie(income_breakdown, values='total', names='category',
                            title='Income Distribution',
                            color_discrete_sequence=px.colors.sequential.Greens_r)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No income data")

    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Investment Breakdown")
            investment_breakdown = db.get_category_breakdown(user_id, 'Investment', str(analytics_start), str(analytics_end))

            # FIX: Show Lifetime Portfolio Value, not just current period investment
            # investment_breakdown = db.get_category_breakdown(user_id, 'Investment')
            if not investment_breakdown.empty:
                fig = px.pie(investment_breakdown, values='total', names='category',
                            title='Investment Distributio',
                            color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No investment data")
        
        with col2:
            st.subheader("Total Liabilities Breakdown (Outstanding)")
            
            # Fetch ALL debts for Balance Sheet view
            all_debts_analytics = db.get_transactions(user_id, trans_type='Debt')
            if not all_debts_analytics.empty:
                # Calculate outstanding
                all_debts_analytics['pid'] = all_debts_analytics['paid_amount'].fillna(0)
                all_debts_analytics['outstanding'] = all_debts_analytics['amount'] - all_debts_analytics['pid']
                
                # 1. Total Liabilities by Category (Pie Chart)
                debt_breakdown = all_debts_analytics.groupby('category')['outstanding'].sum().reset_index()
                debt_breakdown.columns = ['category', 'total']
                debt_breakdown = debt_breakdown[debt_breakdown['total'] > 0] 
                
                if not debt_breakdown.empty:
                    fig = px.pie(debt_breakdown, values='total', names='category',
                                title='Liabilities by Category',
                                color_discrete_sequence=px.colors.sequential.Reds_r)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("🎉 No outstanding liabilities!")
            else:
                st.info("No debt records found")

            # Lower Section: Specific Loans Breakdown
            if not all_debts_analytics.empty:
                st.markdown("---")
                st.subheader("🏦 Active Loans Breakdown")
                
                # Filter for only "Loan" categories
                loan_cats_df = db.get_categories(user_id, 'Debt')
                # Check if 'is_loan' column exists (it should based on schema)
                if 'is_loan' in loan_cats_df.columns:
                    loan_cat_names = loan_cats_df[loan_cats_df['is_loan'] == 1]['name'].tolist()
                else:
                    loan_cat_names = [] # Fallback
                    
                # Filter transactions that are in loan_cat_names AND have outstanding > 0
                active_loans = all_debts_analytics[
                    (all_debts_analytics['category'].isin(loan_cat_names)) & 
                    (all_debts_analytics['outstanding'] > 0)
                ].copy()
                
                if not active_loans.empty:
                    # Use Description or Lender Bank for labels
                    active_loans['label'] = active_loans.apply(lambda x: f"{x['description']} ({x['loan_lender_bank']})" if x['loan_lender_bank'] else x['description'], axis=1)
                    
                    fig_loans = px.bar(active_loans, x='label', y='outstanding',
                                      title='Outstanding Balance by Loan Account',
                                      labels={'outstanding': 'Outstanding Amount (₹)', 'label': 'Loan'},
                                      color='outstanding',
                                      color_continuous_scale='Reds',
                                      text_auto='.2s')
                    st.plotly_chart(fig_loans, use_container_width=True)
                else:
                    st.info("No active formal loans found.")

    with tab4:
        st.subheader("💳 Credit Card Analytics")
        
        cc_year = st.number_input("Select Year", min_value=2000, max_value=2100, value=datetime.now().year, key="cc_analytics_year")
        
        cc_start = datetime(cc_year, 1, 1).date()
        cc_end = datetime(cc_year, 12, 31).date()
        
        cc_trend = db.get_monthly_category_trend(user_id, 'Credit Card', str(cc_start), str(cc_end))
        
        if not cc_trend.empty:
            total_spend = cc_trend['total'].sum()
            if cc_year == datetime.now().year:
                 months_passed = datetime.now().month
            else:
                 months_passed = 12
            
            avg_monthly = total_spend / months_passed if months_passed > 0 else 0
            
            monthly_totals = cc_trend.groupby('month')['total'].sum()
            max_month = monthly_totals.idxmax()
            max_month_val = monthly_totals.max()
            min_month = monthly_totals.idxmin()
            min_month_val = monthly_totals.min()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Spends", f"₹{total_spend:,.0f}")
            m2.metric("Monthly Average", f"₹{avg_monthly:,.0f}")
            m3.metric("Highest Month", f"{max_month}", f"₹{max_month_val:,.0f}")
            m4.metric("Lowest Month", f"{min_month}", f"₹{min_month_val:,.0f}")
            

            
            st.markdown("---")
            
            st.markdown("### 📊 Monthly Spend by Card")
            fig1 = px.bar(cc_trend, x='month', y='total', color='category',
                        title='Monthly Breakdown by Card',
                        labels={'total': 'Amount (₹)', 'month': 'Month', 'category': 'Card'},
                        text_auto='.2s')
            fig1.update_layout(barmode='stack')
            st.plotly_chart(fig1, use_container_width=True)
            
            # --- New Total Trend Chart ---
            st.markdown("### 📈 Total Monthly Spending Trend")
            
            # Reset index for plotting if not already done (it is done later for MoM but we need it here)
            # Use a fresh copy to avoid conflicts with downstream logic
            mt_plot = cc_trend.groupby('month')['total'].sum().reset_index()
            
            fig_total = px.line(mt_plot, x='month', y='total', markers=True,
                               title='Total Monthly Credit Card Bill Trend',
                               labels={'total': 'Total Bill Amount (₹)', 'month': 'Month'})
            fig_total.update_traces(line_color='#e74c3c', line_width=4, marker=dict(size=10))
            fig_total.update_layout(hovermode='x unified')
            # Add text labels
            fig_total.add_trace(go.Scatter(
                x=mt_plot['month'], 
                y=mt_plot['total'],
                mode='text',
                text=[f"₹{x:,.0f}" for x in mt_plot['total']],
                textposition='top center',
                showlegend=False,
                textfont=dict(size=12, color='white')
            ))
            fig_total.update_layout(margin=dict(t=30, b=10))
            
            st.plotly_chart(fig_total, use_container_width=True)
            # -----------------------------
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown("### 💳 Total Spend per Card")
                card_totals = cc_trend.groupby('category')['total'].sum().reset_index()
                fig2 = px.pie(card_totals, values='total', names='category', hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)
                
            with col_g2:
                st.markdown("### 📉 Month-over-Month Change")
                monthly_totals = monthly_totals.reset_index()
                monthly_totals['prev_total'] = monthly_totals['total'].shift(1)
                monthly_totals['diff'] = monthly_totals['total'] - monthly_totals['prev_total']
                monthly_totals['color'] = monthly_totals['diff'].apply(lambda x: '#e74c3c' if x > 0 else '#2ecc71')
                
                mom_data = monthly_totals.dropna()
                
                if not mom_data.empty:
                    fig3 = go.Figure()
                    fig3.add_trace(go.Bar(
                        x=mom_data['month'],
                        y=mom_data['diff'],
                        marker_color=mom_data['color'],
                        text=mom_data['diff'].apply(lambda x: f"₹{x:,.0f}"),
                        textposition='auto'
                    ))
                    fig3.update_layout(title="Change from Previous Month", yaxis_title="Difference (₹)")
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Not enough data for MoM comparison")



            # --- Individual Card Trend ---
            st.markdown("---")
            st.markdown("### 💳 Individual Card Trends")
            
            unique_cards = cc_trend['category'].unique()
            selected_card = st.selectbox("Select Card to View Trend", unique_cards)
            
            if selected_card:
                card_data = cc_trend[cc_trend['category'] == selected_card]
                fig_card = px.line(card_data, x='month', y='total', markers=True,
                                  title=f'{selected_card} - Monthly Trend',
                                  labels={'total': 'Amount (₹)', 'month': 'Month'})
                fig_card.update_traces(line_color='#8e44ad', line_width=3)
                st.plotly_chart(fig_card, use_container_width=True)

            st.markdown("### 🔮 Next Year Prediction (Trend-Based)")
            
            avg_spend = total_spend / months_passed if months_passed > 0 else 0
            
            # Prepare data for regression
            trend_df = monthly_totals.sort_index().reset_index()
            trend_df['month_num'] = np.arange(len(trend_df))
            
            future_months = []
            future_values = []
            
            try:
                if len(trend_df) >= 2:
                    # Linear Regression: y = mx + c
                    z = np.polyfit(trend_df['month_num'], trend_df['total'], 1)
                    p = np.poly1d(z)
                    
                    st.info(f"Projected spending for {cc_year + 1} based on current trend (Slope: ₹{z[0]:.2f}/month).")
                    
                    last_month_num = trend_df['month_num'].iloc[-1]
                    
                    for i in range(1, 13):
                        future_date = datetime(cc_year + 1, i, 1)
                        future_months.append(future_date.strftime('%Y-%m'))
                        # Predict
                        pred_val = p(last_month_num + i)
                        future_values.append(max(0, pred_val)) # Cannot be negative
                else:
                    raise Exception("Not enough data")
            except:
                st.warning("Not enough data for trend analysis. Using average.")
                st.info(f"Projected spending for {cc_year + 1} based on {cc_year} average.")
                for i in range(1, 13):
                    future_date = datetime(cc_year + 1, i, 1)
                    future_months.append(future_date.strftime('%Y-%m'))
                    future_values.append(avg_spend)
            
            fig4 = go.Figure()

            fig4.add_trace(go.Scatter(
                x=future_months, y=future_values,
                mode='lines+markers',
                name='Projected Spend',
                line=dict(color='#9b59b6', dash='dash'),
                fill='tozeroy'
            ))
            fig4.update_layout(title=f"Projected Spending for {cc_year + 1}", yaxis_title="Amount (₹)")
            st.plotly_chart(fig4, use_container_width=True)
            
        else:
            st.info(f"No Credit Card transactions found for {cc_year}")

    with tab5:
        st.subheader("🚗 Vehicle Tracking")
        st.metric("Total Vehicle Spend", f"₹{summary['total_vehicle']:,.0f}")
        
        vehicle_breakdown = db.get_category_breakdown(user_id, 'Vehicle', str(analytics_start), str(analytics_end))
        if not vehicle_breakdown.empty:
            fig = px.bar(vehicle_breakdown, x='category', y='total',
                        title='Vehicle Expenses Breakdown',
                        color='category',
                        text_auto='.2s')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No vehicle data found")

    with tab6:
        st.subheader("⚖️ Period Comparison")
        
        comp_type = st.radio("Compare By", ["Month", "Year"], horizontal=True)
        
        col1, col2 = st.columns(2)
        
        if comp_type == "Month":
            with col1:
                st.markdown("### Period 1 (Base)")
                p1_start = st.date_input("Start Date", datetime.now().replace(day=1) - timedelta(days=30), key="p1_start")
                p1_end = st.date_input("End Date", datetime.now().replace(day=1) - timedelta(days=1), key="p1_end")
                
            with col2:
                st.markdown("### Period 2 (Current)")
                p2_start = st.date_input("Start Date", datetime.now().replace(day=1), key="p2_start")
                p2_end = st.date_input("End Date", datetime.now(), key="p2_end")
        else:
            current_year = datetime.now().year
            with col1:
                st.markdown("### Year 1 (Base)")
                y1 = st.number_input("Select Year", min_value=2000, max_value=2100, value=current_year-1, key="y1")
                p1_start = datetime(y1, 1, 1)
                p1_end = datetime(y1, 12, 31)
                
            with col2:
                st.markdown("### Year 2 (Current)")
                y2 = st.number_input("Select Year", min_value=2000, max_value=2100, value=current_year, key="y2")
                p2_start = datetime(y2, 1, 1)
                p2_end = datetime(y2, 12, 31)
        
        p1_summary = db.get_summary(user_id, str(p1_start), str(p1_end))
        p2_summary = db.get_summary(user_id, str(p2_start), str(p2_end))
            
        st.markdown("---")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Income Difference", f"₹{p2_summary['total_income']:,.0f}", 
                     delta=f"₹{p2_summary['total_income'] - p1_summary['total_income']:,.0f}")
        with c2:
            st.metric("Expense Difference", f"₹{p2_summary['total_expense']:,.0f}", 
                     delta=f"₹{p2_summary['total_expense'] - p1_summary['total_expense']:,.0f}", delta_color="inverse")
        with c3:
            st.metric("Savings Difference", f"₹{p2_summary['net_savings']:,.0f}", 
                     delta=f"₹{p2_summary['net_savings'] - p1_summary['net_savings']:,.0f}")
             
        st.subheader("Comparison Chart")
        
        comp_data = {
            'Period': ['Period 1', 'Period 1', 'Period 2', 'Period 2'],
            'Type': ['Income', 'Expense', 'Income', 'Expense'],
            'Amount': [p1_summary['total_income'], p1_summary['total_expense'], 
                      p2_summary['total_income'], p2_summary['total_expense']]
        }
        comp_df = pd.DataFrame(comp_data)
        
        fig = px.bar(comp_df, x='Period', y='Amount', color='Type', barmode='group',
                    color_discrete_map={'Income': '#2ecc71', 'Expense': '#e74c3c'})
        st.plotly_chart(fig, use_container_width=True)

    with tab7:
        st.subheader("🔮 12-Month Forecast (Reference)")
        st.info("This forecast is based on your historical average monthly income and expenses.")
        
        trend_all = db.get_monthly_trend(user_id)
        
        if not trend_all.empty:
            monthly_stats = trend_all.groupby('type')['total'].mean()
            avg_income = monthly_stats.get('Income', 0)
            avg_expense = monthly_stats.get('Expense', 0)
            avg_savings = avg_income - avg_expense
            
            st.write(f"**Historical Monthly Average:** Income: ₹{avg_income:,.0f} | Expense: ₹{avg_expense:,.0f} | Savings: ₹{avg_savings:,.0f}")
            
            forecast_months = []
            forecast_income = []
            forecast_expense = []
            forecast_savings = []
            
            current_date = datetime.now().replace(day=1)
            
            for i in range(1, 13):
                next_month = current_date + timedelta(days=30*i)
                forecast_months.append(next_month.strftime('%Y-%m'))
                forecast_income.append(avg_income)
                forecast_expense.append(avg_expense)
                forecast_savings.append(avg_savings * i)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=forecast_months, y=forecast_income, mode='lines+markers', name='Projected Income',
                line=dict(color='#2ecc71', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_months, y=forecast_expense, mode='lines+markers', name='Projected Expense',
                line=dict(color='#e74c3c', dash='dash')
            ))
            
            fig.update_layout(title="Projected Income & Expense (Next 12 Months)", xaxis_title="Month", yaxis_title="Amount (₹)")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("💰 Projected Cumulative Savings")
            fig2 = px.area(x=forecast_months, y=forecast_savings, title="Projected Cumulative Savings Growth",
                          labels={'x': 'Month', 'y': 'Cumulative Savings (₹)'})
            fig2.update_traces(line_color='#2980b9')
            st.plotly_chart(fig2, use_container_width=True)
            
        else:
            st.warning("Not enough historical data to generate a forecast.")

    with tab8:
        st.subheader("📺 Subscriptions Tracking")
        
        # Get Subscriptions Data
        # Updated to respect Quick View filters
        ott_trend = db.get_monthly_category_trend(user_id, 'Subscriptions', str(analytics_start), str(analytics_end))
        
        if ott_trend.empty:
            st.info("No Subscriptions data found.")
        else:
            total_ott = ott_trend['total'].sum()
            months_active = len(ott_trend['month'].unique())
            avg_ott = total_ott / months_active if months_active > 0 else 0
            
            c1, c2 = st.columns(2)
            c1.metric("Total Subs Spend", f"₹{total_ott:,.0f}")
            c2.metric("Monthly Average", f"₹{avg_ott:,.0f}")
            
            st.divider()
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### Cost by Platform")
                cat_split = ott_trend.groupby('category')['total'].sum().reset_index()
                fig_ott_pie = px.pie(cat_split, values='total', names='category', hole=0.4)
                st.plotly_chart(fig_ott_pie, use_container_width=True)
                
            with col_chart2:
                st.markdown("### Monthly Trend")
                monthly_ott = ott_trend.groupby('month')['total'].sum().reset_index()
                fig_ott_bar = px.bar(monthly_ott, x='month', y='total', text_auto='.0f')
                st.plotly_chart(fig_ott_bar, use_container_width=True)

    with tab9:
        st.subheader("🏠 Rent Tracking")
        st.info("Tracks expenses where category starts with 'Rent'.")
        
        # Logic: Get Monthly Category Trend for Expense, then filter result
        # This gives us monthly buckets. 
        # But wait, we also want total breakdown by Rent Type (e.g. Rent Home vs Rent Office)
        
        # 1. Fetch ALL expense trend data for the period (lowest granularity if possible? No, monthly is fine for trend)
        # Actually, get_monthly_category_trend groups by Month, Category. Perfect.
        
        rent_trend = db.get_monthly_category_trend(user_id, 'Expense', str(analytics_start), str(analytics_end))
        
        if not rent_trend.empty:
            # Filter for categories starting with "Rent"
            # Using case-insensitive match for robustness
            rent_trend = rent_trend[rent_trend['category'].str.startswith("Rent", na=False) | rent_trend['category'].str.startswith("rent", na=False)]
            
        if rent_trend.empty:
             st.info("No Rent-related expenses found for this period.")
             st.caption("Ensure your rent categories start with 'Rent' (e.g., 'Rent Home', 'Rent Office').")
        else:
            total_rent = rent_trend['total'].sum()
            months_active = len(rent_trend['month'].unique())
            avg_rent = total_rent / months_active if months_active > 0 else 0
            
            c1, c2 = st.columns(2)
            c1.metric("Total Rent Paid", f"₹{total_rent:,.0f}")
            c2.metric("Monthly Average", f"₹{avg_rent:,.0f}")
            
            st.divider()
            
            col_r1, col_r2 = st.columns(2)
            
            with col_r1:
                 st.markdown("### Cost by Type")
                 rent_split = rent_trend.groupby('category')['total'].sum().reset_index()
                 fig_rent_pie = px.pie(rent_split, values='total', names='category', hole=0.4)
                 st.plotly_chart(fig_rent_pie, use_container_width=True)
            
            with col_r2:
                st.markdown("### Monthly Trend")
                monthly_rent = rent_trend.groupby('month')['total'].sum().reset_index()
                fig_rent_bar = px.bar(monthly_rent, x='month', y='total', text_auto='.0f', title="Total Rent per Month")
                st.plotly_chart(fig_rent_bar, use_container_width=True)

    with tab10:
        st.subheader("👤 Self Expenses Tracking")
        st.info("Tracks expenses marked as 'Self / Personal'. These are specific to you and not shared.")
        
        # Logic: Fetch all expenses, then filter by is_self = 1
        # reusing get_monthly_category_trend won't give us the is_self column if it aggregates.
        # So we need to fetch transactions directly.
        
        self_trans = db.get_transactions(user_id, str(analytics_start), str(analytics_end), trans_type='Expense')
        
        if not self_trans.empty and 'is_self' in self_trans.columns:
            self_trans = self_trans[self_trans['is_self'] == 1]
            
        if self_trans.empty:
             st.info("No Self Expenses found for this period.")
        else:
            total_self = self_trans['amount'].sum()
            # Monthly Average
            self_trans['month'] = pd.to_datetime(self_trans['date']).dt.strftime('%Y-%m')
            months_active = len(self_trans['month'].unique())
            avg_self = total_self / months_active if months_active > 0 else 0
            
            c1, c2 = st.columns(2)
            c1.metric("Total Self Expenses", f"₹{total_self:,.0f}")
            c2.metric("Monthly Average", f"₹{avg_self:,.0f}")
            
            st.divider()
            
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                 st.markdown("### Cost by Category")
                 self_split = self_trans.groupby('category')['amount'].sum().reset_index()
                 fig_self_pie = px.pie(self_split, values='amount', names='category', hole=0.4)
                 st.plotly_chart(fig_self_pie, use_container_width=True)
            
            with col_s2:
                st.markdown("### Monthly Trend")
                monthly_self = self_trans.groupby('month')['amount'].sum().reset_index()
                fig_self_bar = px.bar(monthly_self, x='month', y='amount', text_auto='.0f', title="Total Self Expenses per Month")
                st.update_layout = fig_self_bar.update_layout(xaxis_title="Month", yaxis_title="Amount (₹)")
                st.plotly_chart(fig_self_bar, use_container_width=True)




# ========== PORTFOLIO PAGE ==========
elif page == "💼 Portfolio":
    st.markdown('<div class="main-header">💼 Portfolio & Net Worth</div>', unsafe_allow_html=True)
    
    # Fetch Data
    pf = db.get_portfolio_status(user_id)
    assets = pf['assets']
    liabs = pf['liabilities']
    net_worth = pf['net_worth']
    
    total_assets = sum(assets.values())
    total_liabs = sum(liabs.values())
    
    # 1. NET WORTH CARD
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h3 style="margin:0; font-weight: 300; opacity: 0.9;">NET WORTH</h3>
        <h1 style="margin:10px 0; font-size: 4rem; font-weight: 700;">₹{net_worth:,.0f}</h1>
        <div style="display: flex; justify-content: center; gap: 40px; margin-top: 15px;">
            <div>
                <span style="font-size: 0.9rem; opacity: 0.8;">TOTAL ASSETS</span><br>
                <span style="font-size: 1.5rem; font-weight: bold;">₹{total_assets:,.0f}</span>
            </div>
            <div style="border-left: 1px solid rgba(255,255,255,0.3);"></div>
            <div>
                <span style="font-size: 0.9rem; opacity: 0.8;">TOTAL LIABILITIES</span><br>
                <span style="font-size: 1.5rem; font-weight: bold;">₹{total_liabs:,.0f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Main Columns
    col_assets, col_liabs = st.columns(2)
    
    with col_assets:
        st.subheader("🟢 Assets")
        st.info("Includes Cash & Investments")
        
        # Breakdown
        for name, val in assets.items():
            st.metric(name, f"₹{val:,.0f}")
        
        # Donut Chart
        if total_assets > 0:
            asset_df = pd.DataFrame(list(assets.items()), columns=['Type', 'Value'])
            fig_a = px.pie(asset_df, values='Value', names='Type', hole=0.6, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_a.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig_a, use_container_width=True)
            
            # Investment Breakdown Chart
            st.divider()
            st.markdown("### 📈 Investment Breakdown")
            invest_data = db.get_category_breakdown(user_id, 'Investment') # Lifetime
            if not invest_data.empty:
               fig_inv = px.bar(invest_data, x='category', y='total', 
                               text_auto='.2s', 
                               labels={'total': 'Amount (₹)', 'category': 'Mode'},
                               color='category')
               fig_inv.update_layout(showlegend=False, height=300)
               st.plotly_chart(fig_inv, use_container_width=True)
            else:
               st.info("No investments found to graph.")
    with col_liabs:
        st.subheader("🔴 Liabilities")
        st.info("Outstanding Loans (Principal + Interest) & Friends Debt")
        
        # Breakdown
        for name, val in liabs.items():
            st.metric(name, f"₹{val:,.0f}")
            
        # Bar Chart
        if total_liabs > 0:
            liab_df = pd.DataFrame(list(liabs.items()), columns=['Type', 'Value'])
            fig_l = px.bar(liab_df, x='Type', y='Value', color='Type',
                         color_discrete_sequence=['#ff7675', '#d63031'])
            fig_l.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig_l, use_container_width=True)

    st.markdown("---")
    st.markdown("---")
    st.caption("ℹ️ 'Cash' is calculated as Total Lifetime Income minus Total Lifetime Expenses (including Investments, Vehicles & Loan Repayments).")

# ========== SETTINGS PAGE ==========
elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # --- ADMIN SECTION ---
    if st.session_state.is_admin:
        with st.expander("🛡️ Admin Panel - Password Requests", expanded=True):
             requests = db.get_pending_password_requests()
             if not requests.empty:
                 st.subheader(f"🔔 {len(requests)} Pending Request(s)")
                 for _, req in requests.iterrows():
                     with st.container():
                         c1, c2 = st.columns([3, 1])
                         c1.write(f"**User:** {req['username']} | **Date:** {req['request_date']}")
                         with c2:
                             with st.popover("Reset"):
                                 with st.form(f"reset_form_{req['id']}"):
                                     new_pass = st.text_input("New Password", type="password")
                                     if st.form_submit_button("Reset & Resolve"):
                                         if db.resolve_password_request(req['id'], new_pass, st.session_state.user_id):
                                             st.success("Password reset!")
                                             st.rerun()
                                         else:
                                             st.error("Failed.")
                         st.divider()
             else:
                 st.info("No pending password reset requests.")
    
    if st.session_state.is_admin:
        st.subheader("👥 User Management")
        with st.expander("➕ Add New User"):
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                is_admin_check = st.checkbox("Is Admin?")
                
                if st.form_submit_button("Create User"):
                    if new_username and new_password:
                        if db.create_user(new_username, new_password, 1 if is_admin_check else 0):
                            st.success(f"User '{new_username}' created successfully!")
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Please fill all fields")
        

        st.markdown("### Existing Users")
        users_df = db.get_all_users()
        
        # Display users with actions
        for _, user in users_df.iterrows():
            with st.expander(f"👤 {user['username']}" + (" (👑 Admin)" if user['is_admin'] else "")):
                col1, col2, col3 = st.columns([1, 2, 2])
                
                with col1:
                    st.caption(f"ID: {user['id']}")
                    if user['is_admin']:
                        st.badge("Admin")
                
                with col2:
                    # Password Reset
                    new_pwd = st.text_input("New Password", type="password", key=f"reset_pwd_{user['id']}")
                    if st.button("Update Password", key=f"btn_reset_{user['id']}"):
                        if len(new_pwd) >= 6:
                            db.reset_user_password(user['id'], new_pwd)
                            st.success("Password updated!")
                        else:
                            st.error("Password must be at least 6 characters")
                
                with col3:
                    # Delete User (prevent deleting self)
                    if user['id'] != st.session_state.user_id:
                        st.write("") # Spacer
                        st.write("") 
                        if st.button(f"🗑️ Delete {user['username']}", key=f"del_user_{user['id']}", type="secondary"):
                            db.delete_user(user['id'])
                            st.success(f"User {user['username']} deleted!")
                            st.rerun()
                    else:
                        st.info("Cannot delete yourself")

    if st.button("📤 Export to Excel"):
        transactions = db.get_transactions(user_id)
        if not transactions.empty:
            output_file = f"financial_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Export with multiple sheets
            try:
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    # 1. Master Sheet
                    transactions.to_excel(writer, sheet_name='All Transactions', index=False)
                    
                    # 2. Sheets by Type
                    trans_types = transactions['type'].unique()
                    for t_type in trans_types:
                        # Clean sheet name (removed invalid chars if any, limit len 31)
                        sheet_name = str(t_type)[:30]
                        type_df = transactions[transactions['type'] == t_type]
                        type_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                st.success(f"✅ Data exported to {output_file} with separate sheets!")
            except Exception as e:
                st.error(f"Export failed: {e}")
        else:
            st.warning("No data to export")
    
    st.markdown("---")
    
    st.subheader("Database Info")
    transactions = db.get_transactions(user_id)
    categories = db.get_categories(user_id)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Transactions", len(transactions))
    with col2:
        st.metric("Total Categories", len(categories))
    
    st.markdown("---")
    
    # st.subheader("⚠️ Danger Zone")
    # if st.button("🗑️ Clear All Data", type="secondary"):
    #     st.warning("This action cannot be undone!")
    #     if st.checkbox("I understand, delete all data"):
    #         st.error("Feature not implemented yet for safety")
