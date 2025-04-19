import uuid
import datetime

def generate_random_report_id() -> str:
    """Generate a random unique report ID using UUID4 with timestamp prefix"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    random_id = str(uuid.uuid4()).replace("-", "")[:12]
    return f"REP-{timestamp}-{random_id}" 