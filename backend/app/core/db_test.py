"""Test database functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import db_manager
from app.models import Agent, User, Alert, AlertSeverity, AlertType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test database operations"""
    
    # Test agent operations
    logger.info("Testing agent operations...")
    
    # Add a test agent
    agent_data = {
        'hostname': 'test-agent-01',
        'ip': '192.168.1.100',
        'os': 'Windows 10',
        'version': '1.0.0',
        'status': 'online',
        'tags': ['test', 'windows'],
        'system_info': {
            'cpu_count': 4,
            'memory_gb': 16,
            'disk_gb': 500
        }
    }
    
    agent_id = db_manager.add_agent(agent_data)
    logger.info(f"Added agent: {agent_id}")
    
    # Get all agents
    agents = db_manager.get_agents()
    logger.info(f"Total agents: {len(agents)}")
    
    # Get specific agent
    agent = db_manager.get_agent(agent_id)
    if agent:
        logger.info(f"Retrieved agent: {agent['hostname']}")
    
    # Test command history
    logger.info("Testing command history...")
    command_data = {
        'command': 'Get-Process',
        'success': True,
        'output': 'Process list...',
        'execution_time': 0.5
    }
    
    cmd_id = db_manager.add_command_history(agent_id, command_data)
    logger.info(f"Added command history: {cmd_id}")
    
    # Get command history
    history = db_manager.get_command_history(agent_id, limit=10)
    logger.info(f"Command history entries: {len(history)}")
    
    # Test user operations
    logger.info("Testing user operations...")
    import hashlib
    password_hash = hashlib.sha256("testpass123".encode()).hexdigest()
    
    user_id = db_manager.create_user(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        is_admin=True
    )
    
    if user_id:
        logger.info(f"Created user: {user_id}")
        user = db_manager.get_user(user_id)
        if user:
            logger.info(f"Retrieved user: {user['username']}")
    
    # Test groups
    logger.info("Testing agent groups...")
    group_id = db_manager.create_agent_group(
        name="Windows Servers",
        description="All Windows server agents"
    )
    
    if group_id:
        logger.info(f"Created group: {group_id}")
        db_manager.add_agent_to_group(group_id, agent_id)
        logger.info(f"Added agent to group")
        
        group_agents = db_manager.get_group_agents(group_id)
        logger.info(f"Agents in group: {len(group_agents)}")
    
    # Test metrics
    logger.info("Testing agent metrics...")
    metrics_data = {
        'cpu_usage': 45.5,
        'memory_usage': 62.3,
        'disk_usage': 78.1,
        'network_in': 1024.5,
        'network_out': 512.3,
        'process_count': 125
    }
    
    metric_id = db_manager.add_agent_metrics(agent_id, metrics_data)
    logger.info(f"Added metrics: {metric_id}")
    
    metrics = db_manager.get_agent_metrics(agent_id, hours=1)
    logger.info(f"Retrieved metrics: {len(metrics)}")
    
    # Test alerts
    logger.info("Testing alerts...")
    alert_id = db_manager.create_alert(
        agent_id=agent_id,
        alert_type='high_cpu',
        severity='warning',
        message='CPU usage above 80%',
        details={'cpu_usage': 85.5}
    )
    logger.info(f"Created alert: {alert_id}")
    
    active_alerts = db_manager.get_active_alerts()
    logger.info(f"Active alerts: {len(active_alerts)}")
    
    # Test audit logs
    logger.info("Testing audit logs...")
    if user_id:
        audit_id = db_manager.add_audit_log(
            user_id=user_id,
            action='execute',
            resource_type='agent',
            resource_id=agent_id,
            details={'command': 'Get-Process'},
            ip_address='127.0.0.1'
        )
        logger.info(f"Added audit log: {audit_id}")
        
        logs = db_manager.get_audit_logs(limit=10)
        logger.info(f"Audit logs: {len(logs)}")
    
    logger.info("Database tests completed successfully!")

if __name__ == "__main__":
    test_database()