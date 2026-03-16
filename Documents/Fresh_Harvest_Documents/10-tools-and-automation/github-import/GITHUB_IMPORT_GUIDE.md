# 📋 GitHub Epic & PBI Import Guide - FreshHarvest Market

> **Complete guide to importing Epics and PBIs into GitHub Issues and Projects for the organic food marketplace**

---

## 🎯 Overview

This guide provides **4 different methods** to import the roadmap into GitHub:

1. **Manual Creation** (UI-based, good for understanding)
2. **GitHub CLI** (Semi-automated, recommended)
3. **Python Script** (Fully automated)
4. **GitHub API with Postman** (API learning)

---

## 📁 Files in this Directory

- `epics_and_pbis.csv` - All PBIs in CSV format
- `github_import.py` - Python script for automated import
- `github_import.json` - JSON format for API import
- `GITHUB_IMPORT_GUIDE.md` - This file

---

## 🛠️ Method 1: Manual Creation (UI)

**Best for:** Understanding the structure, small projects

**Time:** ~4-6 hours for all 70+ PBIs

### Step 1: Create Labels

1. Go to your repository: `https://github.com/YOUR-USERNAME/FreshHarvest-Market`
2. Click **Issues** → **Labels** → **New label**

**Create Epic Labels:**

```
Epic 1: Product Domain - Color: #FF6B6B
Epic 2: Order Management - Color: #4ECDC4
Epic 3: Payment & Checkout - Color: #45B7D1
Epic 4: Frontend Architecture - Color: #FFA07A
Epic 5: Testing Strategy - Color: #98D8C8
Epic 6: CI/CD Pipeline - Color: #F7B731
Epic 7: Kubernetes - Color: #5F27CD
Epic 8: Observability - Color: #00D2D3
Epic 9: Advanced Features - Color: #FF9FF3
Epic 10: Performance & Security - Color: #54A0FF
```

**Create Story Point Labels:**

```
SP: 1 - Color: #C2E0C6
SP: 2 - Color: #C2E0C6
SP: 3 - Color: #C2E0C6
SP: 5 - Color: #FFFFBA
SP: 8 - Color: #FFFFBA
SP: 13 - Color: #FFDFBA
SP: 21 - Color: #FFDFBA
SP: 34 - Color: #FFB3BA
```

**Create Status Labels:**

```
status: backlog - Color: #DDDDDD
status: in-progress - Color: #FFA500
status: in-review - Color: #800080
status: done - Color: #00FF00
```

**Create Priority Labels:**

```
priority: critical - Color: #FF0000
priority: high - Color: #FFA500
priority: medium - Color: #FFFF00
priority: low - Color: #00FF00
```

---

### Step 2: Create Milestones (Sprints)

1. Go to **Issues** → **Milestones** → **New milestone**

**Create Milestones:**

```
Sprint 1-2: Product Type System
  Due: 2 weeks from start
  Description: PBI 1.1, 1.2

Sprint 3: Pricing & Attributes
  Due: 4 weeks from start
  Description: PBI 1.3, 1.4

(Continue for all sprints...)
```

---

### Step 3: Create Issues

For each PBI, create an issue using this template:

**Title Format:** `[PBI X.Y] PBI Title`

**Example:** `[PBI 1.1] Product Category & Type System`

**Body Template:**

```markdown
## 📝 Description

Implement product hierarchy for organic food (Fresh Fruits, Fresh Vegetables, Grains & Pulses, Dairy & Eggs, Herbs & Spices)

## 🎯 Epic

Epic 1: Enhanced Product Domain & Design Patterns

## 📊 Story Points

13

## 🎯 Acceptance Criteria

- [ ] Create abstract Product base class
- [ ] Implement ProductType enum with all organic categories
- [ ] Create specific product classes (Fruit, Vegetable, Grain, etc.)
- [ ] Add category-specific attributes (origin, certification, expiry date, etc.)
- [ ] Update database schema with inheritance (TPH or TPT)
- [ ] Create migrations
- [ ] Update Product Service API
- [ ] Add category filtering endpoints

## 🔧 Technical Tasks

- [ ] Implement Factory Pattern for product creation
- [ ] Create ProductFactory with registration mechanism
- [ ] Add unit tests for product creation
- [ ] Update Swagger documentation

## 📚 Documentation

- [ ] Update API documentation
- [ ] Update service documentation
- [ ] Add code comments

## 🔗 Dependencies

None (first PBI)

## ✅ Definition of Done

- [ ] Code complete and reviewed
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests (if applicable)
- [ ] Documentation updated
- [ ] PR approved and merged
- [ ] Deployed to development environment
```

**Assign:**

- Labels: `Epic 1: Product Domain`, `SP: 13`, `status: backlog`
- Milestone: `Sprint 1-2: Product Type System`
- Assignee: Yourself (if working solo)

---

### Step 4: Create GitHub Project

1. Click **Projects** (repository level or organization level)
2. Click **New project**
3. Select **Board** or **Table** view
4. Name: "FreshHarvest Market Roadmap"

**Configure Columns (if Board view):**

- 📋 Backlog
- 🎯 Ready
- 🏗️ In Progress
- 👀 In Review
- ✅ Done

**Configure Fields:**

- **Status:** Dropdown (Backlog, Ready, In Progress, In Review, Done)
- **Epic:** Single select (Epic 1, Epic 2, ..., Epic 10)
- **Story Points:** Number
- **Sprint:** Iteration (configure sprint dates)
- **Priority:** Single select (Critical, High, Medium, Low)

---

### Step 5: Add Issues to Project

1. Go to your project board
2. Click **+ Add item**
3. Search for issues
4. Add all issues
5. Organize by dragging to appropriate columns

---

## 🛠️ Method 2: GitHub CLI (Recommended)

**Best for:** Semi-automated, easy to use

**Time:** ~30 minutes

### Prerequisites

```bash
# Install GitHub CLI
# Windows (using winget)
winget install --id GitHub.cli

# Or download from: https://cli.github.com/

# Authenticate
gh auth login
# Follow prompts: GitHub.com → HTTPS → Login with browser
```

---

### Step 1: Create Labels

Create a file `create_labels.sh`:

```bash
#!/bin/bash

REPO="YOUR-USERNAME/FreshHarvest-Market"

# Epic labels
gh label create "Epic 1: Product Domain" --repo $REPO --color "FF6B6B" --description "Enhanced Product Domain & Design Patterns"
gh label create "Epic 2: Order Management" --repo $REPO --color "4ECDC4" --description "Advanced Order Management & Patterns"
gh label create "Epic 3: Payment & Checkout" --repo $REPO --color "45B7D1" --description "Advanced Payment & Checkout"
gh label create "Epic 4: Frontend Architecture" --repo $REPO --color "FFA07A" --description "Frontend Architecture & React Patterns"
gh label create "Epic 5: Testing Strategy" --repo $REPO --color "98D8C8" --description "Testing Strategy"
gh label create "Epic 6: CI/CD Pipeline" --repo $REPO --color "F7B731" --description "CI/CD Pipeline"
gh label create "Epic 7: Kubernetes" --repo $REPO --color "5F27CD" --description "Kubernetes Deployment"
gh label create "Epic 8: Observability" --repo $REPO --color "00D2D3" --description "Observability & Monitoring"
gh label create "Epic 9: Advanced Features" --repo $REPO --color "FF9FF3" --description "Advanced Features"
gh label create "Epic 10: Performance & Security" --repo $REPO --color "54A0FF" --description "Performance & Security"

# Story point labels
for sp in 1 2 3 5 8 13 21 34; do
  gh label create "SP: $sp" --repo $REPO --color "C2E0C6" --description "Story Points: $sp"
done

# Status labels
gh label create "status: backlog" --repo $REPO --color "DDDDDD"
gh label create "status: in-progress" --repo $REPO --color "FFA500"
gh label create "status: in-review" --repo $REPO --color "800080"
gh label create "status: done" --repo $REPO --color "00FF00"

# Priority labels
gh label create "priority: critical" --repo $REPO --color "FF0000"
gh label create "priority: high" --repo $REPO --color "FFA500"
gh label create "priority: medium" --repo $REPO --color "FFFF00"
gh label create "priority: low" --repo $REPO --color "00FF00"
```

Run:

```bash
bash create_labels.sh
```

---

### Step 2: Create Issues from CSV

Create a file `create_issues.sh`:

```bash
#!/bin/bash

REPO="YOUR-USERNAME/FreshHarvest-Market"

# Read CSV and create issues
while IFS=',' read -r epic_id epic_title pbi_id pbi_title story_points description ac_1 ac_2 ac_3 ac_4 task_1 task_2
do
  if [ "$pbi_id" != "PBI ID" ]; then  # Skip header

    # Build issue body
    BODY="## 📝 Description
$description

## 🎯 Epic
$epic_title

## 📊 Story Points
$story_points

## 🎯 Acceptance Criteria
- [ ] $ac_1
- [ ] $ac_2
- [ ] $ac_3
- [ ] $ac_4

## 🔧 Technical Tasks
- [ ] $task_1
- [ ] $task_2

## ✅ Definition of Done
- [ ] Code complete and reviewed
- [ ] Unit tests written (>80% coverage)
- [ ] Documentation updated
- [ ] PR approved and merged
"

    # Create issue
    gh issue create \
      --repo "$REPO" \
      --title "[$pbi_id] $pbi_title" \
      --body "$BODY" \
      --label "$epic_id,$SP: $story_points,status: backlog"

    echo "Created: [$pbi_id] $pbi_title"
    sleep 1  # Rate limiting
  fi
done < epics_and_pbis.csv
```

Run:

```bash
bash create_issues.sh
```

---

### Step 3: Create Project

```bash
# Create project (requires GitHub CLI with project extension)
gh project create --owner YOUR-USERNAME --title "FreshHarvest Market Roadmap" --body "Complete roadmap for production-grade organic food marketplace"

# Get project number
gh project list --owner YOUR-USERNAME

# Add issues to project (replace PROJECT_NUMBER)
gh project item-add PROJECT_NUMBER --owner YOUR-USERNAME --url "https://github.com/YOUR-USERNAME/FreshHarvest-Market/issues/1"
# Repeat for all issues, or use a loop
```

---

## 🛠️ Method 3: Python Script (Fully Automated)

**Best for:** Complete automation, learning GitHub API

**Time:** ~10 minutes (after setup)

### Prerequisites

```bash
# Install required packages
pip install PyGithub pandas requests
```

### Step 1: Create Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Select scopes:
   - `repo` (full control)
   - `project` (full control - if using projects)
4. Click **Generate token**
5. **Copy the token** (you won't see it again!)

### Step 2: Use the Python Script

The script is provided in `github_import.py`. Usage:

```bash
# Set environment variable
export GITHUB_TOKEN="your_token_here"

# Or on Windows
set GITHUB_TOKEN=your_token_here

# Run script
python github_import.py --repo YOUR-USERNAME/FreshHarvest-Market --csv epics_and_pbis.csv
```

**Script Features:**

- ✅ Creates all labels
- ✅ Creates all milestones
- ✅ Creates all issues with full details
- ✅ Assigns labels and milestones
- ✅ Handles rate limiting
- ✅ Progress reporting

---

## 🛠️ Method 4: GitHub REST API with Postman

**Best for:** Learning GitHub API, manual control

### Step 1: Set up Postman

1. Install Postman: https://www.postman.com/downloads/
2. Create new collection: "GitHub FreshHarvest Market Import"
3. Set collection variable:
   - `GITHUB_TOKEN`: your personal access token
   - `REPO_OWNER`: YOUR-USERNAME
   - `REPO_NAME`: FreshHarvest-Market

### Step 2: Create Label Request

**POST** `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/labels`

Headers:

```
Authorization: Bearer {{GITHUB_TOKEN}}
Accept: application/vnd.github.v3+json
Content-Type: application/json
```

Body (JSON):

```json
{
  "name": "Epic 1: Product Domain",
  "color": "FF6B6B",
  "description": "Enhanced Product Domain & Design Patterns"
}
```

### Step 3: Create Issue Request

**POST** `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/issues`

Body (JSON):

```json
{
  "title": "[PBI 1.1] Product Category & Type System",
  "body": "## 📝 Description\nImplement product hierarchy...",
  "labels": ["Epic 1: Product Domain", "SP: 13", "status: backlog"],
  "milestone": 1
}
```

---

## 📊 GitHub Projects Setup

### Project Board Configuration

#### Option 1: Classic Projects

1. **Repository Projects** → **New project** → **Board**
2. Add columns:
   - Backlog
   - Ready
   - In Progress
   - In Review
   - Done
3. Add automation:
   - Move to "In Progress" when assigned
   - Move to "In Review" when PR created
   - Move to "Done" when PR merged

#### Option 2: New Projects (Beta)

**Advantages:**

- Better customization
- Custom fields
- Multiple views
- Better automation

**Setup:**

1. Go to organization or user projects
2. Create new project (Beta)
3. Choose **Team backlog** template
4. Customize fields:
   - **Epic:** Single select (Epic 1, ..., Epic 10)
   - **Story Points:** Number
   - **Sprint:** Iteration
   - **Priority:** Single select
5. Create views:
   - **Backlog:** All open issues
   - **Current Sprint:** Filter by current iteration
   - **Epic View:** Group by epic
   - **Burndown:** Custom chart

---

## 🎯 After Import: Best Practices

### 1. Set Up Branch Protection

**Settings** → **Branches** → **Add rule**

- Branch name pattern: `main`
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

### 2. Configure Automation

**GitHub Actions Workflow** (`.github/workflows/project-automation.yml`):

```yaml
name: Project Automation

on:
  issues:
    types: [opened, assigned, closed]
  pull_request:
    types: [opened, closed]

jobs:
  auto-move:
    runs-on: ubuntu-latest
    steps:
      - name: Move assigned issues to In Progress
        if: github.event.action == 'assigned'
        uses: alex-page/github-project-automation-plus@v0.8.1
        with:
          project: FreshHarvest Market Roadmap
          column: In Progress
          repo-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Move closed issues to Done
        if: github.event.action == 'closed'
        uses: alex-page/github-project-automation-plus@v0.8.1
        with:
          project: FreshHarvest Market Roadmap
          column: Done
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Create Issue Templates

Create `.github/ISSUE_TEMPLATE/pbi.md`:

```markdown
---
name: Product Backlog Item (PBI)
about: Create a new PBI
title: '[PBI X.Y] '
labels: status: backlog
assignees: ''
---

## 📝 Description

Brief description of what needs to be done

## 🎯 Epic

Which epic does this belong to?

## 📊 Story Points

Estimate in Fibonacci sequence

## 🎯 Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## 🔧 Technical Tasks

- [ ] Task 1
- [ ] Task 2

## 🔗 Dependencies

List dependent issues

## ✅ Definition of Done

- [ ] Code complete
- [ ] Tests written
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Merged to main
```

### 4. Sprint Planning Workflow

**Weekly Ritual:**

1. Review completed items from last sprint
2. Move items to Done
3. Plan next sprint:
   - Select PBIs from backlog
   - Assign to sprint milestone
   - Assign to team members
   - Move to Ready column

---

## 📈 Tracking Progress

### Burndown Chart

**Manual Calculation:**

```
Total Story Points: 864
Completed Story Points: Sum of done issues
Remaining: 864 - Completed
```

**Automated (GitHub Projects Beta):**

- Create custom chart
- X-axis: Iteration (Sprint)
- Y-axis: Story Points
- Group by: Status

### Velocity Tracking

**After each sprint:**

- Count completed story points
- Calculate average velocity
- Adjust future sprint planning

**Example:**

```
Sprint 1: 21 points completed
Sprint 2: 26 points completed
Sprint 3: 24 points completed
Average Velocity: ~24 points/sprint
Estimated Completion: 864 / 24 = 36 sprints
```

---

## 🔍 Verification Checklist

After import, verify:

- [ ] All labels created

  - [ ] 10 Epic labels
  - [ ] 8 Story Point labels
  - [ ] 4 Status labels
  - [ ] 4 Priority labels

- [ ] All milestones created

  - [ ] Sprint 1-2
  - [ ] Sprint 3
  - [ ] Sprint 4
  - [ ] ... (all sprints)

- [ ] All issues created

  - [ ] 70+ PBI issues
  - [ ] Correct titles (`[PBI X.Y] ...`)
  - [ ] Proper labels assigned
  - [ ] Milestones assigned

- [ ] Project board created

  - [ ] Issues added to project
  - [ ] Columns configured
  - [ ] Automation set up

- [ ] Repository settings
  - [ ] Branch protection enabled
  - [ ] Issue templates created
  - [ ] CODEOWNERS file exists

---

## 🆘 Troubleshooting

### Issue: "Resource not accessible by personal access token"

**Solution:** Regenerate token with correct scopes (repo, project)

### Issue: "Rate limit exceeded"

**Solution:** Wait 1 hour or use authenticated requests (they have higher limits)

### Issue: "Project not found"

**Solution:** Ensure project is at repository level or use org-level projects

### Issue: Labels not applying

**Solution:** Check exact label name spelling (case-sensitive)

### Issue: Milestones not showing

**Solution:** Create milestones first, then assign to issues

---

## 📚 Additional Resources

- **GitHub CLI Docs:** https://cli.github.com/manual/
- **GitHub REST API:** https://docs.github.com/en/rest
- **GitHub Projects:** https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **PyGithub Docs:** https://pygithub.readthedocs.io/
- **GitHub Actions:** https://docs.github.com/en/actions

---

## 🎉 Success!

Once complete, you'll have:

- ✅ 70+ issues representing all PBIs
- ✅ Organized by Epics (labels)
- ✅ Sized with story points
- ✅ Assigned to sprints (milestones)
- ✅ Trackable on project board
- ✅ Ready to start development!

**Next Step:** Start Sprint 1 and begin Epic 1, PBI 1.1! 🚀

---

**Questions?** Open an issue in the repository or check GitHub Docs.
