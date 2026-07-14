#!/usr/bin/env python3
"""
GitHub Organization Audit CLI Tool

Audits a GitHub organization's repositories and generates CSV and HTML reports
showing repository metadata, contributors, and activity metrics.
"""

import argparse
import os
import sys
from datetime import datetime
from github_client import GitHubAuditClient
from report_generator import generate_csv, generate_html


def get_github_token() -> str:
    """Get GitHub token from environment variable."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("\nPlease set your GitHub Personal Access Token:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("\nRequired scopes: repo, read:org")
        sys.exit(1)
    return token


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Audit a GitHub organization and generate reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit.py my-org
  python audit.py my-org --output my-audit

Required Environment Variables:
  GITHUB_TOKEN    Personal Access Token with 'repo' and 'read:org' scopes
        """
    )

    parser.add_argument(
        'organization',
        help='GitHub organization name to audit'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output filename prefix (default: <org>-audit-<date>)',
        default=None
    )

    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=10,
        help='Number of concurrent workers for API calls (default: 10)'
    )

    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Disable concurrent processing (slower but more reliable)'
    )

    args = parser.parse_args()

    # Get GitHub token
    token = get_github_token()

    # Generate output filename
    if args.output:
        output_prefix = args.output
    else:
        date_str = datetime.now().strftime('%Y%m%d')
        output_prefix = f"{args.organization}-audit-{date_str}"

    csv_filename = f"{output_prefix}.csv"
    html_filename = f"{output_prefix}.html"

    try:
        # Initialize client and perform audit
        print("=" * 60)
        print("GitHub Organization Audit Tool")
        print("=" * 60)

        client = GitHubAuditClient(token, max_workers=args.workers)
        audit_data = client.audit_organization(
            args.organization,
            use_concurrent=not args.sequential
        )

        # Generate reports
        print("\n" + "=" * 60)
        print("Generating Reports")
        print("=" * 60)

        generate_csv(audit_data, csv_filename)
        generate_html(audit_data, html_filename, args.organization)

        print("\n" + "=" * 60)
        print("Audit Complete!")
        print("=" * 60)
        print(f"Total repositories audited: {len(audit_data)}")
        print(f"\nReports saved:")
        print(f"  - CSV:  {csv_filename}")
        print(f"  - HTML: {html_filename}")

    except Exception as e:
        print(f"\nError during audit: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
