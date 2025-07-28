#!/usr/bin/env python3
"""
Project Structure Analyzer and Backup System
Analyzes current project structure and creates backup before cleanup
"""

import os
import json
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import hashlib
import subprocess

class ProjectAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.analysis_results = {}
        self.backup_dir = None
        
        # Define file categories
        self.categories = {
            'frontend': {
                'patterns': ['app/', 'components/', 'lib/', 'hooks/', 'styles/', 'public/'],
                'extensions': ['.tsx', '.ts', '.css', '.scss', '.js', '.jsx'],
                'configs': ['next.config.mjs', 'tailwind.config.ts', 'postcss.config.mjs']
            },
            'backend': {
                'patterns': ['agent/', 'api_server.py', 'main.py'],
                'extensions': ['.py'],
                'configs': ['pyproject.toml', 'requirements.txt', 'uv.lock']
            },
            'infrastructure': {
                'patterns': ['scripts/', 'nginx/', 'ssl/', 'monitoring/', 'infrastructure/'],
                'extensions': ['.sh', '.yml', '.yaml', '.conf'],
                'configs': ['docker-compose*.yml', 'Dockerfile*', 'deploy.sh']
            },
            'documentation': {
                'patterns': ['docs/', 'README.md', 'CONTRIBUTING.md'],
                'extensions': ['.md', '.txt'],
                'configs': []
            },
            'testing': {
                'patterns': ['tests/', 'coverage/'],
                'extensions': ['.test.ts', '.test.js', '.spec.ts', '.spec.js'],
                'configs': ['jest.config.js', 'jest.setup.js', 'playwright.config.ts']
            },
            'configuration': {
                'patterns': ['.env*', '.git*', '.eslint*', '.prettier*'],
                'extensions': ['.json', '.config.js', '.config.ts'],
                'configs': ['package.json', 'tsconfig.json', 'components.json']
            },
            'temporary': {
                'patterns': ['archive/', '.next/', 'node_modules/', '.venv/', '__pycache__/'],
                'extensions': ['.log', '.tmp', '.cache'],
                'configs': []
            },
            'external': {
                'patterns': ['n8n-mcp/', 'tools/'],
                'extensions': [],
                'configs': []
            }
        }
        
        # Files to ignore during analysis
        self.ignore_patterns = {
            '.git/', 'node_modules/', '.next/', '__pycache__/', '.venv/',
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'
        }

    def create_backup(self) -> str:
        """Create a full backup of the project before cleanup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"project_backup_{timestamp}"
        self.backup_dir = self.project_root.parent / backup_name
        
        print(f"Creating backup at: {self.backup_dir}")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Copy entire project (excluding some large directories)
            exclude_dirs = {'.git', 'node_modules', '.next', '__pycache__', '.venv'}
            
            for item in self.project_root.iterdir():
                if item.name not in exclude_dirs:
                    if item.is_dir():
                        shutil.copytree(item, self.backup_dir / item.name, 
                                      ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    else:
                        shutil.copy2(item, self.backup_dir / item.name)
            
            # Create backup manifest
            manifest = {
                'backup_date': timestamp,
                'original_path': str(self.project_root),
                'backup_path': str(self.backup_dir),
                'excluded_dirs': list(exclude_dirs)
            }
            
            with open(self.backup_dir / 'backup_manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Backup created successfully: {self.backup_dir}")
            return str(self.backup_dir)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise

    def analyze_file_structure(self) -> Dict:
        """Analyze current project structure and categorize files"""
        print("🔍 Analyzing project structure...")
        
        analysis = {
            'total_files': 0,
            'total_directories': 0,
            'categories': {cat: {'files': [], 'size': 0} for cat in self.categories.keys()},
            'duplicates': [],
            'issues': [],
            'recommendations': []
        }
        
        # Add uncategorized category
        analysis['categories']['uncategorized'] = {'files': [], 'size': 0}
        
        # Walk through project directory
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            root_path = Path(root)
            relative_root = root_path.relative_to(self.project_root)
            
            analysis['total_directories'] += 1
            
            for file in files:
                if self._should_ignore(file):
                    continue
                    
                file_path = root_path / file
                relative_path = file_path.relative_to(self.project_root)
                
                analysis['total_files'] += 1
                
                # Categorize file
                category = self._categorize_file(relative_path)
                file_info = {
                    'path': str(relative_path),
                    'size': file_path.stat().st_size if file_path.exists() else 0,
                    'category': category
                }
                
                analysis['categories'][category]['files'].append(file_info)
                analysis['categories'][category]['size'] += file_info['size']
        
        # Detect duplicates
        analysis['duplicates'] = self._find_duplicates()
        
        # Identify issues
        analysis['issues'] = self._identify_issues()
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        self.analysis_results = analysis
        return analysis

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored"""
        for pattern in self.ignore_patterns:
            if pattern.endswith('/') and path.startswith(pattern[:-1]):
                return True
            if pattern.startswith('*.') and path.endswith(pattern[1:]):
                return True
            if pattern == path:
                return True
        return False

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize a file based on its path and extension"""
        path_str = str(file_path)
        file_ext = file_path.suffix
        file_name = file_path.name
        
        for category, rules in self.categories.items():
            # Check patterns
            for pattern in rules['patterns']:
                if path_str.startswith(pattern) or pattern in path_str:
                    return category
            
            # Check extensions
            if file_ext in rules['extensions']:
                return category
                
            # Check specific config files
            if file_name in rules['configs']:
                return category
                
            # Check config patterns
            for config in rules['configs']:
                if '*' in config and file_name.startswith(config.replace('*', '')):
                    return category
        
        return 'uncategorized'

    def _find_duplicates(self) -> List[Dict]:
        """Find duplicate files based on content hash"""
        print("🔍 Detecting duplicate files...")
        
        file_hashes = {}
        duplicates = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                    
                file_path = Path(root) / file
                
                try:
                    # Calculate file hash
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            'hash': file_hash,
                            'files': [file_hashes[file_hash], str(file_path.relative_to(self.project_root))],
                            'size': file_path.stat().st_size
                        })
                    else:
                        file_hashes[file_hash] = str(file_path.relative_to(self.project_root))
                        
                except (IOError, OSError):
                    continue
        
        return duplicates

    def _identify_issues(self) -> List[Dict]:
        """Identify structural issues in the project"""
        issues = []
        
        # Check for multiple Docker files
        docker_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.startswith('Dockerfile') or file.startswith('docker-compose'):
                    docker_files.append(str(Path(root, file).relative_to(self.project_root)))
        
        if len(docker_files) > 3:
            issues.append({
                'type': 'multiple_docker_configs',
                'severity': 'medium',
                'description': f'Found {len(docker_files)} Docker configuration files',
                'files': docker_files,
                'recommendation': 'Consolidate Docker configurations'
            })
        
        # Check for scattered environment files
        env_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.startswith('.env'):
                    env_files.append(str(Path(root, file).relative_to(self.project_root)))
        
        if len(env_files) > 2:
            issues.append({
                'type': 'multiple_env_files',
                'severity': 'low',
                'description': f'Found {len(env_files)} environment files',
                'files': env_files,
                'recommendation': 'Consolidate to .env and .env.example'
            })
        
        # Check for root directory clutter
        root_files = [f for f in os.listdir(self.project_root) 
                     if os.path.isfile(os.path.join(self.project_root, f))]
        
        if len(root_files) > 20:
            issues.append({
                'type': 'root_clutter',
                'severity': 'high',
                'description': f'Root directory has {len(root_files)} files',
                'files': root_files[:10],  # Show first 10
                'recommendation': 'Move configuration files to appropriate subdirectories'
            })
        
        return issues

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate cleanup recommendations based on analysis"""
        recommendations = []
        
        # Frontend organization
        frontend_files = len(analysis['categories']['frontend']['files'])
        if frontend_files > 0:
            recommendations.append({
                'category': 'frontend',
                'action': 'organize',
                'description': f'Organize {frontend_files} frontend files into frontend/ directory',
                'priority': 'high'
            })
        
        # Backend organization
        backend_files = len(analysis['categories']['backend']['files'])
        if backend_files > 0:
            recommendations.append({
                'category': 'backend',
                'action': 'organize',
                'description': f'Ensure {backend_files} backend files are properly organized in agent/ directory',
                'priority': 'high'
            })
        
        # Infrastructure consolidation
        infra_files = len(analysis['categories']['infrastructure']['files'])
        if infra_files > 10:
            recommendations.append({
                'category': 'infrastructure',
                'action': 'consolidate',
                'description': f'Consolidate {infra_files} infrastructure files into infrastructure/ directory',
                'priority': 'medium'
            })
        
        # Temporary file cleanup
        temp_files = len(analysis['categories']['temporary']['files'])
        if temp_files > 0:
            recommendations.append({
                'category': 'temporary',
                'action': 'cleanup',
                'description': f'Remove or archive {temp_files} temporary files',
                'priority': 'low'
            })
        
        return recommendations

    def generate_report(self, output_file: str = None) -> str:
        """Generate detailed analysis report"""
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analyze_file_structure() first.")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Project Structure Analysis Report
Generated: {timestamp}
Project: {self.project_root}

## Summary
- Total Files: {self.analysis_results['total_files']}
- Total Directories: {self.analysis_results['total_directories']}
- Backup Location: {self.backup_dir}

## File Categories
"""
        
        for category, data in self.analysis_results['categories'].items():
            file_count = len(data['files'])
            size_mb = data['size'] / (1024 * 1024)
            report += f"- **{category.title()}**: {file_count} files ({size_mb:.1f} MB)\n"
        
        report += "\n## Issues Found\n"
        for issue in self.analysis_results['issues']:
            report += f"- **{issue['type']}** ({issue['severity']}): {issue['description']}\n"
        
        report += "\n## Recommendations\n"
        for rec in self.analysis_results['recommendations']:
            report += f"- **{rec['category'].title()}** ({rec['priority']}): {rec['description']}\n"
        
        report += "\n## Duplicates Found\n"
        for dup in self.analysis_results['duplicates']:
            report += f"- Files: {', '.join(dup['files'])} (Size: {dup['size']} bytes)\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")
        
        return report

    def create_rollback_script(self) -> str:
        """Create a rollback script to restore original structure"""
        if not self.backup_dir:
            raise ValueError("No backup created. Run create_backup() first.")
        
        rollback_script = f"""#!/bin/bash
# Rollback script to restore original project structure
# Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set -e

BACKUP_DIR="{self.backup_dir}"
PROJECT_DIR="{self.project_root}"

echo "🔄 Rolling back project structure..."
echo "Backup: $BACKUP_DIR"
echo "Project: $PROJECT_DIR"

# Confirm rollback
read -p "Are you sure you want to rollback? This will overwrite current changes. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled."
    exit 1
fi

# Create temporary backup of current state
TEMP_BACKUP="$PROJECT_DIR/../temp_backup_$(date +%Y%m%d_%H%M%S)"
echo "Creating temporary backup of current state: $TEMP_BACKUP"
cp -r "$PROJECT_DIR" "$TEMP_BACKUP"

# Remove current project files (except .git)
echo "Removing current project files..."
find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {{}} +

# Restore from backup
echo "Restoring from backup..."
cp -r "$BACKUP_DIR"/* "$PROJECT_DIR/"

echo "✅ Rollback completed successfully!"
echo "Current state backed up to: $TEMP_BACKUP"
echo "You can remove it if rollback was successful."
"""
        
        rollback_path = self.project_root / "rollback_cleanup.sh"
        with open(rollback_path, 'w') as f:
            f.write(rollback_script)
        
        # Make script executable
        os.chmod(rollback_path, 0o755)
        
        print(f"📜 Rollback script created: {rollback_path}")
        return str(rollback_path)

def main():
    """Main function to run project analysis"""
    print("🚀 Starting Project Structure Analysis and Backup")
    print("=" * 50)
    
    analyzer = ProjectAnalyzer()
    
    try:
        # Create backup
        backup_path = analyzer.create_backup()
        
        # Analyze structure
        analysis = analyzer.analyze_file_structure()
        
        # Generate report
        report_path = "infrastructure/cleanup/project_analysis_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        analyzer.generate_report(report_path)
        
        # Create rollback script
        rollback_script = analyzer.create_rollback_script()
        
        # Save analysis results as JSON
        analysis_json_path = "infrastructure/cleanup/project_analysis.json"
        with open(analysis_json_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print("\n" + "=" * 50)
        print("✅ Analysis completed successfully!")
        print(f"📄 Report: {report_path}")
        print(f"📊 Data: {analysis_json_path}")
        print(f"💾 Backup: {backup_path}")
        print(f"📜 Rollback: {rollback_script}")
        print("\nNext steps:")
        print("1. Review the analysis report")
        print("2. Plan the cleanup strategy")
        print("3. Execute cleanup tasks incrementally")
        print("4. Use rollback script if needed")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()