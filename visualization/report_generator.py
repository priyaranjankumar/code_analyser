"""
Report generator for comprehensive HTML reports
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Template
from datetime import datetime


class ReportGenerator:
    """Generates comprehensive HTML reports"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize report generator
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = Path(output_dir)
        self.html_dir = self.output_dir / 'html'
        self.html_dir.mkdir(parents=True, exist_ok=True)
        
        # Load HTML template
        self.template = self._load_template()
    
    def _load_template(self) -> Template:
        """Load HTML report template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legacy Code Analysis Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .section h2 {
            margin-top: 0;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        .file-list {
            list-style: none;
            padding: 0;
        }
        .file-item {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #28a745;
        }
        .file-name {
            font-weight: bold;
            color: #495057;
        }
        .file-info {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .program-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .program-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }
        .program-name {
            font-weight: bold;
            color: #495057;
            margin-bottom: 10px;
        }
        .program-summary {
            color: #6c757d;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 15px;
            margin: 20px 0;
        }
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
        }
        .recommendations ul {
            color: #856404;
            margin: 10px 0;
        }
        .recommendations li {
            margin: 5px 0;
        }
        .recommendation-tips {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            padding: 15px;
            margin-top: 15px;
        }
        .recommendation-tips h4 {
            color: #0056b3;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .recommendation-tips ul {
            color: #0056b3;
            margin: 10px 0;
        }
        .recommendation-tips li {
            margin: 5px 0;
            font-size: 0.95em;
        }
        .footer {
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }
        .nav-tabs {
            display: flex;
            border-bottom: 2px solid #dee2e6;
            margin-bottom: 20px;
        }
        .nav-tab {
            padding: 10px 20px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            border-radius: 6px 6px 0 0;
            margin-right: 5px;
        }
        .nav-tab.active {
            background: #007bff;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-primary {
            background: #007bff;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-small {
            padding: 4px 8px;
            font-size: 0.8em;
        }
        .program-stats {
            margin: 10px 0;
        }
        .stat {
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 10px;
        }
        .program-actions {
            margin-top: 10px;
        }

        .program-summaries {
            margin-top: 20px;
        }
        .program-summary-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 4px solid #007bff;
        }
        .program-summary-card h5 {
            color: #495057;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .summary-content {
            line-height: 1.6;
            color: #495057;
        }
        .summary-content br {
            margin-bottom: 8px;
        }
        .pattern-analysis {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .pattern-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .pattern-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .pattern-name {
            font-weight: bold;
            color: #495057;
        }
        .pattern-count {
            background: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .modal-title {
            font-size: 1.5em;
            font-weight: bold;
            color: #495057;
            margin: 0;
        }
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover {
            color: #000;
        }
        .modal-body {
            line-height: 1.6;
            color: #495057;
        }
        .modal-body p {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Legacy Code Analysis Report</h1>
            <p>Comprehensive analysis of {{ language.upper() }} codebase</p>
            <p>Generated on {{ generation_date }}</p>
        </div>
        
        <div class="content">
            <!-- Navigation Tabs -->
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">Overview</button>
                <button class="nav-tab" onclick="showTab('programs')">Programs</button>
                <button class="nav-tab" onclick="showTab('architecture')">Architecture</button>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h2>Analysis Summary</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{{ summary.total_files }}</div>
                            <div class="stat-label">Files Analyzed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ summary.total_programs }}</div>
                            <div class="stat-label">Programs Found</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Complexity Metrics</h2>
                    <div class="chart-container">
                        <canvas id="overviewComplexityChart" width="400" height="200"></canvas>
                    </div>
                </div>
                

            </div>
            

            
            <!-- Programs Tab -->
            <div id="programs" class="tab-content">
                <div class="section">
                    <h2>Programs Overview</h2>
                    <div class="program-list">
                        {% for program in programs_data %}
                        <div class="program-card">
                            <div class="program-name">{{ program.name }}</div>
                            <div class="program-stats">
                                <span class="stat">File: {{ program.file.split('/')[-1] }}</span>
                                <span class="stat">Type: {{ program.type }}</span>
                            </div>
                            <div class="program-actions">
                                {% if program.flowchart_file %}
                                <a href="{{ program.flowchart_file }}" class="btn btn-primary" target="_blank">View Flowchart</a>
                                {% endif %}
                                <button class="btn btn-secondary" onclick="showProgramSummary('{{ program.name }}')">View Summary</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Program Analysis Recommendations</h2>
                    <div class="recommendations">
                        <h3>Program-Specific Insights</h3>
                        <ul>
                            <li><strong>Flowchart Analysis:</strong> Use interactive flowcharts to understand program logic and identify optimization opportunities</li>
                            <li><strong>Summary Review:</strong> Click "View Summary" for AI-generated insights about each program's purpose and structure</li>
                            <li><strong>Dependency Mapping:</strong> Check the Architecture tab to understand program relationships and call patterns</li>
                            <li><strong>Modernization Priority:</strong> Focus on programs with high complexity or frequent dependencies first</li>
                        </ul>
                        <div class="recommendation-tips">
                            <h4>🔍 Analysis Tips:</h4>
                            <ul>
                                <li>Programs with many procedures may benefit from modularization</li>
                                <li>High statement counts suggest potential for refactoring</li>
                                <li>Check flowchart patterns for repetitive logic that could be extracted</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Architecture Tab -->
            <div id="architecture" class="tab-content">
                {% if architecture_data %}
                <div class="section">
                    <h2>Architecture Summary</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{{ architecture_data.summary.total_programs }}</div>
                            <div class="stat-label">Total Programs</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ architecture_data.summary.total_statements }}</div>
                            <div class="stat-label">Total Statements</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ "%.1f"|format(architecture_data.summary.average_statements_per_program) }}</div>
                            <div class="stat-label">Avg Statements/Program</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ architecture_data.summary.total_procedures }}</div>
                            <div class="stat-label">Total Procedures</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Common Patterns</h2>
                    <div class="pattern-analysis">
                        <h3>Most Common Statement Types</h3>
                        <div class="pattern-list">
                            {% for stmt_type, count in architecture_data.patterns.common_statements.items() %}
                            {% if count > 5 %}
                            <div class="pattern-item">
                                <span class="pattern-name">{{ stmt_type }}</span>
                                <span class="pattern-count">{{ count }}</span>
                            </div>
                            {% endif %}
                            {% endfor %}
                        </div>
                    </div>
                </div>
                

                

                
                <div class="section">
                    <h2>Statement Type Distribution</h2>
                    <div class="chart-container">
                        <canvas id="patternChart" width="400" height="200"></canvas>
                    </div>
                </div>
                

                {% else %}
                <div class="section">
                    <h2>Architecture Analysis</h2>
                    <p>No architecture data available. Run analysis with --generate-architecture flag.</p>
                </div>
                {% endif %}
            </div>
            

        </div>
        
        <!-- Summary Modal -->
        <div id="summaryModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title" id="modalTitle">Program Summary</h2>
                    <span class="close" onclick="closeModal()">&times;</span>
                </div>
                <div class="modal-body" id="modalBody">
                    <!-- Summary content will be inserted here -->
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Legacy Code Analyzer v1.0.0</p>
            <p>Analysis completed in {{ analysis_time }} seconds</p>
        </div>
    </div>

    <script>
        // Tab functionality
        function showTab(tabName) {
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all nav tabs
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
        }
        
        // Charts
        document.addEventListener('DOMContentLoaded', function() {
            // Overview Complexity Chart
            const overviewComplexityCtx = document.getElementById('overviewComplexityChart');
            if (overviewComplexityCtx) {
                new Chart(overviewComplexityCtx.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: ['Low', 'Medium', 'High', 'Very High'],
                        datasets: [{
                            label: 'Programs by Complexity',
                            data: {{ complexity_distribution | safe }},
                            backgroundColor: ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            

            
            // Pattern Chart
            const patternCtx = document.getElementById('patternChart');
            if (patternCtx) {
                new Chart(patternCtx.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: {{ statement_types_labels | safe }},
                        datasets: [{
                            data: {{ statement_types_data | safe }},
                            backgroundColor: [
                                '#007bff', '#28a745', '#ffc107', '#dc3545',
                                '#6f42c1', '#fd7e14', '#20c997', '#6c757d'
                            ]
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });
            }
        });
        
        // Program summary data
        const programSummaries = {
            {% for program in programs_data %}
            '{{ program.name }}': `{{ program.summary | replace('\n', '\\n') | replace("'", "\\'") | safe }}`,
            {% endfor %}
        };
        
        function showProgramSummary(programName) {
            const summary = programSummaries[programName];
            if (summary) {
                document.getElementById('modalTitle').textContent = `${programName} Summary`;
                document.getElementById('modalBody').innerHTML = summary.replace(/\\n/g, '<br>');
                document.getElementById('summaryModal').style.display = 'block';
            } else {
                alert('Summary not available for this program.');
            }
        }
        
        function closeModal() {
            document.getElementById('summaryModal').style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('summaryModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
        """
        return Template(template_content)
    
    def generate_report(self, 
                       file_analyses: List[Dict[str, Any]], 
                       programs_data: List[Dict[str, Any]], 
                       analysis_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive HTML report
        
        Args:
            file_analyses: List of file analysis data
            programs_data: List of program data
            analysis_results: Analysis results summary
            
        Returns:
            Path to generated HTML report
        """
        try:
            # Load architecture data if available
            architecture_data = {}
            if 'architecture_report' in analysis_results:
                try:
                    import json
                    with open(analysis_results['architecture_report'], 'r') as f:
                        architecture_data = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load architecture data: {e}")
            
            # Prepare template variables
            template_vars = {
                'language': 'cobol',
                'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total_files': len(file_analyses),
                    'total_programs': len(programs_data)
                },
                'file_analyses': file_analyses,
                'programs_data': programs_data,
                'recommendations': self._get_recommendations(analysis_results),
                'complexity_distribution': self._get_complexity_distribution(programs_data),
                'statement_types_labels': self._get_statement_types_labels(file_analyses),
                'statement_types_data': self._get_statement_types_data(file_analyses),
                'analysis_time': analysis_results.get('analysis_time', 0),
                'architecture_data': architecture_data
            }
            
            # Generate HTML file
            report_file = self.html_dir / 'comprehensive_report.html'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(self.template.render(**template_vars))
            
            return str(report_file)
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def _get_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get recommendations from analysis results"""
        recommendations = [
            "Consider implementing unit tests for critical business logic",
            "Document business rules and data flow for better maintainability",
            "Review variable naming conventions for consistency",
            "Consider implementing error handling and logging mechanisms",
            "Evaluate opportunities for code modernization and refactoring"
        ]
        
        # Add specific recommendations based on analysis
        if analysis_results.get('files_analyzed', 0) > 10:
            recommendations.append("Large codebase detected - consider modularization")
        
        return recommendations
    
    def _get_complexity_distribution(self, programs_data: List[Dict[str, Any]]) -> List[int]:
        """Get complexity distribution for chart"""
        distribution = [0, 0, 0, 0]  # Low, Medium, High, Very High
        
        for program in programs_data:
            ast_data = program.get('ast', {})
            statements = ast_data.get('statements', [])
            
            # Calculate complexity based on control flow statements
            complexity = 1
            for stmt in statements:
                stmt_type = stmt.get('type', '')
                if stmt_type in ['IF', 'ELSE', 'END-IF', 'PERFORM', 'CALL', 'WHILE', 'UNTIL']:
                    complexity += 1
            
            # Categorize complexity
            if complexity <= 3:
                distribution[0] += 1  # Low
            elif complexity <= 8:
                distribution[1] += 1  # Medium
            elif complexity <= 15:
                distribution[2] += 1  # High
            else:
                distribution[3] += 1  # Very High
        
        return distribution
    
    def _get_statement_types_labels(self, file_analyses: List[Dict[str, Any]]) -> List[str]:
        """Get statement type labels for chart"""
        statement_counts = {}
        
        # Count statement types from all programs
        for file_analysis in file_analyses:
            programs = file_analysis.get('programs', [])
            for program in programs:
                ast_data = program.get('ast', {})
                statements = ast_data.get('statements', [])
                for stmt in statements:
                    stmt_type = stmt.get('type', 'Unknown')
                    statement_counts[stmt_type] = statement_counts.get(stmt_type, 0) + 1
        
        # Get top 8 statement types
        sorted_types = sorted(statement_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        return [stmt_type for stmt_type, _ in sorted_types]
    
    def _get_statement_types_data(self, file_analyses: List[Dict[str, Any]]) -> List[int]:
        """Get statement type data for chart"""
        statement_counts = {}
        
        # Count statement types from all programs
        for file_analysis in file_analyses:
            programs = file_analysis.get('programs', [])
            for program in programs:
                ast_data = program.get('ast', {})
                statements = ast_data.get('statements', [])
                for stmt in statements:
                    stmt_type = stmt.get('type', 'Unknown')
                    statement_counts[stmt_type] = statement_counts.get(stmt_type, 0) + 1
        
        # Get top 8 statement types
        sorted_types = sorted(statement_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        return [count for _, count in sorted_types] 