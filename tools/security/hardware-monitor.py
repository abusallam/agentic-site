#!/usr/bin/env python3
"""
Hardware Security Monitoring System
Monitors hardware integrity, detects tampering, and validates secure boot
"""

import asyncio
import hashlib
import json
import logging
import os
import platform
import psutil
import re
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/hardware-security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HardwareEvent:
    """Hardware security event data structure"""
    timestamp: datetime
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    component: str
    description: str
    details: Dict
    risk_score: int  # 0-100

@dataclass
class HardwareComponent:
    """Hardware component information"""
    component_type: str
    identifier: str
    model: str
    serial: Optional[str]
    firmware_version: Optional[str]
    checksum: Optional[str]
    last_seen: datetime

class SecureBootValidator:
    """Secure boot and boot integrity validation"""
    
    def __init__(self):
        self.boot_measurements: Dict[str, str] = {}
        self.trusted_boot_hashes: Set[str] = set()
        self.load_trusted_hashes()
    
    def load_trusted_hashes(self):
        """Load trusted boot component hashes"""
        try:
            trusted_file = Path('/etc/security/trusted-boot-hashes.txt')
            if trusted_file.exists():
                with open(trusted_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.trusted_boot_hashes.add(line)
            
            logger.info(f"Loaded {len(self.trusted_boot_hashes)} trusted boot hashes")
        except Exception as e:
            logger.error(f"Error loading trusted boot hashes: {e}")
    
    def check_secure_boot_status(self) -> HardwareEvent:
        """Check if secure boot is enabled"""
        try:
            # Check UEFI secure boot status
            if os.path.exists('/sys/firmware/efi'):
                # UEFI system
                secure_boot_file = '/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c'
                if os.path.exists(secure_boot_file):
                    with open(secure_boot_file, 'rb') as f:
                        data = f.read()
                        # Secure boot enabled if last byte is 1
                        secure_boot_enabled = data[-1] == 1
                else:
                    secure_boot_enabled = False
                
                severity = 'LOW' if secure_boot_enabled else 'HIGH'
                description = f"Secure Boot: {'Enabled' if secure_boot_enabled else 'Disabled'}"
                risk_score = 10 if secure_boot_enabled else 70
                
            else:
                # Legacy BIOS system
                secure_boot_enabled = False
                severity = 'MEDIUM'
                description = "Legacy BIOS system - Secure Boot not available"
                risk_score = 40
            
            return HardwareEvent(
                timestamp=datetime.now(),
                event_type='SECURE_BOOT_CHECK',
                severity=severity,
                component='UEFI/BIOS',
                description=description,
                details={'secure_boot_enabled': secure_boot_enabled, 'system_type': 'UEFI' if os.path.exists('/sys/firmware/efi') else 'BIOS'},
                risk_score=risk_score
            )
        
        except Exception as e:
            logger.error(f"Error checking secure boot status: {e}")
            return HardwareEvent(
                timestamp=datetime.now(),
                event_type='SECURE_BOOT_ERROR',
                severity='MEDIUM',
                component='UEFI/BIOS',
                description=f"Error checking secure boot: {e}",
                details={'error': str(e)},
                risk_score=50
            )
    
    def validate_boot_integrity(self) -> List[HardwareEvent]:
        """Validate boot component integrity"""
        events = []
        
        try:
            # Check kernel integrity
            kernel_path = f"/boot/vmlinuz-{platform.release()}"
            if os.path.exists(kernel_path):
                kernel_hash = self.calculate_file_hash(kernel_path)
                
                if kernel_hash in self.trusted_boot_hashes:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='KERNEL_INTEGRITY',
                        severity='LOW',
                        component='KERNEL',
                        description='Kernel integrity verified',
                        details={'kernel_path': kernel_path, 'hash': kernel_hash},
                        risk_score=5
                    ))
                else:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='KERNEL_INTEGRITY',
                        severity='CRITICAL',
                        component='KERNEL',
                        description='Kernel integrity check failed - unknown hash',
                        details={'kernel_path': kernel_path, 'hash': kernel_hash},
                        risk_score=95
                    ))
            
            # Check initrd integrity
            initrd_path = f"/boot/initrd.img-{platform.release()}"
            if os.path.exists(initrd_path):
                initrd_hash = self.calculate_file_hash(initrd_path)
                
                if initrd_hash in self.trusted_boot_hashes:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='INITRD_INTEGRITY',
                        severity='LOW',
                        component='INITRD',
                        description='Initrd integrity verified',
                        details={'initrd_path': initrd_path, 'hash': initrd_hash},
                        risk_score=5
                    ))
                else:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='INITRD_INTEGRITY',
                        severity='HIGH',
                        component='INITRD',
                        description='Initrd integrity check failed - unknown hash',
                        details={'initrd_path': initrd_path, 'hash': initrd_hash},
                        risk_score=80
                    ))
        
        except Exception as e:
            logger.error(f"Error validating boot integrity: {e}")
            events.append(HardwareEvent(
                timestamp=datetime.now(),
                event_type='BOOT_INTEGRITY_ERROR',
                severity='MEDIUM',
                component='BOOT',
                description=f"Error validating boot integrity: {e}",
                details={'error': str(e)},
                risk_score=50
            ))
        
        return events
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

class RootkitDetector:
    """Rootkit and malware detection"""
    
    def __init__(self):
        self.known_rootkit_signatures: Set[str] = set()
        self.system_baselines: Dict[str, str] = {}
        self.load_signatures()
        self.create_baselines()
    
    def load_signatures(self):
        """Load known rootkit signatures"""
        try:
            signatures_file = Path('/etc/security/rootkit-signatures.txt')
            if signatures_file.exists():
                with open(signatures_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.known_rootkit_signatures.add(line)
            
            logger.info(f"Loaded {len(self.known_rootkit_signatures)} rootkit signatures")
        except Exception as e:
            logger.error(f"Error loading rootkit signatures: {e}")
    
    def create_baselines(self):
        """Create system baselines for comparison"""
        try:
            # Baseline critical system files
            critical_files = [
                '/bin/ls', '/bin/ps', '/bin/netstat', '/bin/ss',
                '/usr/bin/who', '/usr/bin/w', '/usr/bin/last',
                '/sbin/ifconfig', '/bin/login'
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    file_hash = self.calculate_file_hash(file_path)
                    self.system_baselines[file_path] = file_hash
            
            logger.info(f"Created baselines for {len(self.system_baselines)} critical files")
        except Exception as e:
            logger.error(f"Error creating system baselines: {e}")
    
    def scan_for_rootkits(self) -> List[HardwareEvent]:
        """Scan system for rootkit indicators"""
        events = []
        
        try:
            # Check for modified system binaries
            events.extend(self.check_system_binaries())
            
            # Check for hidden processes
            events.extend(self.check_hidden_processes())
            
            # Check for suspicious network connections
            events.extend(self.check_suspicious_connections())
            
            # Check for kernel module anomalies
            events.extend(self.check_kernel_modules())
            
            # Run external rootkit scanners
            events.extend(self.run_external_scanners())
        
        except Exception as e:
            logger.error(f"Error during rootkit scan: {e}")
            events.append(HardwareEvent(
                timestamp=datetime.now(),
                event_type='ROOTKIT_SCAN_ERROR',
                severity='MEDIUM',
                component='SCANNER',
                description=f"Error during rootkit scan: {e}",
                details={'error': str(e)},
                risk_score=50
            ))
        
        return events
    
    def check_system_binaries(self) -> List[HardwareEvent]:
        """Check system binaries for modifications"""
        events = []
        
        for file_path, baseline_hash in self.system_baselines.items():
            if os.path.exists(file_path):
                current_hash = self.calculate_file_hash(file_path)
                if current_hash != baseline_hash:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='BINARY_MODIFICATION',
                        severity='CRITICAL',
                        component='SYSTEM_BINARY',
                        description=f'System binary modified: {file_path}',
                        details={
                            'file_path': file_path,
                            'baseline_hash': baseline_hash,
                            'current_hash': current_hash
                        },
                        risk_score=90
                    ))
        
        return events
    
    def check_hidden_processes(self) -> List[HardwareEvent]:
        """Check for hidden processes (rootkit indicator)"""
        events = []
        
        try:
            # Get process list from /proc
            proc_pids = set()
            for item in os.listdir('/proc'):
                if item.isdigit():
                    proc_pids.add(int(item))
            
            # Get process list from ps
            ps_result = subprocess.run(['ps', 'axo', 'pid'], capture_output=True, text=True)
            ps_pids = set()
            if ps_result.returncode == 0:
                for line in ps_result.stdout.strip().split('\n')[1:]:  # Skip header
                    try:
                        ps_pids.add(int(line.strip()))
                    except ValueError:
                        continue
            
            # Find discrepancies
            hidden_pids = proc_pids - ps_pids
            if hidden_pids:
                events.append(HardwareEvent(
                    timestamp=datetime.now(),
                    event_type='HIDDEN_PROCESSES',
                    severity='HIGH',
                    component='PROCESS_MONITOR',
                    description=f'Hidden processes detected: {len(hidden_pids)} processes',
                    details={'hidden_pids': list(hidden_pids)},
                    risk_score=80
                ))
        
        except Exception as e:
            logger.error(f"Error checking hidden processes: {e}")
        
        return events
    
    def check_suspicious_connections(self) -> List[HardwareEvent]:
        """Check for suspicious network connections"""
        events = []
        
        try:
            # Look for connections to unusual ports or IPs
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    # Check for connections to suspicious ports
                    suspicious_ports = [1337, 31337, 4444, 5555, 6666, 7777, 8888, 9999]
                    if remote_port in suspicious_ports:
                        events.append(HardwareEvent(
                            timestamp=datetime.now(),
                            event_type='SUSPICIOUS_CONNECTION',
                            severity='HIGH',
                            component='NETWORK',
                            description=f'Connection to suspicious port: {remote_ip}:{remote_port}',
                            details={'remote_ip': remote_ip, 'remote_port': remote_port},
                            risk_score=75
                        ))
        
        except Exception as e:
            logger.error(f"Error checking suspicious connections: {e}")
        
        return events
    
    def check_kernel_modules(self) -> List[HardwareEvent]:
        """Check for suspicious kernel modules"""
        events = []
        
        try:
            # Get loaded kernel modules
            with open('/proc/modules', 'r') as f:
                modules = f.readlines()
            
            suspicious_module_names = [
                'rootkit', 'backdoor', 'keylogger', 'stealth',
                'hide', 'invisible', 'ghost', 'phantom'
            ]
            
            for module_line in modules:
                module_name = module_line.split()[0]
                
                # Check for suspicious names
                for suspicious in suspicious_module_names:
                    if suspicious in module_name.lower():
                        events.append(HardwareEvent(
                            timestamp=datetime.now(),
                            event_type='SUSPICIOUS_MODULE',
                            severity='HIGH',
                            component='KERNEL',
                            description=f'Suspicious kernel module: {module_name}',
                            details={'module_name': module_name, 'module_line': module_line.strip()},
                            risk_score=80
                        ))
        
        except Exception as e:
            logger.error(f"Error checking kernel modules: {e}")
        
        return events
    
    def run_external_scanners(self) -> List[HardwareEvent]:
        """Run external rootkit scanners"""
        events = []
        
        try:
            # Run rkhunter if available
            if subprocess.run(['which', 'rkhunter'], capture_output=True).returncode == 0:
                result = subprocess.run(['rkhunter', '--check', '--sk'], 
                                      capture_output=True, text=True, timeout=300)
                
                if 'Warning' in result.stdout or 'Infected' in result.stdout:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='RKHUNTER_WARNING',
                        severity='HIGH',
                        component='ROOTKIT_SCANNER',
                        description='rkhunter detected potential threats',
                        details={'scanner_output': result.stdout[:1000]},  # Limit output size
                        risk_score=75
                    ))
            
            # Run chkrootkit if available
            if subprocess.run(['which', 'chkrootkit'], capture_output=True).returncode == 0:
                result = subprocess.run(['chkrootkit'], capture_output=True, text=True, timeout=300)
                
                if 'INFECTED' in result.stdout or 'Checking' not in result.stdout:
                    events.append(HardwareEvent(
                        timestamp=datetime.now(),
                        event_type='CHKROOTKIT_WARNING',
                        severity='HIGH',
                        component='ROOTKIT_SCANNER',
                        description='chkrootkit detected potential threats',
                        details={'scanner_output': result.stdout[:1000]},
                        risk_score=75
                    ))
        
        except subprocess.TimeoutExpired:
            logger.warning("External scanner timed out")
        except Exception as e:
            logger.error(f"Error running external scanners: {e}")
        
        return events
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

class HardwareInventory:
    """Hardware inventory and change detection"""
    
    def __init__(self):
        self.inventory_file = Path('/var/lib/hardware-inventory.json')
        self.current_inventory: Dict[str, HardwareComponent] = {}
        self.baseline_inventory: Dict[str, HardwareComponent] = {}
        self.load_baseline()
    
    def load_baseline(self):
        """Load baseline hardware inventory"""
        try:
            if self.inventory_file.exists():
                with open(self.inventory_file, 'r') as f:
                    data = json.load(f)
                    for key, item in data.items():
                        self.baseline_inventory[key] = HardwareComponent(
                            component_type=item['component_type'],
                            identifier=item['identifier'],
                            model=item['model'],
                            serial=item.get('serial'),
                            firmware_version=item.get('firmware_version'),
                            checksum=item.get('checksum'),
                            last_seen=datetime.fromisoformat(item['last_seen'])
                        )
                
                logger.info(f"Loaded baseline inventory with {len(self.baseline_inventory)} components")
        except Exception as e:
            logger.error(f"Error loading baseline inventory: {e}")
    
    def scan_hardware(self) -> Dict[str, HardwareComponent]:
        """Scan current hardware configuration"""
        inventory = {}
        
        try:
            # CPU information
            cpu_info = self.get_cpu_info()
            if cpu_info:
                inventory['cpu'] = cpu_info
            
            # Memory information
            memory_info = self.get_memory_info()
            if memory_info:
                inventory['memory'] = memory_info
            
            # Disk information
            disk_info = self.get_disk_info()
            inventory.update(disk_info)
            
            # Network interfaces
            network_info = self.get_network_info()
            inventory.update(network_info)
            
            # USB devices
            usb_info = self.get_usb_info()
            inventory.update(usb_info)
            
            # PCI devices
            pci_info = self.get_pci_info()
            inventory.update(pci_info)
        
        except Exception as e:
            logger.error(f"Error scanning hardware: {e}")
        
        self.current_inventory = inventory
        return inventory
    
    def get_cpu_info(self) -> Optional[HardwareComponent]:
        """Get CPU information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            
            model_match = re.search(r'model name\s*:\s*(.+)', cpuinfo)
            model = model_match.group(1).strip() if model_match else 'Unknown'
            
            return HardwareComponent(
                component_type='CPU',
                identifier='cpu0',
                model=model,
                serial=None,
                firmware_version=None,
                checksum=hashlib.sha256(cpuinfo.encode()).hexdigest()[:16],
                last_seen=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return None
    
    def get_memory_info(self) -> Optional[HardwareComponent]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            
            return HardwareComponent(
                component_type='MEMORY',
                identifier='memory0',
                model=f'{memory.total // (1024**3)}GB RAM',
                serial=None,
                firmware_version=None,
                checksum=hashlib.sha256(str(memory.total).encode()).hexdigest()[:16],
                last_seen=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return None
    
    def get_disk_info(self) -> Dict[str, HardwareComponent]:
        """Get disk information"""
        disks = {}
        
        try:
            disk_partitions = psutil.disk_partitions()
            for partition in disk_partitions:
                if partition.device.startswith('/dev/'):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        disks[f"disk_{partition.device.replace('/', '_')}"] = HardwareComponent(
                            component_type='DISK',
                            identifier=partition.device,
                            model=f'{usage.total // (1024**3)}GB {partition.fstype}',
                            serial=None,
                            firmware_version=None,
                            checksum=hashlib.sha256(f"{partition.device}{usage.total}".encode()).hexdigest()[:16],
                            last_seen=datetime.now()
                        )
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
        
        return disks
    
    def get_network_info(self) -> Dict[str, HardwareComponent]:
        """Get network interface information"""
        interfaces = {}
        
        try:
            net_if_addrs = psutil.net_if_addrs()
            for interface, addrs in net_if_addrs.items():
                if interface != 'lo':  # Skip loopback
                    mac_addr = None
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK:
                            mac_addr = addr.address
                            break
                    
                    if mac_addr:
                        interfaces[f"net_{interface}"] = HardwareComponent(
                            component_type='NETWORK',
                            identifier=interface,
                            model=f'Network Interface {interface}',
                            serial=mac_addr,
                            firmware_version=None,
                            checksum=hashlib.sha256(mac_addr.encode()).hexdigest()[:16],
                            last_seen=datetime.now()
                        )
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
        
        return interfaces
    
    def get_usb_info(self) -> Dict[str, HardwareComponent]:
        """Get USB device information"""
        usb_devices = {}
        
        try:
            # Try to read USB device information
            if os.path.exists('/sys/bus/usb/devices'):
                for device_dir in os.listdir('/sys/bus/usb/devices'):
                    device_path = f'/sys/bus/usb/devices/{device_dir}'
                    
                    try:
                        # Read vendor and product IDs
                        vendor_file = f'{device_path}/idVendor'
                        product_file = f'{device_path}/idProduct'
                        
                        if os.path.exists(vendor_file) and os.path.exists(product_file):
                            with open(vendor_file, 'r') as f:
                                vendor_id = f.read().strip()
                            with open(product_file, 'r') as f:
                                product_id = f.read().strip()
                            
                            device_id = f"{vendor_id}:{product_id}"
                            
                            usb_devices[f"usb_{device_dir}"] = HardwareComponent(
                                component_type='USB',
                                identifier=device_dir,
                                model=f'USB Device {device_id}',
                                serial=None,
                                firmware_version=None,
                                checksum=hashlib.sha256(device_id.encode()).hexdigest()[:16],
                                last_seen=datetime.now()
                            )
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error getting USB info: {e}")
        
        return usb_devices
    
    def get_pci_info(self) -> Dict[str, HardwareComponent]:
        """Get PCI device information"""
        pci_devices = {}
        
        try:
            # Use lspci if available
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            pci_id = parts[0]
                            description = parts[1]
                            
                            pci_devices[f"pci_{pci_id.replace(':', '_').replace('.', '_')}"] = HardwareComponent(
                                component_type='PCI',
                                identifier=pci_id,
                                model=description,
                                serial=None,
                                firmware_version=None,
                                checksum=hashlib.sha256(line.encode()).hexdigest()[:16],
                                last_seen=datetime.now()
                            )
        except Exception as e:
            logger.error(f"Error getting PCI info: {e}")
        
        return pci_devices
    
    def detect_changes(self) -> List[HardwareEvent]:
        """Detect hardware changes from baseline"""
        events = []
        
        current = self.scan_hardware()
        
        # Check for removed components
        for key, baseline_component in self.baseline_inventory.items():
            if key not in current:
                events.append(HardwareEvent(
                    timestamp=datetime.now(),
                    event_type='HARDWARE_REMOVED',
                    severity='HIGH',
                    component=baseline_component.component_type,
                    description=f'Hardware component removed: {baseline_component.identifier}',
                    details=asdict(baseline_component),
                    risk_score=70
                ))
        
        # Check for new components
        for key, current_component in current.items():
            if key not in self.baseline_inventory:
                events.append(HardwareEvent(
                    timestamp=datetime.now(),
                    event_type='HARDWARE_ADDED',
                    severity='MEDIUM',
                    component=current_component.component_type,
                    description=f'New hardware component detected: {current_component.identifier}',
                    details=asdict(current_component),
                    risk_score=50
                ))
        
        # Check for modified components
        for key in set(current.keys()) & set(self.baseline_inventory.keys()):
            current_comp = current[key]
            baseline_comp = self.baseline_inventory[key]
            
            if current_comp.checksum != baseline_comp.checksum:
                events.append(HardwareEvent(
                    timestamp=datetime.now(),
                    event_type='HARDWARE_MODIFIED',
                    severity='HIGH',
                    component=current_comp.component_type,
                    description=f'Hardware component modified: {current_comp.identifier}',
                    details={
                        'current': asdict(current_comp),
                        'baseline': asdict(baseline_comp)
                    },
                    risk_score=75
                ))
        
        return events
    
    def save_inventory(self):
        """Save current inventory as baseline"""
        try:
            self.inventory_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for key, component in self.current_inventory.items():
                data[key] = asdict(component)
                data[key]['last_seen'] = component.last_seen.isoformat()
            
            with open(self.inventory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved hardware inventory with {len(data)} components")
        except Exception as e:
            logger.error(f"Error saving inventory: {e}")

class HardwareSecurityMonitor:
    """Main hardware security monitoring system"""
    
    def __init__(self):
        self.secure_boot_validator = SecureBootValidator()
        self.rootkit_detector = RootkitDetector()
        self.hardware_inventory = HardwareInventory()
        self.events_queue: List[HardwareEvent] = []
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start hardware security monitoring"""
        logger.info("Starting hardware security monitoring...")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                events = []
                
                # Secure boot validation
                events.append(self.secure_boot_validator.check_secure_boot_status())
                events.extend(self.secure_boot_validator.validate_boot_integrity())
                
                # Rootkit detection
                events.extend(self.rootkit_detector.scan_for_rootkits())
                
                # Hardware change detection
                events.extend(self.hardware_inventory.detect_changes())
                
                # Process events
                for event in events:
                    await self.process_event(event)
                
                # Save current inventory
                self.hardware_inventory.save_inventory()
                
                # Wait before next scan
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def process_event(self, event: HardwareEvent):
        """Process hardware security event"""
        self.events_queue.append(event)
        
        # Log event
        logger.info(f"Hardware event: {event.event_type} - {event.description}")
        
        # Save event
        await self.save_event(event)
        
        # Trigger response for high-risk events
        if event.risk_score >= 70:
            await self.trigger_response(event)
    
    async def save_event(self, event: HardwareEvent):
        """Save hardware security event"""
        try:
            events_file = Path('/var/log/hardware-security-events.json')
            events_file.parent.mkdir(parents=True, exist_ok=True)
            
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            
            with open(events_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
        
        except Exception as e:
            logger.error(f"Error saving hardware event: {e}")
    
    async def trigger_response(self, event: HardwareEvent):
        """Trigger response to high-risk hardware events"""
        logger.warning(f"High-risk hardware event: {event.description}")
        
        try:
            # Create alert
            alert = {
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity,
                'event_type': event.event_type,
                'component': event.component,
                'description': event.description,
                'risk_score': event.risk_score,
                'response_required': True
            }
            
            # Save alert
            alerts_file = Path('/var/log/hardware-security-alerts.json')
            with open(alerts_file, 'a') as f:
                f.write(json.dumps(alert) + '\n')
            
            logger.info(f"Alert created for hardware event: {event.event_type}")
        
        except Exception as e:
            logger.error(f"Error triggering response: {e}")
    
    def stop_monitoring(self):
        """Stop hardware security monitoring"""
        logger.info("Stopping hardware security monitoring...")
        self.monitoring_active = False
    
    def get_status(self) -> Dict:
        """Get hardware security status"""
        recent_events = [e for e in self.events_queue 
                        if (datetime.now() - e.timestamp).seconds < 3600]
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_active': self.monitoring_active,
            'total_events': len(self.events_queue),
            'recent_events': len(recent_events),
            'severity_counts': defaultdict(int),
            'component_counts': defaultdict(int),
            'security_status': 'SECURE'
        }
        
        for event in recent_events:
            status['severity_counts'][event.severity] += 1
            status['component_counts'][event.component] += 1
        
        # Determine security status
        if status['severity_counts']['CRITICAL'] > 0:
            status['security_status'] = 'CRITICAL'
        elif status['severity_counts']['HIGH'] > 0:
            status['security_status'] = 'WARNING'
        elif status['severity_counts']['MEDIUM'] > 5:
            status['security_status'] = 'CAUTION'
        
        return status

async def main():
    """Main entry point"""
    monitor = HardwareSecurityMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Hardware security monitor stopped by user")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Fatal error in hardware security monitor: {e}")

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs('/var/log', exist_ok=True)
    os.makedirs('/var/lib', exist_ok=True)
    os.makedirs('/etc/security', exist_ok=True)
    
    # Run the monitor
    asyncio.run(main())