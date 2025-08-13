"""
Architecture analyzer for legacy code analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class ArchitectureAnalyzer:
    """Analyzes architecture patterns across multiple programs"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize architecture analyzer
        
        Args:
            output_dir: Output directory for analysis results
        """
        self.output_dir = Path(output_dir)
        self.architecture_dir = self.output_dir / 'architecture'
        self.architecture_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_architecture(self, 
                           programs_data: List[Dict[str, Any]], 
                           file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze architecture patterns across programs
        
        Args:
            programs_data: List of program data
            file_analyses: List of file analysis data
            
        Returns:
            Architecture analysis results
        """
        analysis = {
            'summary': {},
            'patterns': {},
            'dependencies': {},
            'complexity_metrics': {},
            'recommendations': [],
            'visualization_data': {}
        }
        
        # Generate summary statistics
        analysis['summary'] = self._generate_summary(programs_data, file_analyses)
        
        # Analyze patterns
        analysis['patterns'] = self._analyze_patterns(programs_data)
        
        # Analyze dependencies
        analysis['dependencies'] = self._analyze_dependencies(programs_data)
        
        # Calculate complexity metrics
        analysis['complexity_metrics'] = self._calculate_complexity_metrics(programs_data)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        # Generate visualization data
        analysis['visualization_data'] = self._generate_visualization_data(analysis)
        
        return analysis
    
    def _generate_summary(self, 
                         programs_data: List[Dict[str, Any]], 
                         file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_programs = len(programs_data)
        total_files = len(file_analyses)
        
        # Count program types
        program_types = Counter(prog.get('type', 'Unknown') for prog in programs_data)
        
        # Count statement types
        statement_types = Counter()
        total_statements = 0
        total_variables = 0
        total_procedures = 0
        
        for program in programs_data:
            ast_data = program.get('ast', {})
            statements = ast_data.get('statements', [])
            variables = ast_data.get('variables', [])
            procedures = ast_data.get('procedures', [])
            
            total_statements += len(statements)
            total_variables += len(variables)
            total_procedures += len(procedures)
            
            for stmt in statements:
                statement_types[stmt.get('type', 'Unknown')] += 1
        
        return {
            'total_programs': total_programs,
            'total_files': total_files,
            'total_statements': total_statements,
            'total_variables': total_variables,
            'total_procedures': total_procedures,
            'program_types': dict(program_types),
            'statement_types': dict(statement_types),
            'average_statements_per_program': total_statements / total_programs if total_programs > 0 else 0,
            'average_variables_per_program': total_variables / total_programs if total_programs > 0 else 0,
            'average_procedures_per_program': total_procedures / total_programs if total_programs > 0 else 0
        }
    
    def _analyze_patterns(self, programs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common patterns in the codebase"""
        patterns = {
            'common_statements': {},
            'variable_patterns': {},
            'procedure_patterns': {},
            'naming_conventions': {},
            'structural_patterns': {}
        }
        
        # Analyze common statements
        statement_patterns = defaultdict(int)
        for program in programs_data:
            ast_data = program.get('ast', {})
            for stmt in ast_data.get('statements', []):
                stmt_type = stmt.get('type', 'Unknown')
                statement_patterns[stmt_type] += 1
        
        patterns['common_statements'] = dict(statement_patterns)
        
        # Analyze variable patterns
        variable_types = defaultdict(int)
        variable_names = []
        for program in programs_data:
            ast_data = program.get('ast', {})
            for var in ast_data.get('variables', []):
                pic = var.get('pic', '')
                name = var.get('name', '')
                variable_types[pic] += 1
                variable_names.append(name)
        
        patterns['variable_patterns'] = {
            'pic_types': dict(variable_types),
            'naming_patterns': self._analyze_naming_patterns(variable_names)
        }
        
        # Analyze procedure patterns
        procedure_names = []
        for program in programs_data:
            ast_data = program.get('ast', {})
            for proc in ast_data.get('procedures', []):
                name = proc.get('name', '')
                procedure_names.append(name)
        
        patterns['procedure_patterns'] = {
            'naming_patterns': self._analyze_naming_patterns(procedure_names)
        }
        
        # Analyze structural patterns
        patterns['structural_patterns'] = self._analyze_structural_patterns(programs_data)
        
        return patterns
    
    def _analyze_dependencies(self, programs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze dependencies between programs (simplified)"""
        return {
            'call_graph': {},
            'dependency_matrix': {},
            'circular_dependencies': [],
            'dependency_chains': [],
            'isolated_programs': []
        }
    
    def _calculate_complexity_metrics(self, programs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate complexity metrics for the codebase"""
        metrics = {
            'cyclomatic_complexity': {},
            'nesting_depth': {},
            'overall_complexity': {}
        }
        
        total_complexity = 0
        total_nesting = 0
        program_count = len(programs_data)
        
        for program in programs_data:
            program_name = program.get('name', 'Unknown')
            ast_data = program.get('ast', {})
            statements = ast_data.get('statements', [])
            
            # Calculate cyclomatic complexity
            complexity = 1  # Base complexity
            for stmt in statements:
                if stmt.get('type') in ['IF', 'WHILE', 'PERFORM', 'CALL']:
                    complexity += 1
            
            metrics['cyclomatic_complexity'][program_name] = complexity
            total_complexity += complexity
            
            # Calculate nesting depth
            max_nesting = self._calculate_nesting_depth(statements)
            metrics['nesting_depth'][program_name] = max_nesting
            total_nesting = max(total_nesting, max_nesting)
        
        # Calculate averages
        metrics['overall_complexity'] = {
            'average_cyclomatic_complexity': total_complexity / program_count if program_count > 0 else 0,
            'max_nesting_depth': total_nesting,
            'complexity_distribution': self._get_complexity_distribution(metrics['cyclomatic_complexity'])
        }
        
        return metrics
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        summary = analysis['summary']
        complexity = analysis['complexity_metrics']
        dependencies = analysis['dependencies']
        
        # Complexity recommendations
        avg_complexity = complexity['overall_complexity']['average_cyclomatic_complexity']
        if avg_complexity > 10:
            recommendations.append("High cyclomatic complexity detected. Consider refactoring complex programs into smaller, more manageable functions.")
        
        max_nesting = complexity['overall_complexity']['max_nesting_depth']
        if max_nesting > 5:
            recommendations.append("Deep nesting detected. Consider flattening nested structures for better readability.")
        
        # Dependency recommendations
        if dependencies['circular_dependencies']:
            recommendations.append("Circular dependencies detected. Review program dependencies to eliminate cycles.")
        
        if dependencies['isolated_programs']:
            recommendations.append(f"Found {len(dependencies['isolated_programs'])} isolated programs. Consider if these can be removed or integrated.")
        
        # Size recommendations
        avg_statements = summary['average_statements_per_program']
        if avg_statements > 100:
            recommendations.append("Large programs detected. Consider breaking down large programs into smaller, focused modules.")
        
        # Statement type recommendations
        statement_types = summary['statement_types']
        if statement_types.get('GO TO', 0) > 0:
            recommendations.append("GO TO statements detected. Consider replacing with structured programming constructs.")
        
        # General modernization recommendations
        recommendations.extend([
            "Consider implementing unit tests for critical business logic.",
            "Document business rules and data flow for better maintainability.",
            "Review variable naming conventions for consistency.",
            "Consider implementing error handling and logging mechanisms."
        ])
        
        return recommendations
    
    def _generate_visualization_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for visualizations"""
        return {
            'complexity_chart': self._create_complexity_chart_data(analysis['complexity_metrics']),
            'pattern_analysis': self._create_pattern_analysis_data(analysis['patterns'])
        }
    
    def _analyze_naming_patterns(self, names: List[str]) -> Dict[str, Any]:
        """Analyze naming patterns in variables and procedures"""
        patterns = {
            'prefix_patterns': defaultdict(int),
            'suffix_patterns': defaultdict(int),
            'length_distribution': defaultdict(int),
            'case_patterns': defaultdict(int)
        }
        
        for name in names:
            if not name:
                continue
            
            # Analyze prefixes and suffixes
            if '_' in name:
                parts = name.split('_')
                if parts[0]:
                    patterns['prefix_patterns'][parts[0]] += 1
                if parts[-1]:
                    patterns['suffix_patterns'][parts[-1]] += 1
            
            # Analyze length
            length = len(name)
            patterns['length_distribution'][length] += 1
            
            # Analyze case patterns
            if name.isupper():
                patterns['case_patterns']['UPPERCASE'] += 1
            elif name.islower():
                patterns['case_patterns']['lowercase'] += 1
            elif name[0].isupper():
                patterns['case_patterns']['TitleCase'] += 1
            else:
                patterns['case_patterns']['mixed'] += 1
        
        return {k: dict(v) for k, v in patterns.items()}
    
    def _analyze_structural_patterns(self, programs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze structural patterns in programs"""
        patterns = {
            'division_usage': defaultdict(int),
            'section_usage': defaultdict(int),
            'statement_ordering': {},
            'variable_declaration_patterns': {}
        }
        
        for program in programs_data:
            ast_data = program.get('ast', {})
            
            # Analyze divisions
            divisions = ast_data.get('divisions', {})
            for division in divisions:
                patterns['division_usage'][division] += 1
            
            # Analyze sections
            for division, div_data in divisions.items():
                sections = div_data.get('sections', {})
                for section in sections:
                    patterns['section_usage'][section] += 1
        
        return {k: dict(v) for k, v in patterns.items()}
    

    
    def _calculate_nesting_depth(self, statements: List[Dict[str, Any]]) -> int:
        """Calculate maximum nesting depth of statements"""
        max_depth = 0
        current_depth = 0
        
        for statement in statements:
            if statement.get('type') in ['IF', 'WHILE', 'PERFORM']:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif statement.get('type') in ['END-IF', 'END-WHILE', 'END-PERFORM']:
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _get_complexity_distribution(self, complexity_dict: Dict[str, int]) -> Dict[str, int]:
        """Get distribution of complexity levels"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
        
        for complexity in complexity_dict.values():
            if complexity <= 5:
                distribution['low'] += 1
            elif complexity <= 10:
                distribution['medium'] += 1
            elif complexity <= 20:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
        
        return distribution
    

    
    def _create_complexity_chart_data(self, complexity: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for complexity chart visualization"""
        return {
            'programs': list(complexity['cyclomatic_complexity'].keys()),
            'complexity_values': list(complexity['cyclomatic_complexity'].values()),
            'nesting_values': list(complexity['nesting_depth'].values())
        }
    
    def _create_pattern_analysis_data(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for pattern analysis visualization"""
        return {
            'statement_types': patterns['common_statements'],
            'variable_types': patterns['variable_patterns'].get('pic_types', {}),
            'naming_patterns': patterns['variable_patterns'].get('naming_patterns', {})
        } 