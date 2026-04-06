#!/usr/bin/env python3
"""
Verify that the deployment package will include templates.
This script simulates what Zappa or manual packaging should include.
"""

import os
import zipfile
import sys
from pathlib import Path

def check_local_structure():
    """Check if the project structure is correct locally"""
    print("=== Local Project Structure Check ===\n")

    errors = []
    warnings = []

    # Check templates folder
    if os.path.exists('templates'):
        print("✓ templates/ folder exists")
        templates_files = []
        for root, dirs, files in os.walk('templates'):
            for f in files:
                templates_files.append(os.path.join(root, f))
        print(f"  Files: {len(templates_files)}")
        for f in templates_files:
            print(f"    - {f}")

        if not any(f.endswith('.html') for f in templates_files):
            errors.append("No .html files found in templates/")
    else:
        errors.append("templates/ folder is missing!")

    print()

    # Check static folder
    if os.path.exists('static'):
        print("✓ static/ folder exists")
        static_files = []
        for root, dirs, files in os.walk('static'):
            for f in files:
                static_files.append(os.path.join(root, f))
        print(f"  Files: {len(static_files)}")
    else:
        warnings.append("static/ folder is missing (optional but needed for CSS/JS)")

    print()

    # Check key Python files
    required_files = ['app.py', 'auth_integration.py', 'models.py', 'requirements.txt']
    for f in required_files:
        if os.path.exists(f):
            print(f"✓ {f} exists")
        else:
            errors.append(f"Required file missing: {f}")

    print()

    # Check templates in MANIFEST.in
    if os.path.exists('MANIFEST.in'):
        print("✓ MANIFEST.in exists")
        with open('MANIFEST.in', 'r') as f:
            content = f.read()
            if 'recursive-include templates *' in content:
                print("  ✓ templates/** included in MANIFEST.in")
            else:
                warnings.append("MANIFEST.in may not include templates correctly")
    else:
        warnings.append("MANIFEST.in not found (optional but recommended)")

    print()
    print("=== Summary ===")

    if errors:
        print("\n ERRORS (must fix):")
        for e in errors:
            print(f"  ✗ {e}")

    if warnings:
        print("\n WARNINGS:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if not errors:
        print("\n✓ All checks passed! Your project is ready to package.")
        return True
    else:
        print("\n✗ Fix the errors above before deploying.")
        return False

def check_zip_structure(zip_path):
    """Check if an existing ZIP file has correct structure"""
    print(f"\n=== Checking ZIP: {zip_path} ===\n")

    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found")
        return False

    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()

        # Check for templates
        template_files = [n for n in names if n.startswith('templates/') and n.endswith('.html')]
        print(f"Found {len(template_files)} template HTML files:")
        for f in template_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(template_files) > 10:
            print(f"  ... and {len(template_files) - 10} more")

        if not template_files:
            print("ERROR: No template HTML files found in ZIP!")
            print("Contents:", names[:20])
            return False

        # Check for auth.html specifically
        if 'templates/auth.html' in names:
            print("✓ templates/auth.html found")
        else:
            print("✗ templates/auth.html NOT FOUND")

        if 'templates/index.html' in names:
            print("✓ templates/index.html found")
        else:
            print("✗ templates/index.html NOT FOUND")

        # Check structure - templates should not be nested too deep
        for name in names:
            if 'templates' in name:
                parts = name.split('/')
                idx = parts.index('templates')
                depth = len(parts) - idx
                if depth > 2:
                    print(f"WARNING: Deep nesting: {name}")

    print("\n✓ ZIP structure looks correct!")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--zip':
        if len(sys.argv) > 2:
            check_zip_structure(sys.argv[2])
        else:
            # Try common zip names
            for zip_name in ['deployment.zip', 'package.zip', 'app.zip']:
                if os.path.exists(zip_name):
                    check_zip_structure(zip_name)
                    break
    else:
        success = check_local_structure()
        sys.exit(0 if success else 1)
