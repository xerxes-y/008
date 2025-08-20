#!/usr/bin/env python3
"""
Jira Integration for QA Automation Framework
Reports test results to Jira tickets in Jenkins pipelines
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class JiraConfig:
    """Jira configuration"""
    base_url: str
    username: str
    api_token: str
    project_key: str
    issue_type: str = "Test Execution"
    custom_fields: Optional[Dict[str, Any]] = None

class JiraIntegration:
    """Jira integration for reporting test results"""
    
    def __init__(self, config: JiraConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.username, config.api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_test_execution_issue(self, 
                                  summary: str,
                                  description: str,
                                  test_results: Dict[str, Any],
                                  build_info: Dict[str, Any]) -> Optional[str]:
        """Create a test execution issue in Jira"""
        try:
            issue_data = {
                "fields": {
                    "project": {"key": self.config.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": self.config.issue_type}
                }
            }
            
            # Add custom fields if provided
            if self.config.custom_fields:
                issue_data["fields"].update(self.config.custom_fields)
            
            # Add test execution details
            self._add_test_execution_fields(issue_data, test_results, build_info)
            
            response = self.session.post(
                urljoin(self.config.base_url, "/rest/api/2/issue"),
                json=issue_data
            )
            
            if response.status_code == 201:
                issue_key = response.json()["key"]
                logger.info(f"Created Jira issue: {issue_key}")
                return issue_key
            else:
                logger.error(f"Failed to create Jira issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Jira issue: {e}")
            return None
    
    def update_issue_with_results(self, 
                                issue_key: str,
                                test_results: Dict[str, Any],
                                build_info: Dict[str, Any]) -> bool:
        """Update existing issue with test results"""
        try:
            # Create comment with test results
            comment = self._create_test_results_comment(test_results, build_info)
            
            comment_data = {
                "body": comment
            }
            
            response = self.session.post(
                urljoin(self.config.base_url, f"/rest/api/2/issue/{issue_key}/comment"),
                json=comment_data
            )
            
            if response.status_code == 201:
                logger.info(f"Updated Jira issue {issue_key} with test results")
                return True
            else:
                logger.error(f"Failed to update Jira issue: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Jira issue: {e}")
            return False
    
    def add_attachment(self, issue_key: str, file_path: str, filename: str = None) -> bool:
        """Add attachment to Jira issue"""
        try:
            if not filename:
                filename = Path(file_path).name
            
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                
                response = self.session.post(
                    urljoin(self.config.base_url, f"/rest/api/2/issue/{issue_key}/attachments"),
                    files=files
                )
            
            if response.status_code == 200:
                logger.info(f"Added attachment {filename} to Jira issue {issue_key}")
                return True
            else:
                logger.error(f"Failed to add attachment: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding attachment: {e}")
            return False
    
    def _add_test_execution_fields(self, 
                                  issue_data: Dict[str, Any],
                                  test_results: Dict[str, Any],
                                  build_info: Dict[str, Any]):
        """Add test execution specific fields to issue"""
        summary = test_results.get('summary', {})
        
        # Add test execution details as custom fields or description
        execution_details = f"""
**Test Execution Summary:**
- Total Tests: {summary.get('total_tests', 0)}
- Passed: {summary.get('passed', 0)}
- Failed: {summary.get('failed', 0)}
- Success Rate: {summary.get('success_rate', 0)}%
- Execution Time: {summary.get('total_execution_time', 0)}s

**Build Information:**
- Build Number: {build_info.get('build_number', 'N/A')}
- Build URL: {build_info.get('build_url', 'N/A')}
- Git Branch: {build_info.get('git_branch', 'N/A')}
- Git Commit: {build_info.get('git_commit', 'N/A')}
- Environment: {build_info.get('environment', 'N/A')}
        """
        
        # Append to description
        if 'description' in issue_data['fields']:
            issue_data['fields']['description'] += execution_details
        else:
            issue_data['fields']['description'] = execution_details
    
    def _create_test_results_comment(self, 
                                   test_results: Dict[str, Any],
                                   build_info: Dict[str, Any]) -> str:
        """Create a formatted comment with test results"""
        summary = test_results.get('summary', {})
        
        comment = f"""
h3. Test Execution Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

h4. Summary
* Total Tests: {summary.get('total_tests', 0)}
* Passed: {summary.get('passed', 0)}
* Failed: {summary.get('failed', 0)}
* Skipped: {summary.get('skipped', 0)}
* Success Rate: {summary.get('success_rate', 0)}%

h4. Build Information
* Build Number: {build_info.get('build_number', 'N/A')}
* Build URL: {build_info.get('build_url', 'N/A')}
* Git Branch: {build_info.get('git_branch', 'N/A')}
* Git Commit: {build_info.get('git_commit', 'N/A')}
* Environment: {build_info.get('environment', 'N/A')}
        """
        
        # Add test suite breakdown
        test_suites = test_results.get('test_suites', {})
        if test_suites:
            comment += "\nh4. Test Suite Breakdown\n"
            for suite_name, suite_stats in test_suites.items():
                comment += f"* {suite_name}: {suite_stats.get('passed', 0)}/{suite_stats.get('total', 0)} passed\n"
        
        # Add failures if any
        failures = test_results.get('failures', {})
        if failures and failures.get('total_failures', 0) > 0:
            comment += f"\nh4. Failures ({failures.get('total_failures', 0)})\n"
            detailed_results = test_results.get('detailed_results', [])
            for result in detailed_results[:5]:  # Show first 5 failures
                if result.get('status') == 'FAILED':
                    comment += f"* {result.get('test_name', 'Unknown')}: {result.get('error', 'Unknown error')}\n"
        
        return comment

def load_jira_config_from_env() -> Optional[JiraConfig]:
    """Load Jira configuration from environment variables"""
    try:
        return JiraConfig(
            base_url=os.getenv('JIRA_BASE_URL'),
            username=os.getenv('JIRA_USERNAME'),
            api_token=os.getenv('JIRA_API_TOKEN'),
            project_key=os.getenv('JIRA_PROJECT_KEY'),
            issue_type=os.getenv('JIRA_ISSUE_TYPE', 'Test Execution')
        )
    except Exception as e:
        logger.error(f"Failed to load Jira config from environment: {e}")
        return None

def load_jira_config_from_file(config_file: str) -> Optional[JiraConfig]:
    """Load Jira configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return JiraConfig(
            base_url=config_data['base_url'],
            username=config_data['username'],
            api_token=config_data['api_token'],
            project_key=config_data['project_key'],
            issue_type=config_data.get('issue_type', 'Test Execution'),
            custom_fields=config_data.get('custom_fields')
        )
    except Exception as e:
        logger.error(f"Failed to load Jira config from file: {e}")
        return None

def report_to_jira(test_results_file: str,
                  build_info: Dict[str, Any],
                  jira_ticket: Optional[str] = None,
                  config_source: str = 'env') -> Optional[str]:
    """Main function to report test results to Jira"""
    try:
        # Load test results
        with open(test_results_file, 'r') as f:
            test_results = json.load(f)
        
        # Load Jira configuration
        if config_source == 'env':
            jira_config = load_jira_config_from_env()
        else:
            jira_config = load_jira_config_from_file(config_source)
        
        if not jira_config:
            logger.error("Failed to load Jira configuration")
            return None
        
        # Initialize Jira integration
        jira = JiraIntegration(jira_config)
        
        summary = test_results.get('summary', {})
        
        if jira_ticket:
            # Update existing ticket
            success = jira.update_issue_with_results(jira_ticket, test_results, build_info)
            if success:
                # Add test report as attachment
                jira.add_attachment(jira_ticket, test_results_file, "test_report.json")
                logger.info(f"Successfully reported results to Jira ticket: {jira_ticket}")
                return jira_ticket
            else:
                logger.error(f"Failed to update Jira ticket: {jira_ticket}")
                return None
        else:
            # Create new ticket
            summary_text = f"QA Test Execution - {summary.get('passed', 0)}/{summary.get('total_tests', 0)} passed"
            description = f"Automated test execution results from Jenkins build {build_info.get('build_number', 'N/A')}"
            
            issue_key = jira.create_test_execution_issue(
                summary=summary_text,
                description=description,
                test_results=test_results,
                build_info=build_info
            )
            
            if issue_key:
                # Add test report as attachment
                jira.add_attachment(issue_key, test_results_file, "test_report.json")
                logger.info(f"Created new Jira ticket: {issue_key}")
                return issue_key
            else:
                logger.error("Failed to create Jira ticket")
                return None
                
    except Exception as e:
        logger.error(f"Error reporting to Jira: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Report test results to Jira')
    parser.add_argument('--test-results', required=True, help='Path to test results JSON file')
    parser.add_argument('--jira-ticket', help='Existing Jira ticket key to update')
    parser.add_argument('--config-file', help='Path to Jira config JSON file')
    parser.add_argument('--build-number', required=True, help='Build number')
    parser.add_argument('--build-url', help='Build URL')
    parser.add_argument('--git-branch', help='Git branch')
    parser.add_argument('--git-commit', help='Git commit hash')
    parser.add_argument('--environment', default='ci', help='Environment')
    
    args = parser.parse_args()
    
    build_info = {
        'build_number': args.build_number,
        'build_url': args.build_url,
        'git_branch': args.git_branch,
        'git_commit': args.git_commit,
        'environment': args.environment
    }
    
    config_source = args.config_file if args.config_file else 'env'
    
    issue_key = report_to_jira(
        test_results_file=args.test_results,
        build_info=build_info,
        jira_ticket=args.jira_ticket,
        config_source=config_source
    )
    
    if issue_key:
        print(f"Jira issue: {issue_key}")
        sys.exit(0)
    else:
        print("Failed to report to Jira")
        sys.exit(1)
