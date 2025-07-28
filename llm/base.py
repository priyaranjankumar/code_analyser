"""
Base LLM interface and factory for code analysis
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import re


def estimate_tokens(text: str) -> int:
    """
    Conservative estimate of token count for GPT models
    Uses a more conservative ratio to account for tokenization overhead
    """
    # More conservative estimate: 1 token ≈ 3.5 characters for safety
    # This accounts for tokenization overhead and special characters
    return int(len(text) / 3.5)


def create_hierarchical_ast(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a hierarchical AST representation that preserves structure
    while reducing token count through intelligent summarization
    
    Args:
        data: Original AST data
        
    Returns:
        Hierarchical AST with preserved structure
    """
    if not isinstance(data, dict):
        return data
    
    hierarchical = {}
    
    # Keep essential metadata
    for key in ['name', 'type', 'language']:
        if key in data:
            hierarchical[key] = data[key]
    
    # Create hierarchical statement structure
    if 'statements' in data:
        statements = data['statements']
        
        # Group statements by type and create hierarchical structure
        statement_groups = {}
        for stmt in statements:
            stmt_type = stmt.get('type', 'Unknown')
            if stmt_type not in statement_groups:
                statement_groups[stmt_type] = []
            statement_groups[stmt_type].append(stmt)
        
        # Create hierarchical representation
        hierarchical['statement_hierarchy'] = {}
        for stmt_type, stmt_list in statement_groups.items():
            if len(stmt_list) <= 5:
                # Keep all statements if few
                hierarchical['statement_hierarchy'][stmt_type] = {
                    'count': len(stmt_list),
                    'statements': stmt_list
                }
            else:
                # For many statements, create summary with key examples
                key_examples = []
                for stmt in stmt_list[:3]:  # First 3 examples
                    key_examples.append({
                        'line': stmt.get('line', 0),
                        'content': stmt.get('content', '')[:80] + "..." if len(stmt.get('content', '')) > 80 else stmt.get('content', ''),
                        'condition': stmt.get('condition', '')[:50] if stmt.get('condition') else ''
                    })
                
                hierarchical['statement_hierarchy'][stmt_type] = {
                    'count': len(stmt_list),
                    'examples': key_examples,
                    'line_range': f"{stmt_list[0].get('line', 0)}-{stmt_list[-1].get('line', 0)}"
                }
        
        hierarchical['total_statements'] = len(statements)
    
    # Create hierarchical procedure structure
    if 'procedures' in data:
        procedures = data['procedures']
        
        if len(procedures) <= 10:
            hierarchical['procedures'] = procedures
        else:
            # Group procedures by naming pattern or functionality
            proc_groups = {}
            for proc in procedures:
                name = proc.get('name', '')
                # Extract prefix (e.g., "2000-SEND-MAP" -> "2000-SEND")
                prefix = name.split('-')[0] + '-' + name.split('-')[1] if '-' in name and len(name.split('-')) > 2 else name
                if prefix not in proc_groups:
                    proc_groups[prefix] = []
                proc_groups[prefix].append(proc)
            
            hierarchical['procedure_groups'] = {}
            for prefix, proc_list in proc_groups.items():
                hierarchical['procedure_groups'][prefix] = {
                    'count': len(proc_list),
                    'procedures': proc_list[:3],  # Show first 3
                    'line_range': f"{proc_list[0].get('line', 0)}-{proc_list[-1].get('line', 0)}"
                }
        
        hierarchical['total_procedures'] = len(procedures)
    
    # Create hierarchical variable structure
    if 'variables' in data:
        variables = data['variables']
        
        # Group variables by type and scope
        var_groups = {}
        for var in variables:
            var_type = var.get('type', 'Unknown')
            if var_type not in var_groups:
                var_groups[var_type] = []
            var_groups[var_type].append(var)
        
        hierarchical['variable_hierarchy'] = {}
        for var_type, var_list in var_groups.items():
            hierarchical['variable_hierarchy'][var_type] = {
                'count': len(var_list),
                'examples': [var.get('name', '') for var in var_list[:5]],  # First 5 names
                'total_size': sum(len(var.get('name', '')) for var in var_list)
            }
        
        hierarchical['total_variables'] = len(variables)
    
    # Create hierarchical AST structure
    if 'ast' in data:
        ast = data['ast']
        hierarchical['ast_hierarchy'] = create_ast_hierarchy(ast)
    
    return hierarchical


def create_ast_hierarchy(ast_node: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
    """
    Recursively create hierarchical AST representation
    
    Args:
        ast_node: AST node to process
        max_depth: Maximum depth to process
        
    Returns:
        Hierarchical AST node
    """
    if not isinstance(ast_node, dict) or max_depth <= 0:
        return {'type': 'leaf', 'content': str(ast_node)[:50] + "..." if len(str(ast_node)) > 50 else str(ast_node)}
    
    hierarchy = {
        'type': ast_node.get('type', 'Unknown'),
        'line': ast_node.get('line', 0)
    }
    
    # Process children if they exist
    children = ast_node.get('children', [])
    if children:
        if len(children) <= 5:
            # Keep all children if few
            hierarchy['children'] = [create_ast_hierarchy(child, max_depth - 1) for child in children]
        else:
            # Summarize children if many
            hierarchy['children_summary'] = {
                'count': len(children),
                'types': list(set(child.get('type', 'Unknown') for child in children)),
                'examples': [create_ast_hierarchy(child, max_depth - 1) for child in children[:3]]
            }
    
    # Add content if it exists and is not too long
    content = ast_node.get('content', '')
    if content and len(content) <= 100:
        hierarchy['content'] = content
    elif content:
        hierarchy['content_preview'] = content[:100] + "..."
    
    return hierarchy


def chunk_data_for_llm(data: Dict[str, Any], max_tokens: int = 4000) -> List[Dict[str, Any]]:
    """
    Split large data into manageable chunks while preserving context
    
    Args:
        data: Data to chunk
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of data chunks
    """
    if not isinstance(data, dict):
        return [data]
    
    # First, create hierarchical representation
    hierarchical = create_hierarchical_ast(data)
    
    # Estimate tokens for hierarchical version
    hierarchical_str = json.dumps(hierarchical, indent=2)
    hierarchical_tokens = estimate_tokens(hierarchical_str)
    
    if hierarchical_tokens <= max_tokens:
        return [hierarchical]
    
    # If still too large, create chunks
    chunks = []
    
    # Chunk 1: Program overview and metadata
    overview_chunk = {
        'name': hierarchical.get('name', 'Unknown'),
        'type': hierarchical.get('type', 'Unknown'),
        'language': hierarchical.get('language', 'Unknown'),
        'total_statements': hierarchical.get('total_statements', 0),
        'total_procedures': hierarchical.get('total_procedures', 0),
        'total_variables': hierarchical.get('total_variables', 0),
        'chunk_type': 'overview'
    }
    chunks.append(overview_chunk)
    
    # Chunk 2: Key flow control statements
    if 'statement_hierarchy' in hierarchical:
        flow_statements = {}
        key_types = ['IF', 'ELSE', 'END-IF', 'PERFORM', 'CALL', 'OPEN', 'CLOSE', 'READ', 'WRITE', 'DISPLAY', 'ACCEPT', 'STOP']
        
        for stmt_type in key_types:
            if stmt_type in hierarchical['statement_hierarchy']:
                flow_statements[stmt_type] = hierarchical['statement_hierarchy'][stmt_type]
        
        if flow_statements:
            flow_chunk = {
                'name': hierarchical.get('name', 'Unknown'),
                'chunk_type': 'flow_control',
                'flow_statements': flow_statements
            }
            chunks.append(flow_chunk)
    
    # Chunk 3: Procedures
    if 'procedures' in hierarchical or 'procedure_groups' in hierarchical:
        proc_chunk = {
            'name': hierarchical.get('name', 'Unknown'),
            'chunk_type': 'procedures',
            'procedures': hierarchical.get('procedures', {}),
            'procedure_groups': hierarchical.get('procedure_groups', {})
        }
        chunks.append(proc_chunk)
    
    # Chunk 4: Variables and data structures
    if 'variable_hierarchy' in hierarchical:
        var_chunk = {
            'name': hierarchical.get('name', 'Unknown'),
            'chunk_type': 'variables',
            'variable_hierarchy': hierarchical['variable_hierarchy']
        }
        chunks.append(var_chunk)
    
    return chunks


def truncate_for_llm(data: Dict[str, Any], max_tokens: int = 4000) -> Dict[str, Any]:
    """
    Intelligently process data using hierarchical AST and chunking
    
    Args:
        data: Data to process
        max_tokens: Maximum tokens to allow
        
    Returns:
        Processed data
    """
    if not isinstance(data, dict):
        return data
    
    # Estimate original token count
    original_str = json.dumps(data, indent=2)
    original_tokens = estimate_tokens(original_str)
    
    # Try hierarchical approach first
    hierarchical = create_hierarchical_ast(data)
    hierarchical_str = json.dumps(hierarchical, indent=2)
    hierarchical_tokens = estimate_tokens(hierarchical_str)
    
    if hierarchical_tokens <= max_tokens:
        # Log improvement
        if original_tokens > hierarchical_tokens:
            reduction = ((original_tokens - hierarchical_tokens) / original_tokens) * 100
            print(f"📊 Hierarchical AST: {original_tokens:,} → {hierarchical_tokens:,} ({reduction:.1f}% reduction)")
        return hierarchical
    
    # If still too large, use chunking
    chunks = chunk_data_for_llm(data, max_tokens)
    
    # For now, return the first chunk (overview) as the main representation
    # In a full implementation, you'd process all chunks and combine results
    main_chunk = chunks[0] if chunks else hierarchical
    
    # Log chunking approach
    total_chunk_tokens = sum(estimate_tokens(json.dumps(chunk, indent=2)) for chunk in chunks)
    if original_tokens > total_chunk_tokens:
        reduction = ((original_tokens - total_chunk_tokens) / original_tokens) * 100
        print(f"📊 Chunked approach: {original_tokens:,} → {total_chunk_tokens:,} ({reduction:.1f}% reduction, {len(chunks)} chunks)")
    
    return main_chunk


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def analyze_code(self, ast_data: Dict[str, Any]) -> str:
        """
        Analyze code AST and generate summary
        
        Args:
            ast_data: AST data to analyze
            
        Returns:
            Code analysis summary
        """
        pass
    
    @abstractmethod
    def analyze_program(self, program_data: Dict[str, Any]) -> str:
        """
        Analyze a single program and generate summary
        
        Args:
            program_data: Program AST data
            
        Returns:
            Program analysis summary
        """
        pass
    
    @abstractmethod
    def generate_flowchart_description(self, program_data: Dict[str, Any]) -> str:
        """
        Generate flowchart description from program data
        
        Args:
            program_data: Program AST data
            
        Returns:
            Flowchart description
        """
        pass
    
    @abstractmethod
    def analyze_architecture(self, programs_data: List[Dict[str, Any]]) -> str:
        """
        Analyze architecture patterns across multiple programs
        
        Args:
            programs_data: List of program data
            
        Returns:
            Architecture analysis
        """
        pass


class LLMFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create_client(provider: str, api_key: str) -> BaseLLMClient:
        """
        Create LLM client for the specified provider
        
        Args:
            provider: LLM provider name ('openai', 'anthropic', 'mock', etc.)
            api_key: API key for the provider
            
        Returns:
            LLM client instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        
        if provider == 'openai':
            from .openai_client import OpenAIClient
            return OpenAIClient(api_key)
        elif provider == 'anthropic':
            from .anthropic_client import AnthropicClient
            return AnthropicClient(api_key)
        elif provider == 'mock':
            return MockLLMClient()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing purposes"""
    
    def analyze_code(self, ast_data: Dict[str, Any]) -> str:
        """Mock code analysis"""
        programs = ast_data.get('programs', [])
        return f"This code contains {len(programs)} program(s). Mock analysis generated for testing purposes."
    
    def analyze_program(self, program_data: Dict[str, Any]) -> str:
        """Mock program analysis"""
        name = program_data.get('name', 'Unknown')
        statements = program_data.get('statements', [])
        return f"Program '{name}' contains {len(statements)} statements. Mock program analysis."
    
    def generate_flowchart_description(self, program_data: Dict[str, Any]) -> str:
        """Generate mock flowchart description"""
        name = program_data.get('name', 'Unknown')
        statements = program_data.get('statements', [])
        
        # Generate a structured mock response
        mock_response = f"""
{{
    "flow_description": "Mock flowchart analysis for {name}",
    "main_flow": "Program {name} processes data through {len(statements)} statements with business logic validation",
    "decision_points": "IF statements for data validation and business rule enforcement",
    "loops": "PERFORM statements for iterative data processing",
    "error_handling": "Basic error handling through conditional statements",
    "nodes": [
        {{
            "id": "start",
            "type": "START",
            "label": "START",
            "description": "Program initialization",
            "business_logic": "Program entry point",
            "line_number": 1
        }},
        {{
            "id": "process",
            "type": "PROCESS", 
            "label": "Data Processing",
            "description": "Main business logic processing",
            "business_logic": "Core data transformation and validation",
            "line_number": 10
        }},
        {{
            "id": "decision",
            "type": "DECISION",
            "label": "Validation",
            "description": "Data validation check",
            "business_logic": "Business rule validation",
            "line_number": 20
        }},
        {{
            "id": "output",
            "type": "IO",
            "label": "Output Results",
            "description": "Display or write results",
            "business_logic": "Output processed data",
            "line_number": 30
        }},
        {{
            "id": "end",
            "type": "END",
            "label": "END",
            "description": "Program completion",
            "business_logic": "Program termination",
            "line_number": {len(statements) + 1}
        }}
    ],
    "connections": [
        {{
            "from": "start",
            "to": "process",
            "label": "Initialize",
            "type": "NORMAL"
        }},
        {{
            "from": "process", 
            "to": "decision",
            "label": "Validate",
            "type": "NORMAL"
        }},
        {{
            "from": "decision",
            "to": "output",
            "label": "Valid",
            "type": "CONDITION_TRUE"
        }},
        {{
            "from": "output",
            "to": "end",
            "label": "Complete",
            "type": "NORMAL"
        }}
    ]
}}
"""
        return mock_response
    
    def analyze_architecture(self, programs_data: List[Dict[str, Any]]) -> str:
        """Mock architecture analysis"""
        return f"Architecture analysis for {len(programs_data)} programs. Mock architecture insights generated."


class PromptBuilder:
    """Helper class for building LLM prompts"""
    
    @staticmethod
    def build_code_analysis_prompt(ast_data: Dict[str, Any]) -> str:
        """
        Build prompt for code analysis
        
        Args:
            ast_data: AST data
            
        Returns:
            Formatted prompt
        """
        # Truncate the entire AST data
        truncated_ast = truncate_for_llm(ast_data, max_tokens=3000)
        
        programs = truncated_ast.get('programs', [])
        total_variables = truncated_ast.get('total_variables', 0)
        
        prompt = f"""
You are an expert code analyst specializing in legacy programming languages. 
Provide a concise, high-level summary of this codebase in 2-3 paragraphs.

Code Structure:
- Programs: {len(programs)}
- Total Variables: {total_variables}

Program Overview:
"""
        
        for i, program in enumerate(programs, 1):
            name = program.get('name', 'Unknown')
            total_statements = program.get('total_statements', 0)
            total_procedures = program.get('total_procedures', 0)
            prompt += f"- {name}: {total_statements} statements, {total_procedures} procedures\n"
        
        prompt += """
Provide a concise summary in 2-3 paragraphs covering:
1. **Overall Purpose**: What does this codebase accomplish? (1 paragraph)
2. **Key Components**: Main programs and their roles (1 paragraph)
3. **Architecture**: High-level structure and organization (1 paragraph)

Keep it business-focused and avoid technical jargon. Use clear, simple language.
"""
        
        return prompt
    
    @staticmethod
    def build_program_analysis_prompt(program_data: Dict[str, Any]) -> str:
        """
        Build prompt for program analysis
        
        Args:
            program_data: Program AST data
            
        Returns:
            Formatted prompt
        """
        # Process data using hierarchical AST approach
        processed_data = truncate_for_llm(program_data, max_tokens=3000)
        
        name = processed_data.get('name', 'Unknown')
        total_statements = processed_data.get('total_statements', 0)
        total_procedures = processed_data.get('total_procedures', 0)
        total_variables = processed_data.get('total_variables', 0)
        
        # Handle hierarchical statement structure
        statement_hierarchy = processed_data.get('statement_hierarchy', {})
        statement_summary = []
        for stmt_type, stmt_info in statement_hierarchy.items():
            count = stmt_info.get('count', 0)
            if 'statements' in stmt_info:
                # Show examples for key flow control statements
                if stmt_type in ['IF', 'PERFORM', 'CALL', 'READ', 'WRITE']:
                    examples = stmt_info['statements'][:2]  # First 2 examples
                    for stmt in examples:
                        statement_summary.append(f"- {stmt_type}: {stmt.get('content', '')[:60]}...")
            else:
                statement_summary.append(f"- {stmt_type}: {count} statements")
        
        # Handle hierarchical variable structure
        variable_hierarchy = processed_data.get('variable_hierarchy', {})
        variable_summary = []
        for var_type, var_info in variable_hierarchy.items():
            count = var_info.get('count', 0)
            examples = var_info.get('examples', [])
            variable_summary.append(f"- {var_type}: {count} variables")
            if examples:
                variable_summary.append(f"  Examples: {', '.join(examples[:3])}")
        
        # Handle procedures
        procedures = processed_data.get('procedures', [])
        procedure_groups = processed_data.get('procedure_groups', {})
        
        procedure_summary = []
        if procedures:
            for proc in procedures[:5]:
                procedure_summary.append(f"- {proc.get('name', '')}")
        elif procedure_groups:
            for prefix, group_info in procedure_groups.items():
                count = group_info.get('count', 0)
                procedure_summary.append(f"- {prefix}*: {count} procedures")
        
        prompt = f"""
Analyze this COBOL program and provide a concise, high-level summary in 2-3 paragraphs.

Program: {name}
- Total Statements: {total_statements}
- Total Procedures: {total_procedures}
- Total Variables: {total_variables}

Statement Structure:
"""
        
        for summary in statement_summary:
            prompt += f"{summary}\n"
        
        prompt += f"""

Variable Structure:
"""
        
        for summary in variable_summary:
            prompt += f"{summary}\n"
        
        prompt += f"""

Procedures:
"""
        
        for summary in procedure_summary:
            prompt += f"{summary}\n"
        
        prompt += f"""

Provide a concise summary in 2-3 paragraphs covering:
1. **Purpose**: What does this program do? (1 paragraph)
2. **Key Operations**: Main business logic and data processing (1 paragraph)  
3. **Structure**: Brief overview of program organization and flow (1 paragraph)

Keep it high-level and business-focused. Avoid technical jargon. Use clear, simple language.
"""
        
        return prompt
    
    @staticmethod
    def build_flowchart_prompt(program_data: Dict[str, Any]) -> str:
        """
        Build prompt for flowchart generation
        
        Args:
            program_data: Program AST data
            
        Returns:
            Formatted prompt
        """
        # Process data using hierarchical AST approach
        processed_data = truncate_for_llm(program_data, max_tokens=3500)
        
        name = processed_data.get('name', 'Unknown')
        total_statements = processed_data.get('total_statements', 0)
        total_procedures = processed_data.get('total_procedures', 0)
        
        # Extract flow control statements from hierarchy
        statement_hierarchy = processed_data.get('statement_hierarchy', {})
        flow_statements = []
        
        # Focus on key flow control types
        key_types = ['IF', 'ELSE', 'END-IF', 'PERFORM', 'CALL', 'OPEN', 'CLOSE', 'READ', 'WRITE', 'DISPLAY', 'ACCEPT', 'STOP', 'EVALUATE', 'WHEN']
        
        for stmt_type in key_types:
            if stmt_type in statement_hierarchy:
                stmt_info = statement_hierarchy[stmt_type]
                if 'statements' in stmt_info:
                    # Include all statements for flow control
                    for stmt in stmt_info['statements']:
                        flow_statements.append({
                            'line': stmt.get('line', 0),
                            'type': stmt_type,
                            'content': stmt.get('content', ''),
                            'condition': stmt.get('condition', '')
                        })
                else:
                    # For summarized statements, include examples
                    examples = stmt_info.get('examples', [])
                    for example in examples:
                        flow_statements.append({
                            'line': example.get('line', 0),
                            'type': stmt_type,
                            'content': example.get('content', ''),
                            'condition': example.get('condition', '')
                        })
        
        # Sort by line number
        flow_statements.sort(key=lambda x: x['line'])
        
        prompt = f"""
Analyze the program '{name}' and generate a detailed flowchart description.

Program Structure:
- Total statements: {total_statements}
- Total procedures: {total_procedures}
- Flow control statements analyzed: {len(flow_statements)}

Key Flow Control Statements:
"""
        
        for stmt in flow_statements:
            prompt += f"- Line {stmt['line']}: {stmt['type']} - {stmt['content']}\n"
            if stmt.get('condition'):
                prompt += f"  Condition: {stmt['condition']}\n"
        
        prompt += f"""

Please provide a JSON-formatted flowchart description with the following structure:

{{
    "flow_description": "High-level description of the program flow",
    "nodes": [
        {{
            "id": "unique_id",
            "type": "START|PROCESS|DECISION|LOOP|CALL|IO|END",
            "label": "Human readable label",
            "description": "Detailed description of what this node does",
            "line_number": line_number,
            "business_logic": "What business operation this represents"
        }}
    ],
    "connections": [
        {{
            "from": "source_node_id",
            "to": "target_node_id", 
            "label": "Condition or flow description",
            "type": "NORMAL|CONDITION_TRUE|CONDITION_FALSE|LOOP"
        }}
    ],
    "main_flow": "Description of the main program flow path",
    "decision_points": "List of key decision points and their business logic",
    "loops": "Description of any loops or iterations",
    "error_handling": "Description of error handling or validation logic"
}}

Focus on:
1. Business logic and data flow, not technical implementation
2. Clear decision points and their conditions
3. Main program flow and alternative paths
4. Data input/output operations
5. Procedure calls and their purpose
6. Error handling and validation

Make the flowchart meaningful for business users to understand the program's purpose and flow.
"""
        
        return prompt
    
    @staticmethod
    def build_architecture_prompt(programs_data: List[Dict[str, Any]]) -> str:
        """
        Build prompt for architecture analysis
        
        Args:
            programs_data: List of program data
            
        Returns:
            Formatted prompt
        """
        # Truncate each program's data to fit within token limits
        truncated_programs = []
        for program in programs_data:
            truncated_program = truncate_for_llm(program, max_tokens=1500)
            truncated_programs.append(truncated_program)
        
        prompt = f"""
Analyze the architecture and design patterns across {len(truncated_programs)} programs.

Program Overview:
"""
        
        for i, program in enumerate(truncated_programs, 1):
            name = program.get('name', 'Unknown')
            total_statements = program.get('total_statements', 0)
            total_procedures = program.get('total_procedures', 0)
            total_variables = program.get('total_variables', 0)
            
            prompt += f"""
Program {i}: {name}
- Total Statements: {total_statements}
- Total Procedures: {total_procedures}
- Total Variables: {total_variables}
"""
        
        prompt += """
Please provide:
1. Overall system architecture and design patterns
2. Program relationships and dependencies
3. Data flow between programs
4. Common patterns and conventions used
5. System integration points
6. Potential architectural improvements
7. Modernization recommendations

Focus on system-level understanding and architectural insights.
"""
        
        return prompt 