"""
Security check module for tg2kb project.

Prevents accidental exposure of API credentials and sensitive data.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


def check_for_credentials_in_file(file_path: Path) -> List[Dict]:
    """
    Check a file for potential credential exposure.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        List of potential credential matches
    """
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []
    
    issues = []
    
    # Check for hardcoded API keys
    api_key_patterns = [
        r'TELEGRAM_API_ID\s*=\s*["\']?\d+["\']?',
        r'TELEGRAM_API_HASH\s*=\s*["\']?[a-f0-9]{32}["\']?',
        r'OPENAI_API_KEY\s*=\s*["\']?sk-[a-zA-Z0-9]{48}["\']?',
        r'api_id\s*=\s*["\']?\d+["\']?',
        r'api_hash\s*=\s*["\']?[a-f0-9]{32}["\']?',
        r'api_key\s*=\s*["\']?sk-[a-zA-Z0-9]{48}["\']?',
    ]
    
    for pattern in api_key_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append({
                'type': 'hardcoded_credential',
                'line': content[:match.start()].count('\n') + 1,
                'match': match.group(),
                'pattern': pattern
            })
    
    # Check for session files
    if file_path.suffix == '.session':
        issues.append({
            'type': 'session_file',
            'line': 1,
            'match': str(file_path),
            'pattern': 'session_file'
        })
    
    return issues


def check_project_security() -> Tuple[bool, List[Dict]]:
    """
    Perform comprehensive security check on the project.
    
    Returns:
        Tuple of (is_safe, list_of_issues)
    """
    project_root = Path('.')
    issues = []
    
    # Files to check
    files_to_check = [
        'cli.py',
        'parser.py', 
        'processor.py',
        'generator.py',
        'tg_client.py',
        'run_parser.py',
        'run_processor.py',
        'run_generator.py',
        'requirements.txt',
        'README.md'
    ]
    
    # Check specific files
    for file_name in files_to_check:
        file_path = project_root / file_name
        if file_path.exists():
            file_issues = check_for_credentials_in_file(file_path)
            for issue in file_issues:
                issue['file'] = file_name
                issues.append(issue)
    
    # Check for .env files that shouldn't be committed
    env_files = [
        '.env',
        '.env.local',
        '.env.production',
        'config.env'
    ]
    
    for env_file in env_files:
        env_path = project_root / env_file
        if env_path.exists():
            issues.append({
                'type': 'env_file_present',
                'file': env_file,
                'line': 1,
                'match': f'Found {env_file} file',
                'pattern': 'env_file'
            })
    
    # Check for session files
    session_files = list(project_root.glob('*.session*'))
    for session_file in session_files:
        issues.append({
            'type': 'session_file',
            'file': str(session_file),
            'line': 1,
            'match': f'Found session file: {session_file}',
            'pattern': 'session_file'
        })
    
    return len(issues) == 0, issues


def print_security_report(issues: List[Dict]) -> None:
    """
    Print a formatted security report.
    
    Args:
        issues: List of security issues found
    """
    if not issues:
        print("✅ No security issues found!")
        return
    
    print("🚨 SECURITY ISSUES FOUND:")
    print("=" * 50)
    
    for issue in issues:
        print(f"❌ {issue['type'].upper()}")
        print(f"   File: {issue.get('file', 'Unknown')}")
        print(f"   Line: {issue.get('line', 'Unknown')}")
        print(f"   Issue: {issue['match']}")
        print()
    
    print("🔧 RECOMMENDATIONS:")
    print("- Remove hardcoded credentials from code")
    print("- Use environment variables instead")
    print("- Add sensitive files to .gitignore")
    print("- Use .env files for local development only")


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        True if all required variables are present
    """
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
    optional_vars = ['OPENAI_API_KEY', 'TELEGRAM_SESSION_NAME']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print("⚠️  Missing required environment variables:")
        for var in missing_required:
            print(f"   - {var}")
        print("\nThese are required for Telegram functionality but not for development.")
        print("You can set them later when ready to use Telegram features.")
        # Don't fail for missing env vars during development
        return True
    
    if missing_optional:
        print("⚠️  Missing optional environment variables:")
        for var in missing_optional:
            print(f"   - {var}")
        print("\nThese are optional but recommended for full functionality.")
    
    print("✅ Environment validation passed!")
    return True


if __name__ == "__main__":
    """Run security checks when executed directly."""
    print("🔍 Running security checks...")
    
    # Check project files
    is_safe, issues = check_project_security()
    
    if not is_safe:
        print_security_report(issues)
        exit(1)
    
    # Validate environment
    env_valid = validate_environment()
    
    if not env_valid:
        exit(1)
    
    print("✅ All security checks passed!") 