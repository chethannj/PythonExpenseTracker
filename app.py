import sqlite3
import streamlit as st
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DB_NAME="expenses.db"
OUTPUT_DIR=Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

####### DB Connection#####
def get_conn():
    return sqlite3.connect(DB_NAME,check_same_thread=False)

#Initialize DB
def init_db():
    with get_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     amount REAL NOT NULL,
                     category TEXT NOT NULL,
                     note TEXT,
                     created_at TEXT NOT NULL
                        )""")
#Insert Expense
def insert_expense(amount,category,note,created_at):
    with get_conn() as conn:
        conn.execute("INSERT INTO expenses (amount,category,note,created_at) VALUES (?,?,?,?)",
                     (amount,category,note,created_at))
        
#Delete Expense
def delete_expense(expense_id:int):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id=?",(expense_id,))

#Fetch Expenses
def fetch_expenses():
    with get_conn() as conn:
        df=pd.read_sql_query("SELECT * FROM expenses ORDER BY created_at DESC",conn)


    if df.empty:
        return df

    df["created_at"]=pd.to_datetime(df["created_at"])

    df["month"]=df["created_at"].dt.to_period("M").astype(str)
    return df


###### CHARTS & VISUALIZATIONS ######
def monthly_trend_chart(monthly_totals:pd.DataFrame):
    fig=plt.figure(figsize=(8,4))
    plt.plot(monthly_totals["month"],monthly_totals["amount"],marker='o')
    plt.title("Monthly Expense Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def category_bar_chart(category_totals:pd.DataFrame,top_n=6):
    fig=plt.figure(figsize=(8,4))
    top_categories=category_totals.head(top_n)
    plt.bar(top_categories["category"],top_categories["amount"],color='skyblue')
    plt.title("Top Spending Categories")
    plt.xlabel("Category")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

###### STREAMLIT UI ######
st.set_page_config(page_title="Expense Tracker Dashboard", layout="wide")
init_db()
st.title("Expense Tracker Dashboard Python+SQLite+Streamlit")

##Sidebar - Add Expense
st.sidebar.header("Add New Expense")
amount=st.sidebar.number_input("Amount",min_value=0.0,step=10.0,format="%.2f")
category=st.sidebar.selectbox("Category",["Food","Travel","Shopping","Entertainment","Health","Other"])
note=st.sidebar.text_input("Note(Optional)")

expense_date=st.sidebar.date_input("Date")

expense_time=st.sidebar.time_input("Time")

created_at=datetime.combine(expense_date,expense_time).strftime("%Y-%m-%d %H:%M:%S")

if st.sidebar.button("Add Expense"):
    if(amount<=0):
        st.sidebar.error("Amount must be greater than zero.")
    else:
        insert_expense(amount,category,note,created_at)
        st.sidebar.success("Expense added successfully!")
        st.rerun()
st.sidebar.markdown("---")
st.sidebar.info("Tips: Add a few expenses to see visualizations.")

#Main Data
df=fetch_expenses()

if df.empty:
    st.warning("No expenses recorded yet. Please add some expenses using the sidebar.")
    st.stop()

#Filter Options
st.subheader("Filter Expenses")
col1,col2,col3=st.columns(3)
with col1:
    month_filter=st.selectbox("Select Month",options=["All"]+sorted(df["month"].unique().tolist()))
with col2:
    category_filter=st.selectbox("Select Category",options=["All"]+sorted(df["category"].unique().tolist()))
with col3:
    min_amount=st.number_input("Minimum Amount",min_value=0.0,step=10.0,format="%.2f",value=0.0)

filtered_df=df.copy()

if month_filter!="All":
    filtered_df=filtered_df[filtered_df["month"]==month_filter]

if category_filter!="All":
    filtered_df=filtered_df[filtered_df["category"]==category_filter]

filtered_df=filtered_df[filtered_df["amount"]>=min_amount]

st.subheader("Expense Records")
k1,k2,k3=st.columns(3)
k1.metric("Total Spent",f"${filtered_df['amount'].sum():,.2f}")
k2.metric("Number of Expenses",f"{len(filtered_df)}")
k3.metric("Average Expense",f"${filtered_df['amount'].mean():,.2f}")

st.markdown("----")


#Agreggations

monthly_totals=filtered_df.groupby("month")["amount"].sum().reset_index().sort_values("month")
category_totals=filtered_df.groupby("category")["amount"].sum().reset_index().sort_values("amount",ascending=False)

#Charts

st.subheader("Dashboard Charts")
c1,c2=st.columns(2)

with c1:
    st.pyplot(monthly_trend_chart(monthly_totals))
with c2:
    st.pyplot(category_bar_chart(category_totals))
st.markdown("----")

#Data table
st.subheader("Expense Data Table")
st.dataframe(filtered_df[["id","amount","category","note","created_at"]],use_container_width=True)

#Downlod CSV
st.subheader("Download Expense Data")
report_df=monthly_totals.copy()
csv_data=report_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Monthly Expense Report as CSV",
    data=csv_data,
    file_name="monthly_expense_report.csv",
    mime="text/csv"
)

#Delete Expense in Streamlit
st.subheader("Delete an Expense")

delete_id=st.number_input("Enter Expense ID to Delete",min_value=0,step=1)

if st.button("Delete Expense"):
    delete_expense(int(delete_id))
    st.success(f"Expense with ID {int(delete_id)} deleted successfully!")
    st.rerun()
