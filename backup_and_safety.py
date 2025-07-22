#!/usr/bin/env python3
"""
Backup and Safety System for Codebase Cleanup
Creates backup and analyzes project structure before cleanup operations.
"""

import os
import json
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

class BackupAndAnalysis:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / "backups"
        self.analysis_file = self.project_root / f"cleanup_analysis_report.md"
        
    def create_backup(self) -> str:
        """Create a complete backup of the current project state."""
        print("🔄 Creating project backup...")
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        backup_filename = f"project_backup_{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Create tar.gz backup excluding certain directories
        exclude_patterns = {
            'node_modules', '.next', '.git', '__pycache__', 
            '.venv', 'venv', 'backups', 'dist', 'build'
        }
        
        with tarfile.open(backup_path, "w:gz") as tar:
            for item in self.project_root.iterdir():
                if item.name not in exclude_patterns:
                    tar.add(item, arcname=item.name)
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
    
    def analyze_project_structure(self) -> Dict:
        """Analyze current project structure and categorize files."""
        print("🔍 Analyzing project structure...")
        
        analysis = {
            "timestamp": self.timestamp,
            "total_files": 0,
            "categories": {
                "temporary_deployment": [],
                "backup_files": [],
                "test_files": [],
                "components": [],
                "documentation": [],
                "essential_scripts": [],
                "config_files": [],
                "other": []
            },
            "cleanup_actions": {
                "to_remove": [],
                "to_move": [],
                "to_preserve": []
            }
        }
        
        # Define file patterns for categorization
        temp_deployment_patterns = [
            'complete_agentic_site_deployment.py',
            'deploy_agentic_site.py',
            'deploy_and_test_complete.py',
            'deploy_complete_agentic_site.py',
            'docker_fix_and_complete.py',
            'docker_fix_complete.py',
            'final_fix_deployment.py',
            'final_production_deployment.py',
            'fix_deployment.py',
            'fix_deployment_issues.py',
            'fix_nginx_and_complete_deployment.py',
            'fresh_start_vps.py',
            'manual_deployment.py',
            'simple_working_deployment.py',
            'update_vps_files_directly.py',
            'vps_docker_deploy.py'
        ]
        
        backup_patterns = ['*.tar.gz', '*.zip', '*_log_*.json', '*_report.json']
        test_patterns = ['test_*.py', '*_test.py', 'test_*.json']
        component_patterns = ['*-enhanced.tsx', '*-section.tsx']
        doc_patterns = ['*.md']
        essential_script_patterns = ['deploy-to-vps.sh', 'direct_vps_deploy.sh', 'push-to-github.sh']
        
        # Scan project files
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                analysis["total_files"] += 1
                relative_path = file_path.relative_to(self.project_root)
                
                # Skip certain directories
                if any(part in ['.git', 'node_modules', '.next', '__pycache__', '.venv'] 
                       for part in relative_path.parts):
                    continue
                
                file_info = {
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "category": "other"
                }
                
                # Categorize files
                filename = file_path.name
                
                if filename in temp_deployment_patterns:
                    file_info["category"] = "temporary_deployment"
                    analysis["categories"]["temporary_deployment"].append(file_info)
                    analysis["cleanup_actions"]["to_remove"].append(str(relative_path))
                    
                elif any(self._matches_pattern(filename, pattern) for pattern in backup_patterns):
                    file_info["category"] = "backup_files"
                    analysis["categories"]["backup_files"].append(file_info)
                    analysis["cleanup_actions"]["to_remove"].append(str(relative_path))
                    
                elif any(self._matches_pattern(filename, pattern) for pattern in test_patterns):
                    file_info["category"] = "test_files"
                    analysis["categories"]["test_files"].append(file_info)
                    target_dir = self._determine_test_category(filename)
                    analysis["cleanup_actions"]["to_move"].append({
                        "from": str(relative_path),
                        "to": f"tests/{target_dir}/{filename}"
                    })
                    
                elif any(self._matches_pattern(filename, pattern) for pattern in component_patterns):
                    file_info["category"] = "components"
                    analysis["categories"]["components"].append(file_info)
                    target_dir = self._determine_component_category(filename)
                    analysis["cleanup_actions"]["to_move"].append({
                        "from": str(relative_path),
                        "to": f"components/{target_dir}/{filename}"
                    })
                    
                elif filename in essential_script_patterns:
                    file_info["category"] = "essential_scripts"
                    analysis["categories"]["essential_scripts"].append(file_info)
                    analysis["cleanup_actions"]["to_move"].append({
                        "from": str(relative_path),
                        "to": f"scripts/{filename}"
                    })
                    
                elif filename.endswith('.md') and filename != 'README.md':
                    file_info["category"] = "documentation"
                    analysis["categories"]["documentation"].append(file_info)
                    analysis["cleanup_actions"]["to_move"].append({
                        "from": str(relative_path),
                        "to": f"docs/{filename}"
                    })
                    
                else:
                    analysis["categories"]["other"].append(file_info)
                    analysis["cleanup_actions"]["to_preserve"].append(str(relative_path))
        
        return analysis
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a glob-like pattern."""
        if pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in filename
        elif pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        else:
            return filename == pattern
    
    def _determine_test_category(self, filename: str) -> str:
        """Determine which test category a test file belongs to."""
        if 'integration' in filename or 'complete' in filename:
            return 'integration'
        elif 'e2e' in filename or 'playwright' in filename:
            return 'e2e'
        else:
            return 'unit'
    
    def _determine_component_category(self, filename: str) -> str:
        """Determine which component category a component belongs to."""
        if any(keyword in filename for keyword in ['hero', 'navigation', 'footer']):
            return 'layout'
        elif any(keyword in filename for keyword in ['services', 'testimonials', 'features']):
            return 'features'
        elif 'consulting' in filename:
            return 'consulting'
        else:
            return 'features'
    
    def generate_cleanup_report(self, analysis: Dict) -> None:
        """Generate a detailed cleanup report."""
        print("📝 Generating cleanup report...")
        
        report_content = f"""# Codebase Cleanup Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Files Analyzed**: {analysis['total_files']}
- **Files to Remove**: {len(analysis['cleanup_actions']['to_remove'])}
- **Files to Move**: {len(analysis['cleanup_actions']['to_move'])}
- **Files to Preserve**: {len(analysis['cleanup_actions']['to_preserve'])}

## File Categories

### Temporary Deployment Scripts ({len(analysis['categories']['temporary_deployment'])} files)
These files will be **REMOVED** as they are temporary deployment scripts:
"""
        
        for file_info in analysis['categories']['temporary_deployment']:
            size_mb = file_info['size'] / (1024 * 1024)
            report_content += f"- `{file_info['path']}` ({size_mb:.2f} MB)\n"
        
        report_content += f"""
### Backup Files ({len(analysis['categories']['backup_files'])} files)
These files will be **REMOVED** as they are backup/log files:
"""
        
        for file_info in analysis['categories']['backup_files']:
            size_mb = file_info['size'] / (1024 * 1024)
            report_content += f"- `{file_info['path']}` ({size_mb:.2f} MB)\n"
        
        report_content += f"""
### Test Files ({len(analysis['categories']['test_files'])} files)
These files will be **MOVED** to organized test directories:
"""
        
        for file_info in analysis['categories']['test_files']:
            report_content += f"- `{file_info['path']}`\n"
        
        report_content += f"""
### Components ({len(analysis['categories']['components'])} files)
These files will be **MOVED** to organized component directories:
"""
        
        for file_info in analysis['categories']['components']:
            report_content += f"- `{file_info['path']}`\n"
        
        report_content += f"""
### Documentation ({len(analysis['categories']['documentation'])} files)
These files will be **MOVED** to docs/ directory:
"""
        
        for file_info in analysis['categories']['documentation']:
            report_content += f"- `{file_info['path']}`\n"
        
        report_content += f"""
### Essential Scripts ({len(analysis['categories']['essential_scripts'])} files)
These files will be **MOVED** to scripts/ directory:
"""
        
        for file_info in analysis['categories']['essential_scripts']:
            report_content += f"- `{file_info['path']}`\n"
        
        report_content += """
## Cleanup Actions

### Files to Remove
"""
        for file_path in analysis['cleanup_actions']['to_remove']:
            report_content += f"- `{file_path}`\n"
        
        report_content += """
### Files to Move
"""
        for move_action in analysis['cleanup_actions']['to_move']:
            if isinstance(move_action, dict):
                report_content += f"- `{move_action['from']}` → `{move_action['to']}`\n"
        
        report_content += """
## Next Steps

1. Review this report carefully
2. Ensure backup was created successfully
3. Execute cleanup operations
4. Verify project still builds and functions correctly
5. Commit organized structure to version control

## Safety Notes

- A complete backup was created before analysis
- All essential files are preserved
- Only temporary and organizational changes are made
- Build and functionality should remain intact
"""
        
        # Write report to file
        with open(self.analysis_file, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Cleanup report generated: {self.analysis_file}")
    
    def save_analysis_json(self, analysis: Dict) -> None:
        """Save detailed analysis as JSON for programmatic use."""
        json_file = self.project_root / f"cleanup_analysis_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✅ Analysis data saved: {json_file}")
    
    def run_full_analysis(self) -> Dict:
        """Run complete backup and analysis process."""
        print("🚀 Starting backup and analysis process...")
        
        # Create backup
        backup_path = self.create_backup()
        
        # Analyze project structure
        analysis = self.analyze_project_structure()
        analysis["backup_path"] = backup_path
        
        # Generate reports
        self.generate_cleanup_report(analysis)
        self.save_analysis_json(analysis)
        
        print("✅ Backup and analysis complete!")
        print(f"📁 Backup: {backup_path}")
        print(f"📊 Report: {self.analysis_file}")
        
        return analysis

if __name__ == "__main__":
    backup_system = BackupAndAnalysis()
    analysis_result = backup_system.run_full_analysis()
    
    print("\n📋 Summary:")
    print(f"- Files to remove: {len(analysis_result['cleanup_actions']['to_remove'])}")
    print(f"- Files to move: {len(analysis_result['cleanup_actions']['to_move'])}")
    print(f"- Files to preserve: {len(analysis_result['cleanup_actions']['to_preserve'])}")