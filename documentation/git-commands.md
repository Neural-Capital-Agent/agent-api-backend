# Git Commands for Neural Capital Agent API Backend

## Branch Management

### Creating and Switching Branches
```bash
# Create and switch to a new branch
git checkout -b <branch-name>

# Switch to an existing branch
git checkout <branch-name>

# Create a new branch from specific commit
git checkout -b <branch-name> <commit-hash>

# List all branches (local and remote)
git branch -a

# Delete a local branch
git branch -d <branch-name>

# Delete a remote branch
git push origin --delete <branch-name>
```

### Branch Information
```bash
# Show current branch
git branch

# Show branch with last commit info
git branch -v

# Show remote tracking branches
git branch -r
```

## Daily Workflow Commands

### Checking Status and Changes
```bash
# Check repository status
git status

# Show differences in working directory
git diff

# Show differences in staged files
git diff --staged

# Show commit history
git log --oneline
```

### Staging and Committing
```bash
# Add specific files
git add <file1> <file2>

# Add all changes
git add .

# Add all tracked files (excludes new files)
git add -u

# Commit with message
git commit -m "Your commit message"

# Commit all tracked changes (skip staging)
git commit -am "Your commit message"
```

### Pushing and Pulling
```bash
# Push to remote branch (first time)
git push -u origin <branch-name>

# Push to current branch
git push

# Pull latest changes from remote
git pull

# Fetch changes without merging
git fetch origin
```

## Working with Development Branch

### Development Branch Workflow
```bash
# Switch to development branch
git checkout development

# Create feature branch from development
git checkout -b feature/<feature-name> development

# Merge feature back to development
git checkout development
git merge feature/<feature-name>

# Push development branch
git push origin development
```

### Syncing with Master
```bash
# Update development with latest master changes
git checkout development
git pull origin master

# Rebase development on master (alternative to merge)
git checkout development
git rebase master
```

## Advanced Commands

### Stashing Changes
```bash
# Stash current changes
git stash

# Stash with message
git stash save "Work in progress on feature X"

# List all stashes
git stash list

# Apply latest stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Clear all stashes
git stash clear
```

### Undoing Changes
```bash
# Discard changes in working directory
git restore <file>

# Unstage a file
git restore --staged <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert a specific commit
git revert <commit-hash>
```

### Viewing History and Changes
```bash
# Show detailed commit history
git log --graph --oneline --all

# Show changes in specific commit
git show <commit-hash>

# Show file history
git log --follow <file>

# Show who changed what in a file
git blame <file>
```

## Release and Deployment Commands

### Tagging Releases
```bash
# Create a tag
git tag v1.0.0

# Create annotated tag with message
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tags to remote
git push origin --tags

# List all tags
git tag -l

# Delete a tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### Creating Pull Requests (via GitHub CLI)
```bash
# Install GitHub CLI first: https://cli.github.com/

# Create pull request
gh pr create --title "Feature: Add new functionality" --body "Description of changes"

# List pull requests
gh pr list

# Check out a pull request locally
gh pr checkout <pr-number>

# Merge a pull request
gh pr merge <pr-number>
```

## Emergency Commands

### Force Operations (Use with Caution)
```bash
# Force push (overwrites remote history)
git push --force-with-lease origin <branch-name>

# Hard reset to specific commit
git reset --hard <commit-hash>

# Clean untracked files and directories
git clean -fd
```

### Recovery Commands
```bash
# Show reflog (history of HEAD movements)
git reflog

# Recover deleted branch
git checkout -b <branch-name> <commit-hash-from-reflog>

# Find lost commits
git fsck --lost-found
```

## Configuration Commands

### User Configuration
```bash
# Set global user name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set repository-specific user info
git config user.name "Your Name"
git config user.email "your.email@example.com"

# View current configuration
git config --list
```

### Useful Aliases
```bash
# Set up helpful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

## Project-Specific Workflow

### Recommended Workflow for This Project
1. Always work on `development` branch or feature branches
2. Never push directly to `master` branch
3. Create feature branches from `development`:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```
4. When feature is complete:
   ```bash
   git checkout development
   git pull origin development
   git merge feature/your-feature-name
   git push origin development
   ```
5. Create pull requests from `development` to `master` for releases

### Quick Reference for Daily Use
```bash
# Start of day
git checkout development
git pull origin development

# Work on feature
git checkout -b feature/new-feature
# ... make changes ...
git add .
git commit -m "Add new feature"
git push -u origin feature/new-feature

# End of day / feature complete
git checkout development
git pull origin development
git merge feature/new-feature
git push origin development
git branch -d feature/new-feature
```