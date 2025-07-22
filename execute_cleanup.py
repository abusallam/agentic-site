#!/usr/bin/env python3
"""
Cleanup Engine for Codebase Organization
Safely removes temporary files and backup archives based on analysis.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

class CleanupEngine:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cleanup_log = []
        
        # Load analysis data
        self.analysis_data = self._load_analysis_data()
        
    def _load_analysis_data(self) -> Dict:
        """Load the most recent analysis data."""
        analysis_files = list(self.project_root.glob("cleanup_analysis_*.json"))
        if not analysis_files:
            raise FileNotFoundError("No analysis data found. Please run backup_and_safety.py first.")
        
        # Get the most recent analysis file
        latest_analysis = max(analysis_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_analysis, 'r') as f:
            return json.load(f)
    
    def remove_temporary_deployment_scripts(self) -> None:
        """Remove temporary deployment Python scripts."""
        print("🧹 Removing temporary deployment scripts...")
        
        temp_scripts = [
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
        
        removed_count = 0
        for script in temp_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                try:
                    script_path.unlink()
                    self.cleanup_log.append({
                        "action": "removed",
                        "file": script,
                        "reason": "temporary deployment script",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"  ✅ Removed: {script}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to remove {script}: {e}")
                    self.cleanup_log.append({
                        "action": "failed_remove",
                        "file": script,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        print(f"✅ Removed {removed_count} temporary deployment scripts")
    
    def remove_backup_and_log_files(self) -> None:
        """Remove backup archives and log files."""
        print("🧹 Removing backup files and logs...")
        
        # Remove test report files
        report_files = [
            'playwright_test_report.json',
            'ui_test_report.json',
            'deployment_test_report.json'
        ]
        
        removed_count = 0
        for report_file in report_files:
            report_path = self.project_root / report_file
            if report_path.exists():
                try:
                    report_path.unlink()
                    self.cleanup_log.append({
                        "action": "removed",
                        "file": report_file,
                        "reason": "test report file",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"  ✅ Removed: {report_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to remove {report_file}: {e}")
        
        # Remove old backup files (but preserve the one we just created)
        backup_dir = self.project_root / "backups"
        if backup_dir.exists():
            current_backup = f"project_backup_{self.analysis_data.get('timestamp', '')}.tar.gz"
            
            for backup_file in backup_dir.glob("*.tar.gz"):
                # Skip the current backup we just created
                if backup_file.name == current_backup:
                    continue
                    
                try:
                    backup_file.unlink()
                    self.cleanup_log.append({
                        "action": "removed",
                        "file": str(backup_file.relative_to(self.project_root)),
                        "reason": "old backup file",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"  ✅ Removed: {backup_file.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to remove {backup_file.name}: {e}")
        
        print(f"✅ Removed {removed_count} backup and log files")
    
    def preserve_essential_deployment_files(self) -> None:
        """Ensure essential deployment files are preserved."""
        print("🔒 Verifying essential deployment files are preserved...")
        
        essential_files = [
            'deploy-to-vps.sh',
            'direct_vps_deploy.sh',
            'push-to-github.sh'
        ]
        
        preserved_count = 0
        for essential_file in essential_files:
            file_path = self.project_root / essential_file
            if file_path.exists():
                self.cleanup_log.append({
                    "action": "preserved",
                    "file": essential_file,
                    "reason": "essential deployment script",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  ✅ Preserved: {essential_file}")
                preserved_count += 1
            else:
                print(f"  ⚠️  Missing essential file: {essential_file}")
        
        print(f"✅ Verified {preserved_count} essential deployment files")
    
    def clean_analysis_files(self) -> None:
        """Clean up old analysis files, keeping only the most recent."""
        print("🧹 Cleaning up old analysis files...")
        
        # Keep only the most recent analysis files
        analysis_files = list(self.project_root.glob("cleanup_analysis_*.json"))
        if len(analysis_files) > 1:
            # Sort by modification time and keep the newest
            analysis_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for old_analysis in analysis_files[1:]:  # Skip the first (newest) one
                try:
                    old_analysis.unlink()
                    self.cleanup_log.append({
                        "action": "removed",
                        "file": old_analysis.name,
                        "reason": "old analysis file",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"  ✅ Removed old analysis: {old_analysis.name}")
                except Exception as e:
                    print(f"  ❌ Failed to remove {old_analysis.name}: {e}")
    
    def validate_cleanup(self) -> bool:
        """Validate that cleanup was successful and no critical files were removed."""
        print("🔍 Validating cleanup results...")
        
        # Check that essential files still exist
        essential_files = [
            'package.json',
            'next.config.mjs',
            'tailwind.config.ts',
            'tsconfig.json',
            '.gitignore',
            'README.md',
            'docker-compose.yml',
            'Dockerfile'
        ]
        
        missing_files = []
        for essential_file in essential_files:
            if not (self.project_root / essential_file).exists():
                missing_files.append(essential_file)
        
        if missing_files:
            print(f"❌ Critical files missing: {missing_files}")
            return False
        
        # Check that app directory structure is intact
        app_dir = self.project_root / "app"
        if not app_dir.exists():
            print("❌ App directory missing")
            return False
        
        # Check that components directory exists
        components_dir = self.project_root / "components"
        if not components_dir.exists():
            print("❌ Components directory missing")
            return False
        
        print("✅ Cleanup validation passed")
        return True
    
    def save_cleanup_log(self) -> None:
        """Save cleanup log for audit purposes."""
        log_file = self.project_root / f"cleanup_log_{self.timestamp}.json"
        
        cleanup_summary = {
            "timestamp": self.timestamp,
            "total_actions": len(self.cleanup_log),
            "actions": self.cleanup_log,
            "summary": {
                "removed": len([a for a in self.cleanup_log if a["action"] == "removed"]),
                "preserved": len([a for a in self.cleanup_log if a["action"] == "preserved"]),
                "failed": len([a for a in self.cleanup_log if a["action"] == "failed_remove"])
            }
        }
        
        with open(log_file, 'w') as f:
            json.dump(cleanup_summary, f, indent=2)
        
        print(f"📝 Cleanup log saved: {log_file}")
    
    def run_cleanup(self) -> bool:
        """Execute the complete cleanup process."""
        print("🚀 Starting cleanup process...")
        print(f"📊 Analysis data loaded from: {self.analysis_data.get('timestamp', 'unknown')}")
        
        try:
            # Remove temporary deployment scripts
            self.remove_temporary_deployment_scripts()
            
            # Remove backup and log files
            self.remove_backup_and_log_files()
            
            # Verify essential files are preserved
            self.preserve_essential_deployment_files()
            
            # Clean up old analysis files
            self.clean_analysis_files()
            
            # Validate cleanup results
            if not self.validate_cleanup():
                print("❌ Cleanup validation failed!")
                return False
            
            # Save cleanup log
            self.save_cleanup_log()
            
            print("✅ Cleanup process completed successfully!")
            
            # Print summary
            removed_count = len([a for a in self.cleanup_log if a["action"] == "removed"])
            preserved_count = len([a for a in self.cleanup_log if a["action"] == "preserved"])
            
            print(f"\n📋 Cleanup Summary:")
            print(f"  - Files removed: {removed_count}")
            print(f"  - Files preserved: {preserved_count}")
            print(f"  - Total actions: {len(self.cleanup_log)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Cleanup process failed: {e}")
            return False

if __name__ == "__main__":
    cleanup_engine = CleanupEngine()
    success = cleanup_engine.run_cleanup()
    
    if success:
        print("\n🎉 Temporary file cleanup completed successfully!")
        print("Next step: Run file organization to move components and docs to proper directories.")
    else:
        print("\n💥 Cleanup failed. Check the error messages above.")
        print("Your backup is safe at: backups/project_backup_*.tar.gz")