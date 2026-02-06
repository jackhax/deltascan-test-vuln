"""Report generation API with database queries and file operations."""

import os
import sqlite3
from typing import Dict, List, Optional


class ReportGenerator:
    """Generates reports from database and exports to files."""
    
    def __init__(self, db_path: str = "/var/app/reports.db"):
        self.db_path = db_path
        self.export_dir = "/var/app/exports"
        
    def get_user_reports(self, username: str, report_type: str) -> List[Dict]:
        """Fetch user reports from database.
        
        VULNERABILITY: SQL Injection via unsanitized username parameter.
        The username is directly concatenated into the SQL query without 
        any sanitization or parameterization.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQL Injection vulnerability - user input directly in query
        query = f"SELECT * FROM reports WHERE username = '{username}' AND type = '{report_type}'"
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
        finally:
            conn.close()
    
    def export_report(self, report_id: int, filename: str, user_id: str) -> str:
        """Export report to file.
        
        VULNERABILITY: Path Traversal via unsanitized filename parameter.
        The filename is user-controlled and directly used in file path construction
        without validation, allowing directory traversal attacks.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch report data
        cursor.execute("SELECT data FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError("Report not found")
        
        report_data = row[0]
        
        # Path traversal vulnerability - no validation on filename
        # Attacker can use: "../../../etc/passwd" to write to arbitrary locations
        output_path = os.path.join(self.export_dir, user_id, filename)
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report_data)
        
        return output_path
    
    def search_reports(self, search_term: str, user_role: str) -> List[Dict]:
        """Search reports with dynamic filtering.
        
        VULNERABILITY: SQL Injection via ORDER BY clause manipulation.
        The search_term is used in ORDER BY without validation, allowing
        SQL injection through sorting parameters.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build base query
        base_query = "SELECT id, title, created_at FROM reports WHERE role = ?"
        
        # SQL Injection in ORDER BY - user controls sort column
        # Attacker can inject: "title; DROP TABLE reports--"
        query = f"{base_query} ORDER BY {search_term}"
        
        try:
            cursor.execute(query, (user_role,))
            results = cursor.fetchall()
            return [{'id': r[0], 'title': r[1], 'created_at': r[2]} for r in results]
        finally:
            conn.close()
    
    def batch_delete_reports(self, report_ids: str) -> int:
        """Delete multiple reports at once.
        
        VULNERABILITY: SQL Injection via unsafe string formatting in IN clause.
        The report_ids string is directly interpolated into the query.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQL Injection - report_ids directly in query
        # Attacker can pass: "1) OR 1=1--" to delete all reports
        query = f"DELETE FROM reports WHERE id IN ({report_ids})"
        
        cursor.execute(query)
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
