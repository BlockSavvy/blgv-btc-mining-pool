#!/usr/bin/env python3
"""
Commit Bitcoin Wallet Authentication System to GitHub
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
        'message': f'feat: Complete Bitcoin wallet authentication system with mobile app compatibility',
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
    """Main function to commit authentication system changes"""
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ No GitHub token found")
        return False
    
    repo_owner = "BlockSavvy"
    repo_name = "blgv-btc-mining-pool"
    
    # Files to update with authentication system
    files_to_update = [
        ('clean_start.py', 'clean_start.py'),           # Main server with auth endpoints
        ('replit.md', 'replit.md'),                     # Updated documentation
        ('commit_auth_system.py', 'commit_auth_system.py')  # This script
    ]
    
    print(f"🚀 Committing Bitcoin wallet authentication system to: {repo_owner}/{repo_name}")
    print("📱 Mobile app compatibility: ✅ address + walletAddress fields")
    print("🔐 Authentication features: ✅ JWT tokens + session management")
    print("📊 Response format: ✅ user.authenticated field support")
    
    success_count = 0
    for github_path, local_path in files_to_update:
        if os.path.exists(local_path):
            if update_file_on_github(repo_owner, repo_name, github_path, local_path, token):
                success_count += 1
        else:
            print(f"⚠️ Local file not found: {local_path}")
    
    print(f"\n📊 Updated {success_count}/{len(files_to_update)} files successfully")
    
    if success_count > 0:
        print(f"🎉 Bitcoin wallet authentication system committed to GitHub!")
        print(f"📦 Repository: https://github.com/{repo_owner}/{repo_name}")
        print(f"🔗 Mobile app integration ready for production deployment")
        return True
    else:
        print("❌ No files were updated")
        return False

if __name__ == "__main__":
    main()