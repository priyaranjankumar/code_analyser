"""
Data storage and caching for the legacy code analyzer
"""

import json
import pickle
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataStorage:
    """Manages storage and retrieval of analysis data"""
    
    def __init__(self, base_dir: Path):
        """
        Initialize data storage
        
        Args:
            base_dir: Base directory for storing data
        """
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / 'cache'
        self.db_path = self.base_dir / 'analysis.db'
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for storing analysis metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                codebase_path TEXT NOT NULL,
                language TEXT NOT NULL,
                files_analyzed INTEGER DEFAULT 0,
                programs_found INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                ast_file TEXT,
                summary_file TEXT,
                analysis_time REAL,
                FOREIGN KEY (session_id) REFERENCES analysis_sessions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_analysis_id INTEGER,
                program_name TEXT NOT NULL,
                program_type TEXT,
                flowchart_file TEXT,
                summary TEXT,
                FOREIGN KEY (file_analysis_id) REFERENCES file_analyses (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_analysis_session(self, codebase_path: str, language: str) -> int:
        """
        Create a new analysis session
        
        Args:
            codebase_path: Path to the codebase
            language: Programming language
            
        Returns:
            Session ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_sessions (timestamp, codebase_path, language)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), codebase_path, language))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_session_status(self, session_id: int, status: str, **kwargs):
        """
        Update analysis session status and metadata
        
        Args:
            session_id: Session ID
            status: Status ('running', 'completed', 'failed')
            **kwargs: Additional fields to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query
        fields = ['status = ?']
        values = [status]
        
        for key, value in kwargs.items():
            if key in ['files_analyzed', 'programs_found']:
                fields.append(f'{key} = ?')
                values.append(value)
        
        values.append(session_id)
        
        query = f'''
            UPDATE analysis_sessions 
            SET {', '.join(fields)}
            WHERE id = ?
        '''
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def add_file_analysis(self, session_id: int, file_path: str, file_name: str,
                         ast_file: str = None, summary_file: str = None,
                         analysis_time: float = None) -> int:
        """
        Add file analysis record
        
        Args:
            session_id: Session ID
            file_path: Path to the analyzed file
            file_name: Name of the file
            ast_file: Path to AST file
            summary_file: Path to summary file
            analysis_time: Time taken for analysis
            
        Returns:
            File analysis ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_analyses (session_id, file_path, file_name, ast_file, summary_file, analysis_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, file_path, file_name, ast_file, summary_file, analysis_time))
        
        file_analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return file_analysis_id
    
    def add_program(self, file_analysis_id: int, program_name: str, program_type: str = None,
                   flowchart_file: str = None, summary: str = None):
        """
        Add program record
        
        Args:
            file_analysis_id: File analysis ID
            program_name: Name of the program
            program_type: Type of the program
            flowchart_file: Path to flowchart file
            summary: Program summary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO programs (file_analysis_id, program_name, program_type, flowchart_file, summary)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_analysis_id, program_name, program_type, flowchart_file, summary))
        
        conn.commit()
        conn.close()
    
    def get_session_info(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get analysis session information
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_sessions WHERE id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    def get_file_analyses(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all file analyses for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of file analysis dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM file_analyses WHERE session_id = ?
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        return []
    
    def get_programs(self, file_analysis_id: int) -> List[Dict[str, Any]]:
        """
        Get all programs for a file analysis
        
        Args:
            file_analysis_id: File analysis ID
            
        Returns:
            List of program dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM programs WHERE file_analysis_id = ?
        ''', (file_analysis_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        return []
    
    def cache_ast_data(self, file_path: str, ast_data: Dict[str, Any]):
        """
        Cache AST data for a file
        
        Args:
            file_path: Path to the source file
            ast_data: AST data to cache
        """
        cache_key = self._get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(ast_data, f, indent=2)
    
    def get_cached_ast_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached AST data for a file
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Cached AST data or None if not found
        """
        cache_key = self._get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return None
    
    def _get_cache_key(self, file_path: str) -> str:
        """
        Generate cache key for a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Use file path and modification time for cache key
        path_obj = Path(file_path)
        if path_obj.exists():
            mtime = path_obj.stat().st_mtime
            key_string = f"{file_path}_{mtime}"
        else:
            key_string = file_path
        
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear all cached data"""
        import shutil
        
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis history
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of recent analysis sessions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_sessions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        return []
    
    def export_session_data(self, session_id: int, export_path: Path):
        """
        Export all data for a session to JSON
        
        Args:
            session_id: Session ID
            export_path: Path to export file
        """
        session_info = self.get_session_info(session_id)
        if not session_info:
            raise ValueError(f"Session {session_id} not found")
        
        file_analyses = self.get_file_analyses(session_id)
        
        export_data = {
            'session': session_info,
            'file_analyses': []
        }
        
        for file_analysis in file_analyses:
            programs = self.get_programs(file_analysis['id'])
            file_analysis['programs'] = programs
            export_data['file_analyses'].append(file_analysis)
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2) 