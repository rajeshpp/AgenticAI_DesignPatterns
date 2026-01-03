from utils.rules import BP_SYSTOLIC_HIGH, BP_DIASTOLIC_HIGH

def analyze_wearable_data(wearable_data):
    alerts = []

    for record in wearable_data:
        if (record["systolic"] > BP_SYSTOLIC_HIGH or
            record["diastolic"] > BP_DIASTOLIC_HIGH):
            alerts.append(
                f"High BP detected: {record['systolic']}/{record['diastolic']}"
            )

    return alerts
