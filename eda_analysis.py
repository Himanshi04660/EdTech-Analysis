"""
EdTech Growth Analytics — EDA & Funnel Analysis
================================================
Generates all exploratory analysis charts and funnel metrics.
Run AFTER generate_dataset.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

OUTPUT_DIR = "data"
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

plt.style.use("dark_background")
PALETTE = ["#7C3AED", "#EC4899", "#F59E0B", "#10B981", "#3B82F6", "#EF4444"]
sns.set_palette(PALETTE)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
print("Loading data...")
users = pd.read_csv(f"{OUTPUT_DIR}/users.csv", parse_dates=["signup_date"])
courses = pd.read_csv(f"{OUTPUT_DIR}/courses.csv")
activity = pd.read_csv(f"{OUTPUT_DIR}/activity_log.csv", parse_dates=["event_timestamp"])
transactions = pd.read_csv(f"{OUTPUT_DIR}/transactions.csv", parse_dates=["transaction_date"])
features = pd.read_csv(f"{OUTPUT_DIR}/user_features.csv")
print("  ✓ All datasets loaded")

# ─────────────────────────────────────────────
# CHART 1: FUNNEL ANALYSIS
# ─────────────────────────────────────────────
print("Generating funnel chart...")
total_users = len(users)
email_verified = users["email_verified"].sum()
profile_completed = users["profile_completed"].sum()
onboarding_done = users["onboarding_completed"].sum()
ever_enrolled = users["first_course_enrolled_date"].notna().sum()
lesson_completers = features[features["total_lessons_completed"] >= 1].shape[0]
course_completers = features[features["courses_enrolled"] >= 1].shape[0]  # proxy
paid_users = (users["plan_type"] != "free").sum()

funnel_stages = [
    "Signup", "Email Verified", "Profile Complete",
    "Onboarding Done", "Course Enrolled", "Lesson Completed",
    "Any Course Progress", "Paid Conversion"
]
funnel_values = [
    total_users, email_verified, profile_completed, onboarding_done,
    ever_enrolled, lesson_completers, course_completers, paid_users
]

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

colors_funnel = ["#7C3AED", "#6D28D9", "#5B21B6", "#EC4899", "#DB2777", "#F59E0B", "#D97706", "#10B981"]
bar_width = 0.6
bars = ax.barh(funnel_stages[::-1], funnel_values[::-1], color=colors_funnel[::-1],
               height=bar_width, edgecolor="none")

for i, (bar, val) in enumerate(zip(bars, funnel_values[::-1])):
    pct = val / total_users * 100
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
            f"{val:,}  ({pct:.1f}%)", va="center", ha="left",
            color="white", fontsize=10, fontweight="bold")

ax.set_xlabel("Number of Users", color="#9CA3AF", fontsize=11)
ax.set_title("User Journey Funnel — Signup to Paid Conversion",
             color="white", fontsize=14, fontweight="bold", pad=20)
ax.tick_params(colors="white", labelsize=10)
ax.spines[:].set_visible(False)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/01_funnel.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Funnel chart saved")

# ─────────────────────────────────────────────
# CHART 2: MONTHLY REVENUE TREND
# ─────────────────────────────────────────────
print("Generating revenue trend chart...")
txn_success = transactions[transactions["status"] == "success"].copy()
txn_success["month"] = txn_success["transaction_date"].dt.to_period("M")
monthly_rev = txn_success.groupby("month")["amount_usd"].sum().reset_index()
monthly_rev["month_str"] = monthly_rev["month"].astype(str)
monthly_rev = monthly_rev.tail(12)

fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

ax.fill_between(range(len(monthly_rev)), monthly_rev["amount_usd"],
                alpha=0.25, color="#7C3AED")
ax.plot(range(len(monthly_rev)), monthly_rev["amount_usd"],
        color="#7C3AED", linewidth=2.5, marker="o", markersize=7,
        markerfacecolor="#EC4899", markeredgewidth=0)

for i, row in monthly_rev.iterrows():
    idx = list(monthly_rev.index).index(i)
    ax.annotate(f"${row['amount_usd']:,.0f}",
                xy=(idx, row["amount_usd"]),
                xytext=(0, 12), textcoords="offset points",
                ha="center", color="#F9FAFB", fontsize=8)

ax.set_xticks(range(len(monthly_rev)))
ax.set_xticklabels(monthly_rev["month_str"], rotation=45, ha="right", color="#9CA3AF", fontsize=9)
ax.set_ylabel("Revenue (USD)", color="#9CA3AF", fontsize=11)
ax.set_title("Monthly Revenue Trend (Last 12 Months)", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.tick_params(colors="white")
ax.spines[:].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.grid(axis="y", color="#1F2937", linewidth=0.8)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/02_revenue_trend.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Revenue trend chart saved")

# ─────────────────────────────────────────────
# CHART 3: COHORT RETENTION HEATMAP
# ─────────────────────────────────────────────
print("Generating cohort retention heatmap...")
users["cohort_month"] = users["signup_date"].dt.to_period("M")
activity_u = activity.merge(users[["user_id", "signup_date", "cohort_month"]], on="user_id", how="left")
activity_u["activity_month"] = activity_u["event_timestamp"].dt.to_period("M")
activity_u["cohort_month"] = pd.PeriodIndex(activity_u["cohort_month"])
activity_u["period_number"] = (activity_u["activity_month"] - activity_u["cohort_month"]).apply(lambda x: x.n if hasattr(x, 'n') else 0)

cohort_data = activity_u[activity_u["period_number"] >= 0].groupby(
    ["cohort_month", "period_number"])["user_id"].nunique().reset_index()

cohort_pivot = cohort_data.pivot_table(index="cohort_month", columns="period_number",
                                        values="user_id", aggfunc="sum")
cohort_sizes = users.groupby("cohort_month")["user_id"].count()
cohort_pivot = cohort_pivot.divide(cohort_sizes, axis=0) * 100
cohort_pivot = cohort_pivot.iloc[-10:, :8]

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

cmap = sns.color_palette("rocket", as_cmap=True)
sns.heatmap(cohort_pivot.round(1), annot=True, fmt=".1f", cmap=cmap,
            linewidths=0.5, linecolor="#1F2937", ax=ax,
            cbar_kws={"label": "Retention %"},
            annot_kws={"size": 9, "color": "white"})

ax.set_title("Cohort Retention Heatmap (by Month)", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.set_xlabel("Month After Signup", color="#9CA3AF", fontsize=11)
ax.set_ylabel("Signup Cohort", color="#9CA3AF", fontsize=11)
ax.tick_params(colors="white", labelsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/03_cohort_retention.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Cohort retention heatmap saved")

# ─────────────────────────────────────────────
# CHART 4: TOP 10 COURSES BY REVENUE
# ─────────────────────────────────────────────
print("Generating top courses chart...")
course_rev = txn_success[txn_success["course_id"].notna()].merge(
    courses[["course_id", "course_name", "category"]], on="course_id", how="left")
top_courses = course_rev.groupby("course_name")["amount_usd"].sum().nlargest(10).reset_index()

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

colors_c = plt.cm.plasma(np.linspace(0.3, 0.9, len(top_courses)))
bars = ax.barh(top_courses["course_name"][::-1], top_courses["amount_usd"][::-1],
               color=colors_c, edgecolor="none", height=0.65)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 50, bar.get_y() + bar.get_height() / 2,
            f"${w:,.0f}", va="center", ha="left", color="white", fontsize=9, fontweight="bold")

ax.set_title("Top 10 Courses by Revenue", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.set_xlabel("Total Revenue (USD)", color="#9CA3AF", fontsize=11)
ax.tick_params(colors="white", labelsize=9)
ax.spines[:].set_visible(False)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/04_top_courses.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Top courses chart saved")

# ─────────────────────────────────────────────
# CHART 5: CHURN BY CHANNEL
# ─────────────────────────────────────────────
print("Generating churn by channel chart...")
churn_channel = users.groupby("signup_channel")["is_churned"].agg(["sum", "count"]).reset_index()
churn_channel["churn_rate"] = churn_channel["sum"] / churn_channel["count"] * 100
churn_channel = churn_channel.sort_values("churn_rate", ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

bar_colors = ["#10B981" if r < 55 else "#F59E0B" if r < 65 else "#EF4444"
              for r in churn_channel["churn_rate"]]
bars = ax.barh(churn_channel["signup_channel"], churn_channel["churn_rate"],
               color=bar_colors, edgecolor="none", height=0.55)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{w:.1f}%", va="center", ha="left", color="white", fontsize=10, fontweight="bold")

ax.axvline(x=churn_channel["churn_rate"].mean(), color="#6B7280",
           linestyle="--", linewidth=1.5, label=f"Avg: {churn_channel['churn_rate'].mean():.1f}%")
ax.set_title("Churn Rate by Acquisition Channel", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.set_xlabel("Churn Rate (%)", color="#9CA3AF", fontsize=11)
ax.tick_params(colors="white", labelsize=10)
ax.spines[:].set_visible(False)
ax.legend(facecolor="#1F2937", labelcolor="white", fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/05_churn_by_channel.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Churn by channel chart saved")

# ─────────────────────────────────────────────
# CHART 6: CONVERSION RATE BREAKDOWN
# ─────────────────────────────────────────────
print("Generating conversion breakdown chart...")
conv_channel = users.groupby("signup_channel").agg(
    total=("user_id", "count"),
    paid=("plan_type", lambda x: (x != "free").sum())
).reset_index()
conv_channel["conv_rate"] = conv_channel["paid"] / conv_channel["total"] * 100
conv_channel = conv_channel.sort_values("conv_rate", ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

bar_colors2 = ["#7C3AED" if r > conv_channel["conv_rate"].mean() else "#4B5563"
               for r in conv_channel["conv_rate"]]
bars2 = ax.barh(conv_channel["signup_channel"], conv_channel["conv_rate"],
                color=bar_colors2, edgecolor="none", height=0.55)

for bar in bars2:
    w = bar.get_width()
    ax.text(w + 0.2, bar.get_y() + bar.get_height() / 2,
            f"{w:.1f}%", va="center", ha="left", color="white", fontsize=10, fontweight="bold")

ax.axvline(x=conv_channel["conv_rate"].mean(), color="#F59E0B",
           linestyle="--", linewidth=1.5, label=f"Avg: {conv_channel['conv_rate'].mean():.1f}%")
ax.set_title("Free to Paid Conversion Rate by Channel", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.set_xlabel("Conversion Rate (%)", color="#9CA3AF", fontsize=11)
ax.tick_params(colors="white", labelsize=10)
ax.spines[:].set_visible(False)
ax.legend(facecolor="#1F2937", labelcolor="white", fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/06_conversion_by_channel.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Conversion by channel chart saved")

# ─────────────────────────────────────────────
# CHART 7: DEVICE TYPE COMPLETION RATE
# ─────────────────────────────────────────────
print("Generating device completion chart...")
# features already contains device_type — no merge needed
if "device_type" in features.columns:
    device_src = features.copy()
else:
    device_src = features.merge(users[["user_id", "device_type"]], on="user_id", how="left")

device_comp = device_src.groupby("device_type")["lesson_completion_rate"].mean().reset_index()
device_comp["lesson_completion_rate"] *= 100

fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("#0F0F23")
ax.set_facecolor("#0F0F23")

device_colors = ["#7C3AED", "#EC4899", "#F59E0B"]
bars3 = ax.bar(device_comp["device_type"], device_comp["lesson_completion_rate"],
               color=device_colors[:len(device_comp)], edgecolor="none", width=0.5)

for bar in bars3:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
            f"{h:.1f}%", ha="center", va="bottom", color="white", fontsize=12, fontweight="bold")

ax.set_title("Lesson Completion Rate by Device Type", color="white",
             fontsize=14, fontweight="bold", pad=20)
ax.set_ylabel("Avg Completion Rate (%)", color="#9CA3AF", fontsize=11)
ax.tick_params(colors="white", labelsize=11)
ax.spines[:].set_visible(False)
max_val = device_comp["lesson_completion_rate"].max()
ax.set_ylim(0, max_val * 1.25 if max_val > 0 else 10)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/07_device_completion.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  ✓ Device completion chart saved")

print("\n" + "="*50)
print("  EDA COMPLETE — 7 charts saved to ./charts/")
print("="*50)
