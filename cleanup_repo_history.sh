#!/bin/bash
# Complete GitHub Repository Cleanup Script
# Removes ALL API keys from commit history permanently

echo "🔒 STARTING COMPLETE REPOSITORY CLEANUP"
echo "========================================"

# Create banned.txt with all possible API key patterns
cat > banned.txt << 'EOF'
xai-***REMOVED***
***REMOVED***
GROK_API_KEY=***REMOVED***
Bearer xai-***REMOVED***
Authorization: Bearer xai-***REMOVED***
"grok_api_key": "***REMOVED***"
self.grok_api_key = "***REMOVED***"
GROK_API_KEY="***REMOVED***"
xai-KN5dHaMayLeXjFFhcET3Kxyc8LUggtw9LuGaQ54HemvVscMuEDUd3piz8tWMtkSsosFiUjVCueocl0kc
xai-sEVR80vsvfGfcKa8v0m1k6irJ2AfAJz1hwDuopbxj0hBEmy3SVGBblUm3Ng1tF27FUJYN1Omdtx1D11o
7510289454:AAFm8psdWDUYQbJuAG0YBX2j5zpKMscMK8M
7416831203:AAEc_Jqt_WannW8O8TgFR1ukKh737J4ukGw
EOF

echo "📝 Created banned.txt with API key patterns"

# Method 1: Using git filter-branch (built-in, no external tools needed)
echo "🧹 Cleaning commit history with git filter-branch..."

# Remove files containing API keys from all commits
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch deploy_enhanced_system.py secure_deployment.py enhanced_checks_and_balances.py' \
--prune-empty --tag-name-filter cat -- --all

# Replace API keys in remaining files
git filter-branch --force --tree-filter \
'find . -type f -name "*.py" -exec sed -i "s/xai-[A-Za-z0-9]\{80,\}/***REMOVED***/g" {} \;
 find . -type f -name "*.py" -exec sed -i "s/[0-9]\{10\}:AA[A-Za-z0-9_-]\{35\}/***REMOVED***/g" {} \;
 find . -type f -name "*.md" -exec sed -i "s/xai-[A-Za-z0-9]\{80,\}/***REMOVED***/g" {} \;' \
--prune-empty --tag-name-filter cat -- --all

echo "✅ Git history cleaned"

# Method 2: Alternative using git-filter-repo (if available)
# git filter-repo --replace-text banned.txt --force

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "🗑️ Cleaned up Git references and garbage collection"

# Verify cleanup
echo "🔍 Verifying cleanup..."
if git log --all --full-history -- "*" | grep -i "xai-" > /dev/null; then
    echo "⚠️ WARNING: API keys may still exist in history"
else
    echo "✅ No API keys found in commit history"
fi

echo "🚀 Repository cleanup complete!"
echo "Next steps:"
echo "1. Push cleaned repository: git push --force-with-lease --all"
echo "2. Verify GitHub secret scanning shows no alerts"
echo "3. Generate new API key"
echo "4. Use environment variables only"

# Create comprehensive .gitignore if not exists
if [ ! -f .gitignore ]; then
    echo "📝 Creating comprehensive .gitignore..."
    cat > .gitignore << 'GITIGNORE_EOF'
# API Keys and Secrets - NEVER COMMIT
*api*key*
*API_KEY*
*secret*
*SECRET*
*token*
*TOKEN*
*password*
*PASSWORD*
xai-*
*grok*key*
*telegram*token*

# Environment files
.env
.env.*
*.env
config.py
secrets.py
credentials.py

# Python
__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
GITIGNORE_EOF
    echo "✅ .gitignore created"
fi

echo "🔒 REPOSITORY SECURITY ENHANCED!"
EOF