#!/usr/bin/env python3
"""
File Comparison and .gitignore Validation
Validates that .gitignore properly excludes temporary files and includes essential ones.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Set, Dict

class GitignoreValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        
    def get_git_status_files(self) -> Set[str]:
        """Get list of files that would be tracked by git."""
        try:
            # Get all files that git would track (not ignored)
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--cached', '--exclude-standard'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            else:
                print(f"Warning: Could not get git status: {result.stderr}")
                return set()
        except Exception as e:
            print(f"Warning: Git command failed: {e}")
            return set()
    
    def get_ignored_files(self) -> Set[str]:
        """Get list of files that are ignored by git."""
        try:
            # Get all files in the project
            all_files = []
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.project_root)
                    all_files.append(str(relative_path))
            
            # Check which files are ignored
            ignored_files = set()
            for file_path in all_files:
                result = subprocess.run(
                    ['git', 'check-ignore', file_path],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:  # File is ignored
                    ignored_files.add(file_path)
            
            return ignored_files
        except Exception as e:
            print(f"Warning: Could not check ignored files: {e}")
            return set()
    
    def validate_essential_files_tracked(self) -> Dict[str, bool]:
        """Validate that essential files are not ignored."""
        essential_files = [
            'package.json',
            'next.config.mjs',
            'tailwind.config.ts',
            'tsconfig.json',
            '.gitignore',
            'README.md',
            'docker-compose.yml',
            'Dockerfile',
            'deploy-to-vps.sh',
            'direct_vps_deploy.sh',
            'push-to-github.sh',
            '.env.example',
            '.env.production.template'
        ]
        
        validation_results = {}
        ignored_files = self.get_ignored_files()
        
        for essential_file in essential_files:
            file_path = self.project_root / essential_file
            if file_path.exists():
                is_ignored = essential_file in ignored_files
                validation_results[essential_file] = not is_ignored  # True if NOT ignored
                
                if is_ignored:
                    print(f"⚠️  Essential file is ignored: {essential_file}")
                else:
                    print(f"✅ Essential file is tracked: {essential_file}")
            else:
                print(f"ℹ️  Essential file not found: {essential_file}")
                validation_results[essential_file] = None
        
        return validation_results
    
    def validate_temporary_files_ignored(self) -> Dict[str, bool]:
        """Validate that temporary files are properly ignored."""
        # Check for patterns that should be ignored
        temp_patterns = [
            'cleanup_log_*.json',
            'cleanup_analysis_*.json',
            '*_test_report.json',
            '*_deployment.py',
            'deploy_*.py',
            'fix_*.py',
            'debug_*.py',
            '*.backup',
            'project_backup_*.tar.gz'
        ]
        
        validation_results = {}
        
        # Find files matching these patterns
        for pattern in temp_patterns:
            matching_files = list(self.project_root.glob(pattern))
            if matching_files:
                for file_path in matching_files:
                    relative_path = str(file_path.relative_to(self.project_root))
                    
                    # Check if file is ignored
                    result = subprocess.run(
                        ['git', 'check-ignore', relative_path],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    
                    is_ignored = result.returncode == 0
                    validation_results[relative_path] = is_ignored
                    
                    if is_ignored:
                        print(f"✅ Temporary file is ignored: {relative_path}")
                    else:
                        print(f"⚠️  Temporary file is NOT ignored: {relative_path}")
        
        return validation_results
    
    def check_gitignore_syntax(self) -> bool:
        """Check .gitignore file for syntax issues."""
        gitignore_path = self.project_root / '.gitignore'
        
        if not gitignore_path.exists():
            print("❌ .gitignore file not found")
            return False
        
        try:
            with open(gitignore_path, 'r') as f:
                lines = f.readlines()
            
            issues = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check for common issues
                if line.endswith('/') and not line.endswith('*/'):
                    # Directory patterns should be clear
                    pass
                
                if '**' in line and not line.startswith('**/') and not line.endswith('/**'):
                    issues.append(f"Line {i}: Potentially incorrect ** usage: {line}")
            
            if issues:
                print("⚠️  .gitignore syntax issues found:")
                for issue in issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ .gitignore syntax looks good")
                return True
                
        except Exception as e:
            print(f"❌ Error reading .gitignore: {e}")
            return False
    
    def generate_validation_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        print("🔍 Validating .gitignore configuration...")
        
        report = {
            "timestamp": "2025-07-22T03:51:26",
            "gitignore_syntax": self.check_gitignore_syntax(),
            "essential_files": self.validate_essential_files_tracked(),
            "temporary_files": self.validate_temporary_files_ignored(),
            "summary": {}
        }
        
        # Calculate summary
        essential_tracked = sum(1 for v in report["essential_files"].values() if v is True)
        essential_total = len([v for v in report["essential_files"].values() if v is not None])
        
        temp_ignored = sum(1 for v in report["temporary_files"].values() if v is True)
        temp_total = len(report["temporary_files"])
        
        report["summary"] = {
            "essential_files_tracked": f"{essential_tracked}/{essential_total}",
            "temporary_files_ignored": f"{temp_ignored}/{temp_total}",
            "gitignore_syntax_valid": report["gitignore_syntax"]
        }
        
        return report
    
    def run_validation(self) -> bool:
        """Run complete .gitignore validation."""
        print("🚀 Starting .gitignore validation...")
        
        report = self.generate_validation_report()
        
        print(f"\n📋 Validation Summary:")
        print(f"  - Essential files tracked: {report['summary']['essential_files_tracked']}")
        print(f"  - Temporary files ignored: {report['summary']['temporary_files_ignored']}")
        print(f"  - .gitignore syntax valid: {report['summary']['gitignore_syntax_valid']}")
        
        # Determine overall success
        all_essential_tracked = all(v is True for v in report["essential_files"].values() if v is not None)
        all_temp_ignored = all(v is True for v in report["temporary_files"].values())
        syntax_valid = report["gitignore_syntax"]
        
        success = all_essential_tracked and all_temp_ignored and syntax_valid
        
        if success:
            print("✅ .gitignore validation passed!")
        else:
            print("⚠️  .gitignore validation found issues")
        
        return success

if __name__ == "__main__":
    validator = GitignoreValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 .gitignore configuration is properly set up!")
    else:
        print("\n💡 Review the issues above and update .gitignore as needed.")