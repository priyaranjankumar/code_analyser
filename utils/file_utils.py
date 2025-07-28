"""
File utility functions for the legacy code analyzer
"""

import os
from pathlib import Path
from typing import List, Dict, Any


def validate_codebase_path(codebase_path: Path, language: str) -> bool:
    """
    Validate that the codebase path contains files of the specified language
    
    Args:
        codebase_path: Path to the codebase directory
        language: Programming language to check for
        
    Returns:
        True if valid codebase with language files found
    """
    if not codebase_path.exists() or not codebase_path.is_dir():
        return False
    
    # Define file extensions for each language
    language_extensions = {
        'cobol': ['.cbl', '.cob', '.cpy', '.cobol'],
        'fortran': ['.f', '.f90', '.f95', '.f03', '.f08'],
        'pascal': ['.pas', '.pp', '.p'],
        'basic': ['.bas', '.vb', '.vbs'],
        'assembly': ['.asm', '.s', '.a', '.inc']
    }
    
    extensions = language_extensions.get(language.lower(), [])
    if not extensions:
        return False
    
    # Check if any files with the language extensions exist
    for ext in extensions:
        if list(codebase_path.rglob(f"*{ext}")):
            return True
    
    return False


def find_source_files(codebase_path: Path, language: str, max_files: int = None) -> List[Path]:
    """
    Find all source files of the specified language in the codebase
    
    Args:
        codebase_path: Path to the codebase directory
        language: Programming language to search for
        max_files: Maximum number of files to return (for testing)
        
    Returns:
        List of source file paths
    """
    language_extensions = {
        'cobol': ['.cbl', '.cob', '.cpy', '.cobol'],
        'fortran': ['.f', '.f90', '.f95', '.f03', '.f08'],
        'pascal': ['.pas', '.pp', '.p'],
        'basic': ['.bas', '.vb', '.vbs'],
        'assembly': ['.asm', '.s', '.a', '.inc']
    }
    
    extensions = language_extensions.get(language.lower(), [])
    if not extensions:
        return []
    
    source_files = []
    for ext in extensions:
        source_files.extend(codebase_path.rglob(f"*{ext}"))
    
    # Sort files for consistent results
    source_files.sort()
    
    # Limit files if max_files is specified
    if max_files:
        source_files = source_files[:max_files]
    
    return source_files


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get basic information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    stat = file_path.stat()
    
    return {
        'path': str(file_path),
        'name': file_path.name,
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'extension': file_path.suffix,
        'relative_path': str(file_path.relative_to(file_path.parents[len(file_path.parts) - 2]))
    }


def create_output_structure(output_dir: Path) -> Dict[str, Path]:
    """
    Create the output directory structure for analysis results
    
    Args:
        output_dir: Base output directory
        
    Returns:
        Dictionary with paths to different output subdirectories
    """
    structure = {
        'ast': output_dir / 'ast',
        'summaries': output_dir / 'summaries',
        'flowcharts': output_dir / 'flowcharts',
        'architecture': output_dir / 'architecture',
        'reports': output_dir / 'reports',
        'html': output_dir / 'html'
    }
    
    # Create all directories
    for path in structure.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return structure


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed'
    
    return filename


def read_file_content(file_path: Path, encoding: str = 'utf-8') -> str:
    """
    Read file content with proper encoding handling
    
    Args:
        file_path: Path to the file
        encoding: File encoding to use
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encodings for legacy files
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, read as bytes and decode with errors='replace'
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')


def write_json_file(data: Any, file_path: Path, indent: int = 2):
    """
    Write data to a JSON file
    
    Args:
        data: Data to write
        file_path: Path to the output file
        indent: JSON indentation
    """
    import json
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def write_text_file(content: str, file_path: Path):
    """
    Write text content to a file
    
    Args:
        content: Text content to write
        file_path: Path to the output file
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content) 