"""
Management command to analyze and display performance metrics.
"""

import json
from django.core.management.base import BaseCommand
from core.performance import PerformanceAnalyzer


class Command(BaseCommand):
    help = 'Analyze and display performance metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours to analyze (default: 24)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format',
        )
        parser.add_argument(
            '--slow-endpoints',
            action='store_true',
            help='Show slowest endpoints',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show performance summary',
        )
    
    def handle(self, *args, **options):
        hours = options['hours']
        
        if options['slow_endpoints'] or not any([options['summary'], options['slow_endpoints']]):
            self.show_slow_endpoints(hours, options['json'])
        
        if options['summary'] or not any([options['summary'], options['slow_endpoints']]):
            self.show_performance_summary(hours, options['json'])
    
    def show_slow_endpoints(self, hours, json_output):
        """Display slowest endpoints."""
        slow_endpoints = PerformanceAnalyzer.get_slow_endpoints(hours)
        
        if json_output:
            self.stdout.write(json.dumps({'slow_endpoints': slow_endpoints}, indent=2))
        else:
            self.stdout.write(
                self.style.HTTP_INFO(f"\n📊 Slowest Endpoints (Last {hours} hours):")
            )
            self.stdout.write("=" * 80)
            
            if not slow_endpoints:
                self.stdout.write("No performance data available.")
                return
            
            for i, endpoint in enumerate(slow_endpoints, 1):
                avg_time = endpoint['avg_duration']
                max_time = endpoint['max_duration']
                count = endpoint['request_count']
                
                # Color code based on performance
                if avg_time > 2.0:
                    style = self.style.ERROR
                elif avg_time > 1.0:
                    style = self.style.WARNING
                else:
                    style = self.style.SUCCESS
                
                self.stdout.write(
                    style(f"{i:2}. {endpoint['endpoint']}")
                )
                self.stdout.write(
                    f"    Avg: {avg_time:.3f}s | Max: {max_time:.3f}s | Requests: {count}"
                )
                self.stdout.write("")
    
    def show_performance_summary(self, hours, json_output):
        """Display performance summary."""
        summary = PerformanceAnalyzer.get_performance_summary(hours)
        
        if json_output:
            self.stdout.write(json.dumps({'performance_summary': summary}, indent=2))
        else:
            self.stdout.write(
                self.style.HTTP_INFO(f"\n📈 Performance Summary (Last {hours} hours):")
            )
            self.stdout.write("=" * 50)
            
            if not summary or summary.get('request_count', 0) == 0:
                self.stdout.write("No performance data available.")
                return
            
            # Request count
            self.stdout.write(f"Total Requests: {summary['request_count']:,}")
            
            # Response times
            avg_time = summary['avg_response_time']
            p95_time = summary['p95_response_time']
            p99_time = summary['p99_response_time']
            
            # Color code response times
            if avg_time > 2.0:
                avg_style = self.style.ERROR
            elif avg_time > 1.0:
                avg_style = self.style.WARNING
            else:
                avg_style = self.style.SUCCESS
            
            self.stdout.write("")
            self.stdout.write("Response Times:")
            self.stdout.write(avg_style(f"  Average: {avg_time:.3f}s"))
            self.stdout.write(f"  95th percentile: {p95_time:.3f}s")
            self.stdout.write(f"  99th percentile: {p99_time:.3f}s")
            self.stdout.write(f"  Min: {summary['min_response_time']:.3f}s")
            self.stdout.write(f"  Max: {summary['max_response_time']:.3f}s")
            
            # Error rate
            error_rate = summary['error_rate']
            if error_rate > 5.0:
                error_style = self.style.ERROR
            elif error_rate > 1.0:
                error_style = self.style.WARNING
            else:
                error_style = self.style.SUCCESS
            
            self.stdout.write("")
            self.stdout.write(error_style(f"Error Rate: {error_rate:.2f}%"))
            
            # Performance assessment
            self.stdout.write("")
            self.stdout.write("Assessment:")
            
            if avg_time < 0.5 and error_rate < 1.0:
                self.stdout.write(self.style.SUCCESS("✅ Excellent performance"))
            elif avg_time < 1.0 and error_rate < 2.0:
                self.stdout.write(self.style.SUCCESS("✅ Good performance"))
            elif avg_time < 2.0 and error_rate < 5.0:
                self.stdout.write(self.style.WARNING("⚠️ Moderate performance"))
            else:
                self.stdout.write(self.style.ERROR("❌ Poor performance - optimization needed"))
            
            # Recommendations
            recommendations = []
            
            if avg_time > 1.0:
                recommendations.append("Consider optimizing slow endpoints")
            
            if p95_time > 3.0:
                recommendations.append("95th percentile is high - check for outliers")
            
            if error_rate > 2.0:
                recommendations.append("High error rate - investigate error causes")
            
            if summary['request_count'] > 10000:
                recommendations.append("High traffic - consider scaling")
            
            if recommendations:
                self.stdout.write("")
                self.stdout.write("Recommendations:")
                for rec in recommendations:
                    self.stdout.write(f"  • {rec}")
            
            self.stdout.write("")
