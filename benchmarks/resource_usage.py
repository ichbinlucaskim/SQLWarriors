"""
Resource Usage Monitoring
Measures CPU, memory, and storage utilization for both databases
"""

import psutil
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def get_system_resources() -> Dict:
    """
    Get current system resource usage
    
    Returns:
        Dictionary with CPU, memory, and disk usage
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }


def monitor_during_operation(operation_func, *args, **kwargs) -> Dict:
    """
    Monitor resource usage during a database operation
    
    Args:
        operation_func: Function to execute and monitor
        *args, **kwargs: Arguments for operation function
        
    Returns:
        Dictionary with operation results and resource metrics
    """
    # Get baseline resources
    baseline = get_system_resources()
    
    # Execute operation
    result = operation_func(*args, **kwargs)
    
    # Get resources after operation
    after = get_system_resources()
    
    return {
        'baseline': baseline,
        'after': after,
        'operation_result': result
    }


# TODO: Add database-specific resource monitoring
# - PostgreSQL: Query pg_stat_database, pg_stat_user_tables
# - MongoDB: Use db.serverStatus(), db.stats()

