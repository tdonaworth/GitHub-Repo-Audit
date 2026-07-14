"""GitHub API client for fetching organization repository data."""

from github import Github
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class GitHubAuditClient:
    """Client for auditing GitHub organization repositories."""

    def __init__(self, token: str, max_workers: int = 10):
        """Initialize the GitHub client with a personal access token."""
        self.client = Github(token, per_page=100)
        self.user = self.client.get_user()
        self.max_workers = max_workers

    def get_org_repos(self, org_name: str) -> List[Any]:
        """Fetch all repositories for a given organization."""
        org = self.client.get_organization(org_name)
        return list(org.get_repos())

    def get_repo_data(self, repo, index: int = 0, total: int = 0) -> Dict[str, Any]:
        """Extract relevant data from a repository."""
        prefix = f"[{index}/{total}]" if total > 0 else ""
        print(f"{prefix} Processing: {repo.name}")

        # Get last commit date from default branch
        last_commit_date = None
        try:
            commits = repo.get_commits()
            if commits.totalCount > 0:
                last_commit = commits[0]
                last_commit_date = last_commit.commit.author.date
        except Exception as e:
            print(f"  Warning: Could not fetch commits for {repo.name}: {e}")

        # Get open issues and PRs count
        open_issues = repo.open_issues_count
        open_prs = 0
        try:
            open_prs = repo.get_pulls(state='open').totalCount
        except Exception as e:
            print(f"  Warning: Could not fetch PRs for {repo.name}: {e}")

        # Adjust issues count (GitHub API includes PRs in issues count)
        open_issues = open_issues - open_prs

        # Get contributors (limit to top 100 to avoid slowness on huge repos)
        contributors = self.get_contributors(repo)

        return {
            'name': repo.name,
            'url': repo.html_url,
            'owner': repo.owner.login,
            'created_date': repo.created_at,
            'last_commit_date': last_commit_date,
            'is_fork': repo.fork,
            'is_archived': repo.archived,
            'open_issues': open_issues,
            'open_prs': open_prs,
            'primary_language': repo.language or 'N/A',
            'size_kb': repo.size,
            'contributors': contributors
        }

    def get_contributors(self, repo, max_contributors: int = 100) -> List[Dict[str, Any]]:
        """Get contributors for a repository (limited to top N by contribution count)."""
        contributors = []
        try:
            contributor_list = repo.get_contributors()
            count = 0
            for contributor in contributor_list:
                if count >= max_contributors:
                    break
                contributors.append({
                    'name': contributor.name or contributor.login,
                    'email': contributor.email or 'N/A',
                    'contributions': contributor.contributions
                })
                count += 1
        except Exception as e:
            print(f"  Warning: Could not fetch contributors for {repo.name}: {e}")

        return contributors

    def audit_organization(self, org_name: str, use_concurrent: bool = True) -> List[Dict[str, Any]]:
        """Perform a complete audit of an organization."""
        print(f"Fetching repositories for organization: {org_name}")
        repos = self.get_org_repos(org_name)
        total_repos = len(repos)
        print(f"Found {total_repos} repositories\n")

        if not use_concurrent or total_repos <= 5:
            # Sequential processing for small org or if concurrent disabled
            audit_data = []
            for i, repo in enumerate(repos, 1):
                repo_data = self.get_repo_data(repo, i, total_repos)
                audit_data.append(repo_data)
            return audit_data

        # Concurrent processing for better performance
        print(f"Using concurrent processing with {self.max_workers} workers\n")
        audit_data = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_repo = {
                executor.submit(self.get_repo_data, repo, i, total_repos): (repo, i)
                for i, repo in enumerate(repos, 1)
            }

            # Collect results as they complete
            for future in as_completed(future_to_repo):
                try:
                    repo_data = future.result()
                    audit_data.append(repo_data)
                except Exception as e:
                    repo, idx = future_to_repo[future]
                    print(f"[{idx}/{total_repos}] Error processing {repo.name}: {e}")

        # Sort by name to maintain consistent order
        audit_data.sort(key=lambda x: x['name'])

        return audit_data
