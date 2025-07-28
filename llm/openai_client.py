"""
OpenAI client for LLM integration
"""

import json
from typing import Dict, List, Any, Optional
from .base import BaseLLMClient, PromptBuilder


class OpenAIClient(BaseLLMClient):
    """OpenAI API client for code analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
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
        Make API call to OpenAI
        
        Args:
            prompt: Prompt to send
            
        Returns:
            API response
        """
        try:
            # Estimate tokens in the prompt
            from .base import estimate_tokens
            prompt_tokens = estimate_tokens(prompt)
            
            # Calculate safe max_tokens (leave room for system message and response)
            # GPT-4 has 8192 context limit, so we need to be conservative
            system_message = "You are an expert code analyst specializing in legacy programming languages like COBOL. Provide clear, concise, and insightful analysis focusing on business logic and functionality."
            system_tokens = estimate_tokens(system_message)
            total_input_tokens = system_tokens + prompt_tokens
            
            # Leave at least 1000 tokens for response and safety margin
            max_response_tokens = min(8192 - total_input_tokens - 1000, 4000)
            
            # Ensure we have reasonable tokens for response
            if max_response_tokens < 500:
                # If too little space, truncate the prompt
                print(f"⚠️  Prompt too large ({prompt_tokens} tokens), truncating...")
                # Truncate prompt to fit within limits
                max_prompt_tokens = 8192 - system_tokens - 1500  # Leave 1500 for response
                if len(prompt) > max_prompt_tokens * 4:  # Rough conversion back to characters
                    prompt = prompt[:max_prompt_tokens * 4] + "\n\n[Content truncated due to length]"
                    prompt_tokens = estimate_tokens(prompt)
                    max_response_tokens = 8192 - system_tokens - prompt_tokens - 500
            
            print(f"📊 Tokens: Input={prompt_tokens}, System={system_tokens}, Max Response={max_response_tokens}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_response_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to mock response if API call fails
            return f"Error calling OpenAI API: {str(e)}. Using fallback analysis."
    
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