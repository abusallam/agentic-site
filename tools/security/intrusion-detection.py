#!/usr/bin/env python3
"""
Intrusion Detection and Monitoring System
Real-time threat monitoring with behavioral anomaly detection
"""

import asyncio
import json
import logging
import os
import psutil
import socket
import subprocess
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/intrusion-detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: datetime
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip: str
    description: str
    details: Dict
    threat_score: int  # 0-100

@dataclass
class NetworkConnection:
    """Network connection tracking"""
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    pid: Optional[int]
    process_name: Optional[str]

class ThreatIntelligence:
    """Threat intelligence integration"""
    
    def __init__(self):
        self.malicious_ips: Set[str] = set()
        self.suspicious_patterns: List[str] = []
        self.load_threat_feeds()
    
    def load_threat_feeds(self):
        """Load threat intelligence feeds"""
        try:
            # Load known malicious IPs
            malicious_ips_file = Path('/etc/security/malicious-ips.txt')
            if malicious_ips_file.exists():
                with open(malicious_ips_file, 'r') as f:
                    self.malicious_ips.update(line.strip() for line in f if line.strip())
            
            # Load suspicious patterns
            patterns_file = Path('/etc/security/suspicious-patterns.txt')
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.suspicious_patterns.extend(line.strip() for line in f if line.strip())
            
            logger.info(f"Loaded {len(self.malicious_ips)} malicious IPs and {len(self.suspicious_patterns)} patterns")
        except Exception as e:
            logger.error(f"Error loading threat feeds: {e}")
    
    def is_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in malicious list"""
        return ip in self.malicious_ips
    
    def check_suspicious_pattern(self, text: str) -> Optional[str]:
        """Check for suspicious patterns in text"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return pattern
        return None

class BehavioralAnalyzer:
    """Behavioral anomaly detection"""
    
    def __init__(self, window_size: int = 300):  # 5 minutes
        self.window_size = window_size
        self.connection_history: deque = deque(maxlen=1000)
        self.login_attempts: defaultdict = defaultdict(list)
        self.process_baselines: Dict[str, Dict] = {}
        self.network_baselines: Dict[str, int] = defaultdict(int)
        
    def analyze_connection_pattern(self, conn: NetworkConnection) -> int:
        """Analyze connection patterns for anomalies"""
        threat_score = 0
        
        # Check for port scanning
        recent_connections = [c for c in self.connection_history 
                            if c.remote_addr == conn.remote_addr and 
                            (datetime.now() - c.timestamp).seconds < 60]
        
        if len(recent_connections) > 10:  # More than 10 connections in 1 minute
            threat_score += 30
            logger.warning(f"Potential port scan detected from {conn.remote_addr}")
        
        # Check for unusual ports
        if conn.local_port in [22, 80, 443, 3000, 8000]:  # Expected ports
            threat_score += 0
        elif conn.local_port > 49152:  # Ephemeral ports
            threat_score += 5
        else:  # Unusual service ports
            threat_score += 15
        
        return min(threat_score, 100)
    
    def analyze_login_attempts(self, ip: str, success: bool) -> int:
        """Analyze login attempt patterns"""
        now = datetime.now()
        self.login_attempts[ip].append((now, success))
        
        # Clean old attempts (older than 1 hour)
        self.login_attempts[ip] = [(t, s) for t, s in self.login_attempts[ip] 
                                  if (now - t).seconds < 3600]
        
        recent_attempts = self.login_attempts[ip]
        failed_attempts = [a for a in recent_attempts if not a[1]]
        
        threat_score = 0
        if len(failed_attempts) > 5:  # More than 5 failed attempts
            threat_score = min(len(failed_attempts) * 10, 80)
            logger.warning(f"Multiple failed login attempts from {ip}: {len(failed_attempts)}")
        
        return threat_score
    
    def analyze_process_behavior(self, processes: List[Dict]) -> List[SecurityEvent]:
        """Analyze process behavior for anomalies"""
        events = []
        
        for proc in processes:
            try:
                name = proc.get('name', 'unknown')
                cpu_percent = proc.get('cpu_percent', 0)
                memory_percent = proc.get('memory_percent', 0)
                
                # Check for resource abuse
                if cpu_percent > 80:
                    events.append(SecurityEvent(
                        timestamp=datetime.now(),
                        event_type='RESOURCE_ABUSE',
                        severity='MEDIUM',
                        source_ip='localhost',
                        description=f'Process {name} consuming high CPU: {cpu_percent}%',
                        details={'process': name, 'cpu_percent': cpu_percent},
                        threat_score=40
                    ))
                
                if memory_percent > 80:
                    events.append(SecurityEvent(
                        timestamp=datetime.now(),
                        event_type='RESOURCE_ABUSE',
                        severity='MEDIUM',
                        source_ip='localhost',
                        description=f'Process {name} consuming high memory: {memory_percent}%',
                        details={'process': name, 'memory_percent': memory_percent},
                        threat_score=40
                    ))
                
                # Check for suspicious process names
                suspicious_names = ['nc', 'netcat', 'nmap', 'masscan', 'sqlmap', 'metasploit']
                if any(sus in name.lower() for sus in suspicious_names):
                    events.append(SecurityEvent(
                        timestamp=datetime.now(),
                        event_type='SUSPICIOUS_PROCESS',
                        severity='HIGH',
                        source_ip='localhost',
                        description=f'Suspicious process detected: {name}',
                        details={'process': name},
                        threat_score=70
                    ))
                
            except Exception as e:
                logger.error(f"Error analyzing process {proc}: {e}")
        
        return events

class NetworkMonitor:
    """Network traffic monitoring and analysis"""
    
    def __init__(self):
        self.active_connections: Dict[str, NetworkConnection] = {}
        self.connection_stats: defaultdict = defaultdict(int)
        
    def get_network_connections(self) -> List[NetworkConnection]:
        """Get current network connections"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    process_name = None
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            process_name = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    local_addr = conn.laddr.ip if conn.laddr else 'unknown'
                    local_port = conn.laddr.port if conn.laddr else 0
                    remote_addr = conn.raddr.ip if conn.raddr else 'unknown'
                    remote_port = conn.raddr.port if conn.raddr else 0
                    
                    connections.append(NetworkConnection(
                        local_addr=local_addr,
                        local_port=local_port,
                        remote_addr=remote_addr,
                        remote_port=remote_port,
                        status=conn.status,
                        pid=conn.pid,
                        process_name=process_name
                    ))
        
        except Exception as e:
            logger.error(f"Error getting network connections: {e}")
        
        return connections
    
    def analyze_network_traffic(self) -> List[SecurityEvent]:
        """Analyze network traffic for threats"""
        events = []
        connections = self.get_network_connections()
        
        for conn in connections:
            # Check for connections to suspicious IPs
            threat_intel = ThreatIntelligence()
            if threat_intel.is_malicious_ip(conn.remote_addr):
                events.append(SecurityEvent(
                    timestamp=datetime.now(),
                    event_type='MALICIOUS_CONNECTION',
                    severity='CRITICAL',
                    source_ip=conn.remote_addr,
                    description=f'Connection to known malicious IP: {conn.remote_addr}',
                    details=asdict(conn),
                    threat_score=90
                ))
            
            # Check for unusual connection patterns
            analyzer = BehavioralAnalyzer()
            threat_score = analyzer.analyze_connection_pattern(conn)
            if threat_score > 50:
                events.append(SecurityEvent(
                    timestamp=datetime.now(),
                    event_type='SUSPICIOUS_NETWORK',
                    severity='HIGH' if threat_score > 70 else 'MEDIUM',
                    source_ip=conn.remote_addr,
                    description=f'Suspicious network pattern detected',
                    details=asdict(conn),
                    threat_score=threat_score
                ))
        
        return events

class LogAnalyzer:
    """System log analysis for security events"""
    
    def __init__(self):
        self.log_files = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/nginx/access.log',
            '/var/log/nginx/error.log'
        ]
        self.last_positions: Dict[str, int] = {}
    
    def analyze_auth_logs(self) -> List[SecurityEvent]:
        """Analyze authentication logs"""
        events = []
        auth_log = '/var/log/auth.log'
        
        if not os.path.exists(auth_log):
            return events
        
        try:
            with open(auth_log, 'r') as f:
                # Start from last known position
                last_pos = self.last_positions.get(auth_log, 0)
                f.seek(last_pos)
                
                for line in f:
                    # Failed SSH login attempts
                    if 'Failed password' in line:
                        ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            analyzer = BehavioralAnalyzer()
                            threat_score = analyzer.analyze_login_attempts(ip, False)
                            
                            events.append(SecurityEvent(
                                timestamp=datetime.now(),
                                event_type='FAILED_LOGIN',
                                severity='MEDIUM' if threat_score > 50 else 'LOW',
                                source_ip=ip,
                                description=f'Failed SSH login attempt from {ip}',
                                details={'log_line': line.strip()},
                                threat_score=threat_score
                            ))
                    
                    # Successful logins from unusual locations
                    elif 'Accepted password' in line:
                        ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            # Check if IP is from unusual location (basic check)
                            if not ip.startswith(('192.168.', '10.', '172.')):
                                events.append(SecurityEvent(
                                    timestamp=datetime.now(),
                                    event_type='REMOTE_LOGIN',
                                    severity='LOW',
                                    source_ip=ip,
                                    description=f'Remote SSH login from {ip}',
                                    details={'log_line': line.strip()},
                                    threat_score=20
                                ))
                
                # Update last position
                self.last_positions[auth_log] = f.tell()
        
        except Exception as e:
            logger.error(f"Error analyzing auth logs: {e}")
        
        return events
    
    def analyze_nginx_logs(self) -> List[SecurityEvent]:
        """Analyze Nginx access logs for suspicious activity"""
        events = []
        access_log = '/var/log/nginx/access.log'
        
        if not os.path.exists(access_log):
            return events
        
        try:
            with open(access_log, 'r') as f:
                last_pos = self.last_positions.get(access_log, 0)
                f.seek(last_pos)
                
                for line in f:
                    # Check for suspicious patterns
                    threat_intel = ThreatIntelligence()
                    suspicious_pattern = threat_intel.check_suspicious_pattern(line)
                    
                    if suspicious_pattern:
                        ip_match = re.search(r'^(\d+\.\d+\.\d+\.\d+)', line)
                        ip = ip_match.group(1) if ip_match else 'unknown'
                        
                        events.append(SecurityEvent(
                            timestamp=datetime.now(),
                            event_type='SUSPICIOUS_REQUEST',
                            severity='MEDIUM',
                            source_ip=ip,
                            description=f'Suspicious HTTP request pattern: {suspicious_pattern}',
                            details={'log_line': line.strip(), 'pattern': suspicious_pattern},
                            threat_score=50
                        ))
                    
                    # Check for 4xx/5xx errors that might indicate attacks
                    if ' 40' in line or ' 50' in line:
                        if 'sql' in line.lower() or 'script' in line.lower() or '../' in line:
                            ip_match = re.search(r'^(\d+\.\d+\.\d+\.\d+)', line)
                            ip = ip_match.group(1) if ip_match else 'unknown'
                            
                            events.append(SecurityEvent(
                                timestamp=datetime.now(),
                                event_type='ATTACK_ATTEMPT',
                                severity='HIGH',
                                source_ip=ip,
                                description='Potential attack attempt detected in HTTP logs',
                                details={'log_line': line.strip()},
                                threat_score=70
                            ))
                
                self.last_positions[access_log] = f.tell()
        
        except Exception as e:
            logger.error(f"Error analyzing nginx logs: {e}")
        
        return events

class IntrusionDetectionSystem:
    """Main intrusion detection system coordinator"""
    
    def __init__(self):
        self.network_monitor = NetworkMonitor()
        self.log_analyzer = LogAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.threat_intelligence = ThreatIntelligence()
        self.events_queue: deque = deque(maxlen=1000)
        self.alert_thresholds = {
            'LOW': 0,
            'MEDIUM': 40,
            'HIGH': 70,
            'CRITICAL': 90
        }
    
    async def monitor_system(self):
        """Main monitoring loop"""
        logger.info("Starting intrusion detection system...")
        
        while True:
            try:
                # Collect events from all sources
                events = []
                
                # Network monitoring
                events.extend(self.network_monitor.analyze_network_traffic())
                
                # Log analysis
                events.extend(self.log_analyzer.analyze_auth_logs())
                events.extend(self.log_analyzer.analyze_nginx_logs())
                
                # Process monitoring
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                events.extend(self.behavioral_analyzer.analyze_process_behavior(processes))
                
                # Process and correlate events
                for event in events:
                    await self.process_security_event(event)
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def process_security_event(self, event: SecurityEvent):
        """Process and respond to security events"""
        self.events_queue.append(event)
        
        # Log the event
        logger.info(f"Security event: {event.event_type} - {event.description}")
        
        # Save to file for persistence
        await self.save_event(event)
        
        # Check if response is needed
        if event.threat_score >= self.alert_thresholds['HIGH']:
            await self.trigger_response(event)
    
    async def save_event(self, event: SecurityEvent):
        """Save security event to file"""
        try:
            events_file = Path('/var/log/security-events.json')
            events_file.parent.mkdir(parents=True, exist_ok=True)
            
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            
            with open(events_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
        
        except Exception as e:
            logger.error(f"Error saving event: {e}")
    
    async def trigger_response(self, event: SecurityEvent):
        """Trigger automated response to high-severity events"""
        logger.warning(f"Triggering response for high-severity event: {event.description}")
        
        try:
            # Block malicious IPs (if applicable)
            if event.source_ip and event.source_ip != 'localhost':
                if event.severity in ['HIGH', 'CRITICAL']:
                    await self.block_ip(event.source_ip)
            
            # Send alert notification
            await self.send_alert(event)
            
            # Log response action
            logger.info(f"Response triggered for event: {event.event_type}")
        
        except Exception as e:
            logger.error(f"Error triggering response: {e}")
    
    async def block_ip(self, ip: str):
        """Block malicious IP using iptables"""
        try:
            # Add to iptables DROP rule
            cmd = f"iptables -A INPUT -s {ip} -j DROP"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Blocked IP: {ip}")
            else:
                logger.error(f"Failed to block IP {ip}: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error blocking IP {ip}: {e}")
    
    async def send_alert(self, event: SecurityEvent):
        """Send alert notification"""
        try:
            # Create alert message
            alert_msg = {
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity,
                'event_type': event.event_type,
                'description': event.description,
                'source_ip': event.source_ip,
                'threat_score': event.threat_score
            }
            
            # Save alert to file (could be extended to send emails, webhooks, etc.)
            alerts_file = Path('/var/log/security-alerts.json')
            with open(alerts_file, 'a') as f:
                f.write(json.dumps(alert_msg) + '\n')
            
            logger.info(f"Alert sent for {event.event_type}")
        
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_system_status(self) -> Dict:
        """Get current system security status"""
        recent_events = [e for e in self.events_queue 
                        if (datetime.now() - e.timestamp).seconds < 3600]  # Last hour
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'total_events': len(self.events_queue),
            'recent_events': len(recent_events),
            'severity_counts': defaultdict(int),
            'top_threats': [],
            'system_health': 'HEALTHY'
        }
        
        # Count events by severity
        for event in recent_events:
            status['severity_counts'][event.severity] += 1
        
        # Determine system health
        if status['severity_counts']['CRITICAL'] > 0:
            status['system_health'] = 'CRITICAL'
        elif status['severity_counts']['HIGH'] > 5:
            status['system_health'] = 'WARNING'
        elif status['severity_counts']['MEDIUM'] > 10:
            status['system_health'] = 'CAUTION'
        
        return status

async def main():
    """Main entry point"""
    ids = IntrusionDetectionSystem()
    
    try:
        await ids.monitor_system()
    except KeyboardInterrupt:
        logger.info("Intrusion detection system stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in intrusion detection system: {e}")

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs('/var/log', exist_ok=True)
    os.makedirs('/etc/security', exist_ok=True)
    
    # Run the system
    asyncio.run(main())