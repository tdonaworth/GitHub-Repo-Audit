# GitHub Organization Audit Tool

A CLI tool to audit GitHub organization repositories, generating comprehensive reports with repository metadata, contributors, and activity metrics. Designed to help identify outdated repositories for archival.

## Features

- **Comprehensive Repository Data**: Name, owner, creation date, last commit date, fork status, archive status
- **Activity Metrics**: Open issues count, open PRs count, primary language, repository size
- **Contributor Details**: Full list of contributors with names, emails, and contribution counts
- **Multiple Report Formats**: CSV for data analysis and HTML for visual review
- **Interactive HTML Report**: Searchable repository list with sortable data

## Requirements

- Python 3.7+
- GitHub Personal Access Token with the following scopes:
  - `repo` (full control of private repositories)
  - `read:org` (read org and team membership)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your GitHub token:
```bash
export GITHUB_TOKEN='your_personal_access_token_here'
```

To create a token, visit: https://github.com/settings/tokens

## Usage

Basic usage:
```bash
python audit.py <organization-name>
```

Custom output filename:
```bash
python audit.py <organization-name> --output my-custom-report
```

Performance options:
```bash
# Use more workers for faster processing (default: 10)
python audit.py <organization-name> --workers 20

# Use sequential processing (slower but more stable)
python audit.py <organization-name> --sequential
```

### Examples

```bash
# Audit the 'acme-corp' organization
python audit.py acme-corp

# Audit with custom output name
python audit.py acme-corp --output acme-q3-2026

# Audit with more concurrent workers for speed
python audit.py acme-corp --workers 15

# Audit sequentially (no concurrency)
python audit.py acme-corp --sequential
```

## Output

The tool generates two report files:

### CSV Report
- One row per repository-contributor pair
- Columns: repo_name, repo_url, owner, created_date, last_commit_date, is_fork, is_archived, open_issues, open_prs, primary_language, size_kb, contributor_name, contributor_email, contributions
- Suitable for importing into spreadsheet tools for further analysis

### HTML Report
- Visual report with summary statistics
- Repository cards with all metadata
- Contributor tables per repository
- Search/filter functionality
- Mobile-responsive design

## Report Fields

| Field | Description |
|-------|-------------|
| **repo_name** | Repository name |
| **repo_url** | GitHub URL to the repository |
| **owner** | Repository owner username |
| **created_date** | When the repository was created |
| **last_commit_date** | Date of the most recent commit |
| **is_fork** | Whether the repository is a fork |
| **is_archived** | Whether the repository is already archived |
| **open_issues** | Count of open issues (excluding PRs) |
| **open_prs** | Count of open pull requests |
| **primary_language** | Primary programming language |
| **size_kb** | Repository size in kilobytes |
| **contributor_name** | Contributor name or username |
| **contributor_email** | Contributor email (if available) |
| **contributions** | Number of contributions by this contributor |

## Use Cases

- **Repository Archival**: Identify inactive repositories based on last commit date and open issues/PRs
- **Contributor Audit**: See who has contributed to which repositories
- **Organization Cleanup**: Find forks, archived repos, and inactive projects
- **Compliance**: Generate documentation of organizational repository inventory

## Performance

The tool uses concurrent processing by default (10 workers) to speed up API calls. For large organizations:

- **Faster**: Increase workers with `--workers 20` (be mindful of rate limits)
- **More stable**: Use `--sequential` for sequential processing if you encounter issues
- **Contributor limit**: Top 100 contributors per repo to avoid slowness on huge repositories

## Limitations

- **Rate Limiting**: GitHub API has rate limits (5000 requests/hour for authenticated users). Large orgs may hit this limit.
- **Access**: Can only audit repositories the authenticated user has access to
- **Contributor cap**: Limited to top 100 contributors per repository for performance

## Troubleshooting

**Error: GITHUB_TOKEN environment variable not set**
- Ensure you've exported the token in your current shell session
- Verify the token has the correct scopes

**Error: Could not fetch commits/contributors**
- Some repositories may have restricted access or be empty
- These warnings can be safely ignored; the tool will continue processing other repos

**Rate Limit Exceeded**
- Wait for the rate limit to reset (typically 1 hour)
- Consider adding the `--output` flag to save progress
- Future versions will include rate limit handling

## Development

Project structure:
- `audit.py` - Main CLI entry point
- `github_client.py` - GitHub API wrapper
- `report_generator.py` - CSV and HTML report generation
- `requirements.txt` - Python dependencies

## License

MIT License - feel free to use and modify as needed.
