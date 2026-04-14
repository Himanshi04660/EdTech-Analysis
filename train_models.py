"""
EdTech Growth Analytics — ML Models
Trains: Churn (XGBoost), Conversion (LightGBM), Recommender (SVD)
"""
import pandas as pd
import numpy as np
import os, joblib, warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report, average_precision_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = "data"
MODEL_DIR  = "models"
CHARTS_DIR = "charts"
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

print("Loading data...")
features = pd.read_csv(f"{OUTPUT_DIR}/user_features.csv")
activity = pd.read_csv(f"{OUTPUT_DIR}/activity_log.csv")
print(f"  {len(features)} users loaded")

CATEGORICAL = ["signup_channel","country","age_group","gender","device_type","plan_type","utm_source"]
NUMERIC     = ["days_since_signup","days_since_last_login","total_sessions","avg_session_duration",
               "total_lessons_started","total_lessons_completed","lesson_completion_rate",
               "courses_enrolled","first_7d_sessions","referral_count",
               "support_tickets_raised","onboarding_score","days_to_first_enroll"]

df = features.copy()
for col in CATEGORICAL:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str).fillna("unknown"))

df[NUMERIC] = df[NUMERIC].fillna(0)
ALL_FEATS = NUMERIC + [c for c in CATEGORICAL if c in df.columns]

# ── MODEL 1: CHURN ──────────────────────────────────────
print("\nTraining Churn Model (XGBoost)...")
X, y = df[ALL_FEATS], df["is_churned"].astype(int)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
Xtr_s, ytr_s = SMOTE(random_state=42).fit_resample(Xtr, ytr)

churn_model = xgb.XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, eval_metric="logloss", random_state=42,
    n_jobs=-1, verbosity=0)
churn_model.fit(Xtr_s, ytr_s, eval_set=[(Xte, yte)], verbose=False)

yp = churn_model.predict_proba(Xte)[:,1]
auc = roc_auc_score(yte, yp)
print(f"  AUC-ROC: {auc:.4f}")
print(classification_report(yte, (yp>=0.65).astype(int), target_names=["Active","Churned"]))

df["churn_score"] = churn_model.predict_proba(X)[:,1]
out = features[["user_id"]].copy()
out["churn_score"] = df["churn_score"].round(4)
out["churn_risk"]  = pd.cut(df["churn_score"], bins=[0,.35,.65,1.], labels=["Low","Medium","High"])
out.to_csv(f"{OUTPUT_DIR}/churn_scores.csv", index=False)
joblib.dump(churn_model, f"{MODEL_DIR}/churn_model.pkl")
print(f"  Saved: churn_model.pkl, churn_scores.csv")

print("  Generating SHAP chart...")
explainer   = shap.TreeExplainer(churn_model)
shap_vals   = explainer.shap_values(Xte.head(300))
shap_importance = np.abs(shap_vals).mean(axis=0)
sorted_idx  = np.argsort(shap_importance)[::-1][:12]
fig, ax = plt.subplots(figsize=(10,6))
fig.patch.set_facecolor("#0F0F23"); ax.set_facecolor("#0F0F23")
ax.barh([ALL_FEATS[i] for i in sorted_idx[::-1]],
        shap_importance[sorted_idx[::-1]], color="#7C3AED", edgecolor="none")
ax.set_title("SHAP Feature Importance — Churn Model", color="white", fontsize=13, fontweight="bold")
ax.tick_params(colors="white"); ax.spines[:].set_visible(False)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/08_churn_shap.png", dpi=150, bbox_inches="tight", facecolor="#0F0F23")
plt.close()
print("  SHAP chart saved.")

# ── MODEL 2: CONVERSION ─────────────────────────────────
print("\nTraining Conversion Model (LightGBM)...")
Xc, yc = df[ALL_FEATS], df["has_paid"].astype(int)
Xctr, Xcte, yctr, ycte = train_test_split(Xc, yc, test_size=0.2, random_state=42, stratify=yc)
Xctr_s, yctr_s = SMOTE(random_state=42).fit_resample(Xctr, yctr)

conv_model = lgb.LGBMClassifier(n_estimators=400, max_depth=6, learning_rate=0.04,
    num_leaves=31, subsample=0.85, colsample_bytree=0.85, random_state=42, n_jobs=-1, verbose=-1)
conv_model.fit(Xctr_s, yctr_s, eval_set=[(Xcte, ycte)],
    callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)])

ycp = conv_model.predict_proba(Xcte)[:,1]
auc_c = roc_auc_score(ycte, ycp)
ap_c  = average_precision_score(ycte, ycp)
print(f"  AUC-ROC: {auc_c:.4f} | Avg Precision: {ap_c:.4f}")
print(classification_report(ycte, (ycp>=0.5).astype(int), target_names=["Free","Paid"]))

df["conversion_score"] = conv_model.predict_proba(Xc)[:,1]
cout = features[["user_id"]].copy()
cout["conversion_score"]    = df["conversion_score"].round(4)
cout["conversion_priority"] = pd.cut(df["conversion_score"], bins=[0,.3,.6,1.], labels=["Low","Medium","High"])
cout.to_csv(f"{OUTPUT_DIR}/conversion_scores.csv", index=False)
joblib.dump(conv_model, f"{MODEL_DIR}/conversion_model.pkl")
print(f"  Saved: conversion_model.pkl, conversion_scores.csv")

# ── MODEL 3: RECOMMENDER ────────────────────────────────
print("\nTraining Course Recommender (SVD)...")
act = activity[activity["course_id"].notna()].copy()
inter = act.groupby(["user_id","course_id"]).agg(
    cnt=("lesson_number","count"), prog=("progress_pct","mean")).reset_index()
inter["prog"] = inter["prog"].fillna(0)
inter["rating"] = (0.6*(inter["cnt"]/inter["cnt"].max()*5) +
                   0.4*(inter["prog"]/100*5)).clip(0,5).round(2)

uids = inter["user_id"].unique(); cids = inter["course_id"].unique()
uidx = {u:i for i,u in enumerate(uids)}; cidx = {c:i for i,c in enumerate(cids)}
R = np.zeros((len(uids), len(cids)))
for _, row in inter.iterrows():
    R[uidx[row["user_id"]], cidx[row["course_id"]]] = row["rating"]

U, S, Vt = np.linalg.svd(R, full_matrices=False)
k=15; Rp = U[:,:k] @ np.diag(S[:k]) @ Vt[:k,:]

recs = []
for uid in uids[:500]:
    ui = uidx[uid]
    seen = set(inter[inter["user_id"]==uid]["course_id"])
    scores = Rp[ui]; top = np.argsort(scores)[::-1]
    added = 0
    for idx in top:
        cid = cids[idx]
        if cid not in seen:
            recs.append({"user_id":uid,"recommended_course_id":cid,"rank":added+1,
                         "predicted_rating":round(Rp[ui,cidx[cid]],3)})
            added += 1
        if added == 5: break

pd.DataFrame(recs).to_csv(f"{OUTPUT_DIR}/recommendations.csv", index=False)
print(f"  Recommendations for {pd.DataFrame(recs)['user_id'].nunique()} users saved.")

print("\n" + "="*55)
print("  ALL MODELS COMPLETE")
print(f"  Churn AUC      : {auc:.4f}")
print(f"  Conversion AUC : {auc_c:.4f}")
print("="*55)
