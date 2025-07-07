"""
Utility functions for the Finanzas application
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

def validate_date(date_string: str, date_format: str = "%Y-%m-%d") -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format amount as currency"""
    return f"{currency_symbol}{amount:,.2f}"

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def get_date_range(period: str) -> tuple:
    """Get date range for common periods"""
    today = datetime.now().date()
    
    if period == "today":
        return today, today
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period == "month":
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start, end
    elif period == "year":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
    else:
        return today, today

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100

def group_by_period(data: List[Dict[str, Any]], date_field: str, period: str = "month") -> Dict[str, List[Dict[str, Any]]]:
    """Group data by time period"""
    grouped = {}
    
    for item in data:
        date_str = item.get(date_field)
        if not date_str:
            continue
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            if period == "month":
                key = date_obj.strftime("%Y-%m")
            elif period == "week":
                # Get Monday of the week
                monday = date_obj - timedelta(days=date_obj.weekday())
                key = monday.strftime("%Y-%m-%d")
            elif period == "year":
                key = date_obj.strftime("%Y")
            else:  # day
                key = date_obj.strftime("%Y-%m-%d")
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
            
        except ValueError:
            continue
    
    return grouped

def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def is_valid_movement_type(movement_type: str) -> bool:
    """Validate movement type"""
    valid_types = ['Ingreso', 'Gasto', 'Ahorro']
    return movement_type in valid_types

def generate_summary_stats(amounts: List[float]) -> Dict[str, float]:
    """Generate summary statistics for a list of amounts"""
    if not amounts:
        return {
            'total': 0.0,
            'average': 0.0,
            'min': 0.0,
            'max': 0.0,
            'count': 0
        }
    
    return {
        'total': sum(amounts),
        'average': sum(amounts) / len(amounts),
        'min': min(amounts),
        'max': max(amounts),
        'count': len(amounts)
    }