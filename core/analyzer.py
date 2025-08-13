"""
Main analyzer class for legacy code analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from tqdm import tqdm
from datetime import datetime

from .ast_generator import ASTGenerator
from .storage import DataStorage
from llm.base import LLMFactory
from visualization.flowchart import FlowchartGenerator
from visualization.architecture import ArchitectureAnalyzer
from utils.file_utils import (
    find_source_files, 
    create_output_structure, 
    get_file_info,
    write_json_file,
    write_text_file
)


class CodeAnalyzer:
    """Main class for analyzing legacy codebases"""
    
    def __init__(self, 
                 llm_provider: str = 'openai',
                 api_key: str = None,
                 output_dir: Path = None,
                 language: str = 'cobol',
                 verbose: bool = False):
        """
        Initialize the code analyzer
        
        Args:
            llm_provider: LLM provider to use ('openai', 'anthropic', etc.)
            api_key: API key for the LLM provider
            output_dir: Directory to store analysis results
            language: Programming language of the codebase
            verbose: Enable verbose output
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.base_output_dir = Path(output_dir) if output_dir else Path('./output')
        self.language = language.lower()
        self.verbose = verbose
        
        # Create timestamp-segregated output directory
        self.output_dir = self._create_timestamped_output_dir()
        
        # Initialize components
        self.llm_client = LLMFactory.create_client(llm_provider, api_key)
        self.ast_generator = ASTGenerator(language)
        self.storage = DataStorage(self.output_dir)
        self.flowchart_generator = FlowchartGenerator(self.output_dir, llm_client=self.llm_client)
        self.architecture_analyzer = ArchitectureAnalyzer(self.output_dir)
        
        # Create output structure
        self.output_structure = create_output_structure(self.output_dir)
        
        # Analysis results
        self.analysis_results = {
            'files_analyzed': 0,
            'programs_found': 0,
            'flowcharts_generated': 0,
            'architecture_report': None,
            'html_report': None,
            'errors': [],
            'analysis_timestamp': datetime.now().isoformat(),
            'output_directory': str(self.output_dir)
        }
    
    def _create_timestamped_output_dir(self) -> Path:
        """
        Create a timestamp-segregated output directory
        
        Returns:
            Path to the timestamped output directory
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamped_dir = self.base_output_dir / f"analysis_{timestamp}"
        timestamped_dir.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"📁 Created timestamped output directory: {timestamped_dir}")
        
        return timestamped_dir
    
    def analyze_codebase(self, 
                        codebase_path: Path,
                        generate_flowcharts: bool = True,
                        generate_architecture: bool = True,
                        max_files: int = None) -> Dict[str, Any]:
        """
        Analyze an entire codebase
        
        Args:
            codebase_path: Path to the codebase directory
            generate_flowcharts: Whether to generate flowcharts
            generate_architecture: Whether to generate architecture analysis
            max_files: Maximum number of files to analyze
            
        Returns:
            Dictionary with analysis results
        """
        import time
        start_time = time.time()
        
        if self.verbose:
            print(f"🔍 Starting analysis of {codebase_path}")
        
        # Find source files
        source_files = find_source_files(codebase_path, self.language, max_files)
        
        if not source_files:
            raise ValueError(f"No {self.language.upper()} files found in {codebase_path}")
        
        if self.verbose:
            print(f"📄 Found {len(source_files)} source files")
        
        # Analyze each file
        file_analyses = []
        programs_data = []
        
        for file_path in tqdm(source_files, desc="Analyzing files"):
            try:
                file_analysis = self._analyze_file(file_path)
                if file_analysis:
                    file_analyses.append(file_analysis)
                    
                    # Extract program data for architecture analysis
                    if 'programs' in file_analysis:
                        programs_data.extend(file_analysis['programs'])
                        
            except Exception as e:
                error_msg = f"Error analyzing {file_path}: {str(e)}"
                self.analysis_results['errors'].append(error_msg)
                if self.verbose:
                    print(f"❌ {error_msg}")
        
        self.analysis_results['files_analyzed'] = len(file_analyses)
        self.analysis_results['programs_found'] = len(programs_data)
        
        if self.verbose:
            print(f"📊 Found {len(programs_data)} programs for visualization")
        
        # Generate flowcharts if requested
        if generate_flowcharts and programs_data:
            self._generate_flowcharts(programs_data)
        
        # Generate architecture analysis if requested
        if generate_architecture and programs_data:
            self._generate_architecture_analysis(programs_data, file_analyses)
        
        # Calculate total analysis time
        end_time = time.time()
        analysis_time = round(end_time - start_time, 2)
        self.analysis_results['analysis_time'] = analysis_time
        
        if self.verbose:
            print(f"⏱️  Analysis completed in {analysis_time} seconds")
        
        # Generate comprehensive report (after timing calculation)
        self._generate_comprehensive_report(file_analyses, programs_data)
        
        return self.analysis_results
    
    def _analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single file
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Dictionary with file analysis results
        """
        if self.verbose:
            print(f"  📝 Analyzing {file_path.name}")
        
        # Get file information
        file_info = get_file_info(file_path)
        
        # Generate AST
        ast_data = self.ast_generator.parse_file(file_path)
        
        # Store AST data
        ast_filename = f"{file_path.stem}_ast.json"
        ast_file_path = self.output_structure['ast'] / ast_filename
        write_json_file(ast_data, ast_file_path)
        
        # Generate code summary using LLM
        summary = self.llm_client.analyze_code(ast_data)
        
        # Store summary
        summary_filename = f"{file_path.stem}_summary.txt"
        summary_file_path = self.output_structure['summaries'] / summary_filename
        write_text_file(summary, summary_file_path)
        
        # Extract programs from AST
        programs = self._extract_programs(ast_data, file_path)
        
        return {
            'file_info': file_info,
            'ast_data': ast_data,
            'summary': summary,
            'programs': programs,
            'ast_file': str(ast_file_path),
            'summary_file': str(summary_file_path)
        }
    
    def _extract_programs(self, ast_data: Dict[str, Any], file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract program information from AST data
        
        Args:
            ast_data: AST data for the file
            file_path: Path to the source file
            
        Returns:
            List of program dictionaries
        """
        programs = []
        
        if 'programs' in ast_data:
            for program in ast_data['programs']:
                program_info = {
                    'name': program.get('name', 'Unknown'),
                    'type': program.get('type', 'Unknown'),
                    'file': str(file_path),
                    'ast': program,
                    'summary': self.llm_client.analyze_program(program)
                }
                programs.append(program_info)
        
        return programs
    
    def _generate_flowcharts(self, programs_data: List[Dict[str, Any]]):
        """Generate flowcharts for all programs"""
        if self.verbose:
            print("📊 Generating flowcharts...")
        
        flowchart_count = 0
        
        for program in tqdm(programs_data, desc="Generating flowcharts"):
            try:
                flowchart_file = self.flowchart_generator.generate_flowchart(program)
                if flowchart_file:
                    flowchart_count += 1
                    program['flowchart_file'] = str(flowchart_file)
            except Exception as e:
                error_msg = f"Error generating flowchart for {program.get('name', 'Unknown')}: {str(e)}"
                self.analysis_results['errors'].append(error_msg)
                if self.verbose:
                    print(f"❌ {error_msg}")
        
        self.analysis_results['flowcharts_generated'] = flowchart_count
    
    def _generate_architecture_analysis(self, 
                                      programs_data: List[Dict[str, Any]], 
                                      file_analyses: List[Dict[str, Any]]):
        """Generate architecture analysis"""
        if self.verbose:
            print("🏗️  Generating architecture analysis...")
        
        try:
            architecture_report = self.architecture_analyzer.analyze_architecture(
                programs_data, file_analyses
            )
            
            # Store architecture report
            report_file = self.output_structure['architecture'] / 'architecture_report.json'
            write_json_file(architecture_report, report_file)
            
            self.analysis_results['architecture_report'] = str(report_file)
            
        except Exception as e:
            error_msg = f"Error generating architecture analysis: {str(e)}"
            self.analysis_results['errors'].append(error_msg)
            if self.verbose:
                print(f"❌ {error_msg}")
    
    def _generate_comprehensive_report(self, 
                                     file_analyses: List[Dict[str, Any]], 
                                     programs_data: List[Dict[str, Any]]):
        """Generate comprehensive HTML report"""
        if self.verbose:
            print("📋 Generating comprehensive report...")
        
        try:
            from visualization.report_generator import ReportGenerator
            
            report_generator = ReportGenerator(self.output_dir)
            html_report = report_generator.generate_report(
                file_analyses, 
                programs_data, 
                self.analysis_results
            )
            
            self.analysis_results['html_report'] = html_report
            
        except Exception as e:
            error_msg = f"Error generating comprehensive report: {str(e)}"
            self.analysis_results['errors'].append(error_msg)
            if self.verbose:
                print(f"❌ {error_msg}")
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results"""
        return {
            'total_files': self.analysis_results['files_analyzed'],
            'total_programs': self.analysis_results['programs_found'],
            'flowcharts_generated': self.analysis_results['flowcharts_generated'],
            'has_architecture_report': bool(self.analysis_results['architecture_report']),
            'has_html_report': bool(self.analysis_results['html_report']),
            'error_count': len(self.analysis_results['errors']),
            'output_directory': str(self.output_dir)
        } 