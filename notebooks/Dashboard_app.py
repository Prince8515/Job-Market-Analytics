import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.express as px
# Page configuration
st.set_page_config(
    page_title="Job Market Analytics",
    page_icon="📊",
    layout="wide"
)


# Dashboard title
st.title("📊 Job Market Analytics Dashboard")

st.write(
    "Explore job market trends, demand, companies, sources and salary insights."
)
loading = st.empty()

with loading.container():
    with st.spinner("Loading job market dataset..."):
        df = pd.read_csv("job_market_cleaned.csv")

    st.success(
        f"✅ Dataset loaded successfully — "
        f"{df.shape[0]:,} rows × {df.shape[1]} columns"
    )

time.sleep(1)

# =========================
# THEME TOGGLE
# =========================

st.sidebar.markdown("### 🎨 Appearance")

dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=False
)
if dark_mode:

    st.markdown("""
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161a23;
    }

    /* Normal text */
    .stMarkdown,
    p,
    label {
        color: #ffffff !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }

    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    /* Main background */
    .stApp {
        background-color: #ffffff;
        color: #111827;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5f7fb;
    }

    /* Normal text */
    .stMarkdown,
    p,
    label {
        color: #111827 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #111827 !important;
    }

    </style>
    """, unsafe_allow_html=True)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("🔎 Filters")


# -------------------------
# Reset function
# -------------------------

def reset_filters():
    st.session_state["job_role"] = "All"
    st.session_state["company"] = "All"
    st.session_state["schedule"] = "All"
    st.session_state["remote"] = "All"
    st.session_state["date_range"] = (min_date, max_date)


# -------------------------
# Prepare date column
# -------------------------

df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)

min_date = df["date_time"].min().date()
max_date = df["date_time"].max().date()


# -------------------------
# Job Role
# -------------------------

job_roles = ["All"] + sorted(
    df["title"].dropna().unique().tolist()
)

selected_role = st.sidebar.selectbox(
    "Job Role",
    job_roles,
    key="job_role"
)


# -------------------------
# Company
# -------------------------

companies = ["All"] + sorted(
    df["company_name"].dropna().unique().tolist()
)

selected_company = st.sidebar.selectbox(
    "Company",
    companies,
    key="company"
)


# -------------------------
# Job Schedule Type
# -------------------------

schedule_types = ["All"] + sorted(
    df["schedule_type"].dropna().unique().tolist()
)

selected_schedule = st.sidebar.selectbox(
    "Job Schedule Type",
    schedule_types,
    key="schedule"
)


# -------------------------
# Remote / Onsite
# -------------------------

remote_options = [
    "All",
    "Remote",
    "Non-Remote"
]

selected_remote = st.sidebar.selectbox(
    "Remote / Onsite",
    remote_options,
    key="remote"
)


# -------------------------
# Date Range
# -------------------------

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range"
)


# -------------------------
# Clear Filters
# -------------------------

st.sidebar.button(
    "🔄 Clear Filters",
    use_container_width=True,
    on_click=reset_filters
)


# =========================
# APPLY FILTERS
# =========================

filtered_df = df.copy()


# Job Role filter
if selected_role != "All":
    filtered_df = filtered_df[
        filtered_df["title"] == selected_role
    ]


# Company filter
if selected_company != "All":
    filtered_df = filtered_df[
        filtered_df["company_name"] == selected_company
    ]


# Schedule filter
if selected_schedule != "All":
    filtered_df = filtered_df[
        filtered_df["schedule_type"] == selected_schedule
    ]


# Remote filter
if selected_remote == "Remote":

    filtered_df = filtered_df[
        filtered_df["work_from_home"] == True
    ]

elif selected_remote == "Non-Remote":

    filtered_df = filtered_df[
        filtered_df["work_from_home"] != True
    ]


# Date filter
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["date_time"].dt.date >= start_date) &
        (filtered_df["date_time"].dt.date <= end_date)
    ]


# =========================
# SQLITE CONNECTION
# =========================

conn = sqlite3.connect(":memory:")

filtered_df.to_sql(
    "jobs",
    conn,
    index=False,
    if_exists="replace"
)


# =========================
# NOTEBOOK 4 - Q1
# =========================

total_jobs = pd.read_sql_query("""
    SELECT COUNT(*) AS Total_Job_Postings
    FROM jobs;
""", conn).iloc[0]["Total_Job_Postings"]


# Q6 - Remote Jobs
remote_jobs = pd.read_sql_query("""
    SELECT COUNT(*) AS Work_From_Home_Jobs
    FROM jobs
    WHERE work_from_home = 1;
""", conn).iloc[0]["Work_From_Home_Jobs"]


# Unique Companies
unique_companies = pd.read_sql_query("""
    SELECT COUNT(DISTINCT company_name) AS Unique_Companies
    FROM jobs;
""", conn).iloc[0]["Unique_Companies"]


# Q5 - Most Common Schedule
top_schedule = pd.read_sql_query("""
    SELECT schedule_type, COUNT(*) AS Job_Post_Count
    FROM jobs
    GROUP BY schedule_type
    ORDER BY Job_Post_Count DESC
    LIMIT 1;
""", conn).iloc[0]

top_schedule_name = top_schedule["schedule_type"]
top_schedule_count = top_schedule["Job_Post_Count"]


remote_percentage = (remote_jobs / total_jobs) * 100

st.markdown("""
<style>
.kpi-card {
    padding: 18px 20px;
    border-radius: 12px;
    min-height: 125px;
    border: 1px solid #e1e7f0;
}

.kpi-title {
    font-size: 14px;
    font-weight: 600;
    color: #17305f;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 27px;
    font-weight: 700;
    color: #0b1f4b;
}

.kpi-subtitle {
    font-size: 12px;
    color: #5b6b88;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card" style="background-color:#eaf3ff;">
        <div class="kpi-title">📊 Total Job Postings</div>
        <div class="kpi-value">{int(total_jobs):,}</div>
        <div class="kpi-subtitle">In dataset</div>
    </div>
    """, unsafe_allow_html=True)


with col2:
    st.markdown(f"""
    <div class="kpi-card" style="background-color:#e9f9ef;">
        <div class="kpi-title">🏠 Remote Jobs</div>
        <div class="kpi-value">{int(remote_jobs):,}</div>
        <div class="kpi-subtitle">▲ {remote_percentage:.1f}% of total</div>
    </div>
    """, unsafe_allow_html=True)


with col3:
    st.markdown(f"""
    <div class="kpi-card" style="background-color:#fff8df;">
        <div class="kpi-title">🏢 Unique Companies</div>
        <div class="kpi-value">{int(unique_companies):,}</div>
        <div class="kpi-subtitle">Companies hiring</div>
    </div>
    """, unsafe_allow_html=True)


with col4:
    st.markdown(f"""
    <div class="kpi-card" style="background-color:#f3eaff;">
        <div class="kpi-title">📅 Top Schedule Type</div>
        <div class="kpi-value">{top_schedule_name}</div>
        <div class="kpi-subtitle">◷ Most common · {int(top_schedule_count):,} postings</div>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Job Roles + Top 5 Companies

col1, col2 = st.columns(2)

with col1:

    # Notebook 4 - Q2
    top_roles = pd.read_sql_query("""
        SELECT title, COUNT(*) AS Job_Count
        FROM jobs
        GROUP BY title
        ORDER BY Job_Count DESC
        LIMIT 5;
    """, conn)

    fig = px.bar(
        top_roles,
        x="Job_Count",
        y="title",
        orientation="h",
        text="Job_Count",
        title="📊 Top 5 Job Roles"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="",
        xaxis_title="Number of Job Postings",
        yaxis={"categoryorder": "total ascending"},
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    # Notebook 4 - Q3
    top_companies = pd.read_sql_query("""
        SELECT company_name, COUNT(*) AS Job_Post_Count
        FROM jobs
        GROUP BY company_name
        ORDER BY Job_Post_Count DESC
        LIMIT 5;
    """, conn)

    fig = px.bar(
        top_companies,
        x="Job_Post_Count",
        y="company_name",
        orientation="h",
        text="Job_Post_Count",
        title="🏢 Top 5 Companies"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="",
        xaxis_title="Number of Job Postings",
        yaxis={"categoryorder": "total ascending"},
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

# Top 5 JOB-SOURCES + JOB-SCHEDULES
col1 , col2 = st.columns(2)
with col1:

    # Notebook 4 - Q4
    top_sources = pd.read_sql_query("""
        SELECT via, COUNT(*) AS Job_Post_Count
        FROM jobs
        GROUP BY via
        ORDER BY Job_Post_Count DESC
        LIMIT 5;
    """, conn)

    fig = px.bar(
        top_sources,
        x="Job_Post_Count",
        y="via",
        orientation="h",
        text="Job_Post_Count",
        title="🔗 Top 5 Job Sources"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="",
        xaxis_title="Number of Job Postings",
        yaxis={"categoryorder": "total ascending"},
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)
with col2:

    # Notebook 4 - Q5
    schedule_types = pd.read_sql_query("""
        SELECT schedule_type, COUNT(*) AS Job_Post_Count
        FROM jobs
        GROUP BY schedule_type
        ORDER BY Job_Post_Count DESC
        LIMIT 5;
    """, conn)

    fig = px.pie(
        schedule_types,
        names="schedule_type",
        values="Job_Post_Count",
        title="📅 Job Schedule Types"
    )

    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        hovertemplate="<b>%{label}</b><br>Jobs: %{value:,}<br>Share: %{percent}<extra></extra>"
    )

    fig.update_layout(
        height=350,
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5
        ),
        margin=dict(l=10, r=80, t=50, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
#Job postings by month + Average yerea salary by role
col1, col2 = st.columns(2)

with col1:

    # Notebook 4 - Q8
    monthly_jobs = pd.read_sql_query("""
        SELECT Posted_Month, COUNT(*) AS Job_Count
        FROM jobs
        WHERE Posted_Month IS NOT NULL
        GROUP BY Posted_Month
        ORDER BY Posted_Month;
    """, conn)

    # Convert month numbers to names
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    monthly_jobs["Month"] = monthly_jobs["Posted_Month"].map(month_names)

    fig = px.line(
        monthly_jobs,
        x="Month",
        y="Job_Count",
        markers=True,
        title="📈 Job Postings by Month"
    )

    fig.update_traces(
        text=monthly_jobs["Job_Count"],
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Job Postings",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:
    # Notebook 4 - Q7
    salary_by_role = pd.read_sql_query("""
        SELECT title, AVG(salary_yearly) AS Avg_Salary
        FROM jobs
        WHERE salary_yearly IS NOT NULL
        GROUP BY title
        HAVING COUNT(*) >= 10
        ORDER BY Avg_Salary DESC
        LIMIT 5;
    """, conn)

    fig = px.bar(
        salary_by_role,
        x="title",
        y="Avg_Salary",
        text="Avg_Salary",
        title="💰 Average Yearly Salary by Role"
    )

    fig.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Average Yearly Salary ($)",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

# Top Remote Jobs by Role

st.subheader("🏆 Top Remote Jobs by Role")

remote_roles = pd.read_sql_query("""
    SELECT
        title,
        COUNT(*) AS Total_Postings,
        SUM(CASE WHEN work_from_home = 1 THEN 1 ELSE 0 END) AS Remote_Postings
    FROM jobs
    GROUP BY title
    ORDER BY Remote_Postings DESC
    LIMIT 5;
""", conn)

remote_roles["Remote_%"] = (
    remote_roles["Remote_Postings"] /
    remote_roles["Total_Postings"] * 100
)

remote_roles.insert(
    0,
    "Rank",
    range(1, len(remote_roles) + 1)
)

remote_roles["Total_Postings"] = remote_roles["Total_Postings"].map(
    lambda x: f"{int(x):,}"
)

remote_roles["Remote_Postings"] = remote_roles["Remote_Postings"].map(
    lambda x: f"{int(x):,}"
)

remote_roles["Remote_%"] = remote_roles["Remote_%"].map(
    lambda x: f"{x:.1f}%"
)

remote_roles = remote_roles.rename(columns={
    "title": "Job Title",
    "Total_Postings": "Total Postings",
    "Remote_Postings": "Remote Postings",
    "Remote_%": "Remote %"
})

st.dataframe(
    remote_roles,
    use_container_width=True,
    hide_index=True
)
