# Git Branch Management Strategy

## Overview

This document outlines the comprehensive git workflow and branch management strategy for the Agentic AI Platform. It provides clear guidelines for developers and AI agents working on the project.

## Branch Structure

### Main Branches

#### `main` (Production Branch)
- **Purpose**: Production-ready code deployed to https://consulting.sa
- **Protection**: Protected branch with strict merge requirements
- **Deployment**: Automatically deployed to production VPS
- **Access**: Only merge after thorough testing in development
- **Stability**: Must always be in deployable state

#### `develop` (Development Branch)
- **Purpose**: Integration branch for development work
- **Deployment**: Deployed to https://dev.consulting.sa
- **Testing**: All features tested here before production
- **Access**: Primary branch for all development work
- **Stability**: Should be stable but allows for experimental features

### Supporting Branches

#### Feature Branches (`feature/*`)
```
feature/user-authentication
feature/chatbot-improvements
feature/payment-integration
feature/ai-agent-enhancements
```

- **Purpose**: Develop new features or enhancements
- **Naming**: `feature/descriptive-name`
- **Base**: Created from `develop`
- **Merge**: Back to `develop` via Pull Request
- **Lifetime**: Short-lived (days to weeks)

#### Hotfix Branches (`hotfix/*`)
```
hotfix/critical-security-patch
hotfix/payment-gateway-fix
hotfix/ssl-certificate-renewal
```

- **Purpose**: Critical fixes for production issues
- **Naming**: `hotfix/issue-description`
- **Base**: Created from `main`
- **Merge**: To both `main` and `develop`
- **Lifetime**: Very short-lived (hours to days)

#### Release Branches (`release/*`)
```
release/v1.2.0
release/v2.0.0-beta
```

- **Purpose**: Prepare releases and final testing
- **Naming**: `release/version-number`
- **Base**: Created from `develop`
- **Merge**: To `main` and back to `develop`
- **Lifetime**: Short-lived (days)

## Workflow Diagrams

### Standard Development Flow
```
main ────────────────────────────────────────────────────────────
     \                                                          /
      \                                                        /
develop ──────────────────────────────────────────────────────
         \              \                    \               /
          \              \                    \             /
feature/A  ──────────────                     \           /
                        \                      \         /
feature/B ────────────────────────────────      \       /
                                         \      \     /
feature/C ──────────────────────────────────────────
```

### Hotfix Flow
```
main ────────────────●─────────────────────────────────────
                     │\                                   /
                     │ \                                 /
                     │  hotfix/critical-fix ───────────
                     │                                /
develop ─────────────●───────────────────────────────
```

## Branch Management Rules

### Protection Rules

#### Main Branch Protection
- ✅ **Require pull request reviews**: Minimum 1 reviewer
- ✅ **Require status checks**: All CI/CD checks must pass
- ✅ **Require up-to-date branches**: Must be current with main
- ✅ **Include administrators**: No direct pushes allowed
- ✅ **Require linear history**: No merge commits

#### Develop Branch Protection
- ✅ **Require pull request reviews**: Optional for small changes
- ✅ **Require status checks**: Basic CI checks must pass
- ✅ **Allow force pushes**: For development flexibility
- ✅ **Allow deletions**: For cleanup purposes

### Merge Strategies

#### Feature to Develop
- **Strategy**: Squash and merge
- **Reason**: Clean history, single commit per feature
- **Process**: Squash all feature commits into one

#### Develop to Main
- **Strategy**: Merge commit
- **Reason**: Preserve development history
- **Process**: Create merge commit with detailed message

#### Hotfix to Main
- **Strategy**: Fast-forward merge
- **Reason**: Immediate deployment needed
- **Process**: Direct merge after testing

## Development Workflows

### 🚨 Critical Decision Point

**Before starting ANY work, ask:**
> "Should I work on the **development branch** (safe testing) or **production branch** (live system)?"

### Standard Feature Development

#### Step 1: Create Feature Branch
```bash
# Switch to develop branch
git checkout develop

# Pull latest changes
git pull origin develop

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Push branch to remote
git push -u origin feature/your-feature-name
```

#### Step 2: Development Work
```bash
# Make your changes
# ... code changes ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user authentication system

- Implement login/logout functionality
- Add password reset capability
- Create user profile management
- Add comprehensive tests
- Update documentation"

# Push changes
git push origin feature/your-feature-name
```

#### Step 3: Create Pull Request
```markdown
## Pull Request Template

### Description
Brief description of changes made.

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Deployed to development environment

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes introduced
```

#### Step 4: Code Review Process
1. **Automated Checks**: CI/CD pipeline runs
2. **Peer Review**: Team member reviews code
3. **Testing**: Deploy to development environment
4. **Approval**: Reviewer approves changes
5. **Merge**: Squash and merge to develop

### Hotfix Workflow

#### Emergency Production Fix
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue-fix

# Make minimal fix
# ... fix code ...

# Test thoroughly
npm test
npm run build

# Commit fix
git commit -m "hotfix: resolve critical payment processing issue

- Fix null pointer exception in payment handler
- Add validation for payment data
- Update error handling
- Tested on staging environment"

# Push hotfix
git push -u origin hotfix/critical-issue-fix
```

#### Hotfix Deployment
```bash
# Merge to main (after review)
git checkout main
git merge hotfix/critical-issue-fix
git push origin main

# Merge back to develop
git checkout develop
git merge hotfix/critical-issue-fix
git push origin develop

# Delete hotfix branch
git branch -d hotfix/critical-issue-fix
git push origin --delete hotfix/critical-issue-fix
```

### Release Workflow

#### Preparing a Release
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version numbers
# ... update package.json, version files ...

# Final testing and bug fixes
# ... testing and minor fixes ...

# Commit release preparation
git commit -m "chore: prepare release v1.2.0

- Update version numbers
- Update changelog
- Final bug fixes
- Documentation updates"

# Push release branch
git push -u origin release/v1.2.0
```

#### Finalizing Release
```bash
# Merge to main
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge release/v1.2.0
git push origin develop

# Delete release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

## Commit Message Standards

### Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples
```bash
# Feature commit
git commit -m "feat(auth): add OAuth2 integration

- Implement Google OAuth2 login
- Add user profile synchronization
- Update authentication middleware
- Add comprehensive tests

Closes #123"

# Bug fix commit
git commit -m "fix(payment): resolve Stripe webhook validation

- Fix webhook signature verification
- Add proper error handling
- Update webhook endpoint security
- Add monitoring for failed webhooks

Fixes #456"

# Documentation commit
git commit -m "docs: update API documentation

- Add new endpoint documentation
- Update authentication examples
- Fix typos in README
- Add troubleshooting section"
```

## Environment-Specific Workflows

### Development Environment Workflow
```bash
# 1. Work on develop branch
git checkout develop

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push to develop
git push origin develop

# 4. Deploy to development
./infrastructure/scripts/deploy-dev-vps.sh

# 5. Test at https://dev.consulting.sa
# 6. Validate functionality
# 7. Ready for production merge
```

### Production Environment Workflow
```bash
# 1. Ensure develop is thoroughly tested
# 2. Create pull request: develop → main
# 3. Code review and approval
# 4. Merge to main
git checkout main
git merge develop
git push origin main

# 5. Automatic production deployment
# 6. Monitor https://consulting.sa
# 7. Verify functionality
```

## Code Review Guidelines

### Review Checklist

#### Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

#### Code Quality
- [ ] Code is readable and maintainable
- [ ] Follows project conventions
- [ ] No code duplication
- [ ] Proper variable/function naming

#### Testing
- [ ] Unit tests are included
- [ ] Tests cover edge cases
- [ ] Integration tests pass
- [ ] Manual testing completed

#### Security
- [ ] No security vulnerabilities
- [ ] Input validation present
- [ ] Authentication/authorization correct
- [ ] No sensitive data exposed

#### Documentation
- [ ] Code is properly commented
- [ ] Documentation updated
- [ ] README updated if needed
- [ ] API documentation current

### Review Process
1. **Automated Checks**: CI/CD pipeline validates code
2. **Self Review**: Author reviews their own changes
3. **Peer Review**: Team member conducts thorough review
4. **Testing**: Deploy to development environment
5. **Approval**: Reviewer approves or requests changes
6. **Merge**: Code is merged after approval

## Branch Cleanup

### Regular Maintenance
```bash
# List all branches
git branch -a

# Delete merged feature branches
git branch -d feature/completed-feature

# Delete remote tracking branches
git remote prune origin

# Clean up local references
git gc --prune=now
```

### Automated Cleanup
```bash
# Delete branches merged to develop
git branch --merged develop | grep -v develop | xargs -n 1 git branch -d

# Delete remote branches that no longer exist
git remote prune origin
```

## Troubleshooting

### Common Issues

#### Merge Conflicts
```bash
# When conflicts occur during merge
git status
# Edit conflicted files
git add .
git commit -m "resolve: merge conflicts in feature branch"
```

#### Accidental Commits to Wrong Branch
```bash
# Move commits to correct branch
git log --oneline -n 5  # Find commit hash
git checkout correct-branch
git cherry-pick <commit-hash>
git checkout wrong-branch
git reset --hard HEAD~1  # Remove from wrong branch
```

#### Lost Changes
```bash
# Find lost commits
git reflog
git checkout <commit-hash>
git checkout -b recovery-branch
```

### Emergency Procedures

#### Rollback Production
```bash
# Quick rollback to previous version
git checkout main
git reset --hard HEAD~1
git push --force-with-lease origin main
# Deploy immediately
```

#### Fix Broken Develop Branch
```bash
# Reset develop to last known good state
git checkout develop
git reset --hard origin/main
git push --force-with-lease origin develop
```

## Best Practices Summary

### ✅ Do's
- Always work on feature branches
- Write descriptive commit messages
- Test thoroughly before merging
- Keep branches up to date
- Use pull requests for code review
- Delete merged branches
- Tag releases properly

### ❌ Don'ts
- Never commit directly to main
- Don't force push to shared branches
- Avoid large, monolithic commits
- Don't merge without testing
- Never commit secrets or sensitive data
- Don't work on multiple features in one branch
- Avoid merge commits in feature branches

## Conclusion

This branch management strategy ensures:
- **Code Quality**: Through reviews and testing
- **Stability**: Protected main branch
- **Collaboration**: Clear workflows for teams
- **Traceability**: Detailed commit history
- **Flexibility**: Support for various development scenarios

Follow these guidelines to maintain a clean, organized, and efficient development workflow.