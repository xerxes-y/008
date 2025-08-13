"""
Result Reporter Component
Generates comprehensive test reports with input/output data
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ResultReporter:
    def __init__(self):
        self.report_templates = {
            'summary': {
                'title': 'Test Execution Summary',
                'sections': ['overview', 'statistics', 'failures', 'recommendations']
            },
            'detailed': {
                'title': 'Detailed Test Report',
                'sections': ['overview', 'test_results', 'coverage', 'performance', 'issues']
            }
        }

    async def generate_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("Generating test report...")
        
        # Calculate statistics
        statistics = self._calculate_statistics(test_results)
        
        # Analyze failures
        failures = self._analyze_failures(test_results)
        
        # Generate coverage analysis
        coverage = self._analyze_coverage(test_results)
        
        # Performance analysis
        performance = self._analyze_performance(test_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(test_results, failures, coverage)
        
        # Create comprehensive report
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_tests': len(test_results),
                'report_version': '1.0'
            },
            'summary': {
                'total_tests': statistics['total'],
                'passed': statistics['passed'],
                'failed': statistics['failed'],
                'skipped': statistics['skipped'],
                'success_rate': statistics['success_rate'],
                'total_execution_time': statistics['total_time']
            },
            'statistics': statistics,
            'failures': failures,
            'coverage': coverage,
            'performance': performance,
            'recommendations': recommendations,
            'detailed_results': test_results
        }
        
        logger.info(f"Generated report with {len(test_results)} test results")
        return report

    def _calculate_statistics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate test execution statistics"""
        total = len(test_results)
        passed = len([r for r in test_results if r.get('status') == 'PASSED'])
        failed = len([r for r in test_results if r.get('status') == 'FAILED'])
        skipped = len([r for r in test_results if r.get('status') == 'SKIPPED'])
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # Calculate execution times
        execution_times = [r.get('execution_time', 0) for r in test_results]
        total_time = sum(execution_times)
        avg_time = total_time / len(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        
        # Test type breakdown
        test_types = {}
        for result in test_results:
            test_type = result.get('test_case', {}).get('type', 'unknown')
            if test_type not in test_types:
                test_types[test_type] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            test_types[test_type]['total'] += 1
            status = result.get('status', 'UNKNOWN')
            if status == 'PASSED':
                test_types[test_type]['passed'] += 1
            elif status == 'FAILED':
                test_types[test_type]['failed'] += 1
            elif status == 'SKIPPED':
                test_types[test_type]['skipped'] += 1
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': round(success_rate, 2),
            'total_time': round(total_time, 2),
            'avg_time': round(avg_time, 2),
            'min_time': round(min_time, 2),
            'max_time': round(max_time, 2),
            'test_types': test_types
        }

    def _analyze_failures(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test failures"""
        failed_tests = [r for r in test_results if r.get('status') == 'FAILED']
        
        # Group failures by type
        failure_types = {}
        for test in failed_tests:
            test_type = test.get('test_case', {}).get('type', 'unknown')
            if test_type not in failure_types:
                failure_types[test_type] = []
            
            failure_info = {
                'test_name': test.get('test_case', {}).get('name', 'Unknown'),
                'error': test.get('error', 'Unknown error'),
                'execution_time': test.get('execution_time', 0),
                'timestamp': test.get('timestamp', '')
            }
            failure_types[test_type].append(failure_info)
        
        # Common error patterns
        error_patterns = {}
        for test in failed_tests:
            error = test.get('error', '')
            if error not in error_patterns:
                error_patterns[error] = 0
            error_patterns[error] += 1
        
        # Most common errors
        common_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_failures': len(failed_tests),
            'failure_types': failure_types,
            'common_errors': common_errors,
            'failure_rate': round(len(failed_tests) / len(test_results) * 100, 2) if test_results else 0
        }

    def _analyze_coverage(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test coverage"""
        coverage = {
            'services_tested': set(),
            'endpoints_tested': set(),
            'kafka_topics_tested': set(),
            'database_tables_tested': set(),
            'test_categories': set()
        }
        
        for result in test_results:
            test_case = result.get('test_case', {})
            test_type = test_case.get('type', '')
            category = test_case.get('category', '')
            
            coverage['test_categories'].add(category)
            
            if test_type == 'rest_api':
                service = test_case.get('service', '')
                endpoint = test_case.get('endpoint', '')
                if service:
                    coverage['services_tested'].add(service)
                if endpoint:
                    coverage['endpoints_tested'].add(f"{service}:{endpoint}")
            
            elif test_type == 'kafka':
                topic = test_case.get('topic', '')
                if topic:
                    coverage['kafka_topics_tested'].add(topic)
            
            elif test_type == 'database':
                schema = test_case.get('schema', '')
                table = test_case.get('table', '')
                if schema and table:
                    coverage['database_tables_tested'].add(f"{schema}.{table}")
        
        # Convert sets to lists for JSON serialization
        return {
            'services_tested': list(coverage['services_tested']),
            'endpoints_tested': list(coverage['endpoints_tested']),
            'kafka_topics_tested': list(coverage['kafka_topics_tested']),
            'database_tables_tested': list(coverage['database_tables_tested']),
            'test_categories': list(coverage['test_categories'])
        }

    def _analyze_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test performance"""
        # Performance by test type
        performance_by_type = {}
        
        for result in test_results:
            test_type = result.get('test_case', {}).get('type', 'unknown')
            execution_time = result.get('execution_time', 0)
            
            if test_type not in performance_by_type:
                performance_by_type[test_type] = {
                    'times': [],
                    'count': 0,
                    'total_time': 0
                }
            
            performance_by_type[test_type]['times'].append(execution_time)
            performance_by_type[test_type]['count'] += 1
            performance_by_type[test_type]['total_time'] += execution_time
        
        # Calculate performance metrics for each type
        for test_type, data in performance_by_type.items():
            times = data['times']
            data['avg_time'] = round(sum(times) / len(times), 2) if times else 0
            data['min_time'] = round(min(times), 2) if times else 0
            data['max_time'] = round(max(times), 2) if times else 0
            data['total_time'] = round(data['total_time'], 2)
            del data['times']  # Remove raw times to keep report clean
        
        # Identify slow tests
        slow_tests = []
        for result in test_results:
            execution_time = result.get('execution_time', 0)
            if execution_time > 10:  # Threshold for slow tests
                slow_tests.append({
                    'test_name': result.get('test_case', {}).get('name', 'Unknown'),
                    'test_type': result.get('test_case', {}).get('type', 'unknown'),
                    'execution_time': round(execution_time, 2),
                    'status': result.get('status', 'UNKNOWN')
                })
        
        # Sort slow tests by execution time
        slow_tests.sort(key=lambda x: x['execution_time'], reverse=True)
        
        return {
            'performance_by_type': performance_by_type,
            'slow_tests': slow_tests[:10],  # Top 10 slowest tests
            'performance_thresholds': {
                'slow_test_threshold': 10,  # seconds
                'very_slow_test_threshold': 30  # seconds
            }
        }

    def _generate_recommendations(self, test_results: List[Dict[str, Any]], failures: Dict[str, Any], coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Success rate recommendations
        success_rate = failures.get('failure_rate', 0)
        if success_rate > 20:
            recommendations.append({
                'type': 'critical',
                'category': 'test_quality',
                'title': 'High Failure Rate',
                'description': f'Test failure rate is {success_rate}%, which is above the recommended 20% threshold.',
                'action': 'Review and fix failing tests, investigate common error patterns.'
            })
        
        # Coverage recommendations
        if len(coverage.get('services_tested', [])) < 3:
            recommendations.append({
                'type': 'warning',
                'category': 'coverage',
                'title': 'Limited Service Coverage',
                'description': f'Only {len(coverage.get("services_tested", []))} services are being tested.',
                'action': 'Add tests for untested services to improve coverage.'
            })
        
        # Performance recommendations
        slow_tests = failures.get('slow_tests', [])
        if len(slow_tests) > 5:
            recommendations.append({
                'type': 'warning',
                'category': 'performance',
                'title': 'Multiple Slow Tests',
                'description': f'{len(slow_tests)} tests are taking longer than 10 seconds to execute.',
                'action': 'Optimize slow tests or investigate performance bottlenecks.'
            })
        
        # Test type distribution recommendations
        test_types = coverage.get('test_categories', [])
        if 'integration' not in test_types:
            recommendations.append({
                'type': 'info',
                'category': 'coverage',
                'title': 'Missing Integration Tests',
                'description': 'No integration tests found in the test suite.',
                'action': 'Add integration tests to verify end-to-end workflows.'
            })
        
        # Error pattern recommendations
        common_errors = failures.get('common_errors', [])
        if common_errors:
            top_error = common_errors[0]
            if top_error[1] > 3:  # More than 3 occurrences
                recommendations.append({
                    'type': 'critical',
                    'category': 'error_patterns',
                    'title': 'Recurring Error Pattern',
                    'description': f'Error "{top_error[0]}" occurs {top_error[1]} times.',
                    'action': 'Investigate and fix the root cause of this recurring error.'
                })
        
        return recommendations

    def save_report_to_file(self, report: Dict[str, Any], output_dir: Path, format: str = 'json') -> str:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"test_report_{timestamp}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'html':
            filename = f"test_report_{timestamp}.html"
            filepath = output_dir / filename
            
            html_content = self._generate_html_report(report)
            with open(filepath, 'w') as f:
                f.write(html_content)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Report saved to {filepath}")
        return str(filepath)

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Execution Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { display: flex; justify-content: space-around; margin: 20px 0; }
                .metric { text-align: center; padding: 10px; }
                .metric-value { font-size: 24px; font-weight: bold; }
                .passed { color: green; }
                .failed { color: red; }
                .skipped { color: orange; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .recommendation { margin: 10px 0; padding: 10px; border-left: 4px solid; }
                .critical { border-color: red; background-color: #ffe6e6; }
                .warning { border-color: orange; background-color: #fff3e6; }
                .info { border-color: blue; background-color: #e6f3ff; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Test Execution Report</h1>
                <p>Generated at: {generated_at}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <div class="metric-value passed">{passed}</div>
                    <div>Passed</div>
                </div>
                <div class="metric">
                    <div class="metric-value failed">{failed}</div>
                    <div>Failed</div>
                </div>
                <div class="metric">
                    <div class="metric-value skipped">{skipped}</div>
                    <div>Skipped</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{success_rate}%</div>
                    <div>Success Rate</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Statistics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Tests</td><td>{total_tests}</td></tr>
                    <tr><td>Total Execution Time</td><td>{total_time}s</td></tr>
                    <tr><td>Average Execution Time</td><td>{avg_time}s</td></tr>
                    <tr><td>Success Rate</td><td>{success_rate}%</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Coverage</h2>
                <table>
                    <tr><th>Component</th><th>Coverage</th></tr>
                    <tr><td>Services Tested</td><td>{services_count}</td></tr>
                    <tr><td>Endpoints Tested</td><td>{endpoints_count}</td></tr>
                    <tr><td>Kafka Topics Tested</td><td>{kafka_topics_count}</td></tr>
                    <tr><td>Database Tables Tested</td><td>{db_tables_count}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {recommendations_html}
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        summary = report.get('summary', {})
        coverage = report.get('coverage', {})
        recommendations = report.get('recommendations', [])
        
        # Generate recommendations HTML
        recommendations_html = ""
        for rec in recommendations:
            css_class = rec.get('type', 'info')
            recommendations_html += f"""
            <div class="recommendation {css_class}">
                <h4>{rec.get('title', '')}</h4>
                <p>{rec.get('description', '')}</p>
                <p><strong>Action:</strong> {rec.get('action', '')}</p>
            </div>
            """
        
        return html_template.format(
            generated_at=report.get('report_metadata', {}).get('generated_at', ''),
            passed=summary.get('passed', 0),
            failed=summary.get('failed', 0),
            skipped=summary.get('skipped', 0),
            success_rate=summary.get('success_rate', 0),
            total_tests=summary.get('total_tests', 0),
            total_time=summary.get('total_execution_time', 0),
            avg_time=summary.get('avg_time', 0),
            services_count=len(coverage.get('services_tested', [])),
            endpoints_count=len(coverage.get('endpoints_tested', [])),
            kafka_topics_count=len(coverage.get('kafka_topics_tested', [])),
            db_tables_count=len(coverage.get('database_tables_tested', [])),
            recommendations_html=recommendations_html
        )
