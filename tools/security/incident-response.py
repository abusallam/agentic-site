#!/usr/bin/env python3
"""
Security Incident Response Automation System
Automated threat containment, forensic data collection, and response coordination
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import tarfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/incident-response.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    incident_id: str
    timestamp: datetime
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    incident_type: str
    source: str
    description: str
    affected_systems: List[str]
    indicators: Dict
    status: str  # DETECTED, INVESTIGATING, CONTAINED, RESOLVED
    response_actions: List[str]
    forensic_data: Dict

@dataclass
class ResponseAction:
    """Response action data structure"""
    action_id: str
    incident_id: str
    action_type: str
    description: str
    timestamp: datetime
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    result: Optional[str]
    evidence_collected: List[str]

class ForensicCollector:
    """Forensic data collection and preservation"""
    
    def __init__(self):
        self.evidence_dir = Path('/var/lib/incident-response/evidence')
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.chain_of_custody = []
    
    async def collect_system_state(self, incident_id: str) -> Dict[str, str]:
        """Collect comprehensive system state for forensic analysis"""
        logger.info(f"Collecting system state for incident {incident_id}")
        
        evidence_path = self.evidence_dir / f"incident-{incident_id}"
        evidence_path.mkdir(exist_ok=True)
        
        collected_evidence = {}
        
        try:
            # Collect running processes
            processes_file = evidence_path / "running_processes.txt"
            with open(processes_file, 'w') as f:
                subprocess.run(['ps', 'auxwww'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['processes'] = str(processes_file)
            
            # Collect network connections
            netstat_file = evidence_path / "network_connections.txt"
            with open(netstat_file, 'w') as f:
                subprocess.run(['netstat', '-tulpn'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['network'] = str(netstat_file)
            
            # Collect system information
            sysinfo_file = evidence_path / "system_info.txt"
            with open(sysinfo_file, 'w') as f:
                f.write("=== SYSTEM INFORMATION ===\n")
                subprocess.run(['uname', '-a'], stdout=f, stderr=subprocess.DEVNULL)
                f.write("\n=== UPTIME ===\n")
                subprocess.run(['uptime'], stdout=f, stderr=subprocess.DEVNULL)
                f.write("\n=== MEMORY USAGE ===\n")
                subprocess.run(['free', '-h'], stdout=f, stderr=subprocess.DEVNULL)
                f.write("\n=== DISK USAGE ===\n")
                subprocess.run(['df', '-h'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['system_info'] = str(sysinfo_file)
            
            # Collect loaded kernel modules
            modules_file = evidence_path / "kernel_modules.txt"
            with open(modules_file, 'w') as f:
                subprocess.run(['lsmod'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['modules'] = str(modules_file)
            
            # Collect open files
            lsof_file = evidence_path / "open_files.txt"
            with open(lsof_file, 'w') as f:
                subprocess.run(['lsof'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['open_files'] = str(lsof_file)
            
            # Collect environment variables
            env_file = evidence_path / "environment.txt"
            with open(env_file, 'w') as f:
                subprocess.run(['env'], stdout=f, stderr=subprocess.DEVNULL)
            collected_evidence['environment'] = str(env_file)
            
            # Collect recent log entries
            await self.collect_log_evidence(evidence_path, incident_id)
            collected_evidence['logs'] = str(evidence_path / "logs")
            
            # Create evidence hash
            evidence_hash = await self.create_evidence_hash(evidence_path)
            collected_evidence['evidence_hash'] = evidence_hash
            
            # Update chain of custody
            self.update_chain_of_custody(incident_id, collected_evidence)
            
            logger.info(f"System state collected for incident {incident_id}")
            return collected_evidence
        
        except Exception as e:
            logger.error(f"Error collecting system state: {e}")
            return {}
    
    async def collect_log_evidence(self, evidence_path: Path, incident_id: str):
        """Collect relevant log files for forensic analysis"""
        logs_dir = evidence_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Important log files to collect
        log_files = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/kern.log',
            '/var/log/nginx/access.log',
            '/var/log/nginx/error.log',
            '/var/log/intrusion-detection.log',
            '/var/log/hardware-security.log',
            '/var/log/automated-pentest.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    # Copy last 1000 lines of each log
                    dest_file = logs_dir / Path(log_file).name
                    with open(dest_file, 'w') as f:
                        subprocess.run(['tail', '-n', '1000', log_file], stdout=f, stderr=subprocess.DEVNULL)
                except Exception as e:
                    logger.error(f"Error collecting log {log_file}: {e}")
    
    async def collect_memory_dump(self, incident_id: str) -> Optional[str]:
        """Collect memory dump for critical incidents"""
        try:
            evidence_path = self.evidence_dir / f"incident-{incident_id}"
            memory_dump = evidence_path / "memory_dump.raw"
            
            # Use dd to create memory dump (requires root)
            result = subprocess.run([
                'dd', 'if=/dev/mem', f'of={memory_dump}', 'bs=1M', 'count=100'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Memory dump collected: {memory_dump}")
                return str(memory_dump)
            else:
                logger.warning("Memory dump collection failed - insufficient privileges")
                return None
        
        except Exception as e:
            logger.error(f"Error collecting memory dump: {e}")
            return None
    
    async def create_evidence_hash(self, evidence_path: Path) -> str:
        """Create hash of all collected evidence for integrity verification"""
        try:
            # Create tar archive of evidence
            archive_path = evidence_path.parent / f"{evidence_path.name}.tar.gz"
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(evidence_path, arcname=evidence_path.name)
            
            # Calculate SHA256 hash
            sha256_hash = hashlib.sha256()
            with open(archive_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            evidence_hash = sha256_hash.hexdigest()
            
            # Save hash to file
            hash_file = evidence_path / "evidence.sha256"
            with open(hash_file, 'w') as f:
                f.write(f"{evidence_hash}  {archive_path.name}\n")
            
            logger.info(f"Evidence hash created: {evidence_hash}")
            return evidence_hash
        
        except Exception as e:
            logger.error(f"Error creating evidence hash: {e}")
            return ""
    
    def update_chain_of_custody(self, incident_id: str, evidence: Dict[str, str]):
        """Update chain of custody record"""
        custody_record = {
            'incident_id': incident_id,
            'timestamp': datetime.now().isoformat(),
            'collector': 'IncidentResponseSystem',
            'evidence_items': evidence,
            'integrity_hash': evidence.get('evidence_hash', ''),
            'location': str(self.evidence_dir)
        }
        
        self.chain_of_custody.append(custody_record)
        
        # Save to file
        custody_file = self.evidence_dir / 'chain_of_custody.json'
        with open(custody_file, 'w') as f:
            json.dump(self.chain_of_custody, f, indent=2)

class ThreatContainment:
    """Automated threat containment and mitigation"""
    
    def __init__(self):
        self.containment_actions = {
            'MALICIOUS_IP': self.block_malicious_ip,
            'SUSPICIOUS_PROCESS': self.terminate_suspicious_process,
            'COMPROMISED_ACCOUNT': self.disable_compromised_account,
            'MALWARE_DETECTED': self.quarantine_malware,
            'NETWORK_INTRUSION': self.isolate_network_segment,
            'DATA_EXFILTRATION': self.block_data_transfer,
            'PRIVILEGE_ESCALATION': self.revoke_elevated_privileges,
            'BRUTE_FORCE_ATTACK': self.implement_rate_limiting
        }
    
    async def execute_containment(self, incident: SecurityIncident) -> List[ResponseAction]:
        """Execute appropriate containment actions based on incident type"""
        logger.info(f"Executing containment for incident {incident.incident_id}")
        
        actions = []
        containment_function = self.containment_actions.get(incident.incident_type)
        
        if containment_function:
            try:
                action = await containment_function(incident)
                if action:
                    actions.append(action)
            except Exception as e:
                logger.error(f"Error executing containment for {incident.incident_type}: {e}")
        
        # Execute additional containment based on severity
        if incident.severity == 'CRITICAL':
            actions.extend(await self.critical_incident_containment(incident))
        elif incident.severity == 'HIGH':
            actions.extend(await self.high_severity_containment(incident))
        
        return actions
    
    async def block_malicious_ip(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Block malicious IP addresses using iptables"""
        try:
            malicious_ips = incident.indicators.get('malicious_ips', [])
            if isinstance(malicious_ips, str):
                malicious_ips = [malicious_ips]
            
            blocked_ips = []
            for ip in malicious_ips:
                # Add iptables rule to block IP
                result = subprocess.run([
                    'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    blocked_ips.append(ip)
                    logger.info(f"Blocked malicious IP: {ip}")
            
            if blocked_ips:
                # Save iptables rules
                subprocess.run(['iptables-save'], check=False)
                
                return ResponseAction(
                    action_id=f"block_ip_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='IP_BLOCKING',
                    description=f"Blocked malicious IPs: {', '.join(blocked_ips)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully blocked {len(blocked_ips)} IPs",
                    evidence_collected=[f"iptables_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error blocking malicious IP: {e}")
            return None
    
    async def terminate_suspicious_process(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Terminate suspicious processes"""
        try:
            suspicious_pids = incident.indicators.get('suspicious_pids', [])
            if isinstance(suspicious_pids, (str, int)):
                suspicious_pids = [suspicious_pids]
            
            terminated_pids = []
            for pid in suspicious_pids:
                try:
                    # First try graceful termination
                    subprocess.run(['kill', str(pid)], check=True)
                    time.sleep(2)
                    
                    # Check if process still exists
                    result = subprocess.run(['kill', '-0', str(pid)], capture_output=True)
                    if result.returncode == 0:
                        # Force kill if still running
                        subprocess.run(['kill', '-9', str(pid)], check=True)
                    
                    terminated_pids.append(str(pid))
                    logger.info(f"Terminated suspicious process: {pid}")
                
                except subprocess.CalledProcessError:
                    # Process might already be dead
                    continue
            
            if terminated_pids:
                return ResponseAction(
                    action_id=f"terminate_process_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='PROCESS_TERMINATION',
                    description=f"Terminated suspicious processes: {', '.join(terminated_pids)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully terminated {len(terminated_pids)} processes",
                    evidence_collected=[f"process_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error terminating suspicious process: {e}")
            return None
    
    async def disable_compromised_account(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Disable compromised user accounts"""
        try:
            compromised_users = incident.indicators.get('compromised_users', [])
            if isinstance(compromised_users, str):
                compromised_users = [compromised_users]
            
            disabled_users = []
            for username in compromised_users:
                # Disable user account
                result = subprocess.run([
                    'usermod', '-L', username  # Lock account
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    disabled_users.append(username)
                    logger.info(f"Disabled compromised account: {username}")
                    
                    # Also kill any active sessions
                    subprocess.run(['pkill', '-u', username], check=False)
            
            if disabled_users:
                return ResponseAction(
                    action_id=f"disable_account_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='ACCOUNT_DISABLE',
                    description=f"Disabled compromised accounts: {', '.join(disabled_users)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully disabled {len(disabled_users)} accounts",
                    evidence_collected=[f"user_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error disabling compromised account: {e}")
            return None
    
    async def quarantine_malware(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Quarantine detected malware files"""
        try:
            malware_files = incident.indicators.get('malware_files', [])
            if isinstance(malware_files, str):
                malware_files = [malware_files]
            
            quarantine_dir = Path('/var/lib/incident-response/quarantine')
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            quarantined_files = []
            for file_path in malware_files:
                if os.path.exists(file_path):
                    # Move file to quarantine
                    quarantine_path = quarantine_dir / f"{Path(file_path).name}_{int(time.time())}"
                    shutil.move(file_path, quarantine_path)
                    
                    # Set restrictive permissions
                    os.chmod(quarantine_path, 0o000)
                    
                    quarantined_files.append(file_path)
                    logger.info(f"Quarantined malware file: {file_path}")
            
            if quarantined_files:
                return ResponseAction(
                    action_id=f"quarantine_malware_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='MALWARE_QUARANTINE',
                    description=f"Quarantined malware files: {', '.join(quarantined_files)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully quarantined {len(quarantined_files)} files",
                    evidence_collected=[f"quarantine_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error quarantining malware: {e}")
            return None
    
    async def isolate_network_segment(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Isolate compromised network segments"""
        try:
            # This is a simplified implementation - in production, this would
            # integrate with network infrastructure (switches, routers, firewalls)
            
            affected_ips = incident.indicators.get('affected_ips', [])
            if isinstance(affected_ips, str):
                affected_ips = [affected_ips]
            
            isolated_ips = []
            for ip in affected_ips:
                # Block all traffic to/from affected IP
                subprocess.run([
                    'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'
                ], check=False)
                subprocess.run([
                    'iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'DROP'
                ], check=False)
                
                isolated_ips.append(ip)
                logger.info(f"Isolated network segment: {ip}")
            
            if isolated_ips:
                return ResponseAction(
                    action_id=f"isolate_network_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='NETWORK_ISOLATION',
                    description=f"Isolated network segments: {', '.join(isolated_ips)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully isolated {len(isolated_ips)} network segments",
                    evidence_collected=[f"network_isolation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error isolating network segment: {e}")
            return None
    
    async def block_data_transfer(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Block suspicious data transfers"""
        try:
            # Block outbound connections on suspicious ports
            suspicious_ports = incident.indicators.get('suspicious_ports', [])
            if isinstance(suspicious_ports, (str, int)):
                suspicious_ports = [suspicious_ports]
            
            blocked_ports = []
            for port in suspicious_ports:
                subprocess.run([
                    'iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', str(port), '-j', 'DROP'
                ], check=False)
                
                blocked_ports.append(str(port))
                logger.info(f"Blocked outbound traffic on port: {port}")
            
            if blocked_ports:
                return ResponseAction(
                    action_id=f"block_data_transfer_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='DATA_TRANSFER_BLOCK',
                    description=f"Blocked data transfer on ports: {', '.join(blocked_ports)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully blocked {len(blocked_ports)} ports",
                    evidence_collected=[f"blocked_ports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error blocking data transfer: {e}")
            return None
    
    async def revoke_elevated_privileges(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Revoke elevated privileges from compromised accounts"""
        try:
            compromised_users = incident.indicators.get('compromised_users', [])
            if isinstance(compromised_users, str):
                compromised_users = [compromised_users]
            
            revoked_users = []
            for username in compromised_users:
                # Remove from sudo group
                subprocess.run([
                    'deluser', username, 'sudo'
                ], capture_output=True, check=False)
                
                # Remove from admin groups
                for group in ['admin', 'wheel', 'root']:
                    subprocess.run([
                        'deluser', username, group
                    ], capture_output=True, check=False)
                
                revoked_users.append(username)
                logger.info(f"Revoked elevated privileges for: {username}")
            
            if revoked_users:
                return ResponseAction(
                    action_id=f"revoke_privileges_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='PRIVILEGE_REVOCATION',
                    description=f"Revoked privileges for users: {', '.join(revoked_users)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully revoked privileges for {len(revoked_users)} users",
                    evidence_collected=[f"privilege_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error revoking elevated privileges: {e}")
            return None
    
    async def implement_rate_limiting(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Implement rate limiting for brute force attacks"""
        try:
            attacking_ips = incident.indicators.get('attacking_ips', [])
            if isinstance(attacking_ips, str):
                attacking_ips = [attacking_ips]
            
            rate_limited_ips = []
            for ip in attacking_ips:
                # Implement rate limiting using iptables
                subprocess.run([
                    'iptables', '-A', 'INPUT', '-s', ip, '-m', 'limit',
                    '--limit', '1/minute', '--limit-burst', '3', '-j', 'ACCEPT'
                ], check=False)
                subprocess.run([
                    'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'
                ], check=False)
                
                rate_limited_ips.append(ip)
                logger.info(f"Implemented rate limiting for: {ip}")
            
            if rate_limited_ips:
                return ResponseAction(
                    action_id=f"rate_limit_{int(time.time())}",
                    incident_id=incident.incident_id,
                    action_type='RATE_LIMITING',
                    description=f"Implemented rate limiting for IPs: {', '.join(rate_limited_ips)}",
                    timestamp=datetime.now(),
                    status='COMPLETED',
                    result=f"Successfully rate limited {len(rate_limited_ips)} IPs",
                    evidence_collected=[f"rate_limiting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
        
        except Exception as e:
            logger.error(f"Error implementing rate limiting: {e}")
            return None
    
    async def critical_incident_containment(self, incident: SecurityIncident) -> List[ResponseAction]:
        """Additional containment actions for critical incidents"""
        actions = []
        
        try:
            # Create system snapshot
            snapshot_action = await self.create_system_snapshot(incident)
            if snapshot_action:
                actions.append(snapshot_action)
            
            # Enable enhanced monitoring
            monitoring_action = await self.enable_enhanced_monitoring(incident)
            if monitoring_action:
                actions.append(monitoring_action)
            
        except Exception as e:
            logger.error(f"Error in critical incident containment: {e}")
        
        return actions
    
    async def high_severity_containment(self, incident: SecurityIncident) -> List[ResponseAction]:
        """Additional containment actions for high severity incidents"""
        actions = []
        
        try:
            # Increase logging verbosity
            logging_action = await self.increase_logging_verbosity(incident)
            if logging_action:
                actions.append(logging_action)
            
        except Exception as e:
            logger.error(f"Error in high severity containment: {e}")
        
        return actions
    
    async def create_system_snapshot(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Create system snapshot for critical incidents"""
        try:
            snapshot_dir = Path(f'/var/lib/incident-response/snapshots/incident-{incident.incident_id}')
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Create configuration snapshot
            config_files = [
                '/etc/passwd', '/etc/shadow', '/etc/group', '/etc/sudoers',
                '/etc/ssh/sshd_config', '/etc/nginx/nginx.conf'
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, snapshot_dir)
            
            return ResponseAction(
                action_id=f"system_snapshot_{int(time.time())}",
                incident_id=incident.incident_id,
                action_type='SYSTEM_SNAPSHOT',
                description='Created system configuration snapshot',
                timestamp=datetime.now(),
                status='COMPLETED',
                result=f'Snapshot saved to {snapshot_dir}',
                evidence_collected=[str(snapshot_dir)]
            )
        
        except Exception as e:
            logger.error(f"Error creating system snapshot: {e}")
            return None
    
    async def enable_enhanced_monitoring(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Enable enhanced monitoring for critical incidents"""
        try:
            # Enable audit logging
            subprocess.run(['auditctl', '-e', '1'], check=False)
            
            # Enable process accounting
            subprocess.run(['accton', '/var/log/pacct'], check=False)
            
            return ResponseAction(
                action_id=f"enhanced_monitoring_{int(time.time())}",
                incident_id=incident.incident_id,
                action_type='ENHANCED_MONITORING',
                description='Enabled enhanced system monitoring',
                timestamp=datetime.now(),
                status='COMPLETED',
                result='Enhanced monitoring activated',
                evidence_collected=['audit_log', 'process_accounting']
            )
        
        except Exception as e:
            logger.error(f"Error enabling enhanced monitoring: {e}")
            return None
    
    async def increase_logging_verbosity(self, incident: SecurityIncident) -> Optional[ResponseAction]:
        """Increase logging verbosity for high severity incidents"""
        try:
            # Increase SSH logging
            subprocess.run([
                'sed', '-i', 's/LogLevel INFO/LogLevel DEBUG/', '/etc/ssh/sshd_config'
            ], check=False)
            
            # Restart SSH service
            subprocess.run(['systemctl', 'reload', 'ssh'], check=False)
            
            return ResponseAction(
                action_id=f"increase_logging_{int(time.time())}",
                incident_id=incident.incident_id,
                action_type='LOGGING_ENHANCEMENT',
                description='Increased system logging verbosity',
                timestamp=datetime.now(),
                status='COMPLETED',
                result='Logging verbosity increased',
                evidence_collected=['ssh_config_change']
            )
        
        except Exception as e:
            logger.error(f"Error increasing logging verbosity: {e}")
            return None

class NotificationSystem:
    """Incident notification and escalation system"""
    
    def __init__(self):
        self.notification_config = self.load_notification_config()
        self.escalation_rules = self.load_escalation_rules()
    
    def load_notification_config(self) -> Dict:
        """Load notification configuration"""
        config_file = Path('/etc/incident-response/notifications.json')
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading notification config: {e}")
        
        # Default configuration
        return {
            'email': {
                'enabled': False,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'webhook': {
                'enabled': False,
                'url': '',
                'headers': {}
            },
            'syslog': {
                'enabled': True,
                'facility': 'local0'
            }
        }
    
    def load_escalation_rules(self) -> Dict:
        """Load escalation rules"""
        return {
            'CRITICAL': {
                'immediate': ['email', 'webhook', 'syslog'],
                'escalation_time': 300,  # 5 minutes
                'escalation_actions': ['email_manager', 'call_oncall']
            },
            'HIGH': {
                'immediate': ['email', 'syslog'],
                'escalation_time': 900,  # 15 minutes
                'escalation_actions': ['email_manager']
            },
            'MEDIUM': {
                'immediate': ['syslog'],
                'escalation_time': 3600,  # 1 hour
                'escalation_actions': ['email']
            },
            'LOW': {
                'immediate': ['syslog'],
                'escalation_time': 86400,  # 24 hours
                'escalation_actions': []
            }
        }
    
    async def send_incident_notification(self, incident: SecurityIncident):
        """Send incident notification based on severity"""
        logger.info(f"Sending notification for incident {incident.incident_id}")
        
        escalation_rule = self.escalation_rules.get(incident.severity, self.escalation_rules['LOW'])
        
        for notification_type in escalation_rule['immediate']:
            try:
                if notification_type == 'email':
                    await self.send_email_notification(incident)
                elif notification_type == 'webhook':
                    await self.send_webhook_notification(incident)
                elif notification_type == 'syslog':
                    await self.send_syslog_notification(incident)
            except Exception as e:
                logger.error(f"Error sending {notification_type} notification: {e}")
    
    async def send_email_notification(self, incident: SecurityIncident):
        """Send email notification"""
        if not self.notification_config['email']['enabled']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.notification_config['email']['username']
            msg['To'] = ', '.join(self.notification_config['email']['recipients'])
            msg['Subject'] = f"Security Incident Alert - {incident.severity} - {incident.incident_id}"
            
            body = f"""
Security Incident Detected

Incident ID: {incident.incident_id}
Severity: {incident.severity}
Type: {incident.incident_type}
Timestamp: {incident.timestamp}
Source: {incident.source}
Description: {incident.description}

Affected Systems: {', '.join(incident.affected_systems)}
Status: {incident.status}

Response Actions Taken:
{chr(10).join(f'- {action}' for action in incident.response_actions)}

This is an automated alert from the Security Incident Response System.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.notification_config['email']['smtp_server'],
                self.notification_config['email']['smtp_port']
            )
            server.starttls()
            server.login(
                self.notification_config['email']['username'],
                self.notification_config['email']['password']
            )
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for incident {incident.incident_id}")
        
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def send_webhook_notification(self, incident: SecurityIncident):
        """Send webhook notification"""
        if not self.notification_config['webhook']['enabled']:
            return
        
        try:
            import requests
            
            payload = {
                'incident_id': incident.incident_id,
                'severity': incident.severity,
                'incident_type': incident.incident_type,
                'timestamp': incident.timestamp.isoformat(),
                'source': incident.source,
                'description': incident.description,
                'affected_systems': incident.affected_systems,
                'status': incident.status,
                'response_actions': incident.response_actions
            }
            
            response = requests.post(
                self.notification_config['webhook']['url'],
                json=payload,
                headers=self.notification_config['webhook']['headers'],
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook notification sent for incident {incident.incident_id}")
            else:
                logger.error(f"Webhook notification failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def send_syslog_notification(self, incident: SecurityIncident):
        """Send syslog notification"""
        try:
            import syslog
            
            syslog.openlog("IncidentResponse", syslog.LOG_PID, syslog.LOG_LOCAL0)
            
            priority = syslog.LOG_CRIT if incident.severity == 'CRITICAL' else \
                      syslog.LOG_ERR if incident.severity == 'HIGH' else \
                      syslog.LOG_WARNING if incident.severity == 'MEDIUM' else \
                      syslog.LOG_INFO
            
            message = f"Security Incident: {incident.incident_id} | {incident.severity} | {incident.incident_type} | {incident.description}"
            
            syslog.syslog(priority, message)
            syslog.closelog()
            
            logger.info(f"Syslog notification sent for incident {incident.incident_id}")
        
        except Exception as e:
            logger.error(f"Error sending syslog notification: {e}")

class IncidentResponseSystem:
    """Main incident response coordination system"""
    
    def __init__(self):
        self.forensic_collector = ForensicCollector()
        self.threat_containment = ThreatContainment()
        self.notification_system = NotificationSystem()
        self.active_incidents: Dict[str, SecurityIncident] = {}
        self.response_actions: List[ResponseAction] = []
        self.incident_counter = 0
    
    async def handle_security_event(self, event_data: Dict) -> str:
        """Handle incoming security event and create incident if necessary"""
        try:
            # Generate incident ID
            self.incident_counter += 1
            incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{self.incident_counter:04d}"
            
            # Create security incident
            incident = SecurityIncident(
                incident_id=incident_id,
                timestamp=datetime.now(),
                severity=event_data.get('severity', 'MEDIUM'),
                incident_type=event_data.get('event_type', 'UNKNOWN'),
                source=event_data.get('source', 'UNKNOWN'),
                description=event_data.get('description', 'Security event detected'),
                affected_systems=event_data.get('affected_systems', ['localhost']),
                indicators=event_data.get('indicators', {}),
                status='DETECTED',
                response_actions=[],
                forensic_data={}
            )
            
            # Add to active incidents
            self.active_incidents[incident_id] = incident
            
            # Start incident response workflow
            await self.execute_incident_response(incident)
            
            logger.info(f"Security incident created and handled: {incident_id}")
            return incident_id
        
        except Exception as e:
            logger.error(f"Error handling security event: {e}")
            return ""
    
    async def execute_incident_response(self, incident: SecurityIncident):
        """Execute complete incident response workflow"""
        try:
            logger.info(f"Executing incident response for {incident.incident_id}")
            
            # Phase 1: Immediate containment
            incident.status = 'INVESTIGATING'
            containment_actions = await self.threat_containment.execute_containment(incident)
            self.response_actions.extend(containment_actions)
            incident.response_actions.extend([action.description for action in containment_actions])
            
            # Phase 2: Forensic data collection
            if incident.severity in ['HIGH', 'CRITICAL']:
                forensic_data = await self.forensic_collector.collect_system_state(incident.incident_id)
                incident.forensic_data.update(forensic_data)
                
                # Collect memory dump for critical incidents
                if incident.severity == 'CRITICAL':
                    memory_dump = await self.forensic_collector.collect_memory_dump(incident.incident_id)
                    if memory_dump:
                        incident.forensic_data['memory_dump'] = memory_dump
            
            # Phase 3: Notification and escalation
            await self.notification_system.send_incident_notification(incident)
            
            # Phase 4: Update incident status
            if containment_actions:
                incident.status = 'CONTAINED'
            
            # Save incident data
            await self.save_incident_data(incident)
            
            logger.info(f"Incident response completed for {incident.incident_id}")
        
        except Exception as e:
            logger.error(f"Error executing incident response: {e}")
            incident.status = 'ERROR'
    
    async def save_incident_data(self, incident: SecurityIncident):
        """Save incident data to persistent storage"""
        try:
            incidents_dir = Path('/var/lib/incident-response/incidents')
            incidents_dir.mkdir(parents=True, exist_ok=True)
            
            incident_file = incidents_dir / f"{incident.incident_id}.json"
            
            incident_data = asdict(incident)
            incident_data['timestamp'] = incident.timestamp.isoformat()
            
            with open(incident_file, 'w') as f:
                json.dump(incident_data, f, indent=2)
            
            # Also append to incidents log
            incidents_log = Path('/var/log/security-incidents.json')
            with open(incidents_log, 'a') as f:
                f.write(json.dumps(incident_data) + '\n')
            
            logger.info(f"Incident data saved: {incident.incident_id}")
        
        except Exception as e:
            logger.error(f"Error saving incident data: {e}")
    
    def get_incident_status(self, incident_id: str) -> Optional[Dict]:
        """Get status of specific incident"""
        incident = self.active_incidents.get(incident_id)
        if incident:
            return asdict(incident)
        return None
    
    def get_system_status(self) -> Dict:
        """Get overall incident response system status"""
        active_count = len(self.active_incidents)
        critical_count = len([i for i in self.active_incidents.values() if i.severity == 'CRITICAL'])
        high_count = len([i for i in self.active_incidents.values() if i.severity == 'HIGH'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_incidents': active_count,
            'critical_incidents': critical_count,
            'high_severity_incidents': high_count,
            'total_response_actions': len(self.response_actions),
            'system_status': 'CRITICAL' if critical_count > 0 else 'WARNING' if high_count > 0 else 'NORMAL'
        }

async def main():
    """Main entry point for incident response system"""
    response_system = IncidentResponseSystem()
    
    # Example: Handle a test security event
    test_event = {
        'severity': 'HIGH',
        'event_type': 'MALICIOUS_IP',
        'source': 'intrusion_detection',
        'description': 'Malicious IP detected attempting brute force attack',
        'affected_systems': ['web-server'],
        'indicators': {
            'malicious_ips': ['192.168.1.100'],
            'attack_type': 'brute_force',
            'target_service': 'ssh'
        }
    }
    
    incident_id = await response_system.handle_security_event(test_event)
    
    if incident_id:
        logger.info(f"Test incident handled: {incident_id}")
        
        # Show system status
        status = response_system.get_system_status()
        print("\n🚨 Incident Response System Status")
        print("=" * 40)
        print(f"Active incidents: {status['active_incidents']}")
        print(f"Critical incidents: {status['critical_incidents']}")
        print(f"High severity incidents: {status['high_severity_incidents']}")
        print(f"Total response actions: {status['total_response_actions']}")
        print(f"System status: {status['system_status']}")

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs('/var/lib/incident-response', exist_ok=True)
    os.makedirs('/var/log', exist_ok=True)
    os.makedirs('/etc/incident-response', exist_ok=True)
    
    # Run the system
    asyncio.run(main())