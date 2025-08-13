#!/usr/bin/env python3
"""
Legacy Code Analyzer CLI Tool
Main entry point for the code analysis tool
"""

import click
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import CodeAnalyzer
from utils.config import ConfigManager
from utils.file_utils import validate_codebase_path


def get_timestamp():
    """Get current timestamp in a readable format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
              default='./output',
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
        
        timestamp = get_timestamp()
        click.echo(f"🚀 Starting analysis of {codebase_path}")
        click.echo(f"📊 Output directory: {output_dir}")
        click.echo(f"🤖 LLM Provider: {llm}")
        click.echo(f"🔤 Language: {language.upper()}")
        click.echo(f"⏰ Analysis started at: {timestamp}")
        
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
        end_timestamp = get_timestamp()
        click.echo("\n" + "="*60)
        click.echo("🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
        click.echo("="*60)
        click.echo(f"📁 Results saved to: {results.get('output_directory', output_dir)}")
        click.echo(f"📄 Files analyzed: {results['files_analyzed']}")
        click.echo(f"🔍 Programs found: {results['programs_found']}")
        click.echo(f"📊 Flowcharts generated: {results['flowcharts_generated']}")
        click.echo(f"🏗️  Architecture report: {results['architecture_report']}")
        click.echo(f"⏰ Analysis completed at: {end_timestamp}")
        click.echo(f"⏱️  Total analysis time: {results.get('analysis_time', 'N/A')} seconds")
        click.echo(f"🆔 Analysis ID: {results.get('analysis_timestamp', 'N/A')}")
        
        # Show what was generated
        click.echo("\n📋 Generated Files:")
        if results.get('html_report'):
            click.echo(f"  🌐 Main Report: {results['html_report']}")
        if results['flowcharts_generated'] > 0:
            click.echo(f"  📊 Interactive Flowcharts: {results['flowcharts_generated']} files")
        if results.get('architecture_report'):
            click.echo(f"  🏗️  Architecture Analysis: {results['architecture_report']}")
        
        # Open results in browser if available
        if results.get('html_report'):
            click.echo(f"\n🌐 Opening report in browser...")
            try:
                import webbrowser
                webbrowser.open(f"file://{results['html_report']}")
                click.echo("✅ Report opened in your default browser!")
            except Exception as e:
                click.echo(f"⚠️  Could not open browser automatically. Please open: {results['html_report']}")
        
        click.echo("\n" + "="*60)
                
    except Exception as e:
        error_timestamp = get_timestamp()
        click.echo(f"❌ Error during analysis at {error_timestamp}: {str(e)}", err=True)
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
@click.option('--help-examples', '-h',
              is_flag=True,
              help='Show usage examples')
def config(set_llm, set_api_key, show, help_examples):
    """
    Manage configuration settings.
    """
    config_manager = ConfigManager()
    
    if show:
        config = config_manager.get_config()
        timestamp = get_timestamp()
        click.echo(f"Current Configuration (as of {timestamp}):")
        click.echo(f"  LLM Provider: {config.get('llm_provider', 'Not set')}")
        click.echo(f"  API Key: {'*' * 10 if config.get('api_key') else 'Not set'}")
        click.echo(f"  Default Language: {config.get('language', 'cobol')}")
        click.echo(f"  Default Output Dir: {config.get('output_dir', './output')}")
    
    if set_llm:
        config_manager.set_config('llm_provider', set_llm)
        timestamp = get_timestamp()
        click.echo(f"✅ Default LLM provider set to: {set_llm} at {timestamp}")
    
    if set_api_key:
        config_manager.set_config('api_key', set_api_key)
        timestamp = get_timestamp()
        click.echo(f"✅ API key saved to configuration at {timestamp}")
    
    if help_examples:
        click.echo("\n📚 USAGE EXAMPLES:")
        click.echo("="*50)
        click.echo("1. Basic analysis:")
        click.echo("   python main.py analyze sample_cobol")
        click.echo()
        click.echo("2. Full analysis with visualizations:")
        click.echo("   python main.py analyze sample_cobol --generate-flowcharts --generate-architecture")
        click.echo()
        click.echo("3. Parse single file:")
        click.echo("   python main.py parse sample_cobol/B18PGM1.cbl --output ast.json")
        click.echo()
        click.echo("4. Generate summary from AST:")
        click.echo("   python main.py summarize ast.json")
        click.echo()
        click.echo("5. Set up configuration:")
        click.echo("   python main.py config --set-llm openai --set-api-key YOUR_API_KEY")
        click.echo()
        click.echo("6. View current config:")
        click.echo("   python main.py config --show")
        click.echo()
        click.echo("7. List previous analyses:")
        click.echo("   python main.py history --list-analyses")
        click.echo("="*50)


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
        
        timestamp = get_timestamp()
        click.echo(f"🔍 Parsing {file_path} at {timestamp}...")
        ast_data = ast_generator.parse_file(file_path)
        
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(ast_data, f, indent=2)
            end_timestamp = get_timestamp()
            click.echo(f"✅ AST saved to: {output} at {end_timestamp}")
        else:
            import json
            click.echo(json.dumps(ast_data, indent=2))
            
    except Exception as e:
        error_timestamp = get_timestamp()
        click.echo(f"❌ Error parsing file at {error_timestamp}: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--list-analyses', '-l',
              is_flag=True,
              help='List previous analysis runs')
def history(list_analyses):
    """
    Manage analysis history and previous runs.
    """
    if list_analyses:
        base_output_dir = Path('./output')
        if not base_output_dir.exists():
            click.echo("No previous analyses found.")
            return
        
        # Find all analysis directories
        analysis_dirs = []
        for item in base_output_dir.iterdir():
            if item.is_dir() and item.name.startswith('analysis_'):
                analysis_dirs.append(item)
        
        if not analysis_dirs:
            click.echo("No previous analyses found.")
            return
        
        # Sort by creation time (newest first)
        analysis_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
        
        click.echo(f"\n📋 Previous Analysis Runs (found {len(analysis_dirs)}):")
        click.echo("="*60)
        
        for i, analysis_dir in enumerate(analysis_dirs[:10], 1):  # Show last 10
            timestamp = analysis_dir.name.replace('analysis_', '')
            # Convert timestamp to readable format
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                readable_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                readable_time = timestamp
            
            # Check if report exists
            report_file = analysis_dir / 'html' / 'comprehensive_report.html'
            has_report = "✅" if report_file.exists() else "❌"
            
            click.echo(f"{i:2d}. {has_report} {readable_time}")
            click.echo(f"    📁 {analysis_dir}")
        
        if len(analysis_dirs) > 10:
            click.echo(f"\n... and {len(analysis_dirs) - 10} more analyses")
        
        click.echo("\n💡 Tip: Use 'python main.py history --list-analyses' to see this list again")


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
        
        timestamp = get_timestamp()
        click.echo(f"🤖 Generating summary at {timestamp}...")
        summary = llm_client.analyze_code(ast_data)
        
        click.echo("\n📝 Code Summary:")
        click.echo("=" * 50)
        click.echo(summary)
        
    except Exception as e:
        error_timestamp = get_timestamp()
        click.echo(f"❌ Error generating summary at {error_timestamp}: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 