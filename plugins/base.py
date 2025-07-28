"""
Base plugin interface and plugin manager for language-specific parsers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import importlib
import pkgutil


class BaseParser(ABC):
    """Base class for language-specific parsers"""
    
    @abstractmethod
    def preprocess(self, content: str) -> str:
        """
        Preprocess source code content
        
        Args:
            content: Raw source code content
            
        Returns:
            Preprocessed content
        """
        pass
    
    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse preprocessed content and generate AST
        
        Args:
            content: Preprocessed source code content
            
        Returns:
            Dictionary containing AST data
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions supported by this parser
        
        Returns:
            List of file extensions (e.g., ['.cbl', '.cob'])
        """
        pass


class PluginManager:
    """Manages language-specific parser plugins"""
    
    def __init__(self):
        self.parsers = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Load all available parser plugins"""
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins (if any)
        self._load_external_plugins()
    
    def _load_builtin_plugins(self):
        """Load built-in parser plugins"""
        try:
            # Load COBOL parser
            from .cobol.parser import COBOLParser
            self.parsers['cobol'] = COBOLParser()
        except ImportError as e:
            print(f"Warning: Could not load COBOL parser: {e}")
        
        # Add more built-in parsers here as they are implemented
        # try:
        #     from .fortran.parser import FortranParser
        #     self.parsers['fortran'] = FortranParser()
        # except ImportError:
        #     pass
    
    def _load_external_plugins(self):
        """Load external parser plugins from user-defined locations"""
        # This could be extended to load plugins from custom paths
        # or from installed packages
        pass
    
    def get_parser(self, language: str) -> BaseParser:
        """
        Get parser for a specific language
        
        Args:
            language: Programming language name
            
        Returns:
            Parser instance for the language
            
        Raises:
            ValueError: If no parser is available for the language
        """
        language = language.lower()
        
        if language not in self.parsers:
            available = ', '.join(self.parsers.keys())
            raise ValueError(f"No parser available for language '{language}'. Available: {available}")
        
        return self.parsers[language]
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages
        
        Returns:
            List of supported language names
        """
        return list(self.parsers.keys())
    
    def register_parser(self, language: str, parser: BaseParser):
        """
        Register a custom parser
        
        Args:
            language: Programming language name
            parser: Parser instance
        """
        if not isinstance(parser, BaseParser):
            raise ValueError("Parser must inherit from BaseParser")
        
        self.parsers[language.lower()] = parser
    
    def has_parser(self, language: str) -> bool:
        """
        Check if a parser is available for a language
        
        Args:
            language: Programming language name
            
        Returns:
            True if parser is available
        """
        return language.lower() in self.parsers


class MockParser(BaseParser):
    """Mock parser for testing purposes"""
    
    def preprocess(self, content: str) -> str:
        """Mock preprocessing - returns content as-is"""
        return content
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Mock parsing - returns basic AST structure"""
        return {
            'programs': [
                {
                    'name': 'MockProgram',
                    'type': 'PROGRAM',
                    'statements': [
                        {
                            'type': 'COMMENT',
                            'line': 1,
                            'content': 'Mock program for testing'
                        }
                    ],
                    'variables': [],
                    'procedures': []
                }
            ]
        }
    
    def get_supported_extensions(self) -> List[str]:
        """Return mock file extensions"""
        return ['.mock']


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance
    
    Returns:
        PluginManager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager 