#!/usr/bin/env python3
"""
Legacy Code Analyzer CLI Tool
Main entry point for the code analysis tool
"""

import click
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import CodeAnalyzer
from utils.config import ConfigManager
from utils.file_utils import validate_codebase_path


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Legacy Code Analyzer - Analyze legacy codebases using AST, LLM, and D3.js visualizations.
    
    This tool helps you understand legacy code by:
    - Generating AST representations
    - Using LLM for code analysis and summarization
    - Creating interactive flowcharts
    - Analyzing architecture patterns
    """
    pass


@cli.command()
@click.argument('codebase_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--llm', '-l', 
              type=click.Choice(['openai', 'anthropic', 'mock', 'custom']), 
              default='openai',
              help='LLM provider to use for analysis')
@click.option('--api-key', '-k', 
              envvar='LLM_API_KEY',
              help='API key for the LLM provider')
@click.option('--output-dir', '-o', 
              type=click.Path(file_okay=False, dir_okay=True),
              default='./analysis_results',
              help='Output directory for analysis results')
@click.option('--language', '-lang',
              type=click.Choice(['cobol']),
              default='cobol',
              help='Programming language of the codebase')
@click.option('--generate-flowcharts', '-f',
              is_flag=True,
              default=False,
              help='Generate interactive flowcharts for programs')
@click.option('--generate-architecture', '-a',
              is_flag=True,
              default=False,
              help='Generate architecture analysis and patterns')
@click.option('--max-files', '-m',
              type=int,
              default=None,
              help='Maximum number of files to analyze (for testing)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output')
def analyze(codebase_path, llm, api_key, output_dir, language, 
           generate_flowcharts, generate_architecture, max_files, verbose):
    """
    Analyze a legacy codebase and generate comprehensive reports.
    
    CODEBASE_PATH: Path to the directory containing the source code
    """
    try:
        # Get configuration manager
        config_manager = ConfigManager()
        
        # Use default values from config if not provided
        if not llm:
            llm = config_manager.get_llm_provider() or 'openai'
        if not api_key and llm != 'mock':
            api_key = config_manager.get_api_key()
        
        # Validate inputs
        if not api_key and llm != 'mock':
            click.echo("❌ Error: API key is required. Use --api-key or set LLM_API_KEY environment variable.", err=True)
            sys.exit(1)
        
        codebase_path = Path(codebase_path).resolve()
        output_dir = Path(output_dir).resolve()
        
        # Validate codebase path
        if not validate_codebase_path(codebase_path, language):
            click.echo(f"❌ Error: Invalid codebase path or no {language.upper()} files found.", err=True)
            sys.exit(1)
        
        click.echo(f"🚀 Starting analysis of {codebase_path}")
        click.echo(f"📊 Output directory: {output_dir}")
        click.echo(f"🤖 LLM Provider: {llm}")
        click.echo(f"🔤 Language: {language.upper()}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(
            llm_provider=llm,
            api_key=api_key,
            output_dir=output_dir,
            language=language,
            verbose=verbose
        )
        
        # Run analysis
        results = analyzer.analyze_codebase(
            codebase_path=codebase_path,
            generate_flowcharts=generate_flowcharts,
            generate_architecture=generate_architecture,
            max_files=max_files
        )
        
        # Display results
        click.echo("\n✅ Analysis completed successfully!")
        click.echo(f"📁 Results saved to: {output_dir}")
        click.echo(f"📄 Files analyzed: {results['files_analyzed']}")
        click.echo(f"🔍 Programs found: {results['programs_found']}")
        click.echo(f"📊 Flowcharts generated: {results['flowcharts_generated']}")
        click.echo(f"🏗️  Architecture report: {results['architecture_report']}")
        
        # Open results in browser if available
        if results.get('html_report'):
            click.echo(f"🌐 Opening report in browser: {results['html_report']}")
            try:
                import webbrowser
                webbrowser.open(f"file://{results['html_report']}")
            except:
                pass
                
    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--set-llm', 
              type=click.Choice(['openai', 'anthropic', 'mock', 'custom']),
              help='Set default LLM provider')
@click.option('--set-api-key',
              help='Set default API key')
@click.option('--show', '-s',
              is_flag=True,
              help='Show current configuration')
def config(set_llm, set_api_key, show):
    """
    Manage configuration settings.
    """
    config_manager = ConfigManager()
    
    if show:
        config = config_manager.get_config()
        click.echo("Current Configuration:")
        click.echo(f"  LLM Provider: {config.get('llm_provider', 'Not set')}")
        click.echo(f"  API Key: {'*' * 10 if config.get('api_key') else 'Not set'}")
        click.echo(f"  Default Language: {config.get('language', 'cobol')}")
        click.echo(f"  Default Output Dir: {config.get('output_dir', './analysis_results')}")
    
    if set_llm:
        config_manager.set_config('llm_provider', set_llm)
        click.echo(f"✅ Default LLM provider set to: {set_llm}")
    
    if set_api_key:
        config_manager.set_config('api_key', set_api_key)
        click.echo("✅ API key saved to configuration")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--language', '-lang',
              type=click.Choice(['cobol']),
              default='cobol',
              help='Programming language of the file')
@click.option('--output', '-o',
              type=click.Path(file_okay=True, dir_okay=False),
              help='Output file for AST (default: stdout)')
def parse(file_path, language, output):
    """
    Parse a single file and generate its AST.
    
    FILE_PATH: Path to the source code file to parse
    """
    try:
        from core.ast_generator import ASTGenerator
        
        file_path = Path(file_path)
        ast_generator = ASTGenerator(language)
        
        click.echo(f"🔍 Parsing {file_path}...")
        ast_data = ast_generator.parse_file(file_path)
        
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(ast_data, f, indent=2)
            click.echo(f"✅ AST saved to: {output}")
        else:
            import json
            click.echo(json.dumps(ast_data, indent=2))
            
    except Exception as e:
        click.echo(f"❌ Error parsing file: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('ast_file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--llm', '-l',
              type=click.Choice(['openai', 'anthropic', 'mock']),
              default='openai',
              help='LLM provider to use')
@click.option('--api-key', '-k',
              envvar='LLM_API_KEY',
              help='API key for the LLM provider')
def summarize(ast_file, llm, api_key):
    """
    Generate a summary of code from its AST.
    
    AST_FILE: Path to the JSON file containing AST data
    """
    try:
        if not api_key and llm != 'mock':
            click.echo("❌ Error: API key is required.", err=True)
            sys.exit(1)
        
        from llm.base import LLMFactory
        
        llm_client = LLMFactory.create_client(llm, api_key)
        
        import json
        with open(ast_file, 'r') as f:
            ast_data = json.load(f)
        
        click.echo("🤖 Generating summary...")
        summary = llm_client.analyze_code(ast_data)
        
        click.echo("\n📝 Code Summary:")
        click.echo("=" * 50)
        click.echo(summary)
        
    except Exception as e:
        click.echo(f"❌ Error generating summary: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 