#!/usr/bin/env python3
"""
Project Structure Analysis Tool
Compares root directory with agentic-site folder to identify cleanup requirements
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ProjectAnalyzer:
    def __init__(self, root_path: str = ".", agentic_path: str = "agentic-site"):
        self.root_path = Path(root_path)
        self.agentic_path = Path(agentic_path)
        self.analysis_results = {
            "duplicates": [],
            "unique_to_agentic": [],
            "unique_to_root": [],
            "mcp_files": [],
            "conflicts": [],
            "summary": {}
        }
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "ERROR"
    
    def get_directory_files(self, base_path: Path) -> Dict[str, Dict]:
        """Get all files in a directory with their metadata"""
        files = {}
        if not base_path.exists():
            return files
            
        for file_path in base_path.rglob('*'):
            if file_path.is_file():
                # Skip certain directories and files
                skip_dirs = {'.git', 'node_modules', '.next', '__pycache__', '.venv', 'dist'}
                if any(part in skip_dirs for part in file_path.parts):
                    continue
                
                relative_path = file_path.relative_to(base_path)
                files[str(relative_path)] = {
                    'full_path': str(file_path),
                    'size': file_path.stat().st_size,
                    'hash': self.get_file_hash(file_path)
                }
        return files
    
    def identify_mcp_files(self, files: Dict[str, Dict]) -> List[str]:
        """Identify MCP-related files"""
        mcp_patterns = [
            'n8n-mcp',
            'mcp',
            'agent/n8n_mcp_agent',
            'agent/my_adk_agent',
            '.python-version',
            'pyproject.toml',
            'uv.lock'
        ]
        
        mcp_files = []
        for file_path, info in files.items():
            if any(pattern in file_path for pattern in mcp_patterns):
                mcp_files.append(file_path)
        
        return mcp_files
    
    def analyze_structure(self):
        """Main analysis function"""
        print("🔍 Analyzing project structure...")
        
        # Get files from both directories
        root_files = self.get_directory_files(self.root_path)
        agentic_files = self.get_directory_files(self.agentic_path)
        
        print(f"📁 Root directory: {len(root_files)} files")
        print(f"📁 Agentic-site directory: {len(agentic_files)} files")
        
        # Find duplicates and unique files
        root_set = set(root_files.keys())
        agentic_set = set(agentic_files.keys())
        
        common_files = root_set & agentic_set
        unique_to_root = root_set - agentic_set
        unique_to_agentic = agentic_set - root_set
        
        # Analyze duplicates
        for file_path in common_files:
            root_info = root_files[file_path]
            agentic_info = agentic_files[file_path]
            
            identical = root_info['hash'] == agentic_info['hash']
            
            duplicate_info = {
                'file_path': file_path,
                'root_path': root_info['full_path'],
                'agentic_path': agentic_info['full_path'],
                'identical': identical,
                'root_size': root_info['size'],
                'agentic_size': agentic_info['size'],
                'action': 'keep_root' if identical else 'manual_review'
            }
            
            if identical:
                self.analysis_results['duplicates'].append(duplicate_info)
            else:
                self.analysis_results['conflicts'].append(duplicate_info)
        
        # Store unique files
        self.analysis_results['unique_to_root'] = list(unique_to_root)
        self.analysis_results['unique_to_agentic'] = list(unique_to_agentic)
        
        # Identify MCP files
        all_files = {**root_files, **agentic_files}
        self.analysis_results['mcp_files'] = self.identify_mcp_files(all_files)
        
        # Create summary
        self.analysis_results['summary'] = {
            'total_root_files': len(root_files),
            'total_agentic_files': len(agentic_files),
            'identical_duplicates': len(self.analysis_results['duplicates']),
            'conflicting_files': len(self.analysis_results['conflicts']),
            'unique_to_root': len(unique_to_root),
            'unique_to_agentic': len(unique_to_agentic),
            'mcp_files_count': len(self.analysis_results['mcp_files'])
        }
        
        return self.analysis_results
    
    def print_analysis_report(self):
        """Print a detailed analysis report"""
        results = self.analysis_results
        summary = results['summary']
        
        print("\n" + "="*60)
        print("📊 PROJECT STRUCTURE ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📈 SUMMARY:")
        print(f"  • Root directory files: {summary['total_root_files']}")
        print(f"  • Agentic-site files: {summary['total_agentic_files']}")
        print(f"  • Identical duplicates: {summary['identical_duplicates']}")
        print(f"  • Conflicting files: {summary['conflicting_files']}")
        print(f"  • Unique to root: {summary['unique_to_root']}")
        print(f"  • Unique to agentic-site: {summary['unique_to_agentic']}")
        print(f"  • MCP-related files: {summary['mcp_files_count']}")
        
        if results['conflicts']:
            print(f"\n⚠️  CONFLICTING FILES (need manual review):")
            for conflict in results['conflicts'][:10]:  # Show first 10
                print(f"  • {conflict['file_path']}")
                print(f"    Root: {conflict['root_size']} bytes")
                print(f"    Agentic: {conflict['agentic_size']} bytes")
        
        if results['unique_to_agentic']:
            print(f"\n📦 UNIQUE FILES IN AGENTIC-SITE (will be moved):")
            for file_path in results['unique_to_agentic'][:10]:  # Show first 10
                print(f"  • {file_path}")
        
        if results['mcp_files']:
            print(f"\n🔧 MCP-RELATED FILES (will be moved to VPS):")
            for file_path in results['mcp_files'][:10]:  # Show first 10
                print(f"  • {file_path}")
        
        print(f"\n✅ CLEANUP ACTIONS REQUIRED:")
        print(f"  1. Remove {summary['identical_duplicates']} identical duplicate files")
        print(f"  2. Review and resolve {summary['conflicting_files']} conflicting files")
        print(f"  3. Move {summary['unique_to_agentic']} unique files from agentic-site")
        print(f"  4. Organize {summary['mcp_files_count']} MCP files on VPS")
        print(f"  5. Remove agentic-site folder after cleanup")
    
    def save_analysis(self, output_file: str = "project_analysis.json"):
        """Save analysis results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        print(f"\n💾 Analysis saved to: {output_file}")

def main():
    analyzer = ProjectAnalyzer()
    
    # Check if agentic-site exists
    if not analyzer.agentic_path.exists():
        print("❌ agentic-site folder not found!")
        return
    
    # Run analysis
    analyzer.analyze_structure()
    analyzer.print_analysis_report()
    analyzer.save_analysis()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Review the analysis results")
    print(f"  2. Backup important files before cleanup")
    print(f"  3. Execute cleanup process")
    print(f"  4. Organize MCP files on VPS")

if __name__ == "__main__":
    main()