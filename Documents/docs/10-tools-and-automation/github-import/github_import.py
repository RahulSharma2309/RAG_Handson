#!/usr/bin/env python3
"""
GitHub Issue Import Script for E-Commerce Roadmap

This script automates the creation of GitHub issues from the CSV file containing
all Epics and PBIs.

Usage:
    python github_import.py --repo OWNER/REPO --csv epics_and_pbis.csv --token YOUR_TOKEN

Or set GITHUB_TOKEN environment variable:
    export GITHUB_TOKEN=your_token_here
    python github_import.py --repo OWNER/REPO --csv epics_and_pbis.csv

Requirements:
    pip install PyGithub pandas requests
"""

import os
import sys
import csv
import argparse
import time
from typing import Dict, List
from github import Github, GithubException

# Epic configurations
EPIC_CONFIGS = {
    "Epic 1": {"name": "Epic 1: Product Domain", "color": "FF6B6B", "description": "Enhanced Product Domain & Design Patterns"},
    "Epic 2": {"name": "Epic 2: Order Management", "color": "4ECDC4", "description": "Advanced Order Management & Patterns"},
    "Epic 3": {"name": "Epic 3: Payment & Checkout", "color": "45B7D1", "description": "Advanced Payment & Checkout"},
    "Epic 4": {"name": "Epic 4: Frontend Architecture", "color": "FFA07A", "description": "Frontend Architecture & React Patterns"},
    "Epic 5": {"name": "Epic 5: Testing Strategy", "color": "98D8C8", "description": "Testing Strategy"},
    "Epic 6": {"name": "Epic 6: CI/CD Pipeline", "color": "F7B731", "description": "CI/CD Pipeline"},
    "Epic 7": {"name": "Epic 7: Kubernetes", "color": "5F27CD", "description": "Kubernetes Deployment"},
    "Epic 8": {"name": "Epic 8: Observability", "color": "00D2D3", "description": "Observability & Monitoring"},
    "Epic 9": {"name": "Epic 9: Advanced Features", "color": "FF9FF3", "description": "Advanced Features"},
    "Epic 10": {"name": "Epic 10: Performance & Security", "color": "54A0FF", "description": "Performance & Security"},
}

# Sprint configurations
SPRINT_CONFIGS = {
    "Sprint 1-2": {"title": "Sprint 1-2: Product Type System", "description": "PBI 1.1, 1.2"},
    "Sprint 3": {"title": "Sprint 3: Pricing & Attributes", "description": "PBI 1.3, 1.4"},
    "Sprint 4": {"title": "Sprint 4: Media & Search", "description": "PBI 1.5, 1.6"},
    "Sprint 5": {"title": "Sprint 5: Inventory & Reviews", "description": "PBI 1.7, 1.8"},
    "Sprint 6": {"title": "Sprint 6: Wishlist & Comparison", "description": "PBI 1.9, 1.10"},
    "Sprint 7": {"title": "Sprint 7: Order State Machine", "description": "PBI 2.1, 2.2"},
    "Sprint 8": {"title": "Sprint 8: Cancellation & Modification", "description": "PBI 2.3, 2.4"},
    "Sprint 9": {"title": "Sprint 9: Saga & Invoice", "description": "PBI 2.5, 2.6"},
    "Sprint 10": {"title": "Sprint 10: Payment Methods", "description": "PBI 3.1, 3.2"},
    "Sprint 11": {"title": "Sprint 11: Retry & Discounts", "description": "PBI 3.3, 3.4"},
    "Sprint 12": {"title": "Sprint 12: Server State & Global State", "description": "PBI 4.1, 4.2"},
    "Sprint 13": {"title": "Sprint 13: Forms & Optimization", "description": "PBI 4.3, 4.4"},
    "Sprint 14": {"title": "Sprint 14: PWA & Accessibility", "description": "PBI 4.5, 4.6"},
    "Sprint 15": {"title": "Sprint 15: Animation & Quality", "description": "PBI 4.7, 4.8"},
    "Sprint 16": {"title": "Sprint 16: Component Library & Performance", "description": "PBI 4.9, 4.10"},
    "Sprint 17": {"title": "Sprint 17: Backend Tests", "description": "PBI 5.1, 5.2"},
    "Sprint 18": {"title": "Sprint 18: Frontend & E2E Tests", "description": "PBI 5.3, 5.4"},
    "Sprint 19": {"title": "Sprint 19: CI Setup", "description": "PBI 6.1, 6.2"},
    "Sprint 20": {"title": "Sprint 20: Versioning & Quality", "description": "PBI 6.3, 6.4, 6.5, 6.6"},
    "Sprint 21": {"title": "Sprint 21: K8s Setup", "description": "PBI 7.1, 7.2"},
    "Sprint 22": {"title": "Sprint 22: Helm & Ingress", "description": "PBI 7.3, 7.4"},
    "Sprint 23": {"title": "Sprint 23: Storage & Autoscaling", "description": "PBI 7.5, 7.6, 7.7"},
    "Sprint 24": {"title": "Sprint 24: Advanced K8s (Optional)", "description": "PBI 7.8, 7.9"},
    "Sprint 25": {"title": "Sprint 25: Logging", "description": "PBI 8.1, 8.2"},
    "Sprint 26": {"title": "Sprint 26: Metrics & Dashboards", "description": "PBI 8.3, 8.4"},
    "Sprint 27": {"title": "Sprint 27: Tracing", "description": "PBI 8.5"},
    "Sprint 28": {"title": "Sprint 28: Notifications", "description": "PBI 9.1"},
    "Sprint 29": {"title": "Sprint 29: Recommendations", "description": "PBI 9.2"},
    "Sprint 30-31": {"title": "Sprint 30-31: Admin Dashboard", "description": "PBI 9.3"},
    "Sprint 32": {"title": "Sprint 32: Search & Real-time", "description": "PBI 9.4, 9.5"},
    "Sprint 33": {"title": "Sprint 33: Caching & Rate Limiting", "description": "PBI 10.1, 10.2"},
    "Sprint 34": {"title": "Sprint 34: Security Hardening", "description": "PBI 10.3, 10.4, 10.5"},
    "Sprint 35": {"title": "Sprint 35: Security Testing", "description": "PBI 10.6"},
}


class GitHubImporter:
    """Import issues into GitHub from CSV"""
    
    def __init__(self, token: str, repo_name: str):
        """Initialize GitHub client"""
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)
        self.created_labels = {}
        self.created_milestones = {}
        
    def create_labels(self):
        """Create all required labels"""
        print("\n📋 Creating labels...")
        
        # Epic labels
        for epic_id, config in EPIC_CONFIGS.items():
            try:
                label = self.repo.create_label(
                    name=config["name"],
                    color=config["color"],
                    description=config["description"]
                )
                self.created_labels[epic_id] = label
                print(f"  ✅ Created: {config['name']}")
            except GithubException as e:
                if e.status == 422:  # Label already exists
                    label = self.repo.get_label(config["name"])
                    self.created_labels[epic_id] = label
                    print(f"  ⏭️  Exists: {config['name']}")
                else:
                    print(f"  ❌ Error creating {config['name']}: {e}")
        
        # Story point labels
        story_points = [1, 2, 3, 5, 8, 13, 21, 34]
        for sp in story_points:
            label_name = f"SP: {sp}"
            try:
                label = self.repo.create_label(
                    name=label_name,
                    color="C2E0C6" if sp <= 3 else "FFFFBA" if sp <= 8 else "FFDFBA" if sp <= 21 else "FFB3BA",
                    description=f"Story Points: {sp}"
                )
                self.created_labels[f"SP{sp}"] = label
                print(f"  ✅ Created: {label_name}")
            except GithubException as e:
                if e.status == 422:
                    label = self.repo.get_label(label_name)
                    self.created_labels[f"SP{sp}"] = label
                    print(f"  ⏭️  Exists: {label_name}")
                else:
                    print(f"  ❌ Error creating {label_name}: {e}")
        
        # Status labels
        statuses = [
            ("status: backlog", "DDDDDD", "In backlog"),
            ("status: in-progress", "FFA500", "In progress"),
            ("status: in-review", "800080", "In review"),
            ("status: done", "00FF00", "Done"),
        ]
        for name, color, desc in statuses:
            try:
                label = self.repo.create_label(name=name, color=color, description=desc)
                print(f"  ✅ Created: {name}")
            except GithubException as e:
                if e.status == 422:
                    print(f"  ⏭️  Exists: {name}")
                else:
                    print(f"  ❌ Error creating {name}: {e}")
        
        # Priority labels
        priorities = [
            ("priority: critical", "FF0000", "Critical priority"),
            ("priority: high", "FFA500", "High priority"),
            ("priority: medium", "FFFF00", "Medium priority"),
            ("priority: low", "00FF00", "Low priority"),
        ]
        for name, color, desc in priorities:
            try:
                label = self.repo.create_label(name=name, color=color, description=desc)
                print(f"  ✅ Created: {name}")
            except GithubException as e:
                if e.status == 422:
                    print(f"  ⏭️  Exists: {name}")
                else:
                    print(f"  ❌ Error creating {name}: {e}")
    
    def create_milestones(self):
        """Create all sprint milestones"""
        print("\n📅 Creating milestones...")
        
        for sprint_id, config in SPRINT_CONFIGS.items():
            try:
                milestone = self.repo.create_milestone(
                    title=config["title"],
                    description=config["description"]
                )
                self.created_milestones[sprint_id] = milestone
                print(f"  ✅ Created: {config['title']}")
            except GithubException as e:
                if e.status == 422:  # Milestone already exists
                    # Find existing milestone
                    milestones = self.repo.get_milestones(state="open")
                    for ms in milestones:
                        if ms.title == config["title"]:
                            self.created_milestones[sprint_id] = ms
                            print(f"  ⏭️  Exists: {config['title']}")
                            break
                else:
                    print(f"  ❌ Error creating {config['title']}: {e}")
    
    def create_issue_from_row(self, row: Dict):
        """Create a single issue from CSV row"""
        epic_id = row["Epic ID"]
        pbi_id = row["PBI ID"]
        pbi_title = row["PBI Title"]
        story_points = int(row["Story Points"])
        description = row["Description"]
        sprint = row["Sprint"]
        
        # Build issue title
        title = f"[{pbi_id}] {pbi_title}"
        
        # Build issue body
        body = f"""## 📝 Description
{description}

## 🎯 Epic
{EPIC_CONFIGS[epic_id]["name"]}

## 📊 Story Points
{story_points}

## 🎯 Acceptance Criteria
- [ ] See description for detailed acceptance criteria

## 🔧 Technical Tasks
- [ ] See description for technical tasks

## 📚 Documentation
- [ ] Update API documentation
- [ ] Update service documentation  
- [ ] Add code comments
- [ ] Update user flow documentation (if applicable)

## 🔗 Dependencies
Check roadmap document for dependencies

## ✅ Definition of Done
- [ ] Code complete and reviewed
- [ ] Unit tests written (>80% coverage for new code)
- [ ] Integration tests (if applicable)
- [ ] Documentation updated
- [ ] PR approved and merged to main
- [ ] Deployed to development environment
- [ ] Functionality verified

---

**For detailed acceptance criteria and technical tasks, see:**
- `docs/PROJECT_ROADMAP.md`
- `docs/ITERATION_CHECKLIST.md`
"""
        
        # Get labels
        labels = []
        if epic_id in self.created_labels:
            labels.append(self.created_labels[epic_id].name)
        
        sp_key = f"SP{story_points}"
        if sp_key in self.created_labels:
            labels.append(self.created_labels[sp_key].name)
        
        labels.append("status: backlog")
        
        # Get milestone
        milestone = self.created_milestones.get(sprint, None)
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels,
                milestone=milestone
            )
            print(f"  ✅ Created: {title}")
            return issue
        except GithubException as e:
            print(f"  ❌ Error creating {title}: {e}")
            return None
    
    def import_from_csv(self, csv_file: str):
        """Import all issues from CSV file"""
        print(f"\n📥 Reading CSV: {csv_file}")
        
        issues_created = 0
        issues_failed = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            total = len(rows)
            
            print(f"\n🚀 Creating {total} issues...\n")
            
            for i, row in enumerate(rows, 1):
                print(f"[{i}/{total}] ", end="")
                issue = self.create_issue_from_row(row)
                
                if issue:
                    issues_created += 1
                else:
                    issues_failed += 1
                
                # Rate limiting: sleep to avoid hitting GitHub API limits
                if i % 10 == 0:
                    print(f"\n  ⏳ Pausing for rate limit (created {i}/{total})...")
                    time.sleep(2)
        
        print(f"\n✅ Import complete!")
        print(f"  Created: {issues_created}")
        print(f"  Failed: {issues_failed}")
        print(f"  Total: {total}")
    
    def run(self, csv_file: str):
        """Run the complete import process"""
        print("=" * 60)
        print("🚀 GitHub E-Commerce Roadmap Importer")
        print("=" * 60)
        print(f"Repository: {self.repo.full_name}")
        print(f"CSV File: {csv_file}")
        
        try:
            self.create_labels()
            self.create_milestones()
            self.import_from_csv(csv_file)
            
            print("\n" + "=" * 60)
            print("✅ All done! Check your repository:")
            print(f"   {self.repo.html_url}/issues")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Import E-Commerce roadmap to GitHub")
    parser.add_argument("--repo", required=True, help="Repository in format OWNER/REPO")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    # Get token from args or environment
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GitHub token required!")
        print("   Provide via --token argument or GITHUB_TOKEN environment variable")
        sys.exit(1)
    
    # Validate CSV file exists
    if not os.path.exists(args.csv):
        print(f"❌ Error: CSV file not found: {args.csv}")
        sys.exit(1)
    
    # Run import
    importer = GitHubImporter(token=token, repo_name=args.repo)
    importer.run(csv_file=args.csv)


if __name__ == "__main__":
    main()

