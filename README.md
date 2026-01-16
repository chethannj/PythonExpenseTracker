# 💰 Expense Tracker Dashboard (Streamlit + SQLite)

A **real-world Python web app** to track daily expenses, store them in a **SQLite database**, and visualize spending insights using an interactive **Streamlit dashboard**.

✅ Add expenses  
✅ Store data in SQLite (persistent storage)  
✅ Filter by month / category / minimum amount  
✅ KPI cards (Total spent, Average expense, Total entries)  
✅ Charts (Monthly trend + Category spending)  
✅ Export monthly report as CSV  
✅ Delete wrong entries  

---

🚀 Tech Stack

Python

Streamlit (UI Dashboard)

SQLite (Database)

Pandas (Data Analysis)

Matplotlib (Charts)

expense-tracker-streamlit/
│
├── app.py
├── expenses.db          # auto-created
├── outputs/             # auto-created
├── requirements.txt
└── README.md

Installation
Option A: Using uv (Recommended)
1) Clone the repository
git clone <your-repo-url>
cd expense-tracker-streamlit

2) Create virtual environment
uv venv
