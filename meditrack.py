import json, os, uuid, datetime, csv

DATA_DIR = "data"
EXPORT_DIR = "exports"

def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)

def _path(name):
    return os.path.join(DATA_DIR, f"{name}.json")

def _load(name):
    _ensure_dirs()
    p = _path(name)
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(name, rows):
    _ensure_dirs()
    with open(_path(name), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

def _now_date():
    return datetime.date.today().isoformat()

def _input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Value cannot be empty.")

def _pick(rows, key="id"):
    if not rows:
        print("No records found.")
        return None
    rid = input("Enter ID: ").strip()
    for r in rows:
        if str(r.get(key)) == rid:
            return r
    print("ID not found.")
    return None

# ================= PATIENTS =================

def patients_add():
    rows = _load("patients")
    rec = {
        "patient_id": str(uuid.uuid4())[:8],
        "name": _input_nonempty("Name: "),
        "age": int(input("Age: ") or 0),
        "sex": input("Sex (M/F/O): ").strip().upper() or "O",
        "phone": _input_nonempty("Phone: "),
        "blood_group": input("Blood group: ").strip().upper(),
        "address": input("Address: ").strip()
    }
    rows.append(rec)
    _save("patients", rows)
    print("Saved with ID:", rec["patient_id"])

def patients_list():
    rows = _load("patients")
    print(f"Total patients: {len(rows)}")
    for r in rows:
        print(f"{r['patient_id']} | {r['name']} | {r['age']} | {r['sex']} | {r['phone']}")

# ================= DOCTORS =================

def doctors_add():
    rows = _load("doctors")
    rec = {
        "doctor_id": str(uuid.uuid4())[:8],
        "name": _input_nonempty("Doctor name: "),
        "department": _input_nonempty("Department: "),
        "phone": _input_nonempty("Phone: ")
    }
    rows.append(rec)
    _save("doctors", rows)
    print("Saved with ID:", rec["doctor_id"])

def doctors_list():
    rows = _load("doctors")
    print(f"Total doctors: {len(rows)}")
    for r in rows:
        print(f"{r['doctor_id']} | {r['name']} | {r['department']} | {r['phone']}")

# ================= APPOINTMENTS =================

def appointments_book():
    patients = _load("patients")
    doctors = _load("doctors")
    if not patients or not doctors:
        print("Need at least one patient and one doctor.")
        return

    appts = _load("appointments")
    rec = {
        "appt_id": str(uuid.uuid4())[:8],
        "patient_id": _input_nonempty("Patient ID: "),
        "doctor_id": _input_nonempty("Doctor ID: "),
        "date": input("Date (YYYY-MM-DD) [today]: ").strip() or _now_date(),
        "time": input("Time (HH:MM): ").strip() or "10:00",
        "status": "Booked"
    }
    appts.append(rec)
    _save("appointments", appts)
    print("Appointment booked with ID:", rec["appt_id"])

def appointments_list():
    appts = _load("appointments")
    print(f"Total appointments: {len(appts)}")
    for a in appts:
        print(f"{a['appt_id']} | P:{a['patient_id']} | D:{a['doctor_id']} | {a['date']} {a['time']} | {a['status']}")

def appointments_update_status():
    appts = _load("appointments")
    a = _pick(appts, key="appt_id")
    if not a: return

    new = input("Status (Booked/Completed/No-Show): ").strip().title()
    if new not in {"Booked","Completed","No-Show"}:
        print("Invalid status.")
        return

    a["status"] = new
    _save("appointments", appts)
    print("Status updated.")

# ================= ADMISSIONS =================

def admissions_admit():
    adms = _load("admissions")
    rec = {
        "adm_id": str(uuid.uuid4())[:8],
        "patient_id": _input_nonempty("Patient ID: "),
        "admit_date": input("Admit date (YYYY-MM-DD) [today]: ").strip() or _now_date(),
        "discharge_date": "",
        "ward": input("Ward: ").strip() or "General",
        "bed_no": input("Bed no: ").strip() or "-",
        "diagnosis": input("Diagnosis: ").strip()
    }
    adms.append(rec)
    _save("admissions", adms)
    print("Admitted with ID:", rec["adm_id"])

def admissions_discharge():
    adms = _load("admissions")
    a = _pick(adms, key="adm_id")
    if not a: return

    if a.get("discharge_date"):
        print("Already discharged.")
        return

    a["discharge_date"] = input("Discharge date (YYYY-MM-DD) [today]: ").strip() or _now_date()
    _save("admissions", adms)
    print("Discharged.")

def admissions_list():
    adms = _load("admissions")
    print(f"Total admissions: {len(adms)}")
    for a in adms:
        print(f"{a['adm_id']} | P:{a['patient_id']} | {a['admit_date']} -> {a.get('discharge_date') or '—'} | {a['ward']} | {a['diagnosis']}")

# ================= BILLING =================

def billing_create():
    bills = _load("billing")
    rec = {
        "bill_id": str(uuid.uuid4())[:8],
        "patient_id": _input_nonempty("Patient ID: "),
        "date": input("Bill date (YYYY-MM-DD) [today]: ").strip() or _now_date(),
        "amount": float(input("Amount: ") or 0.0),
        "mode": (input("Mode (Cash/Card/UPI): ").strip().title() or "Cash"),
        "remarks": input("Remarks: ").strip()
    }
    bills.append(rec)
    _save("billing", bills)
    print("Bill created with ID:", rec["bill_id"])

def billing_list():
    bills = _load("billing")
    total = sum(b.get("amount",0) for b in bills)
    print(f"Total bills: {len(bills)} | Total amount: {total}")
    for b in bills:
        print(f"{b['bill_id']} | P:{b['patient_id']} | {b['date']} | {b['amount']} | {b['mode']} | {b['remarks']}")

# ================= REPORTS =================

def report_todays_appointments():
    appts = _load("appointments")
    today = _now_date()
    todays = [a for a in appts if a.get("date") == today]
    print(f"Today's appointments ({today}): {len(todays)}")
    for a in todays:
        print(f"{a['appt_id']} | P:{a['patient_id']} | D:{a['doctor_id']} | {a['time']} | {a['status']}")

def report_current_occupancy(total_beds=100):
    adms = _load("admissions")
    current = [a for a in adms if not a.get("discharge_date")]
    occ = len(current)
    rate = (occ/total_beds)*100 if total_beds else 0
    print(f"Current in-patients: {occ} / {total_beds} beds ({rate:.1f}% occupancy)")

# ================= EXPORT CSV =================

def export_analytics_csv():
    _ensure_dirs()
    mapping = {
        "patients": ["patient_id","name","age","sex","phone","blood_group","address"],
        "doctors": ["doctor_id","name","department","phone"],
        "appointments": ["appt_id","patient_id","doctor_id","date","time","status"],
        "admissions": ["adm_id","patient_id","admit_date","discharge_date","ward","bed_no","diagnosis"],
        "billing": ["bill_id","patient_id","date","amount","mode","remarks"],
    }

    for name, cols in mapping.items():
        rows = _load(name)
        out = os.path.join(EXPORT_DIR, f"{name}.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in cols})
        print("Exported:", out)

# ================= MENUS =================

def patients_menu():
    while True:
        print("\n-- Patients --\n1) Add  2) List  0) Back")
        c = input("Choose: ").strip()
        if c == "1": patients_add()
        elif c == "2": patients_list()
        elif c == "0": return

def doctors_menu():
    while True:
        print("\n-- Doctors --\n1) Add  2) List  0) Back")
        c = input("Choose: ").strip()
        if c == "1": doctors_add()
        elif c == "2": doctors_list()
        elif c == "0": return

def appointments_menu():
    while True:
        print("\n-- Appointments --\n1) Book  2) List  3) Update Status  0) Back")
        c = input("Choose: ").strip()
        if c == "1": appointments_book()
        elif c == "2": appointments_list()
        elif c == "3": appointments_update_status()
        elif c == "0": return

def admissions_menu():
    while True:
        print("\n-- Admissions --\n1) Admit  2) Discharge  3) List  0) Back")
        c = input("Choose: ").strip()
        if c == "1": admissions_admit()
        elif c == "2": admissions_discharge()
        elif c == "3": admissions_list()
        elif c == "0": return

def billing_menu():
    while True:
        print("\n-- Billing --\n1) Create Bill  2) List Bills  0) Back")
        c = input("Choose: ").strip()
        if c == "1": billing_create()
        elif c == "2": billing_list()
        elif c == "0": return

def reports_menu():
    while True:
        print("\n-- Reports --\n1) Today's Appointments  2) Current Occupancy  0) Back")
        c = input("Choose: ").strip()
        if c == "1": report_todays_appointments()
        elif c == "2": report_current_occupancy()
        elif c == "0": return

# ================= MAIN MENU =================

def main():
    while True:
        print("\n=== MediTrack ===")
        print("1) Patients  2) Doctors  3) Appointments  4) Admissions")
        print("5) Billing   6) Reports   7) Export Analytics CSV  0) Exit")
        ch = input("Choose: ").strip()

        if ch == "1": patients_menu()
        elif ch == "2": doctors_menu()
        elif ch == "3": appointments_menu()
        elif ch == "4": admissions_menu()
        elif ch == "5": billing_menu()
        elif ch == "6": reports_menu()
        elif ch == "7": export_analytics_csv()
        elif ch == "0":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
