#!/usr/bin/env python3
"""
Validation script to verify the organized codebase structure.
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Verify that all expected directories exist."""
    expected_dirs = [
        'components/ui',
        'components/layout',
        'components/features',
        'components/consulting',
        'components/chatbot',
        'tests/unit',
        'tests/integration',
        'tests/e2e',
        'tests/integration/agent',
        'docs/deployment',
        'docs/troubleshooting',
        'docs/project-status',
        'agent/my_adk_agent',
        'scripts',
        'app',
        'lib',
        'hooks',
        'styles',
        'public'
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        return False
    else:
        print("✅ All expected directories exist")
        return True

def check_component_organization():
    """Verify components are properly organized."""
    layout_components = [
        'components/layout/hero-section-enhanced.tsx',
        'components/layout/navigation-enhanced.tsx',
        'components/layout/footer-enhanced.tsx'
    ]
    
    feature_components = [
        'components/features/services-section-enhanced.tsx',
        'components/features/testimonials-section-enhanced.tsx',
        'components/features/features-section.tsx',
        'components/features/contact-section-enhanced.tsx'
    ]
    
    all_components = layout_components + feature_components
    missing_components = []
    
    for component in all_components:
        if not os.path.exists(component):
            missing_components.append(component)
    
    if missing_components:
        print("❌ Missing organized components:")
        for component in missing_components:
            print(f"  - {component}")
        return False
    else:
        print("✅ Components properly organized")
        return True

def check_test_organization():
    """Verify tests are properly organized."""
    expected_test_files = [
        'tests/unit/test_backend.py',
        'tests/unit/test_frontend.py',
        'tests/integration/test_integration.py',
        'tests/integration/test_complete_system.py',
        'tests/integration/test_connection.py',
        'tests/integration/agent/test_agent.py',
        'tests/integration/agent/test_multi_agent_system.py',
        'tests/integration/agent/test_n8n_mcp_integration.py',
        'tests/e2e/test_with_playwright_mcp.py'
    ]
    
    missing_tests = []
    for test_file in expected_test_files:
        if not os.path.exists(test_file):
            missing_tests.append(test_file)
    
    if missing_tests:
        print("❌ Missing organized test files:")
        for test_file in missing_tests:
            print(f"  - {test_file}")
        return False
    else:
        print("✅ Tests properly organized")
        return True

def check_documentation_organization():
    """Verify documentation is properly organized."""
    expected_docs = [
        'docs/deployment/DEPLOYMENT.md',
        'docs/deployment/DEPLOYMENT_READY.md',
        'docs/deployment/VPS_DEPLOYMENT_SUCCESS.md',
        'docs/troubleshooting/TROUBLESHOOTING.md',
        'docs/troubleshooting/SSL_TROUBLESHOOTING.md',
        'docs/project-status/PROJECT_STATUS_FINAL.md',
        'docs/project-status/PROJECT_SUMMARY.md'
    ]
    
    missing_docs = []
    for doc_file in expected_docs:
        if not os.path.exists(doc_file):
            missing_docs.append(doc_file)
    
    if missing_docs:
        print("❌ Missing organized documentation:")
        for doc_file in missing_docs:
            print(f"  - {doc_file}")
        return False
    else:
        print("✅ Documentation properly organized")
        return True

def check_essential_files():
    """Verify essential files are preserved."""
    essential_files = [
        'README.md',
        'CONTRIBUTING.md',
        'package.json',
        'next.config.mjs',
        'tailwind.config.ts',
        'tsconfig.json',
        '.gitignore',
        'docker-compose.yml',
        'Dockerfile'
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing essential files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✅ All essential files preserved")
        return True

def main():
    """Run all validation checks."""
    print("🔍 Validating organized codebase structure...\n")
    
    checks = [
        check_directory_structure,
        check_component_organization,
        check_test_organization,
        check_documentation_organization,
        check_essential_files
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All validation checks passed! Codebase is properly organized.")
        return 0
    else:
        print("❌ Some validation checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())