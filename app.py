import streamlit as st 
import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = "data.json"

# Load data
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save data
def save_expenses(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Convert to DataFrame
def get_dataframe(expenses):
    return pd.DataFrame(expenses)

# Pie chart
def pie_chart(df):
    fig, ax = plt.subplots()
    cat_totals = df.groupby("category")["amount"].sum()
    ax.pie(cat_totals, labels=cat_totals.index, autopct='%1.1f%%')
    ax.set_title("Spending by Category")
    st.pyplot(fig)

# Bar chart
def bar_chart(df):
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    month_totals = df.groupby("month")["amount"].sum()
    fig, ax = plt.subplots()
    month_totals.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_title("Monthly Expense Summary")
    ax.set_ylabel("Amount")
    st.pyplot(fig)

# --- Streamlit UI ---

st.title("💰 Personal Expense Tracker")

# Load data
expenses = load_expenses()

# ➕ Add Expense Form
with st.form("expense_form"):
    st.subheader("➕ Add New Expense")
    date = st.date_input("📅 Date", value=datetime.today())
    category = st.selectbox("📂 Category", ["Food", "Transport", "Bills", "Shopping", "Other"])
    amount = st.number_input("💵 Amount", min_value=0.0, step=0.1)
    description = st.text_input("📝 Description (optional)")
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        new_expense = {
            "date": date.strftime("%Y-%m-%d"),
            "category": category,
            "amount": amount,
            "description": description
        }
        expenses.append(new_expense)
        save_expenses(expenses)
        st.success("✅ Expense added!")
        st.rerun()

# 🗑️ Delete Expense
if expenses:
    st.subheader("🗑️ Delete Expense")
    delete_options = [f"{i} - {e['date']} | {e['category']} | ${e['amount']} | {e['description']}" for i, e in enumerate(expenses)]
    to_delete = st.selectbox("Select expense to delete", delete_options)
    if st.button("❌ Delete Selected Expense"):
        index = int(to_delete.split(" - ")[0])
        deleted_item = expenses.pop(index)
        save_expenses(expenses)
        st.success(f"🗂️ Deleted: {deleted_item['category']} on {deleted_item['date']} (${deleted_item['amount']})")
        st.rerun()

# 📋 All Expenses Table
df = get_dataframe(expenses)
if not df.empty:
    st.subheader("📋 All Expenses")
    st.dataframe(df)

    # 🔍 Filters
    st.subheader("🔍 Filter Expenses")
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("📁 Filter by Category", ["All"] + sorted(df["category"].unique()))
    with col2:
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        month_filter = st.selectbox("📆 Filter by Month", ["All"] + sorted(df["month"].unique()))

    filtered_df = df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]
    if month_filter != "All":
        filtered_df = filtered_df[filtered_df["month"] == month_filter]

    st.markdown("### 🔽 Filtered Results")
    st.dataframe(filtered_df.drop(columns=["month"], errors="ignore"))

    # 📊 Summary Section
    st.subheader("📊 Summary Report")
    total = filtered_df["amount"].sum()
    average = filtered_df["amount"].mean() if not filtered_df.empty else 0
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label="🧾 Total Expenses", value=f"${total:.2f}")
    with col4:
        st.metric(label="📉 Average Expense", value=f"${average:.2f}")

    # 📈 Charts
    st.subheader("📈 Visualizations")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### 🥧 Pie Chart")
        pie_chart(filtered_df)
    with col6:
        st.markdown("#### 📊 Bar Chart")
        bar_chart(filtered_df)

    # 📤 Export
    st.subheader("📤 Export")
    csv = filtered_df.drop(columns='month', errors='ignore').to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data as CSV", csv, "expenses.csv", "text/csv")
else:
    st.info("ℹ️ No expenses yet. Add some above!")
