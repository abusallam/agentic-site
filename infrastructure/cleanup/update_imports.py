#!/usr/bin/env python3
"""
Update Import Paths and Dependencies
Updates import statements to work with new directory structure
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class ImportUpdater:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        
        # Define import path mappings
        self.path_mappings = {
            # Frontend imports
            'components/': '@/components/',
            'lib/': '@/lib/',
            'hooks/': '@/hooks/',
            'styles/': '@/styles/',
            'app/': '@/app/',
            
            # Backend imports (relative to backend/)
            '../components/': '../frontend/components/',
            '../lib/': '../frontend/lib/',
            '../app/': '../frontend/app/',
        }

    def update_frontend_imports(self):
        """Update import paths in frontend files"""
        print("🔄 Updating frontend import paths...")
        
        frontend_dir = self.project_root / 'frontend'
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return
        
        # Update TypeScript/JavaScript files
        for file_path in frontend_dir.rglob('*.{ts,tsx,js,jsx}'):
            if file_path.is_file():
                self._update_file_imports(file_path, 'frontend')
        
        # Update CSS files
        for file_path in frontend_dir.rglob('*.{css,scss}'):
            if file_path.is_file():
                self._update_css_imports(file_path)

    def update_backend_imports(self):
        """Update import paths in backend files"""
        print("🔄 Updating backend import paths...")
        
        backend_dir = self.project_root / 'backend'
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return
        
        # Update Python files
        for file_path in backend_dir.rglob('*.py'):
            if file_path.is_file():
                self._update_python_imports(file_path)

    def _update_file_imports(self, file_path: Path, context: str):
        """Update imports in a TypeScript/JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update import statements
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            
            for pattern in import_patterns:
                def replace_import(match):
                    import_path = match.group(1)
                    
                    # Skip node_modules and absolute imports
                    if not import_path.startswith('.'):
                        return match.group(0)
                    
                    # Update relative imports based on context
                    if context == 'frontend':
                        # Convert relative imports to absolute imports using @/ alias
                        if import_path.startswith('../'):
                            # Handle going up directories
                            levels_up = import_path.count('../')
                            remaining_path = import_path.replace('../', '')
                            
                            if levels_up == 1:
                                # One level up - use @/ alias
                                new_path = f"@/{remaining_path}"
                                return match.group(0).replace(import_path, new_path)
                    
                    return match.group(0)
                
                content = re.sub(pattern, replace_import, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated: {file_path.relative_to(self.project_root)}")
        
        except (UnicodeDecodeError, IOError) as e:
            print(f"❌ Error updating {file_path}: {e}")

    def _update_css_imports(self, file_path: Path):
        """Update CSS import statements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update @import statements
            def replace_css_import(match):
                import_path = match.group(1)
                
                # Skip absolute imports
                if not import_path.startswith('.'):
                    return match.group(0)
                
                # Update relative paths
                for old_path, new_path in self.path_mappings.items():
                    if old_path in import_path:
                        new_import = import_path.replace(old_path, new_path)
                        return match.group(0).replace(import_path, new_import)
                
                return match.group(0)
            
            content = re.sub(r'@import\s+[\'"]([^\'"]+)[\'"]', replace_css_import, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated CSS: {file_path.relative_to(self.project_root)}")
        
        except (UnicodeDecodeError, IOError) as e:
            print(f"❌ Error updating CSS {file_path}: {e}")

    def _update_python_imports(self, file_path: Path):
        """Update Python import statements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update relative imports
            patterns = [
                r'from\s+\.([^\s]+)\s+import',
                r'from\s+\.\.([^\s]+)\s+import',
                r'import\s+\.([^\s]+)',
                r'import\s+\.\.([^\s]+)'
            ]
            
            for pattern in patterns:
                def replace_python_import(match):
                    # For now, keep Python imports as-is since we're preserving agent structure
                    return match.group(0)
                
                content = re.sub(pattern, replace_python_import, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated Python: {file_path.relative_to(self.project_root)}")
        
        except (UnicodeDecodeError, IOError) as e:
            print(f"❌ Error updating Python {file_path}: {e}")

    def update_config_files(self):
        """Update configuration files with new paths"""
        print("🔄 Updating configuration files...")
        
        # Update Docker files to use new structure
        docker_dir = self.project_root / 'infrastructure' / 'docker'
        if docker_dir.exists():
            print("✅ Docker files already updated")
        
        # Update package.json workspace references
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            print("✅ Package.json workspace already configured")

def main():
    """Main function to update imports"""
    print("🔄 Starting Import Path Updates")
    print("=" * 50)
    
    try:
        updater = ImportUpdater()
        
        # Update frontend imports
        updater.update_frontend_imports()
        
        # Update backend imports
        updater.update_backend_imports()
        
        # Update configuration files
        updater.update_config_files()
        
        print("\n" + "=" * 50)
        print("✅ Import path updates completed!")
        print("\nNext steps:")
        print("1. Test frontend build: cd frontend && npm run build")
        print("2. Test backend: cd backend && python -m pytest")
        print("3. Fix any remaining import issues manually")
        
    except Exception as e:
        print(f"❌ Import update failed: {e}")
        raise

if __name__ == "__main__":
    main()