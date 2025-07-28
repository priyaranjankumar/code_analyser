"""
Configuration management for the legacy code analyzer
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration settings for the code analyzer"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.code_analyzer'
        self.config_file = self.config_dir / 'config.yaml'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def set_config(self, key: str, value: Any):
        """Set a configuration value"""
        config = self.get_config()
        config[key] = value
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with default"""
        config = self.get_config()
        return config.get(key, default)
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from config or environment"""
        # First try environment variable
        api_key = os.environ.get('LLM_API_KEY')
        if api_key:
            return api_key
        
        # Then try config file
        return self.get('api_key')
    
    def get_llm_provider(self) -> str:
        """Get LLM provider from config or environment"""
        # First try environment variable
        provider = os.environ.get('LLM_PROVIDER')
        if provider:
            return provider
        
        # Then try config file
        return self.get('llm_provider', 'openai')
    
    def get_default_language(self) -> str:
        """Get default language from config"""
        return self.get('language', 'cobol')
    
    def get_default_output_dir(self) -> str:
        """Get default output directory from config"""
        return self.get('output_dir', './analysis_results') 