#!/usr/bin/env python3
"""
File Categorization and Mapping Logic
Creates detailed mapping plan for project reorganization
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re

class FileMapper:
    def __init__(self, analysis_file: str = "infrastructure/cleanup/project_analysis.json"):
        self.analysis_file = Path(analysis_file)
        self.project_root = Path(".")
        self.analysis_data = self._load_analysis()
        
        # Define target structure
        self.target_structure = {
            'frontend/': {
                'description': 'Next.js application and React components',
                'subdirs': ['app/', 'components/', 'lib/', 'hooks/', 'styles/', 'public/'],
                'configs': ['next.config.mjs', 'tailwind.config.ts', 'postcss.config.mjs', 
                           'jest.config.js', 'jest.setup.js', 'playwright.config.ts']
            },
            'backend/': {
                'description': 'Python ADK agent system (keep current agent/ structure)',
                'subdirs': ['agent/'],
                'configs': []  # Keep existing structure
            },
            'infrastructure/': {
                'description': 'Deployment, Docker, and infrastructure code',
                'subdirs': ['docker/', 'scripts/', 'nginx/', 'ssl/', 'monitoring/', 'ansible/'],
                'configs': ['docker-compose*.yml', 'Dockerfile*', 'deploy.sh']
            },
            'docs/': {
                'description': 'Documentation and guides',
                'subdirs': ['deployment/', 'monitoring/', 'troubleshooting/'],
                'configs': []
            },
            'tests/': {
                'description': 'Integration and E2E tests (keep current structure)',
                'subdirs': ['e2e/', 'integration/', 'unit/'],
                'configs': []
            },
            'tools/': {
                'description': 'Development tools and utilities (keep current structure)',
                'subdirs': ['database/', 'monitoring/', 'security/'],
                'configs': []
            }
        }
        
        # Files to keep at root level
        self.root_files = {
            'README.md', 'LICENSE', 'CONTRIBUTING.md', 'DEPLOYMENT_GUIDE.md',
            'PROJECT_STRUCTURE.md', '.gitignore', '.env', '.env.example',
            'package.json', 'tsconfig.json', 'components.json',
            '.eslintrc.json', '.prettierrc', '.prettierignore'
        }
        
        # Files/directories to preserve as-is
        self.preserve_structure = {
            'agent/',  # Backend ADK structure
            'n8n-mcp/',  # External MCP server
            'tests/',  # Test structure
            'tools/',  # Tools structure
            '.git/', '.github/', '.husky/', '.kiro/',
            'node_modules/', '.next/', '.venv/', '__pycache__/',
            'coverage/', 'archive/'
        }

    def _load_analysis(self) -> Dict:
        """Load analysis data from JSON file"""
        if not self.analysis_file.exists():
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_file}")
        
        with open(self.analysis_file, 'r') as f:
            return json.load(f)

    def create_file_mapping(self) -> Dict:
        """Create comprehensive file mapping plan"""
        print("🗺️ Creating file mapping plan...")
        
        mapping_plan = {
            'moves': [],
            'copies': [],
            'merges': [],
            'deletes': [],
            'conflicts': [],
            'preserves': [],
            'summary': {
                'total_operations': 0,
                'files_to_move': 0,
                'files_to_delete': 0,
                'conflicts_found': 0
            }
        }
        
        # Process each category
        for category, data in self.analysis_data['categories'].items():
            if category == 'temporary':
                continue  # Skip temporary files for now
                
            for file_info in data['files']:
                file_path = Path(file_info['path'])
                operation = self._determine_operation(file_path, category)
                
                if operation:
                    mapping_plan[operation['type']].append(operation)
                    mapping_plan['summary']['total_operations'] += 1
                    
                    if operation['type'] == 'moves':
                        mapping_plan['summary']['files_to_move'] += 1
                    elif operation['type'] == 'deletes':
                        mapping_plan['summary']['files_to_delete'] += 1
        
        # Handle duplicates
        for duplicate in self.analysis_data['duplicates']:
            conflict = self._resolve_duplicate(duplicate)
            if conflict:
                mapping_plan['conflicts'].append(conflict)
                mapping_plan['summary']['conflicts_found'] += 1
        
        # Add directory creation operations
        mapping_plan['create_dirs'] = self._plan_directory_creation()
        
        return mapping_plan

    def _determine_operation(self, file_path: Path, category: str) -> Optional[Dict]:
        """Determine what operation to perform on a file"""
        path_str = str(file_path)
        
        # Check if file should be preserved as-is
        for preserve_pattern in self.preserve_structure:
            if path_str.startswith(preserve_pattern):
                return {
                    'type': 'preserves',
                    'source': path_str,
                    'reason': f'Preserve {preserve_pattern} structure',
                    'category': category
                }
        
        # Check if file should stay at root
        if file_path.name in self.root_files and len(file_path.parts) == 1:
            return {
                'type': 'preserves',
                'source': path_str,
                'reason': 'Keep at root level',
                'category': category
            }
        
        # Determine target location based on category and file type
        target = self._get_target_location(file_path, category)
        
        if target and target != path_str:
            return {
                'type': 'moves',
                'source': path_str,
                'target': target,
                'category': category,
                'reason': f'Organize {category} files'
            }
        
        # Check if file should be deleted (duplicates, empty files, etc.)
        if self._should_delete(file_path):
            return {
                'type': 'deletes',
                'source': path_str,
                'reason': 'Duplicate or unnecessary file',
                'category': category
            }
        
        return None

    def _get_target_location(self, file_path: Path, category: str) -> Optional[str]:
        """Determine target location for a file based on its category"""
        path_str = str(file_path)
        
        if category == 'frontend':
            # Frontend files organization
            if path_str.startswith('app/'):
                return f"frontend/{path_str}"
            elif path_str.startswith('components/'):
                return f"frontend/{path_str}"
            elif path_str.startswith('lib/'):
                return f"frontend/{path_str}"
            elif path_str.startswith('hooks/'):
                return f"frontend/{path_str}"
            elif path_str.startswith('styles/'):
                return f"frontend/{path_str}"
            elif path_str.startswith('public/'):
                return f"frontend/{path_str}"
            elif file_path.name in self.target_structure['frontend/']['configs']:
                return f"frontend/{file_path.name}"
        
        elif category == 'backend':
            # Backend files - mostly keep in agent/ but move to backend/
            if path_str.startswith('agent/'):
                return f"backend/{path_str}"
            elif file_path.suffix == '.py' and not path_str.startswith('tests/'):
                return f"backend/{path_str}"
        
        elif category == 'infrastructure':
            # Infrastructure files organization
            if 'docker' in path_str.lower() or file_path.name.startswith('Dockerfile'):
                return f"infrastructure/docker/{file_path.name}"
            elif path_str.startswith('scripts/'):
                return f"infrastructure/{path_str}"
            elif path_str.startswith('nginx/'):
                return f"infrastructure/{path_str}"
            elif path_str.startswith('ssl/'):
                return f"infrastructure/{path_str}"
            elif path_str.startswith('monitoring/'):
                return f"infrastructure/{path_str}"
            elif file_path.name == 'deploy.sh':
                return f"infrastructure/scripts/{file_path.name}"
        
        elif category == 'documentation':
            # Documentation organization
            if path_str.startswith('docs/'):
                return path_str  # Keep existing docs structure
            elif file_path.suffix == '.md' and file_path.name not in self.root_files:
                return f"docs/{file_path.name}"
        
        elif category == 'configuration':
            # Configuration files - most stay at root
            if file_path.name in self.root_files:
                return path_str  # Keep at root
            elif 'docker' in file_path.name.lower():
                return f"infrastructure/docker/{file_path.name}"
        
        return None

    def _should_delete(self, file_path: Path) -> bool:
        """Check if a file should be deleted"""
        path_str = str(file_path)
        
        # Delete empty files (0 bytes)
        if file_path.exists() and file_path.stat().st_size == 0:
            return True
        
        # Delete specific temporary files
        temp_patterns = [
            'simple_working_deployment.py',  # One-off script
            'rollback_cleanup.sh',  # Will be regenerated
        ]
        
        return file_path.name in temp_patterns

    def _resolve_duplicate(self, duplicate: Dict) -> Optional[Dict]:
        """Resolve duplicate files by determining which to keep"""
        files = duplicate['files']
        
        # Prioritize files based on location
        priority_order = [
            'components/',  # Keep component files over hooks
            'agent/',       # Keep agent files over tests
            'lib/',         # Keep lib files
            'app/',         # Keep app files
        ]
        
        keep_file = None
        delete_files = []
        
        for priority in priority_order:
            for file in files:
                if file.startswith(priority):
                    keep_file = file
                    delete_files = [f for f in files if f != keep_file]
                    break
            if keep_file:
                break
        
        if not keep_file:
            # If no priority match, keep the first one
            keep_file = files[0]
            delete_files = files[1:]
        
        if delete_files:
            return {
                'type': 'duplicate_resolution',
                'keep': keep_file,
                'delete': delete_files,
                'reason': f'Duplicate files with same content (hash: {duplicate["hash"][:8]})',
                'size': duplicate['size']
            }
        
        return None

    def _plan_directory_creation(self) -> List[Dict]:
        """Plan directory structure creation"""
        dirs_to_create = []
        
        for dir_path, config in self.target_structure.items():
            dirs_to_create.append({
                'path': dir_path,
                'description': config['description'],
                'subdirs': config['subdirs']
            })
        
        return dirs_to_create

    def detect_import_dependencies(self) -> Dict:
        """Detect import dependencies that need updating"""
        print("🔍 Analyzing import dependencies...")
        
        dependencies = {
            'typescript_imports': [],
            'python_imports': [],
            'css_imports': [],
            'asset_references': []
        }
        
        # Scan TypeScript/JavaScript files for imports
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                file_path = Path(root) / file
                
                if file_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                    deps = self._extract_ts_imports(file_path)
                    if deps:
                        dependencies['typescript_imports'].extend(deps)
                
                elif file_path.suffix == '.py':
                    deps = self._extract_python_imports(file_path)
                    if deps:
                        dependencies['python_imports'].extend(deps)
                
                elif file_path.suffix in ['.css', '.scss']:
                    deps = self._extract_css_imports(file_path)
                    if deps:
                        dependencies['css_imports'].extend(deps)
        
        return dependencies

    def _extract_ts_imports(self, file_path: Path) -> List[Dict]:
        """Extract TypeScript/JavaScript import statements"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match import statements
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.startswith('.'):  # Relative import
                        imports.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'import': match,
                            'type': 'relative'
                        })
        
        except (UnicodeDecodeError, IOError):
            pass
        
        return imports

    def _extract_python_imports(self, file_path: Path) -> List[Dict]:
        """Extract Python import statements"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match relative imports
            relative_patterns = [
                r'from\s+\.([^\s]+)\s+import',
                r'from\s+\.\.([^\s]+)\s+import'
            ]
            
            for pattern in relative_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    imports.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'import': match,
                        'type': 'relative'
                    })
        
        except (UnicodeDecodeError, IOError):
            pass
        
        return imports

    def _extract_css_imports(self, file_path: Path) -> List[Dict]:
        """Extract CSS import statements"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match @import statements
            import_pattern = r'@import\s+[\'"]([^\'"]+)[\'"]'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                if match.startswith('.'):  # Relative import
                    imports.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'import': match,
                        'type': 'relative'
                    })
        
        except (UnicodeDecodeError, IOError):
            pass
        
        return imports

    def generate_mapping_report(self, mapping_plan: Dict, output_file: str = None) -> str:
        """Generate detailed mapping report"""
        report = f"""
# File Mapping and Reorganization Plan

## Summary
- Total Operations: {mapping_plan['summary']['total_operations']}
- Files to Move: {mapping_plan['summary']['files_to_move']}
- Files to Delete: {mapping_plan['summary']['files_to_delete']}
- Conflicts Found: {mapping_plan['summary']['conflicts_found']}

## Directory Structure to Create
"""
        
        for dir_info in mapping_plan['create_dirs']:
            report += f"- **{dir_info['path']}**: {dir_info['description']}\n"
            for subdir in dir_info['subdirs']:
                report += f"  - {subdir}\n"
        
        report += "\n## File Moves\n"
        for move in mapping_plan['moves'][:20]:  # Show first 20
            report += f"- `{move['source']}` → `{move['target']}` ({move['reason']})\n"
        
        if len(mapping_plan['moves']) > 20:
            report += f"... and {len(mapping_plan['moves']) - 20} more moves\n"
        
        report += "\n## Files to Delete\n"
        for delete in mapping_plan['deletes']:
            report += f"- `{delete['source']}` ({delete['reason']})\n"
        
        report += "\n## Conflicts to Resolve\n"
        for conflict in mapping_plan['conflicts']:
            report += f"- **Keep**: `{conflict['keep']}`\n"
            report += f"  **Delete**: {', '.join([f'`{f}`' for f in conflict['delete']])}\n"
            report += f"  **Reason**: {conflict['reason']}\n\n"
        
        report += "\n## Files to Preserve\n"
        preserve_count = len(mapping_plan['preserves'])
        report += f"- {preserve_count} files will be preserved in their current locations\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"📄 Mapping report saved to: {output_file}")
        
        return report

    def save_mapping_plan(self, mapping_plan: Dict, output_file: str):
        """Save mapping plan as JSON"""
        with open(output_file, 'w') as f:
            json.dump(mapping_plan, f, indent=2)
        print(f"💾 Mapping plan saved to: {output_file}")

def main():
    """Main function to create file mapping"""
    print("🗺️ Starting File Mapping and Categorization")
    print("=" * 50)
    
    try:
        mapper = FileMapper()
        
        # Create file mapping plan
        mapping_plan = mapper.create_file_mapping()
        
        # Detect dependencies
        dependencies = mapper.detect_import_dependencies()
        mapping_plan['dependencies'] = dependencies
        
        # Generate report
        report_path = "infrastructure/cleanup/file_mapping_report.md"
        mapper.generate_mapping_report(mapping_plan, report_path)
        
        # Save mapping plan
        plan_path = "infrastructure/cleanup/file_mapping_plan.json"
        mapper.save_mapping_plan(mapping_plan, plan_path)
        
        print("\n" + "=" * 50)
        print("✅ File mapping completed successfully!")
        print(f"📄 Report: {report_path}")
        print(f"💾 Plan: {plan_path}")
        print(f"🔍 Dependencies analyzed: {len(dependencies['typescript_imports'])} TS imports")
        print("\nNext steps:")
        print("1. Review the mapping plan")
        print("2. Resolve any conflicts")
        print("3. Execute the reorganization")
        
    except Exception as e:
        print(f"❌ File mapping failed: {e}")
        raise

if __name__ == "__main__":
    main()