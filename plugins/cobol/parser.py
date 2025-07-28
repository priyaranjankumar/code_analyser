"""
COBOL parser for legacy code analysis
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from ..base import BaseParser


class COBOLParser(BaseParser):
    """Parser for COBOL source code"""
    
    def __init__(self):
        # COBOL keywords and patterns
        self.divisions = ['IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE']
        self.sections = ['CONFIGURATION', 'INPUT-OUTPUT', 'FILE', 'WORKING-STORAGE', 'LINKAGE']
        
        # Statement patterns
        self.statement_patterns = {
            'PROGRAM-ID': r'PROGRAM-ID\.\s+(\w+)',
            'CALL': r'CALL\s+["\']?(\w+)["\']?',
            'PERFORM': r'PERFORM\s+(\w+)',
            'IF': r'IF\s+(.+)',
            'ELSE': r'ELSE',
            'END-IF': r'END-IF',
            'MOVE': r'MOVE\s+(.+)',
            'DISPLAY': r'DISPLAY\s+(.+)',
            'ACCEPT': r'ACCEPT\s+(.+)',
            'READ': r'READ\s+(\w+)',
            'WRITE': r'WRITE\s+(\w+)',
            'OPEN': r'OPEN\s+(.+)',
            'CLOSE': r'CLOSE\s+(.+)',
            'STOP': r'STOP\s+(.+)',
            'EXIT': r'EXIT',
            'GO TO': r'GO\s+TO\s+(\w+)',
            'PARAGRAPH': r'(\w+)\.',
            'VARIABLE': r'(\d+)\s+(\w+)\s+PIC\s+(.+)',
            'COMMENT': r'^\s*\*.*$'
        }
    
    def preprocess(self, content: str) -> str:
        """
        Preprocess COBOL source code
        
        Args:
            content: Raw COBOL source code
            
        Returns:
            Preprocessed content
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Remove comments
            if line.strip().startswith('*'):
                continue
            
            # Remove sequence numbers (columns 1-6)
            if len(line) > 6:
                line = line[6:]
            
            # Remove indicator area (column 7)
            if len(line) > 0:
                if line[0] in ['*', '/', '-', '+']:
                    continue
                line = line[1:]
            
            # Clean up whitespace
            line = line.rstrip()
            
            if line.strip():
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse preprocessed COBOL content and generate AST
        
        Args:
            content: Preprocessed COBOL source code
            
        Returns:
            Dictionary containing AST data
        """
        lines = content.split('\n')
        ast_data = {
            'programs': [],
            'divisions': {},
            'variables': [],
            'procedures': []
        }
        
        current_program = None
        current_division = None
        current_section = None
        current_paragraph = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check for divisions
            division_match = self._match_division(line)
            if division_match:
                current_division = division_match
                ast_data['divisions'][current_division] = {
                    'start_line': line_num,
                    'sections': {}
                }
                continue
            
            # Check for sections
            section_match = self._match_section(line)
            if section_match:
                current_section = section_match
                if current_division:
                    ast_data['divisions'][current_division]['sections'][current_section] = {
                        'start_line': line_num
                    }
                continue
            
            # Check for PROGRAM-ID
            program_match = re.search(self.statement_patterns['PROGRAM-ID'], line, re.IGNORECASE)
            if program_match:
                program_name = program_match.group(1)
                current_program = {
                    'name': program_name,
                    'type': 'PROGRAM',
                    'start_line': line_num,
                    'statements': [],
                    'variables': [],
                    'procedures': [],
                    'divisions': {}
                }
                ast_data['programs'].append(current_program)
                continue
            
            # Check for variables (PIC clauses)
            variable_match = re.search(self.statement_patterns['VARIABLE'], line, re.IGNORECASE)
            if variable_match:
                level = variable_match.group(1)
                name = variable_match.group(2)
                pic = variable_match.group(3)
                
                variable = {
                    'level': int(level),
                    'name': name,
                    'pic': pic,
                    'line': line_num
                }
                
                if current_program:
                    current_program['variables'].append(variable)
                ast_data['variables'].append(variable)
                continue
            
            # Check for paragraphs
            paragraph_match = re.search(self.statement_patterns['PARAGRAPH'], line, re.IGNORECASE)
            if paragraph_match:
                paragraph_name = paragraph_match.group(1)
                current_paragraph = {
                    'name': paragraph_name,
                    'start_line': line_num,
                    'statements': []
                }
                
                if current_program:
                    current_program['procedures'].append(current_paragraph)
                ast_data['procedures'].append(current_paragraph)
                continue
            
            # Parse statements
            statement = self._parse_statement(line, line_num)
            if statement:
                if current_program:
                    current_program['statements'].append(statement)
                if current_paragraph:
                    current_paragraph['statements'].append(statement)
        
        # Set end lines for programs and paragraphs
        self._set_end_lines(ast_data)
        
        return ast_data
    
    def _match_division(self, line: str) -> Optional[str]:
        """Match COBOL division"""
        for division in self.divisions:
            if re.search(rf'^{division}\s+DIVISION', line, re.IGNORECASE):
                return division
        return None
    
    def _match_section(self, line: str) -> Optional[str]:
        """Match COBOL section"""
        for section in self.sections:
            if re.search(rf'^{section}\s+SECTION', line, re.IGNORECASE):
                return section
        return None
    
    def _parse_statement(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single COBOL statement
        
        Args:
            line: Line of COBOL code
            line_num: Line number
            
        Returns:
            Statement dictionary or None
        """
        # Check for comments
        if re.match(self.statement_patterns['COMMENT'], line):
            return {
                'type': 'COMMENT',
                'line': line_num,
                'content': line
            }
        
        # Check for various statement types
        for stmt_type, pattern in self.statement_patterns.items():
            if stmt_type in ['PROGRAM-ID', 'VARIABLE', 'PARAGRAPH', 'COMMENT']:
                continue  # Already handled
            
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                statement = {
                    'type': stmt_type,
                    'line': line_num,
                    'content': line
                }
                
                # Add specific data based on statement type
                if stmt_type in ['CALL', 'PERFORM', 'GO TO']:
                    statement['target'] = match.group(1)
                elif stmt_type == 'IF':
                    statement['condition'] = match.group(1)
                elif stmt_type in ['MOVE', 'DISPLAY', 'ACCEPT']:
                    statement['operands'] = match.group(1)
                elif stmt_type in ['READ', 'WRITE', 'OPEN', 'CLOSE']:
                    statement['file'] = match.group(1)
                elif stmt_type == 'STOP':
                    statement['stop_type'] = match.group(1)
                
                return statement
        
        # If no specific pattern matches, treat as generic statement
        return {
            'type': 'STATEMENT',
            'line': line_num,
            'content': line
        }
    
    def _set_end_lines(self, ast_data: Dict[str, Any]):
        """Set end line numbers for programs and paragraphs"""
        # Set end lines for programs
        for i, program in enumerate(ast_data['programs']):
            if i < len(ast_data['programs']) - 1:
                program['end_line'] = ast_data['programs'][i + 1]['start_line'] - 1
            else:
                # Last program - estimate end line
                program['end_line'] = program['start_line'] + 100  # Default estimate
        
        # Set end lines for procedures
        for procedure in ast_data['procedures']:
            # Find next procedure or end of program
            start_line = procedure['start_line']
            end_line = start_line
            
            for other_proc in ast_data['procedures']:
                if other_proc['start_line'] > start_line:
                    end_line = other_proc['start_line'] - 1
                    break
            
            procedure['end_line'] = end_line
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported COBOL file extensions"""
        return ['.cbl', '.cob', '.cpy', '.cobol']
    
    def extract_program_structure(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract high-level program structure
        
        Args:
            ast_data: AST data
            
        Returns:
            Program structure summary
        """
        structure = {
            'total_programs': len(ast_data['programs']),
            'total_variables': len(ast_data['variables']),
            'total_procedures': len(ast_data['procedures']),
            'divisions_found': list(ast_data['divisions'].keys()),
            'programs': []
        }
        
        for program in ast_data['programs']:
            prog_info = {
                'name': program['name'],
                'type': program['type'],
                'variables': len(program['variables']),
                'procedures': len(program['procedures']),
                'statements': len(program['statements']),
                'start_line': program['start_line'],
                'end_line': program.get('end_line', 0)
            }
            structure['programs'].append(prog_info)
        
        return structure
    
    def find_dependencies(self, ast_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Find dependencies between programs and procedures
        
        Args:
            ast_data: AST data
            
        Returns:
            Dictionary mapping program names to their dependencies
        """
        dependencies = {}
        
        for program in ast_data['programs']:
            program_name = program['name']
            deps = []
            
            for statement in program['statements']:
                if statement['type'] in ['CALL', 'PERFORM']:
                    target = statement.get('target')
                    if target:
                        deps.append(target)
            
            dependencies[program_name] = list(set(deps))  # Remove duplicates
        
        return dependencies 