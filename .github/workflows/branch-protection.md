# Branch Protection Setup Guide

This document outlines the recommended branch protection rules for the Lumni repository.

## Recommended Settings

### For `main` branch (or `master`):

1. **Go to**: Settings → Branches → Add rule

2. **Branch name pattern**: `main` (or `master`)

3. **Enable the following protections**:
   - ✅ Require a pull request before merging
     - Require approvals: **1**
     - Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
     - Required status checks:
       - `Test Python 3.11`
       - `Test Python 3.12`
       - `Lint and Format Check`
       - `Type Check`
     - Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history
   - ✅ Include administrators
   - ✅ Restrict who can push to matching branches
     - (Optional) Restrict to specific teams/users

4. **Rules for pull requests**:
   - Require pull request reviews before merging
   - Required number of reviewers: **1**
   - Dismiss stale reviews when new commits are pushed

## Additional Recommendations

- **Create a `develop` branch** for ongoing development
- **Use feature branches** for new features (`feature/feature-name`)
- **Use fix branches** for bug fixes (`fix/bug-description`)
- **Use release branches** for releases (`release/v2.1.0`)

## Branch Naming Convention

- `main` / `master` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical production fixes
- `release/*` - Release preparation

## Setting Up via GitHub CLI (Optional)

If you have GitHub CLI installed:

```bash
gh api repos/artemis-sophia/lumni/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Test Python 3.11","Test Python 3.12","Lint and Format Check"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

Note: Adjust the branch name and contexts based on your CI workflow names.

