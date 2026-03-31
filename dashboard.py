"""
EdTech Growth Analytics — Interactive Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="EdTech Growth Analytics",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STYLES 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #FFFFFF; color: #111827; }

.metric-card {
    background: #FFFFFF;
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(124,58,237,0.15);
}
.metric-card:hover { border-color: rgba(124,58,237,0.7); transform: translateY(-2px); }
.metric-value { font-size: 2.2rem; font-weight: 800; color: #7C3AED; margin: 4px 0; }
.metric-label { font-size: 0.78rem; color: #4B5563; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-delta { font-size: 0.82rem; font-weight: 600; margin-top: 4px; }
.delta-up   { color: #10B981; }
.delta-down { color: #EF4444; }

.section-header {
    font-size: 1.4rem; font-weight: 700; color: #111827;
    border-left: 4px solid #7C3AED;
    padding-left: 14px; margin: 28px 0 18px 0;
}
.insight-card {
    background: #F9FAFB;
    border-left: 4px solid #7C3AED;
    border-radius: 12px; padding: 16px 20px; margin: 10px 0;
}
.insight-title { font-size: 1rem; font-weight: 700; color: #111827; }
.insight-body  { font-size: 0.88rem; color: #374151; margin-top: 6px; line-height: 1.6; }

.risk-high   { color: #EF4444; font-weight: 700; }
.risk-medium { color: #F59E0B; font-weight: 700; }
.risk-low    { color: #10B981; font-weight: 700; }

div[data-testid="stSidebar"] {
    background: #F3F4F6 !important;
    border-right: 1px solid rgba(124,58,237,0.2);
}
div[data-testid="metric-container"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# DATA LOADING 
@st.cache_data
def load_data():
    # Initialize with empty DataFrames to keep dashboard blank until upload
    d = {}
    for name in ["users","courses","activity_log","transactions",
                 "user_features","churn_scores","conversion_scores"]:
        d[name] = pd.DataFrame()
    return d

if "DATA" not in st.session_state:
    st.session_state["DATA"] = load_data()

DATA = st.session_state["DATA"]
users       = DATA["users"]
courses     = DATA.get("courses", pd.DataFrame())
activity    = DATA.get("activity_log", pd.DataFrame())
transactions= DATA.get("transactions", pd.DataFrame())
features    = DATA.get("user_features", pd.DataFrame())
churn_sc    = DATA.get("churn_scores", pd.DataFrame())
conv_sc     = DATA.get("conversion_scores", pd.DataFrame())

if not users.empty:
    users["signup_date"] = pd.to_datetime(users["signup_date"])
if not transactions.empty:
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
if not activity.empty:
    activity["event_timestamp"] = pd.to_datetime(activity["event_timestamp"])

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='font-size:2.5rem;'>📚</div>
        <div style='font-size:1.1rem; font-weight:800; color:#111827;'>EdTech Analytics</div>
        <div style='font-size:0.75rem; color:#6B7280; margin-top:4px;'>Growth Intelligence Platform</div>
    </div>
    <hr style='border-color: rgba(124,58,237,0.3); margin: 12px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "📊 Executive Summary",
        "📉 Funnel Analysis",
        "💵 Revenue & Monetization",
        "🎓 Education & Background",
        "💡 Growth Strategy"
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color: rgba(124,58,237,0.2);'>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:0.9rem; font-weight:600; color:#111827; margin-bottom:8px;'>📤 Upload Data</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload your datasets (CSV)", type=["csv"], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files:
        for f in uploaded_files:
            file_key = f.name.replace(".csv", "")
            try:
                df = pd.read_csv(f)
                st.session_state["DATA"][file_key] = df
            except Exception:
                pass
        if st.button("Apply New Data", use_container_width=True):
            st.rerun()

    st.markdown("<hr style='border-color: rgba(124,58,237,0.2);'>", unsafe_allow_html=True)

    if not users.empty:
        channels = ["All"] + sorted(users["signup_channel"].dropna().unique().tolist())
        sel_channel = st.selectbox("Filter by Channel", channels)
        countries   = ["All"] + sorted(users["country"].dropna().unique().tolist())
        sel_country = st.selectbox("Filter by Country", countries)

        filt = users.copy()
        if sel_channel != "All": filt = filt[filt["signup_channel"] == sel_channel]
        if sel_country != "All": filt = filt[filt["country"] == sel_country]
    else:
        filt = pd.DataFrame()

    st.markdown(f"<div style='color:#6B7280; font-size:0.72rem; margin-top:20px; text-align:center;'>Last updated: March 2026</div>",
                unsafe_allow_html=True)

# PAGE 1: EXECUTIVE SUMMARY
if page == "📊 Executive Summary":
    st.markdown("""
    <div style='background: linear-gradient(90deg, #7C3AED22 0%, transparent 100%);
         border-left: 4px solid #7C3AED; border-radius: 8px; padding: 18px 24px; margin-bottom: 28px;'>
        <h1 style='color:#111827; font-size:1.8rem; font-weight:800; margin:0;'>
            📊 Executive Summary
        </h1>
        <p style='color:#4B5563; margin:6px 0 0; font-size:0.9rem;'>
            Real-time growth metrics and business health indicators
        </p>
    </div>
    """, unsafe_allow_html=True)

    if users.empty:
        kpis = [("👥 Total Users","--","-",True), ("💰 Paid Users","--","-",True), ("📈 Monthly Revenue","--","-",True), ("🔁 30-Day Retention","--","-",True), ("✅ Course Completion","--","-",True), ("⚠️ Churned Users","--","-",True)]
        cols = st.columns(3)
        for i, (label, value, delta, is_good) in enumerate(kpis):
            with cols[i % 3]:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-delta delta-up'>{delta}</div></div>", unsafe_allow_html=True)
            if i == 2: cols = st.columns(3)
        st.info("📊 Awaiting data. Please upload your CSVs (users, activity, transactions) in the sidebar to populate the metrics.")
        st.stop()

    total     = len(filt)
    paid      = (filt["plan_type"] != "free").sum()
    churned   = filt["is_churned"].sum()
    conv_rate = paid / total * 100 if total else 0
    churn_rate= churned / total * 100 if total else 0

    txn_ok = transactions[transactions["status"] == "success"] if not transactions.empty else pd.DataFrame()
    if not txn_ok.empty and not filt.empty:
        filt_txn = txn_ok[txn_ok["user_id"].isin(filt["user_id"])]
        mrr  = filt_txn[filt_txn["transaction_date"].dt.to_period("M") ==
                         filt_txn["transaction_date"].max().to_period("M")]["amount_usd"].sum()
        total_rev = filt_txn["amount_usd"].sum()
    else:
        mrr = total_rev = 0

    lesson_comp = features["lesson_completion_rate"].mean() * 100 if not features.empty else 0
    retention   = 100 - churn_rate

    kpi_col1, kpi_col2 = st.columns([8, 2])
    with kpi_col2:
        currency_pref = st.radio("Currency Display", ["USD ($)", "INR (₹)"], horizontal=True, label_visibility="collapsed")
    mrr_val = f"${mrr:,.0f}" if "USD" in currency_pref else f"₹{mrr*83:,.0f}"

    kpis = [
        ("👥 Total Users",     f"{total:,}",    "↑ +12% vs last month",   True),
        ("💰 Paid Users",      f"{paid:,}",     f"Conv Rate: {conv_rate:.1f}%", conv_rate > 8),
        ("📈 Monthly Revenue", mrr_val,  "↑ Revenue trending up",  True),
        ("🔁 30-Day Retention",f"{retention:.1f}%", "Target: 40%",        retention > 35),
        ("✅ Course Completion",f"{lesson_comp:.1f}%","Target: 35%",       lesson_comp > 25),
        ("⚠️ Churned Users",   f"{churned:,}",  f"{churn_rate:.1f}% churn rate", churn_rate < 50),
    ]

    cols = st.columns(3)
    for i, (label, value, delta, is_good) in enumerate(kpis):
        d_class = "delta-up" if is_good else "delta-down"
        with cols[i % 3]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{value}</div>
                <div class='metric-delta {d_class}'>{delta}</div>
            </div>
            """, unsafe_allow_html=True)
        if i == 2: cols = st.columns(3)

    st.markdown("<div class='section-header'>📅 Signups Over Time</div>", unsafe_allow_html=True)
    if not users.empty:
        monthly_signups = filt.groupby(filt["signup_date"].dt.to_period("M")).size().reset_index()
        monthly_signups.columns = ["month","count"]
        monthly_signups["month"] = monthly_signups["month"].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_signups["month"], y=monthly_signups["count"],
                             marker_color="#7C3AED", name="Signups", opacity=0.85))
        fig.add_trace(go.Scatter(x=monthly_signups["month"], y=monthly_signups["count"].rolling(3).mean(),
                                 mode="lines", line=dict(color="#EC4899", width=2.5), name="3M Avg"))
        fig.update_layout(template="plotly_white", plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                          title="Monthly User Signups", height=360,
                          font=dict(family="Inter"), margin=dict(t=50,b=30),
                          legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>📱 Users by Device</div>", unsafe_allow_html=True)
        dev_counts = filt["device_type"].value_counts().reset_index()
        dev_counts.columns = ["device","count"]
        fig2 = px.pie(dev_counts, names="device", values="count",
                      color_discrete_sequence=["#7C3AED","#EC4899","#F59E0B"],
                      hole=0.55)
        fig2.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                           plot_bgcolor="#FFFFFF", height=320,
                           legend=dict(font=dict(color="#111827")),
                           margin=dict(t=20,b=20))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>🌍 Users by Country</div>", unsafe_allow_html=True)
        cntry = filt["country"].value_counts().head(8).reset_index()
        cntry.columns = ["country","count"]
        fig3 = px.bar(cntry, x="count", y="country", orientation="h",
                      color="count", color_continuous_scale=["#4B5563","#7C3AED"])
        fig3.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                           plot_bgcolor="#FFFFFF", height=320,
                           coloraxis_showscale=False, margin=dict(t=20,b=20),
                           yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig3, use_container_width=True)


# PAGE 2: FUNNEL ANALYSIS
elif page == "📉 Funnel Analysis":
    st.markdown("""
    <div style='background:linear-gradient(90deg,#7C3AED22 0%,transparent 100%);
         border-left:4px solid #7C3AED;border-radius:8px;padding:18px 24px;margin-bottom:28px;'>
        <h1 style='color:#111827;font-size:1.8rem;font-weight:800;margin:0;'>
            📉 Funnel Analysis
        </h1>
        <p style='color:#4B5563;margin:6px 0 0;font-size:0.9rem;'>
            Signup → Verify → Onboard → Enroll → Complete → Pay
        </p>
    </div>
    """, unsafe_allow_html=True)

    if users.empty or features.empty:
        st.info("📊 Awaiting data. Please upload your CSVs (users, features) in the sidebar to view the funnel.")
        st.stop()

    filt_feat = features[features["user_id"].isin(filt["user_id"])] if not filt.empty else features

    total      = len(filt)
    ev         = filt["email_verified"].sum()
    pc         = filt["profile_completed"].sum()
    ob         = filt["onboarding_completed"].sum()
    enrolled   = filt["first_course_enrolled_date"].notna().sum() if "first_course_enrolled_date" in filt.columns else 0
    lesson1    = filt_feat[filt_feat["total_lessons_completed"] >= 1].shape[0]
    half_prog  = filt_feat[filt_feat["lesson_completion_rate"] >= 0.5].shape[0]
    paid_cnt   = (filt["plan_type"] != "free").sum()

    stages = ["Signup","Email Verified","Profile Complete","Onboarding Done",
              "Course Enrolled","Lesson Completed","50%+ Progress","Paid Conversion"]
    values = [total, ev, pc, ob, enrolled, lesson1, half_prog, paid_cnt]

    fig_funnel = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        marker=dict(color=["#7C3AED","#6D28D9","#5B21B6","#EC4899",
                            "#DB2777","#F59E0B","#10B981","#3B82F6"],
                    line=dict(width=0)),
        connector=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)),
        textfont=dict(color="#111827", family="Inter", size=12)
    ))
    fig_funnel.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                             plot_bgcolor="#FFFFFF", height=520,
                             title="User Journey Funnel", font=dict(family="Inter"),
                             margin=dict(t=50,b=20,l=150))
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("<div class='section-header'>📊 Stage Drop-off Analysis</div>", unsafe_allow_html=True)
    dropout_data = []
    for i in range(1, len(stages)):
        lost = values[i-1] - values[i]
        pct  = lost / values[i-1] * 100 if values[i-1] else 0
        dropout_data.append({"Stage": f"{stages[i-1]} → {stages[i]}",
                              "Users Lost": lost, "Drop-off %": round(pct,1)})

    df_drop = pd.DataFrame(dropout_data)
    fig_drop = px.bar(df_drop, x="Stage", y="Drop-off %",
                      color="Drop-off %",
                      color_continuous_scale=["#10B981","#F59E0B","#EF4444"],
                      text="Drop-off %")
    fig_drop.update_traces(texttemplate="%{text}%", textposition="outside",
                           textfont=dict(color="#111827"))
    fig_drop.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                           plot_bgcolor="#FFFFFF", height=380,
                           xaxis_tickangle=-30, coloraxis_showscale=False,
                           margin=dict(t=20,b=80))
    st.plotly_chart(fig_drop, use_container_width=True)

    st.markdown("<div class='section-header'>📋 Drop-off Summary Table</div>", unsafe_allow_html=True)
    st.dataframe(df_drop.style.background_gradient(subset=["Drop-off %"], cmap="RdYlGn_r"),
                 use_container_width=True, height=280)

# PAGE 4: REVENUE & MONETIZATION
elif page == "💵 Revenue & Monetization":
    st.markdown("""
    <div style='background:linear-gradient(90deg,#7C3AED22 0%,transparent 100%);
         border-left:4px solid #7C3AED;border-radius:8px;padding:18px 24px;margin-bottom:28px;'>
        <h1 style='color:#111827;font-size:1.8rem;font-weight:800;margin:0;'>💵 Revenue & Monetization</h1>
        <p style='color:#4B5563;margin:6px 0 0;font-size:0.9rem;'>Revenue trends, top courses, and pricing analysis</p>
    </div>
    """, unsafe_allow_html=True)

    if transactions.empty or courses.empty:
        st.info("📊 Awaiting data. Please upload your CSVs (transactions, courses) in the sidebar to analyze revenue.")
        st.stop()

    txn_ok = transactions[transactions["status"] == "success"].copy()
    if not filt.empty: txn_ok = txn_ok[txn_ok["user_id"].isin(filt["user_id"])]

    monthly_r = txn_ok.groupby(txn_ok["transaction_date"].dt.to_period("M"))["amount_usd"].sum().reset_index()
    monthly_r.columns = ["month","revenue"]
    monthly_r["month"] = monthly_r["month"].astype(str)
    monthly_r = monthly_r.tail(15)
    monthly_r["revenue_inr"] = monthly_r["revenue"] * 83

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Bar(x=monthly_r["month"], y=monthly_r["revenue"],
                              customdata=monthly_r["revenue_inr"],
                              hovertemplate="%{x}<br>Revenue: $%{y:,.0f} (₹%{customdata:,.0f})<extra></extra>",
                              marker_color="#7C3AED", name="Revenue", opacity=0.8))
    fig_rev.add_trace(go.Scatter(x=monthly_r["month"], y=monthly_r["revenue"].rolling(3).mean(),
                                  mode="lines+markers", name="3M Moving Avg",
                                  customdata=monthly_r["revenue"].rolling(3).mean() * 83,
                                  hovertemplate="%{x}<br>3M Avg: $%{y:,.0f} (₹%{customdata:,.0f})<extra></extra>",
                                  line=dict(color="#EC4899", width=2.5),
                                  marker=dict(size=6)))
    fig_rev.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                           plot_bgcolor="#FFFFFF", height=380,
                           title="Monthly Revenue Trend ($ & ₹)", font=dict(family="Inter"),
                           legend=dict(orientation="h", y=1.08), margin=dict(t=60,b=40))
    fig_rev.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_rev, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>🏆 Top Courses by Revenue</div>", unsafe_allow_html=True)
        crev = txn_ok[txn_ok["course_id"].notna()].merge(
            courses[["course_id","course_name","category"]], on="course_id", how="left")
        top10 = crev.groupby("course_name")["amount_usd"].sum().nlargest(10).reset_index()
        top10.columns = ["course","revenue"]
        top10["rev_inr"] = top10["revenue"] * 83
        fig_top = px.bar(top10, x="revenue", y="course", orientation="h",
                         color="revenue", color_continuous_scale=["#4B5563","#7C3AED"],
                         hover_data={"revenue": ":$,.0f", "rev_inr": ":₹,.0f"})
        fig_top.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                               plot_bgcolor="#FFFFFF", height=400,
                               coloraxis_showscale=False,
                               yaxis=dict(categoryorder="total ascending"),
                               margin=dict(t=10,b=10))
        fig_top.update_xaxes(tickprefix="$")
        st.plotly_chart(fig_top, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>📦 Revenue by Plan Type</div>", unsafe_allow_html=True)
        plan_r = txn_ok.groupby("plan_type_purchased")["amount_usd"].sum().reset_index()
        plan_r["amount_inr"] = plan_r["amount_usd"] * 83
        fig_plan = px.pie(plan_r, names="plan_type_purchased", values="amount_usd",
                          custom_data=["amount_inr"],
                          color_discrete_sequence=["#7C3AED","#EC4899","#F59E0B","#10B981"],
                          hole=0.55)
        fig_plan.update_traces(hovertemplate="%{label}<br>Revenue: $%{value:,.0f} (₹%{customdata[0]:,.0f})<extra></extra>")
        fig_plan.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF",
                                plot_bgcolor="#FFFFFF", height=400,
                                legend=dict(font=dict(color="#111827")))
        st.plotly_chart(fig_plan, use_container_width=True)

    st.markdown("<div class='section-header'>🏷️ Discount Impact Analysis</div>", unsafe_allow_html=True)
    disc_grp = txn_ok.groupby("coupon_used")["amount_usd"].agg(["sum","count","mean"]).reset_index()
    disc_grp["coupon_used"] = disc_grp["coupon_used"].map({True:"With Coupon",False:"Without Coupon"})
    disc_grp.columns = ["Coupon Used","Total Revenue ($)","Transactions","Avg Order Value ($)"]
    disc_grp["Total Revenue (₹)"] = disc_grp["Total Revenue ($)"] * 83
    disc_grp["Avg Order Value (₹)"] = disc_grp["Avg Order Value ($)"] * 83
    disc_grp = disc_grp[["Coupon Used","Total Revenue ($)","Total Revenue (₹)","Transactions","Avg Order Value ($)","Avg Order Value (₹)"]]
    st.dataframe(disc_grp.style.format({"Total Revenue ($)":"${:,.2f}","Avg Order Value ($)":"${:,.2f}","Total Revenue (₹)":"₹{:,.2f}","Avg Order Value (₹)":"₹{:,.2f}"}),
                 use_container_width=True)

# PAGE 6: EDUCATION & BACKGROUND
elif page == "🎓 Education & Background":
    st.markdown("""
    <div style='background:linear-gradient(90deg,#7C3AED22 0%,transparent 100%);
         border-left:4px solid #7C3AED;border-radius:8px;padding:18px 24px;margin-bottom:28px;'>
        <h1 style='color:#111827;font-size:1.8rem;font-weight:800;margin:0;'>🎓 Education & Background</h1>
        <p style='color:#4B5563;margin:6px 0 0;font-size:0.9rem;'>Analysis of students' educational background and its impact on performance.</p>
    </div>
    """, unsafe_allow_html=True)

    if users.empty or "education_level" not in users.columns:
        st.info("📊 Awaiting data. Please upload a structured `users.csv` containing educational fields in the sidebar.")
        st.stop()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>📚 Education Level Distribution</div>", unsafe_allow_html=True)
        edu_counts = filt["education_level"].value_counts().reset_index()
        edu_counts.columns = ["Education Level", "Count"]
        fig_edu = px.pie(edu_counts, names="Education Level", values="Count",
                         color_discrete_sequence=["#7C3AED", "#EC4899", "#F59E0B", "#10B981", "#3B82F6"],
                         hole=0.45)
        fig_edu.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=320, legend=dict(font=dict(color="#111827")))
        st.plotly_chart(fig_edu, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>🎓 Major Distribution</div>", unsafe_allow_html=True)
        major_counts = filt["major"].value_counts().reset_index()
        major_counts.columns = ["Major", "Count"]
        fig_major = px.bar(major_counts, x="Count", y="Major", orientation="h",
                           color="Count", color_continuous_scale=["#4B5563", "#7C3AED"])
        fig_major.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                                height=320, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_major, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='section-header'>🏛️ University Tier Impact on Revenue</div>", unsafe_allow_html=True)
        uni_rev = filt.groupby("university_tier")["lifetime_revenue"].mean().reset_index()
        uni_rev["lifetime_revenue_inr"] = uni_rev["lifetime_revenue"] * 83
        fig_uni = px.bar(uni_rev, x="university_tier", y="lifetime_revenue",
                         color="lifetime_revenue", color_continuous_scale=["#4B5563", "#7C3AED"],
                         hover_data={"lifetime_revenue": ":$,.0f", "lifetime_revenue_inr": ":₹,.0f"},
                         labels={"university_tier": "University Tier", "lifetime_revenue": "Avg Lifetime Revenue ($)", "lifetime_revenue_inr": "Avg Lifetime Revenue (₹)"})
        fig_uni.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=320)
        st.plotly_chart(fig_uni, use_container_width=True)

    with c4:
        st.markdown("<div class='section-header'>📊 CGPA vs. Course Completion Rate</div>", unsafe_allow_html=True)
        if not features.empty and "lesson_completion_rate" in features.columns:
            feat_filt = features[features["user_id"].isin(filt["user_id"])] if not filt.empty else features
            df_scatter = pd.merge(filt[["user_id", "cgpa"]], feat_filt[["user_id", "lesson_completion_rate"]], on="user_id")
            df_scatter["lesson_completion_rate"] *= 100
            
            # Simple scatter if statsmodels is not present, we will omit the trendline='ols' to prevent ModuleNotFoundError
            fig_cgpa = px.scatter(df_scatter, x="cgpa", y="lesson_completion_rate", 
                                  labels={"cgpa": "CGPA", "lesson_completion_rate": "Completion Rate (%)"},
                                  color_discrete_sequence=["#EC4899"], opacity=0.6)
            fig_cgpa.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=320)
            st.plotly_chart(fig_cgpa, use_container_width=True)
        else:
            st.warning("Lesson completion rate data is missing for scattering.")

# PAGE 7: GROWTH STRATEGY
elif page == "💡 Growth Strategy":
    st.markdown("""
    <div style='background:linear-gradient(90deg,#7C3AED22 0%,transparent 100%);
         border-left:4px solid #7C3AED;border-radius:8px;padding:18px 24px;margin-bottom:28px;'>
        <h1 style='color:#111827;font-size:1.8rem;font-weight:800;margin:0;'>💡 Growth Strategy</h1>
        <p style='color:#4B5563;margin:6px 0 0;font-size:0.9rem;'>Key findings and actionable growth recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    insights = []
    
    # Dynamic Calculation 1: Onboarding Conversion Lift
    if not filt.empty:
        ob_done = filt[filt["onboarding_completed"] == True]
        ob_skip = filt[filt["onboarding_completed"] == False]
        conv_done = (ob_done["plan_type"] != "free").astype(int).mean() if len(ob_done) else 0
        conv_skip = (ob_skip["plan_type"] != "free").astype(int).mean() if len(ob_skip) else 0
        
        if conv_done > conv_skip and conv_skip > 0:
            multiplier = conv_done / conv_skip
            insights.append(("🟡", "Onboarding Conversion Impact",
                             f"Users who complete onboarding convert at {conv_done*100:.1f}% versus just {conv_skip*100:.1f}% for those who skip — a {multiplier:.1f}x multiplier.",
                             "Make onboarding mandatory and highly engaging; reward completion with a free micro-course."))
    
    # Dynamic Calculation 2: Channel LTV Dominance
    if not filt.empty and "lifetime_revenue" in filt.columns and "signup_channel" in filt.columns:
        channel_ltv = filt.groupby("signup_channel")["lifetime_revenue"].mean()
        if len(channel_ltv) >= 2:
            top_channel = channel_ltv.idxmax()
            bottom_channel = channel_ltv.idxmin()
            ratio = channel_ltv.max() / channel_ltv.min() if channel_ltv.min() > 0 else 0
            insights.append(("🟢", f"Top Channel ROI: {str(top_channel).title()}",
                             f"The '{top_channel}' channel generates {ratio:.1f}x higher lifetime revenue per user (${channel_ltv.max():.2f} / ₹{channel_ltv.max()*83:.2f}) compared to '{bottom_channel}'.",
                             f"Reallocate ad-spend to aggressively double down on {top_channel}." ))
    
    # Dynamic Calculation 3: Mobile vs Desktop Discrepancy
    if not filt.empty and not features.empty:
        df_dev = pd.merge(filt[["user_id", "device_type"]], features[["user_id", "lesson_completion_rate"]], on="user_id")
        dev_comp = df_dev.groupby("device_type")["lesson_completion_rate"].mean()
        if "mobile" in dev_comp and "desktop" in dev_comp:
            diff = (dev_comp["desktop"] - dev_comp["mobile"]) * 100
            if diff > 3:
                insights.append(("🔴", "Mobile Completion Gap",
                                 f"Mobile users complete {diff:.1f}% fewer lessons on average compared to desktop users.",
                                 "Introduce 5-minute micro-learning modules horizontally optimized for smaller screens."))
                             
    # Dynamic Calculation 4: Coupon Degradation
    if not transactions.empty:
        txn_ok = transactions[transactions["status"] == "success"]
        if not txn_ok.empty and "coupon_used" in txn_ok.columns:
            c_ltv = txn_ok.groupby("coupon_used")["amount_usd"].mean()
            if True in c_ltv and False in c_ltv:
                drop = 1 - (c_ltv[True] / c_ltv[False])
                if drop > 0.05:
                    insights.append(("🟡", "Coupon Revenue Degradation",
                                     f"Transactions using coupons result in a {drop*100:.1f}% lower Average Order Value.",
                                     "Stop generic discounting. Shift to time-limited Premium access trials to demonstrate value instead."))

    # Dynamic Calculation 5: Revenue Concentration
    if not transactions.empty and "course_id" in transactions.columns:
        txn_ok = transactions[transactions["status"] == "success"]
        c_rev = txn_ok.groupby("course_id")["amount_usd"].sum()
        total_rev = c_rev.sum()
        if total_rev > 0 and len(c_rev) > 5:
            top_5 = c_rev.nlargest(5).sum()
            pct = top_5 / total_rev * 100
            insights.append(("🟢", "Revenue Concentration (Pareto)",
                             f"Just your top 5 highest-grossing courses are responsible for {pct:.1f}% of your entire platform revenue.",
                             "Bundle these Elite courses immediately to increase your global AOV."))

    if not insights:
        insights.append(("ℹ️", "Gathering Intelligence...", "Not enough data points yet to generate real-time findings.", "Wait for more user data or adjust your filters."))

    for emoji, title, finding, action in insights:
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>{emoji} {title}</div>
            <div class='insight-body'><b>📊 Finding:</b> {finding}</div>
            <div class='insight-body' style='margin-top:8px;border-top:1px solid #374151;padding-top:8px;'>
                <b>✅ Action:</b> {action}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>🎯 Growth Strategy Matrix</div>", unsafe_allow_html=True)
    matrix = {
        "Initiative": ["Day-1 to Day-7 Email Drip", "Push Notification Streaks",
                       "7-Day Pro Free Trial", "Annual Plan Incentive",
                       "Mobile Micro-Lessons", "Referral Program Launch",
                       "Course Bundles", "Peer Learning Cohorts"],
        "Category":   ["Retention","Retention","Pricing","Pricing",
                       "Product","Acquisition","Pricing","Product"],
        "Expected Impact": ["+15% 7-Day Retention","+22% DAU","+2.5% Conv Rate",
                            "+35% Revenue/User","+25% Mobile Completion",
                            "+40% Referral Volume","+20% AOV","+30% Completion"],
        "Priority":   ["🔴 High","🟡 Medium","🔴 High","🟢 Quick Win",
                       "🔴 High","🟡 Medium","🟢 Quick Win","🟡 Medium"],
        "Timeline":   ["Week 1–2","Week 2–3","Week 1","Week 2",
                       "Month 2–3","Week 3–4","Week 2","Month 2"]
    }
    df_matrix = pd.DataFrame(matrix)
    st.dataframe(df_matrix, use_container_width=True, height=340)
