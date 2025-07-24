#!/usr/bin/env python3
"""
Project Structure Analyzer and Backup System
Analyzes current project structure and creates backup before cleanup
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import fnmatch

class ProjectAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.analysis_results = {}
        self.backup_dir = None
        
        # File categories for organization
        self.file_categories = {
            'frontend': {
                'patterns': ['app/**/*', 'components/**/*', 'lib/**/*', 'public/**/*', 
                           'styles/**/*', 'hooks/**/*', 'next.config.*', 'tailwind.config.*'],
                'extensions': ['.tsx', '.jsx', '.css', '.scss']
            },
            'backend': {
                'patterns': ['agent/**/*', 'pyproject.toml', 'uv.lock'],
                'extensions': ['.py']
            },
            'infrastructure': {
                'patterns': ['Dockerfile*', 'docker-compose*', 'scripts/**/*', 
                           'deploy*.sh', '*.sh'],
                'extensions': ['.sh', '.yml', '.yaml']
            },
            'config': {
                'patterns': ['.env*', '*.json', '*.config.*', '.eslintrc*', 
                           '.prettierrc*', 'tsconfig.json', 'package*.json'],
                'extensions': ['.json', '.env']
            },
            'docs': {
                'patterns': ['docs/**/*', '*.md', 'README*', 'CONTRIBUTING*', 'LICENSE'],
                'extensions': ['.md', '.txt']
            },
            'tests': {
                'patterns': ['tests/**/*', '**/*.test.*', '**/*.spec.*'],
                'extensions': ['.py', '.js', '.ts']
            },
            'temp_cleanup': {
                'patterns': ['*cleanup*', '*analysis*', '*log*', '*backup*', 
                           'analyze_*.py', 'execute_*.py', 'fix_*.py', 'setup_*.py',
                           'test_*.py', 'create_*.py', 'deploy_*.py', 'resolve_*.py',
                           'organize_*.py', 'comprehensive_*.py', 'connection_*.py'],
                'extensions': ['.json', '.log']
            }
        }
        
        # Directories to ignore during analysis
        self.ignore_patterns = [
            '.git', '.next', 'node_modules', '.venv', '__pycache__', 
            '.pytest_cache', 'dist', 'build', '.cache', '.kiro'
        ]

    def create_backup(self) -> str:
        """Create a full backup of the project before cleanup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"project_backup_{timestamp}"
        self.backup_dir = self.project_root.parent / backup_name
        
        print(f"Creating backup at: {self.backup_dir}")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Copy entire project (excluding large directories)
            for item in self.project_root.iterdir():
                if item.name not in ['.git', 'node_modules', '.next', '.venv', '__pycache__']:
                    if item.is_dir():
                        shutil.copytree(item, self.backup_dir / item.name, 
                                      ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    else:
                        shutil.copy2(item, self.backup_dir / item.name)
            
            # Create backup manifest
            manifest = {
                'backup_created': timestamp,
                'original_path': str(self.project_root),
                'backup_path': str(self.backup_dir),
                'files_backed_up': self._count_files(self.backup_dir)
            }
            
            with open(self.backup_dir / 'backup_manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Backup created successfully: {backup_name}")
            return str(self.backup_dir)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise

    def analyze_project_structure(self) -> Dict:
        """Analyze current project structure and categorize files"""
        print("🔍 Analyzing project structure...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'total_files': 0,
            'total_directories': 0,
            'file_categories': {},
            'duplicates': [],
            'large_files': [],
            'issues': []
        }
        
        # Initialize category counters
        for category in self.file_categories:
            analysis['file_categories'][category] = {
                'files': [],
                'count': 0,
                'total_size': 0
            }
        
        # Walk through project directory
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in self.ignore_patterns)]
            
            root_path = Path(root)
            relative_root = root_path.relative_to(self.project_root)
            
            analysis['total_directories'] += 1
            
            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(self.project_root)
                
                try:
                    file_size = file_path.stat().st_size
                    analysis['total_files'] += 1
                    
                    # Categorize file
                    category = self._categorize_file(relative_path)
                    if category:
                        analysis['file_categories'][category]['files'].append({
                            'path': str(relative_path),
                            'size': file_size,
                            'modified': file_path.stat().st_mtime
                        })
                        analysis['file_categories'][category]['count'] += 1
                        analysis['file_categories'][category]['total_size'] += file_size
                    
                    # Check for large files (>10MB)
                    if file_size > 10 * 1024 * 1024:
                        analysis['large_files'].append({
                            'path': str(relative_path),
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        })
                
                except (OSError, PermissionError) as e:
                    analysis['issues'].append(f"Cannot access {relative_path}: {e}")
        
        # Identify potential duplicates
        analysis['duplicates'] = self._find_duplicates()
        
        # Identify issues
        analysis['issues'].extend(self._identify_issues())
        
        self.analysis_results = analysis
        return analysis

    def _categorize_file(self, file_path: Path) -> Optional[str]:
        """Categorize a file based on patterns and extensions"""
        file_str = str(file_path)
        file_ext = file_path.suffix.lower()
        
        for category, rules in self.file_categories.items():
            # Check patterns
            for pattern in rules['patterns']:
                if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                    return category
            
            # Check extensions
            if file_ext in rules.get('extensions', []):
                return category
        
        return 'uncategorized'

    def _find_duplicates(self) -> List[Dict]:
        """Find potential duplicate files"""
        duplicates = []
        
        # Look for common duplicate patterns
        duplicate_patterns = [
            ('Dockerfile', 'Dockerfile.*'),
            ('docker-compose.yml', 'docker-compose.*.yml'),
            ('.env', '.env.*'),
            ('package.json', 'package-lock.json')
        ]
        
        for base_pattern, variant_pattern in duplicate_patterns:
            base_files = list(self.project_root.glob(base_pattern))
            variant_files = list(self.project_root.glob(variant_pattern))
            
            if len(base_files) > 0 and len(variant_files) > 0:
                duplicates.append({
                    'type': 'configuration_variants',
                    'base_files': [str(f.relative_to(self.project_root)) for f in base_files],
                    'variant_files': [str(f.relative_to(self.project_root)) for f in variant_files],
                    'recommendation': 'consolidate_configs'
                })
        
        return duplicates

    def _identify_issues(self) -> List[str]:
        """Identify structural issues in the project"""
        issues = []
        
        # Check for root directory clutter
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        if len(root_files) > 20:
            issues.append(f"Root directory has {len(root_files)} files - consider organizing into subdirectories")
        
        # Check for multiple Docker files
        docker_files = list(self.project_root.glob("Dockerfile*"))
        if len(docker_files) > 3:
            issues.append(f"Found {len(docker_files)} Docker files - consider consolidating")
        
        # Check for temporary files in root
        temp_files = [f for f in root_files if any(pattern in f.name.lower() 
                     for pattern in ['temp', 'backup', 'old', 'test_', 'fix_'])]
        if temp_files:
            issues.append(f"Found {len(temp_files)} temporary files in root directory")
        
        return issues

    def _count_files(self, directory: Path) -> int:
        """Count total files in directory"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count

    def generate_report(self, output_file: str = None) -> str:
        """Generate detailed analysis report"""
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analyze_project_structure() first.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_file:
            output_file = f"project_analysis_report_{timestamp}.json"
        
        # Add summary statistics
        report = self.analysis_results.copy()
        report['summary'] = {
            'total_files': report['total_files'],
            'total_directories': report['total_directories'],
            'categories_found': len([cat for cat, data in report['file_categories'].items() if data['count'] > 0]),
            'issues_found': len(report['issues']),
            'duplicates_found': len(report['duplicates']),
            'large_files_found': len(report['large_files'])
        }
        
        # Save report
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Analysis report saved: {output_file}")
        return str(output_path)

    def create_rollback_script(self) -> str:
        """Create rollback script to restore original structure"""
        if not self.backup_dir:
            raise ValueError("No backup created. Run create_backup() first.")
        
        rollback_script = f"""#!/bin/bash
# Rollback script generated on {datetime.now().isoformat()}
# This script restores the project to its original state

set -e

BACKUP_DIR="{self.backup_dir}"
PROJECT_DIR="{self.project_root}"

echo "🔄 Rolling back project to original state..."
echo "Backup location: $BACKUP_DIR"
echo "Project location: $PROJECT_DIR"

# Verify backup exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Create rollback backup of current state
ROLLBACK_BACKUP="${{PROJECT_DIR}}_rollback_$(date +%Y%m%d_%H%M%S)"
echo "Creating rollback backup at: $ROLLBACK_BACKUP"
cp -r "$PROJECT_DIR" "$ROLLBACK_BACKUP"

# Remove current project files (except .git)
echo "Removing current project files..."
find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {{}} +

# Restore from backup
echo "Restoring from backup..."
cp -r "$BACKUP_DIR"/* "$PROJECT_DIR/"

echo "✅ Rollback completed successfully"
echo "Current state backed up to: $ROLLBACK_BACKUP"
"""
        
        rollback_path = self.project_root / "rollback_cleanup.sh"
        with open(rollback_path, 'w') as f:
            f.write(rollback_script)
        
        # Make script executable
        os.chmod(rollback_path, 0o755)
        
        print(f"🔄 Rollback script created: rollback_cleanup.sh")
        return str(rollback_path)

def main():
    """Main execution function"""
    print("🚀 Starting Project Analysis and Backup System")
    print("=" * 50)
    
    analyzer = ProjectAnalyzer()
    
    try:
        # Create backup
        backup_path = analyzer.create_backup()
        print(f"Backup created at: {backup_path}")
        
        # Analyze project structure
        analysis = analyzer.analyze_project_structure()
        
        # Generate report
        report_path = analyzer.generate_report()
        
        # Create rollback script
        rollback_path = analyzer.create_rollback_script()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Total Files: {analysis['total_files']}")
        print(f"Total Directories: {analysis['total_directories']}")
        print(f"Issues Found: {len(analysis['issues'])}")
        print(f"Duplicates Found: {len(analysis['duplicates'])}")
        print(f"Large Files: {len(analysis['large_files'])}")
        
        print("\n📁 FILE CATEGORIES:")
        for category, data in analysis['file_categories'].items():
            if data['count'] > 0:
                size_mb = round(data['total_size'] / (1024 * 1024), 2)
                print(f"  {category}: {data['count']} files ({size_mb} MB)")
        
        if analysis['issues']:
            print("\n⚠️  ISSUES IDENTIFIED:")
            for issue in analysis['issues']:
                print(f"  - {issue}")
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Report: {report_path}")
        print(f"💾 Backup: {backup_path}")
        print(f"🔄 Rollback: {rollback_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()