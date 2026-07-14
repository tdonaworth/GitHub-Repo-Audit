"""Generate CSV and HTML reports from GitHub audit data."""

import csv
from jinja2 import Template
from datetime import datetime
from typing import List, Dict, Any


def flatten_repo_data(audit_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten repository data for CSV export (one row per repo-contributor pair)."""
    flattened = []

    for repo in audit_data:
        if not repo['contributors']:
            # Repository with no contributors
            flattened.append({
                'repo_name': repo['name'],
                'repo_url': repo['url'],
                'owner': repo['owner'],
                'created_date': repo['created_date'],
                'last_commit_date': repo['last_commit_date'],
                'is_fork': repo['is_fork'],
                'is_archived': repo['is_archived'],
                'open_issues': repo['open_issues'],
                'open_prs': repo['open_prs'],
                'primary_language': repo['primary_language'],
                'size_kb': repo['size_kb'],
                'contributor_name': 'N/A',
                'contributor_email': 'N/A',
                'contributions': 0
            })
        else:
            # One row per contributor
            for contributor in repo['contributors']:
                flattened.append({
                    'repo_name': repo['name'],
                    'repo_url': repo['url'],
                    'owner': repo['owner'],
                    'created_date': repo['created_date'],
                    'last_commit_date': repo['last_commit_date'],
                    'is_fork': repo['is_fork'],
                    'is_archived': repo['is_archived'],
                    'open_issues': repo['open_issues'],
                    'open_prs': repo['open_prs'],
                    'primary_language': repo['primary_language'],
                    'size_kb': repo['size_kb'],
                    'contributor_name': contributor['name'],
                    'contributor_email': contributor['email'],
                    'contributions': contributor['contributions']
                })

    return flattened


def generate_csv(audit_data: List[Dict[str, Any]], filename: str):
    """Generate a CSV report from audit data."""
    flattened = flatten_repo_data(audit_data)

    # Sort by repo name, then by contribution count (descending)
    flattened.sort(key=lambda x: (x['repo_name'], -x['contributions']))

    # Write CSV manually to avoid pandas datetime issues
    if not flattened:
        print("No data to write to CSV")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = flattened[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in flattened:
            # Convert datetime objects to strings
            row_copy = row.copy()
            for key, value in row_copy.items():
                if isinstance(value, datetime):
                    row_copy[key] = value.strftime('%Y-%m-%d %H:%M:%S') if value else 'N/A'
            writer.writerow(row_copy)

    print(f"\nCSV report saved to: {filename}")


def generate_html(audit_data: List[Dict[str, Any]], filename: str, org_name: str):
    """Generate an HTML report from audit data."""

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Audit Report - {{ org_name }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #24292e;
            color: white;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0 0 10px 0;
        }
        .header p {
            margin: 5px 0;
            opacity: 0.9;
        }
        .summary {
            background-color: white;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .summary-item {
            text-align: center;
        }
        .summary-item .number {
            font-size: 32px;
            font-weight: bold;
            color: #0366d6;
        }
        .summary-item .label {
            color: #586069;
            margin-top: 5px;
        }
        .repo-card {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .repo-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        .repo-name {
            font-size: 20px;
            font-weight: bold;
            color: #0366d6;
            text-decoration: none;
        }
        .repo-name:hover {
            text-decoration: underline;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }
        .badge-fork {
            background-color: #e1e4e8;
            color: #586069;
        }
        .badge-archived {
            background-color: #ffeaa7;
            color: #6c5ce7;
        }
        .repo-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
            padding: 15px;
            background-color: #f6f8fa;
            border-radius: 4px;
        }
        .meta-item {
            font-size: 14px;
        }
        .meta-label {
            color: #586069;
            font-weight: bold;
        }
        .contributors-section {
            margin-top: 15px;
        }
        .contributors-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #24292e;
        }
        .contributors-table {
            width: 100%;
            border-collapse: collapse;
        }
        .contributors-table th {
            background-color: #f6f8fa;
            padding: 8px;
            text-align: left;
            font-size: 12px;
            color: #586069;
            border-bottom: 1px solid #e1e4e8;
        }
        .contributors-table td {
            padding: 8px;
            border-bottom: 1px solid #e1e4e8;
            font-size: 14px;
        }
        .no-contributors {
            color: #586069;
            font-style: italic;
        }
        .filter-section {
            background-color: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .filter-section input {
            width: 100%;
            padding: 10px;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>GitHub Organization Audit Report</h1>
        <p><strong>Organization:</strong> {{ org_name }}</p>
        <p><strong>Generated:</strong> {{ generated_date }}</p>
    </div>

    <div class="summary">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="number">{{ total_repos }}</div>
                <div class="label">Total Repositories</div>
            </div>
            <div class="summary-item">
                <div class="number">{{ total_contributors }}</div>
                <div class="label">Total Contributors</div>
            </div>
            <div class="summary-item">
                <div class="number">{{ total_forks }}</div>
                <div class="label">Forks</div>
            </div>
            <div class="summary-item">
                <div class="number">{{ total_archived }}</div>
                <div class="label">Archived</div>
            </div>
        </div>
    </div>

    <div class="filter-section">
        <input type="text" id="searchInput" placeholder="Search repositories by name..." onkeyup="filterRepos()">
    </div>

    <div id="repoContainer">
        {% for repo in repos %}
        <div class="repo-card" data-repo-name="{{ repo.name|lower }}">
            <div class="repo-header">
                <div>
                    <a href="{{ repo.url }}" class="repo-name" target="_blank">{{ repo.name }}</a>
                    {% if repo.is_fork %}
                    <span class="badge badge-fork">FORK</span>
                    {% endif %}
                    {% if repo.is_archived %}
                    <span class="badge badge-archived">ARCHIVED</span>
                    {% endif %}
                </div>
            </div>

            <div class="repo-meta">
                <div class="meta-item">
                    <span class="meta-label">Owner:</span> {{ repo.owner }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Language:</span> {{ repo.primary_language }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Created:</span> {{ repo.created_date.strftime('%Y-%m-%d') if repo.created_date else 'N/A' }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Last Commit:</span> {{ repo.last_commit_date.strftime('%Y-%m-%d') if repo.last_commit_date else 'N/A' }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Open Issues:</span> {{ repo.open_issues }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Open PRs:</span> {{ repo.open_prs }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Size:</span> {{ repo.size_kb }} KB
                </div>
            </div>

            <div class="contributors-section">
                <div class="contributors-title">Contributors ({{ repo.contributors|length }})</div>
                {% if repo.contributors %}
                <table class="contributors-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Contributions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for contributor in repo.contributors %}
                        <tr>
                            <td>{{ contributor.name }}</td>
                            <td>{{ contributor.email }}</td>
                            <td>{{ contributor.contributions }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="no-contributors">No contributors found</p>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function filterRepos() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const repoCards = document.querySelectorAll('.repo-card');

            repoCards.forEach(card => {
                const repoName = card.getAttribute('data-repo-name');
                if (repoName.includes(filter)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
    """

    # Calculate summary statistics
    total_repos = len(audit_data)
    total_contributors = len(set(
        c['name'] for repo in audit_data
        for c in repo['contributors']
    ))
    total_forks = sum(1 for repo in audit_data if repo['is_fork'])
    total_archived = sum(1 for repo in audit_data if repo['is_archived'])

    template = Template(html_template)
    html_content = template.render(
        org_name=org_name,
        generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_repos=total_repos,
        total_contributors=total_contributors,
        total_forks=total_forks,
        total_archived=total_archived,
        repos=audit_data
    )

    with open(filename, 'w') as f:
        f.write(html_content)

    print(f"HTML report saved to: {filename}")
