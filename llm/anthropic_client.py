"""
Anthropic client for LLM integration
"""

import json
from typing import Dict, List, Any, Optional
from .base import BaseLLMClient, PromptBuilder


class AnthropicClient(BaseLLMClient):
    """Anthropic API client for code analysis"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic client
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet-20240229)
        """
        self.api_key = api_key
        self.model = model
        self._init_client()
    
    def _init_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    def analyze_code(self, ast_data: Dict[str, Any]) -> str:
        """
        Analyze code AST and generate summary
        
        Args:
            ast_data: AST data to analyze
            
        Returns:
            Code analysis summary
        """
        prompt = PromptBuilder.build_code_analysis_prompt(ast_data)
        return self._call_api(prompt)
    
    def analyze_program(self, program_data: Dict[str, Any]) -> str:
        """
        Analyze a single program and generate summary
        
        Args:
            program_data: Program AST data
            
        Returns:
            Program analysis summary
        """
        prompt = PromptBuilder.build_program_analysis_prompt(program_data)
        return self._call_api(prompt)
    
    def generate_flowchart_description(self, program_data: Dict[str, Any]) -> str:
        """
        Generate flowchart description from program data
        
        Args:
            program_data: Program AST data
            
        Returns:
            Flowchart description
        """
        prompt = PromptBuilder.build_flowchart_prompt(program_data)
        return self._call_api(prompt)
    
    def analyze_architecture(self, programs_data: List[Dict[str, Any]]) -> str:
        """
        Analyze architecture patterns across multiple programs
        
        Args:
            programs_data: List of program data
            
        Returns:
            Architecture analysis
        """
        prompt = PromptBuilder.build_architecture_prompt(programs_data)
        return self._call_api(prompt)
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to Anthropic
        
        Args:
            prompt: Prompt to send
            
        Returns:
            API response
        """
        try:
            system_prompt = """You are an expert code analyst specializing in legacy programming languages like COBOL. Provide clear, concise, and insightful analysis focusing on business logic and functionality. Your responses should be well-structured and easy to understand."""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            # Fallback to mock response if API call fails
            return f"Error calling Anthropic API: {str(e)}. Using fallback analysis."
    
    def _call_api_with_fallback(self, prompt: str, fallback_response: str) -> str:
        """
        Make API call with fallback response
        
        Args:
            prompt: Prompt to send
            fallback_response: Fallback response if API fails
            
        Returns:
            API response or fallback
        """
        try:
            return self._call_api(prompt)
        except Exception:
            return fallback_response 