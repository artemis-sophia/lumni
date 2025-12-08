# GitHub Models API Token Setup Guide

## Research Findings

After thorough investigation, here are the key findings:

### Token Type Required
- **Classic Personal Access Token (PAT)** - NOT fine-grained token
- Fine-grained tokens do NOT support the `models` permission
- The `models:read` permission is not available in fine-grained token CLI tool or web UI

### Account Access
- ✅ Account verified to have access to GitHub Models API
- ✅ API calls return 200 with valid classic token
- Account type: Personal account (verified via `gh auth status`)

### Working Token Scopes
Verified working token has these scopes:
- `admin:public_key`
- `gist`
- `read:org`
- `repo` (likely the key scope for Models API access)

## How to Create a Token

### Step 1: Create Classic Personal Access Token

1. Navigate to: https://github.com/settings/tokens
2. Click: **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a descriptive name: `Lumni Models Token`
4. Set expiration (recommended: 90 days or custom)
5. **Select scopes:**
   - ✅ **`repo`** - Full control of private repositories (required for Models API)
   - ✅ **`gist`** - Optional, for gist access
   - ✅ **`read:org`** - Optional, for organization access
6. Click **"Generate token"**
7. **Copy the token immediately** - it won't be shown again!

### Step 2: Add Token to Project

Add the token to your `.env` file:

```bash
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Verify Token Works

**Option 1: Use the test script (Recommended)**

```bash
npm run test:github
```

Or directly:
```bash
./scripts/test-github-api.sh
```

**Option 2: Manual test with .env loaded**

First, load the environment variables:
```bash
source scripts/load-env.sh
```

Then test:
```bash
curl -X POST https://models.github.ai/inference/chat/completions \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }'
```

**Option 3: Direct test (token in command)**

```bash
curl -X POST https://models.github.ai/inference/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }'
```

Expected: JSON response with `choices` array containing the model's response.

## Why Fine-Grained Tokens Don't Work

1. **CLI Tool Limitation:** The `github-fine-grained-token-client` tool does not recognize `models:read` as a valid permission
2. **Web UI Limitation:** The Models permission is not available in the fine-grained token creation UI
3. **API Requirement:** GitHub Models API (`models.github.ai`) requires classic token authentication

## Alternative: Using GitHub CLI Token

If you have GitHub CLI (`gh`) authenticated, you can use its token:

```bash
# Get the token
gh auth token

# Test it works
curl -X POST https://models.github.ai/inference/chat/completions \
  -H "Authorization: Bearer $(gh auth token)" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-4o","messages":[{"role":"user","content":"test"}]}'
```

However, for production use, create a dedicated classic token with minimal required scopes.

## Troubleshooting

### Error: "No access to model"
- Token may not have `repo` scope
- Token may be expired
- Account may not have access to that specific model

### Error: "Unauthorized"
- Token is invalid or expired
- Token doesn't have required scopes
- Token is a fine-grained token (use classic token instead)

### Token Not Working
1. Verify token is classic (starts with `ghp_` or `github_pat_`)
2. Check token has `repo` scope
3. Verify token hasn't expired
4. Test token directly with curl command above

## Summary

- ✅ **Use Classic Personal Access Token**
- ✅ **Requires `repo` scope (minimum)**
- ✅ **Account has access verified**
- ❌ **Fine-grained tokens do NOT work**
- ❌ **`models:read` permission not available in fine-grained tokens**

