"""Cloud Engineer Agent - Entry point for feature implementation from GitLab issues."""

import argparse
import json
import logging
import sys
from typing import Dict, Any

from agent.app.cloud_engineer_agent import CloudEngineerAgent


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def load_issue_content(file_path: str) -> str:
    """Load issue content from file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Issue content file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading issue content file: {e}")


def save_results(results: Dict[str, Any], output_file: str) -> None:
    """Save implementation results to file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")


def main():
    """Main entry point for the Cloud Engineer Agent."""
    parser = argparse.ArgumentParser(
        description="Cloud Engineer Agent - Implement features from GitLab issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Implement feature from issue content
  python main.py --issue-id 123 --issue-content "Title: Add monitoring\\n## Context\\n..." --project-name my-project --target-branch main

  # Load issue content from file
  python main.py --issue-id 123 --issue-file issue.md --project-name my-project --target-branch main

  # Save results to file
  python main.py --issue-id 123 --issue-file issue.md --project-name my-project --target-branch main --output results.json

  # Start new session with additional prompt
  python main.py --issue-id 123 --issue-file issue.md --project-name my-project --target-branch main --prompt "Focus on security best practices"

  # Continue existing session with specific session ID
  python main.py --issue-id 123 --issue-file issue.md --project-name my-project --target-branch main --session-id "abc123-def456" --prompt "Add comprehensive monitoring"
        """,
    )

    # Required arguments
    parser.add_argument("--issue-id", required=True, help="GitLab issue ID")

    parser.add_argument(
        "--project-name", required=True, help="GitLab project name or URL-encoded path"
    )

    parser.add_argument(
        "--target-branch", required=True, help="Target branch to base implementation on"
    )

    # Issue content (mutually exclusive)
    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument(
        "--issue-content",
        help="Issue content as string (with title, context, todo, definition of done)",
    )
    content_group.add_argument(
        "--issue-file", help="Path to file containing issue content"
    )

    # Optional arguments
    parser.add_argument("--output", help="Output file to save results (JSON format)")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate inputs without executing implementation",
    )

    parser.add_argument(
        "--session-id",
        help="Session ID to continue existing session or create new one if not provided",
    )

    parser.add_argument(
        "--prompt",
        help="Additional prompt text to append to the existing prompt",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load issue content
        if args.issue_file:
            logger.info(f"Loading issue content from: {args.issue_file}")
            issue_content = load_issue_content(args.issue_file)
        else:
            issue_content = args.issue_content

        logger.info(f"Starting feature implementation for issue {args.issue_id}")

        if args.dry_run:
            # Dry run - validate inputs only
            logger.info("Dry run mode - validating inputs...")
            agent = CloudEngineerAgent(
                session_id=args.session_id, additional_prompt=args.prompt
            )
            parsed_issue = agent.parse_issue_content(issue_content)

            print("✅ Validation successful!")
            print(f"Issue Title: {parsed_issue.title}")
            print(f"Context Length: {len(parsed_issue.context)} characters")
            print(f"Todo Length: {len(parsed_issue.todo)} characters")
            print(
                f"Definition of Done Length: {len(parsed_issue.definition_of_done)} characters"
            )

            agent.cleanup()
            return

        # Execute implementation
        agent = CloudEngineerAgent(
            session_id=args.session_id, additional_prompt=args.prompt
        )

        try:
            results = agent.implement_feature(
                issue_id=args.issue_id,
                description=issue_content,
                project_name=args.project_name,
                target_branch=args.target_branch,
            )

            # Print summary
            if results["status"] == "success":
                print("✅ Feature implementation completed successfully!")
                print(f"Feature Branch: {results['feature_branch']}")
                if "merge_request_result" in results:
                    mr_result = results["merge_request_result"]
                    if "web_url" in mr_result:
                        print(f"Merge Request: {mr_result['web_url']}")
            else:
                print("❌ Feature implementation failed!")
                print(f"Error: {results.get('message', 'Unknown error')}")

            # Save results if output file specified
            if args.output:
                save_results(results, args.output)

            # Exit with appropriate code
            sys.exit(0 if results["status"] == "success" else 1)

        finally:
            agent.cleanup()

    except KeyboardInterrupt:
        print("\n🛑 Implementation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Implementation failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
