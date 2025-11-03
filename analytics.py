import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

EXPORT_DIR = "exports"

def _read_csv(name, parse_dates=None):
    path = os.path.join(EXPORT_DIR, f"{name}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Export not found: {path}. Run Export in meditrack.py first.")
    return pd.read_csv(path, parse_dates=parse_dates)

def main():
    patients = _read_csv("patients")
    doctors = _read_csv("doctors")
    appts = _read_csv("appointments", parse_dates=["date"])
    adms = _read_csv("admissions", parse_dates=["admit_date","discharge_date"])
    bills = _read_csv("billing", parse_dates=["date"])

    # KPI: No-show rate
    no_show_rate = (appts["status"].eq("No-Show").mean() * 100.0) if len(appts) else 0.0

    # KPI: Admissions per month
    if len(adms):
        adms["adm_month"] = adms["admit_date"].dt.to_period("M").dt.to_timestamp()
        adm_trend = adms.groupby("adm_month")["adm_id"].count()
    else:
        adm_trend = pd.Series(dtype=int)

    # KPI: Average Length of Stay (ALOS)
    if len(adms):
        dd = (adms["discharge_date"] - adms["admit_date"]).dt.days
        alos = dd.dropna().clip(lower=0).mean()
    else:
        alos = np.nan

    # KPI: Revenue by day
    if len(bills):
        bills["bill_day"] = bills["date"].dt.date
        rev_by_day = bills.groupby("bill_day")["amount"].sum()
    else:
        rev_by_day = pd.Series(dtype=float)

    # Print results
    print("\n==== KPI SUMMARY ====")
    print(f"Patients: {len(patients)} | Doctors: {len(doctors)} | Appointments: {len(appts)}")
    print(f"No-Show Rate: {no_show_rate:.2f}%")
    print(f"Average Stay (days): {0 if pd.isna(alos) else round(alos,2)}")
    print(f"Total Revenue: {bills['amount'].sum() if len(bills) else 0}")

    # Charts folder
    os.makedirs("charts", exist_ok=True)

    # Line chart: Admissions trend
    if len(adm_trend):
        plt.figure()
        adm_trend.plot(kind="line", marker="o", title="Admissions per Month")
        plt.xlabel("Month"); plt.ylabel("Admissions")
        plt.tight_layout(); plt.savefig("charts/admissions_per_month.png")
        print("Saved: charts/admissions_per_month.png")

    # Bar chart: Revenue by day
    if len(rev_by_day):
        plt.figure()
        rev_by_day.plot(kind="bar", title="Revenue by Day")
        plt.xlabel("Day"); plt.ylabel("Revenue")
        plt.tight_layout(); plt.savefig("charts/revenue_by_day.png")
        print("Saved: charts/revenue_by_day.png")

    # Pie: top diagnoses
    if len(adms) and adms["diagnosis"].notna().any():
        diag_counts = adms["diagnosis"].fillna("").str.strip()
        diag_counts = diag_counts[diag_counts != ""].value_counts().head(5)
        if len(diag_counts):
            plt.figure()
            diag_counts.plot(kind="pie", autopct="%1.0f%%", title="Top Diagnoses Distribution")
            plt.ylabel("")
            plt.tight_layout(); plt.savefig("charts/top_diagnoses_pie.png")
            print("Saved: charts/top_diagnoses_pie.png")

if __name__ == "__main__":
    main()
