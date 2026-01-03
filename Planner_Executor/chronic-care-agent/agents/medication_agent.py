from utils.rules import NON_ADHERENCE_DAYS

def check_medication_adherence(med_log):
    missed_days = [d for d in med_log if not d["taken"]]

    if len(missed_days) >= NON_ADHERENCE_DAYS:
        return f"Missed medication for {len(missed_days)} days"

    return "Medication adherence OK"
