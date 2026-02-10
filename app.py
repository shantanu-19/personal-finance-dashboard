import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

# --- DATA LOADING ---
# Updated path to match your folder structure
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "finances.csv")

def load_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- SIDEBAR: TRANSACTION ENTRY ---
st.sidebar.header("Add New Transaction")
date = st.sidebar.date_input("Date", datetime.today())
category = st.sidebar.selectbox("Category", ["Rent", "Food", "Salary", "Transport", "Entertainment", "Utilities", "Other"])
t_type = st.sidebar.radio("Type", ["Income", "Expense"])
amount = st.sidebar.number_input("Amount", min_value=0.0, step=10.0)

if st.sidebar.button("Add Transaction"):
    new_data = pd.DataFrame([[pd.to_datetime(date), category, t_type, amount]], 
                            columns=["Date", "Category", "Type", "Amount"])
    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df)
    st.sidebar.success("Added!")
    st.rerun()

# --- MAIN DASHBOARD ---
st.title("💸 Personal Finance Dashboard")

if not df.empty:
    # 1. Metrics
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_savings = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income:,.2f}")
    col2.metric("Total Expenses", f"${total_expense:,.2f}")
    col3.metric("Net Savings", f"${net_savings:,.2f}", delta=f"{net_savings:,.2f}")

    # 2. Visualizations
    st.divider()
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Spending by Category")
        expense_df = df[df["Type"] == "Expense"].groupby("Category")["Amount"].sum()
        if not expense_df.empty:
            fig, ax = plt.subplots()
            expense_df.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90, colors=plt.cm.Paired.colors)
            ax.set_ylabel("")
            st.pyplot(fig)
        else:
            st.info("No expenses to show.")

    with chart_col2:
        st.subheader("Income vs Expenses Over Time")
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        monthly_df = df.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
        
        fig, ax = plt.subplots()
        monthly_df.plot(kind='bar', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # 3. Savings Prediction
    st.divider()
    st.subheader("🔮 Monthly Savings Prediction")
    
    monthly_summary = df.copy()
    monthly_summary['Month'] = monthly_summary['Date'].dt.to_period('M').astype(str)
    monthly_savings = monthly_summary.pivot_table(index='Month', columns='Type', values='Amount', aggfunc='sum').fillna(0)
    
    if 'Income' in monthly_savings and 'Expense' in monthly_savings:
        monthly_savings['Savings'] = monthly_savings['Income'] - monthly_savings['Expense']
        
        if len(monthly_savings) >= 1:
            avg_savings = monthly_savings['Savings'].mean()
            st.write(f"Based on your data, your predicted monthly savings is: **${avg_savings:,.2f}**")
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(monthly_savings.index, monthly_savings['Savings'], marker='o', color='green')
            ax.axhline(avg_savings, color='red', linestyle='--', label='Average')
            st.pyplot(fig)
    
    with st.expander("View Transaction History"):
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
else:
    st.info("Please add transactions in the sidebar to get started!")