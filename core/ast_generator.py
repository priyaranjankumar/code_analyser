"""
AST Generator for legacy code analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from utils.file_utils import read_file_content
from plugins.base import PluginManager


class ASTGenerator:
    """Generates AST (Abstract Syntax Tree) from source code files"""
    
    def __init__(self, language: str = 'cobol'):
        """
        Initialize AST generator
        
        Args:
            language: Programming language to parse
        """
        self.language = language.lower()
        self.plugin_manager = PluginManager()
        self.parser = self.plugin_manager.get_parser(self.language)
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a source file and generate AST
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Dictionary containing AST data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        content = read_file_content(file_path)
        
        # Preprocess content using language-specific plugin
        preprocessed_content = self.parser.preprocess(content)
        
        # Generate AST
        ast_data = self.parser.parse(preprocessed_content)
        
        # Add metadata
        ast_data['metadata'] = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'language': self.language,
            'content_length': len(content),
            'preprocessed_length': len(preprocessed_content)
        }
        
        return ast_data
    
    def parse_string(self, content: str, file_name: str = "unknown") -> Dict[str, Any]:
        """
        Parse source code string and generate AST
        
        Args:
            content: Source code content
            file_name: Name of the file (for metadata)
            
        Returns:
            Dictionary containing AST data
        """
        # Preprocess content
        preprocessed_content = self.parser.preprocess(content)
        
        # Generate AST
        ast_data = self.parser.parse(preprocessed_content)
        
        # Add metadata
        ast_data['metadata'] = {
            'file_path': file_name,
            'file_name': file_name,
            'language': self.language,
            'content_length': len(content),
            'preprocessed_length': len(preprocessed_content)
        }
        
        return ast_data
    
    def validate_ast(self, ast_data: Dict[str, Any]) -> bool:
        """
        Validate AST data structure
        
        Args:
            ast_data: AST data to validate
            
        Returns:
            True if AST is valid
        """
        required_keys = ['metadata', 'programs']
        
        if not isinstance(ast_data, dict):
            return False
        
        for key in required_keys:
            if key not in ast_data:
                return False
        
        if not isinstance(ast_data['programs'], list):
            return False
        
        return True
    
    def get_ast_summary(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of AST data
        
        Args:
            ast_data: AST data to summarize
            
        Returns:
            Dictionary with AST summary
        """
        if not self.validate_ast(ast_data):
            return {'error': 'Invalid AST data'}
        
        programs = ast_data.get('programs', [])
        
        summary = {
            'total_programs': len(programs),
            'program_types': {},
            'total_statements': 0,
            'total_variables': 0,
            'total_procedures': 0
        }
        
        for program in programs:
            program_type = program.get('type', 'Unknown')
            summary['program_types'][program_type] = summary['program_types'].get(program_type, 0) + 1
            
            # Count statements, variables, procedures
            summary['total_statements'] += len(program.get('statements', []))
            summary['total_variables'] += len(program.get('variables', []))
            summary['total_procedures'] += len(program.get('procedures', []))
        
        return summary
    
    def extract_program_flow(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract program flow information from AST
        
        Args:
            ast_data: AST data
            
        Returns:
            List of program flow dictionaries
        """
        flows = []
        
        for program in ast_data.get('programs', []):
            flow = {
                'program_name': program.get('name', 'Unknown'),
                'program_type': program.get('type', 'Unknown'),
                'flow': self._extract_flow_from_program(program)
            }
            flows.append(flow)
        
        return flows
    
    def _extract_flow_from_program(self, program: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract flow information from a single program
        
        Args:
            program: Program AST data
            
        Returns:
            List of flow steps
        """
        flow = []
        
        for statement in program.get('statements', []):
            step = {
                'type': statement.get('type', 'Unknown'),
                'line': statement.get('line', 0),
                'content': statement.get('content', ''),
                'target': statement.get('target', None),
                'condition': statement.get('condition', None)
            }
            flow.append(step)
        
        return flow
    
    def find_dependencies(self, ast_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Find dependencies between programs
        
        Args:
            ast_data: AST data
            
        Returns:
            Dictionary mapping program names to their dependencies
        """
        dependencies = {}
        
        for program in ast_data.get('programs', []):
            program_name = program.get('name', 'Unknown')
            deps = []
            
            # Look for CALL statements, PERFORM statements, etc.
            for statement in program.get('statements', []):
                if statement.get('type') in ['CALL', 'PERFORM']:
                    target = statement.get('target')
                    if target:
                        deps.append(target)
            
            dependencies[program_name] = list(set(deps))  # Remove duplicates
        
        return dependencies
    
    def get_complexity_metrics(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complexity metrics for the code
        
        Args:
            ast_data: AST data
            
        Returns:
            Dictionary with complexity metrics
        """
        metrics = {
            'total_programs': 0,
            'total_statements': 0,
            'total_variables': 0,
            'cyclomatic_complexity': 0,
            'nesting_depth': 0,
            'average_statements_per_program': 0
        }
        
        programs = ast_data.get('programs', [])
        metrics['total_programs'] = len(programs)
        
        for program in programs:
            statements = program.get('statements', [])
            metrics['total_statements'] += len(statements)
            metrics['total_variables'] += len(program.get('variables', []))
            
            # Calculate cyclomatic complexity (simplified)
            for statement in statements:
                if statement.get('type') in ['IF', 'WHILE', 'PERFORM', 'CALL']:
                    metrics['cyclomatic_complexity'] += 1
            
            # Calculate nesting depth
            max_nesting = self._calculate_nesting_depth(statements)
            metrics['nesting_depth'] = max(metrics['nesting_depth'], max_nesting)
        
        if metrics['total_programs'] > 0:
            metrics['average_statements_per_program'] = metrics['total_statements'] / metrics['total_programs']
        
        return metrics
    
    def _calculate_nesting_depth(self, statements: List[Dict[str, Any]]) -> int:
        """
        Calculate maximum nesting depth of statements
        
        Args:
            statements: List of statement dictionaries
            
        Returns:
            Maximum nesting depth
        """
        max_depth = 0
        current_depth = 0
        
        for statement in statements:
            if statement.get('type') in ['IF', 'WHILE', 'PERFORM']:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif statement.get('type') in ['END-IF', 'END-WHILE', 'END-PERFORM']:
                current_depth = max(0, current_depth - 1)
        
        return max_depth 