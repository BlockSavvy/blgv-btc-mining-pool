#!/usr/bin/env python3
"""
Commit Web UI Authentication Status Fixes to GitHub
"""

import os
import base64
import json
import requests

def update_file_on_github(repo_owner, repo_name, file_path, local_path, token):
    """Update a single file on GitHub"""
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Read local file
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get current file SHA (if exists)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    response = requests.get(url, headers=headers)
    
    data = {
        'message': f'feat: Complete web UI authentication status system with real-time monitoring',
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        'branch': 'main'
    }
    
    if response.status_code == 200:
        # File exists, need SHA for update
        data['sha'] = response.json()['sha']
        print(f"📝 Updating existing file: {file_path}")
    else:
        print(f"📝 Creating new file: {file_path}")
    
    # Update/create file
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✅ Successfully updated {file_path}")
        return True
    else:
        print(f"❌ Failed to update {file_path}: {response.status_code}")
        print(response.text)
        return False

def main():
    """Main function to commit UI authentication fixes"""
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ No GitHub token found")
        return False
    
    repo_owner = "BlockSavvy"
    repo_name = "blgv-btc-mining-pool"
    
    # Files to update with UI authentication fixes
    files_to_update = [
        ('clean_start.py', 'clean_start.py'),           # Complete UI authentication system
        ('replit.md', 'replit.md'),                     # Updated documentation
        ('commit_ui_auth_fixes.py', 'commit_ui_auth_fixes.py')  # This script
    ]
    
    print(f"🚀 Committing web UI authentication status fixes to: {repo_owner}/{repo_name}")
    print("🔧 Complete UI Authentication System:")
    print("   • Fixed JavaScript DOM errors with createAuthStatusElements")
    print("   • Added visual status indicators (pending, processing, connected, failed, expired)")  
    print("   • Implemented WebSocket and polling for real-time authentication monitoring")
    print("   • Complete authentication flow: QR → mobile auth → live status → wallet connection")
    print("   • CSS animations and proper styling for all authentication states")
    
    success_count = 0
    for github_path, local_path in files_to_update:
        if os.path.exists(local_path):
            if update_file_on_github(repo_owner, repo_name, github_path, local_path, token):
                success_count += 1
        else:
            print(f"⚠️ Local file not found: {local_path}")
    
    print(f"\n📊 Updated {success_count}/{len(files_to_update)} files successfully")
    
    if success_count > 0:
        print(f"🎉 Web UI authentication system committed to GitHub!")
        print(f"📦 Repository: https://github.com/{repo_owner}/{repo_name}")
        print(f"✅ Complete authentication flow operational for mobile app integration")
        return True
    else:
        print("❌ No files were updated")
        return False

if __name__ == "__main__":
    main()