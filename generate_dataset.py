"""
EdTech Growth Analytics — Synthetic Dataset Generator
======================================================
Generates realistic dummy data for 3,500 users with:
- users table
- courses table
- activity_log table
- transactions table
- user_features (engineered) table
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
NUM_USERS = 3500
NUM_COURSES = 75
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REF_DATE = datetime(2026, 3, 20)
START_DATE = REF_DATE - timedelta(days=540)  # 18 months back

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

# ─────────────────────────────────────────────
# 1. GENERATE COURSES TABLE
# ─────────────────────────────────────────────
print("Generating courses...")

categories = ["tech", "business", "design", "marketing", "personal_dev", "finance"]
difficulties = ["beginner", "intermediate", "advanced"]
languages = ["english", "hindi", "spanish", "french"]

course_names_pool = [
    "Python for Beginners", "Data Science Bootcamp", "Machine Learning A-Z",
    "Web Development Masterclass", "React JS Complete Guide", "Excel for Data Analysis",
    "Digital Marketing Fundamentals", "SQL for Analytics", "Tableau Dashboard Design",
    "Power BI for Business", "JavaScript Essentials", "Deep Learning with TensorFlow",
    "Product Management 101", "UX/UI Design Principles", "Financial Modeling",
    "Business Communication", "Presentation Skills", "Content Marketing Strategy",
    "AWS Cloud Practitioner", "Docker & Kubernetes", "Git & GitHub Essentials",
    "Statistics for Data Science", "Natural Language Processing", "Computer Vision",
    "Blockchain Fundamentals", "Cybersecurity Basics", "Agile & Scrum",
    "Leadership Development", "Growth Hacking", "SEO Masterclass",
    "Social Media Marketing", "Email Marketing Automation", "Canva Design Basics",
    "Photography for Beginners", "Video Editing with DaVinci Resolve",
    "Personal Finance & Investing", "Stock Market Trading", "Crypto Investing 101",
    "Accounting Fundamentals", "Tax Planning Basics", "Brand Building",
    "Entrepreneurship Essentials", "Startup Pitching", "Venture Capital 101",
    "Negotiation Skills", "Time Management Mastery", "Mental Health at Work",
    "Yoga & Mindfulness", "Public Speaking", "Speed Reading",
    "Node.js Backend Development", "Flutter App Development", "iOS Development with Swift",
    "Android Development", "Vue.js Fundamentals", "Angular Complete Guide",
    "C++ Programming", "Java for Beginners", "Data Structures & Algorithms",
    "System Design Interview Prep", "Rust Programming", "Go Programming",
    "Apache Spark", "Hadoop Ecosystem", "Data Warehousing with Snowflake",
    "dbt for Analytics Engineers", "Looker Studio Dashboards", "Google Analytics 4",
    "A/B Testing & Experimentation", "Product Analytics with Mixpanel",
    "Customer Success Fundamentals", "HR Analytics", "Supply Chain Analytics",
    "Operations Management", "Project Management Professional (PMP)",
]

courses = []
for i in range(NUM_COURSES):
    price_options = [0, 9.99, 19.99, 29.99, 49.99, 99.99, 199.99]
    price_weights = [15, 10, 20, 15, 25, 10, 5]

    courses.append({
        "course_id": f"CRS-{str(i+1).zfill(3)}",
        "course_name": course_names_pool[i % len(course_names_pool)],
        "category": weighted_choice(categories, [30, 20, 15, 15, 10, 10]),
        "difficulty_level": weighted_choice(difficulties, [40, 40, 20]),
        "duration_hours": round(random.uniform(2.0, 45.0), 1),
        "num_lessons": random.randint(5, 120),
        "instructor_name": fake.name(),
        "price_usd": weighted_choice(price_options, price_weights),
        "avg_rating": round(random.uniform(3.2, 5.0), 1),
        "completion_rate_pct": round(random.uniform(5.0, 85.0), 1),
        "is_featured": random.random() < 0.15,
        "launch_date": random_date(START_DATE, REF_DATE - timedelta(days=30)).strftime("%Y-%m-%d"),
        "has_certificate": random.random() < 0.60,
        "language": weighted_choice(languages, [55, 25, 12, 8]),
    })

df_courses = pd.DataFrame(courses)
df_courses.to_csv(f"{OUTPUT_DIR}/courses.csv", index=False)
print(f"  ✓ {len(df_courses)} courses created")

# ─────────────────────────────────────────────
# 2. GENERATE USERS TABLE
# ─────────────────────────────────────────────
print("Generating users...")

channels = ["organic", "google_ads", "instagram", "referral", "email_campaign", "youtube", "linkedin", "whatsapp"]
channel_weights = [20, 15, 15, 15, 10, 5, 12, 8]
countries = ["India", "USA", "UK", "Nigeria", "Brazil", "Canada", "Germany", "Philippines"]
country_weights = [35, 20, 10, 10, 8, 5, 5, 7]
age_groups = ["18-24", "25-34", "35-44", "45+"]
age_weights = [30, 40, 20, 10]
genders = ["male", "female", "non-binary", "prefer_not_to_say"]
gender_weights = [48, 46, 3, 3]
devices = ["mobile", "desktop", "tablet"]
device_weights = [60, 30, 10]
plans = ["free", "basic", "pro", "enterprise"]
plan_weights = [70, 15, 12, 3]
education_levels = ["High School", "Bachelor's", "Master's", "PhD", "Bootcamp/Other"]
education_weights = [15, 50, 25, 5, 5]
majors = ["Computer Science", "Business Admin", "Engineering", "Arts & Humanities", "Sciences", "Other"]
major_weights = [35, 25, 15, 10, 10, 5]
universities = ["Tier 1 University", "Tier 2 University", "Tier 3 University", "Community College", "Online/Self-Taught"]
university_weights = [15, 30, 35, 10, 10]

users = []
for i in range(NUM_USERS):
    signup_date = random_date(START_DATE, REF_DATE - timedelta(days=1))
    channel = weighted_choice(channels, channel_weights)
    plan = weighted_choice(plans, plan_weights)
    is_paid = plan != "free"

    # Churn modelling: 47% churn in first 3 days, cascading after
    days_since_signup = (REF_DATE - signup_date).days
    churn_roll = random.random()
    if churn_roll < 0.47 and days_since_signup >= 3:
        is_churned = True
        churn_offset = random.randint(0, min(3, days_since_signup))
        churn_date = (signup_date + timedelta(days=churn_offset)).strftime("%Y-%m-%d")
    elif churn_roll < 0.62 and days_since_signup >= 7:
        is_churned = True
        churn_offset = random.randint(4, min(7, days_since_signup))
        churn_date = (signup_date + timedelta(days=churn_offset)).strftime("%Y-%m-%d")
    elif churn_roll < 0.72 and days_since_signup >= 30:
        is_churned = True
        churn_offset = random.randint(8, min(30, days_since_signup))
        churn_date = (signup_date + timedelta(days=churn_offset)).strftime("%Y-%m-%d")
    else:
        is_churned = False
        churn_date = None

    profile_complete = random.random() < 0.60
    email_verified = random.random() < 0.85
    onboarding = random.random() < 0.40

    # First enrollment date
    if random.random() < 0.72 and days_since_signup >= 1:
        enroll_offset = random.randint(0, min(days_since_signup, 365))
        first_enroll_date = (signup_date + timedelta(days=enroll_offset)).strftime("%Y-%m-%d")
    else:
        first_enroll_date = None

    revenue = 0.0
    if is_paid:
        revenue = round(random.uniform(9.99, 499.99), 2)

    users.append({
        "user_id": str(uuid.uuid4()),
        "signup_date": signup_date.strftime("%Y-%m-%d"),
        "signup_channel": channel,
        "country": weighted_choice(countries, country_weights),
        "age_group": weighted_choice(age_groups, age_weights),
        "gender": weighted_choice(genders, gender_weights),
        "device_type": weighted_choice(devices, device_weights),
        "plan_type": plan,
        "education_level": weighted_choice(education_levels, education_weights),
        "major": weighted_choice(majors, major_weights),
        "university_tier": weighted_choice(universities, university_weights),
        "cgpa": round(random.uniform(2.5, 4.0), 2),
        "profile_completed": profile_complete,
        "email_verified": email_verified,
        "onboarding_completed": onboarding,
        "first_course_enrolled_date": first_enroll_date,
        "lifetime_revenue": revenue,
        "is_churned": is_churned,
        "churn_date": churn_date,
        "referral_count": max(0, int(np.random.exponential(0.4))),
        "support_tickets_raised": max(0, int(np.random.exponential(0.5))),
        "utm_source": weighted_choice(["google", "facebook", "twitter", "direct", "linkedin"],
                                       [30, 25, 10, 20, 15]),
    })

df_users = pd.DataFrame(users)
df_users.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
print(f"  ✓ {len(df_users)} users created")

# ─────────────────────────────────────────────
# 3. GENERATE ACTIVITY LOG
# ─────────────────────────────────────────────
print("Generating activity log (this may take a moment)...")

event_types_base = [
    "app_open", "search", "course_browse", "course_detail_view",
    "course_enroll", "lesson_start", "lesson_complete", "lesson_pause",
    "lesson_resume", "quiz_attempt", "quiz_pass", "course_complete",
    "certificate_download", "payment_initiate", "support_ticket"
]

activity_log = []
user_last_login = {}

for _, user in df_users.iterrows():
    uid = user["user_id"]
    signup_dt = datetime.strptime(user["signup_date"], "%Y-%m-%d")
    is_churned = user["is_churned"]
    churn_dt = datetime.strptime(user["churn_date"], "%Y-%m-%d") if user["churn_date"] else REF_DATE

    # Number of sessions: churned users have fewer
    if is_churned:
        n_sessions = max(1, int(np.random.exponential(2.5)))
    else:
        n_sessions = max(1, int(np.random.exponential(12)))

    n_sessions = min(n_sessions, 80)

    enrolled_courses = random.sample(df_courses["course_id"].tolist(),
                                      min(random.randint(0, 5), len(df_courses)))

    session_date = signup_dt
    last_event_dt = signup_dt

    for s in range(n_sessions):
        session_id = str(uuid.uuid4())[:8]
        max_days = (churn_dt - signup_dt).days
        if max_days <= 0:
            break
        session_offset = int(np.random.exponential(max_days / max(n_sessions * 0.5, 1)))
        session_date = signup_dt + timedelta(days=min(session_offset + s, max_days))
        if session_date > churn_dt or session_date > REF_DATE:
            break

        session_duration = round(max(1.0, np.random.exponential(25.0)), 1)
        device = user["device_type"]

        # Base events in this session
        events_in_session = ["app_open", "course_browse"]

        # Possibly enroll or engage with a course
        if enrolled_courses and random.random() < 0.7:
            crs = random.choice(enrolled_courses)
            course_row = df_courses[df_courses["course_id"] == crs].iloc[0]
            n_lessons = course_row["num_lessons"]

            lesson_reached = int(clamp(
                n_lessons * abs(np.random.normal(0.25, 0.20)),
                1, n_lessons
            ))
            # Lesson 3 wall: extra drop here
            if lesson_reached >= 3 and random.random() < 0.38:
                lesson_reached = random.randint(1, 3)

            progress_pct = round((lesson_reached / n_lessons) * 100, 1)

            for ln in range(1, lesson_reached + 1):
                vid_watch = round(random.uniform(30, 100), 1) if ln < lesson_reached else round(random.uniform(10, 100), 1)
                quiz_att = random.random() < 0.4
                quiz_score = round(random.uniform(40, 100), 1) if quiz_att else None

                activity_log.append({
                    "event_id": str(uuid.uuid4()),
                    "user_id": uid,
                    "course_id": crs,
                    "event_type": "lesson_start",
                    "event_timestamp": (session_date + timedelta(minutes=ln * 8)).strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": session_id,
                    "session_duration_minutes": session_duration,
                    "lesson_number": ln,
                    "progress_pct": progress_pct,
                    "device_type": device,
                    "platform": weighted_choice(["ios", "android", "windows", "macos", "web"],
                                                 [25, 30, 20, 10, 15]),
                    "video_watch_pct": vid_watch,
                    "quiz_attempted": quiz_att,
                    "quiz_score": quiz_score,
                })

                if vid_watch >= 80 and random.random() < 0.75:
                    activity_log.append({
                        "event_id": str(uuid.uuid4()),
                        "user_id": uid,
                        "course_id": crs,
                        "event_type": "lesson_complete",
                        "event_timestamp": (session_date + timedelta(minutes=ln * 8 + 5)).strftime("%Y-%m-%d %H:%M:%S"),
                        "session_id": session_id,
                        "session_duration_minutes": session_duration,
                        "lesson_number": ln,
                        "progress_pct": progress_pct,
                        "device_type": device,
                        "platform": weighted_choice(["ios", "android", "windows", "macos", "web"],
                                                     [25, 30, 20, 10, 15]),
                        "video_watch_pct": vid_watch,
                        "quiz_attempted": quiz_att,
                        "quiz_score": quiz_score,
                    })
        else:
            # Just browsing event
            activity_log.append({
                "event_id": str(uuid.uuid4()),
                "user_id": uid,
                "course_id": None,
                "event_type": "course_browse",
                "event_timestamp": session_date.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "session_duration_minutes": session_duration,
                "lesson_number": None,
                "progress_pct": None,
                "device_type": device,
                "platform": weighted_choice(["ios", "android", "windows", "macos", "web"],
                                             [25, 30, 20, 10, 15]),
                "video_watch_pct": None,
                "quiz_attempted": False,
                "quiz_score": None,
            })

        last_event_dt = session_date

    user_last_login[uid] = last_event_dt

df_activity = pd.DataFrame(activity_log)
df_activity.to_csv(f"{OUTPUT_DIR}/activity_log.csv", index=False)
print(f"  ✓ {len(df_activity)} activity events created")

# ─────────────────────────────────────────────
# 4. GENERATE TRANSACTIONS TABLE
# ─────────────────────────────────────────────
print("Generating transactions...")

paid_users = df_users[df_users["plan_type"] != "free"]
transactions = []
payment_methods = ["credit_card", "upi", "paypal", "netbanking"]
payment_weights = [40, 30, 20, 10]
plan_prices = {"basic": (9.99, 19.99), "pro": (49.99, 99.99), "enterprise": (199.99, 499.99)}

for _, user in paid_users.iterrows():
    uid = user["user_id"]
    signup_dt = datetime.strptime(user["signup_date"], "%Y-%m-%d")
    plan = user["plan_type"]
    n_txns = random.randint(1, 6)
    price_range = plan_prices.get(plan, (9.99, 49.99))

    for t in range(n_txns):
        days_to_pay = int(np.random.choice(
            [random.randint(0, 7), random.randint(8, 30), random.randint(31, 90), random.randint(91, 365)],
            p=[0.20, 0.40, 0.30, 0.10]
        ))
        txn_date = signup_dt + timedelta(days=days_to_pay)
        if txn_date > REF_DATE:
            txn_date = REF_DATE - timedelta(days=random.randint(1, 30))

        coupon_used = random.random() < 0.30
        discount_pct = weighted_choice([0, 10, 20, 30, 50], [40, 20, 20, 15, 5]) if coupon_used else 0
        base_amount = round(random.uniform(*price_range), 2)
        final_amount = round(base_amount * (1 - discount_pct / 100), 2)

        crs_id = random.choice(df_courses["course_id"].tolist()) if random.random() < 0.5 else None
        txn_type = weighted_choice(
            ["one_time_purchase", "subscription_monthly", "subscription_annual"],
            [40, 40, 20]
        )

        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "user_id": uid,
            "course_id": crs_id,
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "transaction_type": txn_type,
            "amount_usd": final_amount,
            "payment_method": weighted_choice(payment_methods, payment_weights),
            "coupon_used": coupon_used,
            "discount_pct": discount_pct,
            "currency": weighted_choice(["USD", "INR", "GBP", "EUR"], [50, 30, 10, 10]),
            "status": weighted_choice(["success", "failed", "refunded"], [88, 8, 4]),
            "plan_type_purchased": plan,
            "is_first_purchase": (t == 0),
            "days_since_signup": days_to_pay,
        })

df_transactions = pd.DataFrame(transactions)
df_transactions.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)
print(f"  ✓ {len(df_transactions)} transactions created")

# ─────────────────────────────────────────────
# 5. GENERATE USER FEATURES (ENGINEERED)
# ─────────────────────────────────────────────
print("Engineering user features...")

# Aggregate activity
activity_agg = df_activity.groupby("user_id").agg(
    total_sessions=("session_id", "nunique"),
    avg_session_duration=("session_duration_minutes", "mean"),
    total_lessons_started=("event_type", lambda x: (x == "lesson_start").sum()),
    total_lessons_completed=("event_type", lambda x: (x == "lesson_complete").sum()),
    courses_enrolled=("course_id", "nunique"),
    last_activity_date=("event_timestamp", "max"),
).reset_index()

activity_agg["lesson_completion_rate"] = (
    activity_agg["total_lessons_completed"] / activity_agg["total_lessons_started"].replace(0, np.nan)
).fillna(0).round(3)

# Early engagement: sessions in first 7 days
df_activity["event_timestamp"] = pd.to_datetime(df_activity["event_timestamp"])
early_events = df_activity.copy()
user_signup_map = df_users.set_index("user_id")["signup_date"].to_dict()
early_events["signup_date"] = pd.to_datetime(early_events["user_id"].map(user_signup_map))
early_events["days_since_signup"] = (early_events["event_timestamp"] - early_events["signup_date"]).dt.days
first_7d = early_events[early_events["days_since_signup"] <= 7].groupby("user_id")["session_id"].nunique().reset_index()
first_7d.columns = ["user_id", "first_7d_sessions"]

# Transaction agg
txn_agg = df_transactions[df_transactions["status"] == "success"].groupby("user_id").agg(
    total_revenue=("amount_usd", "sum"),
    num_transactions=("transaction_id", "count"),
    avg_discount_pct=("discount_pct", "mean"),
).reset_index()

# Merge all
features = df_users[[
    "user_id", "signup_date", "signup_channel", "country", "age_group",
    "gender", "device_type", "plan_type", "education_level", "major",
    "university_tier", "cgpa", "profile_completed",
    "email_verified", "onboarding_completed", "first_course_enrolled_date",
    "lifetime_revenue", "is_churned", "referral_count", "support_tickets_raised"
]].copy()

features = features.merge(activity_agg, on="user_id", how="left")
features = features.merge(first_7d, on="user_id", how="left")
features = features.merge(txn_agg, on="user_id", how="left")

features["signup_date"] = pd.to_datetime(features["signup_date"])
features["last_activity_date"] = pd.to_datetime(features["last_activity_date"])
features["days_since_signup"] = (REF_DATE - features["signup_date"]).dt.days
features["days_since_last_login"] = (REF_DATE - features["last_activity_date"]).dt.days

features["days_to_first_enroll"] = (
    pd.to_datetime(features["first_course_enrolled_date"]) - features["signup_date"]
).dt.days

# Fill NAs
fill_zeros = [
    "total_sessions", "avg_session_duration", "total_lessons_started",
    "total_lessons_completed", "lesson_completion_rate", "courses_enrolled",
    "first_7d_sessions", "total_revenue", "num_transactions", "avg_discount_pct"
]
features[fill_zeros] = features[fill_zeros].fillna(0)
features["days_since_last_login"] = features["days_since_last_login"].fillna(features["days_since_signup"])

# Onboarding steps proxy
features["onboarding_score"] = (
    features["email_verified"].astype(int) +
    features["profile_completed"].astype(int) +
    features["onboarding_completed"].astype(int)
)

features["has_paid"] = (features["plan_type"] != "free").astype(int)
features["discount_sensitivity"] = (features["avg_discount_pct"] > 0).astype(int)

features.to_csv(f"{OUTPUT_DIR}/user_features.csv", index=False)
print(f"  ✓ User features engineered for {len(features)} users")

# ─────────────────────────────────────────────
# 6. SUMMARY STATS
# ─────────────────────────────────────────────
print("\n" + "="*55)
print("  DATASET GENERATION COMPLETE")
print("="*55)
print(f"  Users:          {len(df_users):,}")
print(f"  Courses:        {len(df_courses):,}")
print(f"  Activity Events:{len(df_activity):,}")
print(f"  Transactions:   {len(df_transactions):,}")
print(f"  Churned Users:  {df_users['is_churned'].sum():,} ({df_users['is_churned'].mean()*100:.1f}%)")
print(f"  Paid Users:     {(df_users['plan_type'] != 'free').sum():,} ({(df_users['plan_type'] != 'free').mean()*100:.1f}%)")
print(f"  Total Revenue:  ${df_transactions[df_transactions['status']=='success']['amount_usd'].sum():,.2f}")
print("="*55)
print("  Output files saved to ./data/")
print("  - users.csv")
print("  - courses.csv")
print("  - activity_log.csv")
print("  - transactions.csv")
print("  - user_features.csv")
print("="*55)
