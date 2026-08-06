from datetime import datetime

def format_currency(value: float) -> str:
    """Format float to currency string."""
    return f"{value:,.2f} ₺"

def get_current_timestamp() -> str:
    """Get formatted current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
