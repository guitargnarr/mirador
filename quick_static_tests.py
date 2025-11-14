#!/usr/bin/env python3
"""
Quick Static Tests for Mirador - No Ollama Required
Tests file structure, syntax, and configuration without running models
"""

import os
import sys
import subprocess
from pathlib import Path
import json

class MiradorStaticTests:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def test_pass(self, name):
        self.passed += 1
        print(f"✅ PASS: {name}")

    def test_fail(self, name, reason=""):
        self.failed += 1
        print(f"❌ FAIL: {name}")
        if reason:
            print(f"   Reason: {reason}")

    def test_warn(self, name, reason=""):
        self.warnings += 1
        print(f"⚠️  WARN: {name}")
        if reason:
            print(f"   Reason: {reason}")

    def test_directory_structure(self):
        """Test that required directories exist"""
        self.print_header("Directory Structure Tests")

        required_dirs = [
            'bin',
            'tests',
            'docs',
            'config',
            'docker'
        ]

        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.test_pass(f"Directory exists: {dir_name}")
            else:
                self.test_fail(f"Directory missing: {dir_name}")

    def test_key_files(self):
        """Test that key files exist"""
        self.print_header("Key Files Tests")

        key_files = [
            'README.md',
            'CLAUDE.md',
            'requirements.txt',
            'bin/mirador-smart-v2',
            'tests/run_tests.sh',
            'docker/Dockerfile',
            'docker/docker-compose.yml'
        ]

        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                self.test_pass(f"File exists: {file_path}")
            else:
                self.test_fail(f"File missing: {file_path}")

    def test_shell_scripts_syntax(self):
        """Test shell script syntax"""
        self.print_header("Shell Script Syntax Tests")

        scripts_to_test = [
            'bin/mirador-smart-v2',
            'tests/run_tests.sh',
            'docker/install.sh',
        ]

        for script in scripts_to_test:
            script_path = self.project_root / script
            if not script_path.exists():
                self.test_warn(f"Script not found: {script}")
                continue

            try:
                result = subprocess.run(
                    ['bash', '-n', str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.test_pass(f"Syntax OK: {script}")
                else:
                    self.test_fail(f"Syntax error: {script}", result.stderr)
            except Exception as e:
                self.test_fail(f"Error testing: {script}", str(e))

    def test_python_files_syntax(self):
        """Test Python file syntax"""
        self.print_header("Python File Syntax Tests")

        python_files = [
            'tests/test_chains.py',
            'tests/test_models.py',
            'tests/test_performance.py',
            'tests/mirador_test_suite.py',
            'docker/mirador_server.py'
        ]

        for py_file in python_files:
            file_path = self.project_root / py_file
            if not file_path.exists():
                self.test_warn(f"Python file not found: {py_file}")
                continue

            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.test_pass(f"Syntax OK: {py_file}")
                else:
                    self.test_fail(f"Syntax error: {py_file}", result.stderr)
            except Exception as e:
                self.test_fail(f"Error testing: {py_file}", str(e))

    def test_documentation(self):
        """Test documentation files"""
        self.print_header("Documentation Tests")

        doc_files = [
            'README.md',
            'CLAUDE.md',
            'docs/ARCHITECTURE.md',
            'docs/PROMPT_LIBRARY.md',
            'docker/DOCKER_DEPLOYMENT.md'
        ]

        for doc_file in doc_files:
            file_path = self.project_root / doc_file
            if file_path.exists():
                size = file_path.stat().st_size
                if size > 100:  # At least 100 bytes
                    self.test_pass(f"Documentation exists: {doc_file} ({size} bytes)")
                else:
                    self.test_warn(f"Documentation too small: {doc_file}")
            else:
                self.test_fail(f"Documentation missing: {doc_file}")

    def test_requirements(self):
        """Test requirements.txt"""
        self.print_header("Requirements Tests")

        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            self.test_pass("requirements.txt exists")

            # Check for key dependencies
            with open(req_file, 'r') as f:
                content = f.read()

            key_deps = ['numpy', 'pandas', 'pyyaml', 'rich']
            for dep in key_deps:
                if dep in content.lower():
                    self.test_pass(f"Dependency listed: {dep}")
                else:
                    self.test_warn(f"Dependency not found: {dep}")
        else:
            self.test_fail("requirements.txt missing")

    def test_docker_config(self):
        """Test Docker configuration"""
        self.print_header("Docker Configuration Tests")

        # Test Dockerfile
        dockerfile = self.project_root / 'docker' / 'Dockerfile'
        if dockerfile.exists():
            self.test_pass("Dockerfile exists")
            with open(dockerfile, 'r') as f:
                content = f.read()
                if 'FROM' in content:
                    self.test_pass("Dockerfile has FROM instruction")
                if 'WORKDIR' in content:
                    self.test_pass("Dockerfile has WORKDIR instruction")
        else:
            self.test_fail("Dockerfile missing")

        # Test docker-compose.yml
        compose_file = self.project_root / 'docker' / 'docker-compose.yml'
        if compose_file.exists():
            self.test_pass("docker-compose.yml exists")
        else:
            self.test_fail("docker-compose.yml missing")

    def run_all_tests(self):
        """Run all static tests"""
        print("\n" + "="*60)
        print("  MIRADOR STATIC TEST SUITE")
        print("  (No Ollama Required)")
        print("="*60)

        self.test_directory_structure()
        self.test_key_files()
        self.test_shell_scripts_syntax()
        self.test_python_files_syntax()
        self.test_documentation()
        self.test_requirements()
        self.test_docker_config()

        # Print summary
        self.print_header("TEST SUMMARY")
        print(f"✅ Passed:   {self.passed}")
        print(f"❌ Failed:   {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"📊 Total:    {self.passed + self.failed + self.warnings}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return 1

if __name__ == "__main__":
    tester = MiradorStaticTests()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
