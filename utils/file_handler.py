"""
File Input/Output Handler for Batch Processing
Allows reading expressions from files and exporting results
"""

import os
from datetime import datetime

class FileHandler:
    """Handles file input/output operations for batch processing"""
    
    def __init__(self):
        """Initialize file handler"""
        self.supported_input_formats = ['.txt', '.expr']
        self.supported_output_formats = ['.txt', '.csv', '.json']
    
    def read_expressions_from_file(self, filepath):
        """
        Read expressions from a file
        
        Args:
            filepath (str): Path to input file
            
        Returns:
            list: List of expressions (strings)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Check file extension
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in self.supported_input_formats:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {', '.join(self.supported_input_formats)}")
        
        expressions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip empty lines and comments
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        expressions.append({
                            'expression': line,
                            'line_number': line_num
                        })
        except Exception as e:
            raise IOError(f"Error reading file: {str(e)}")
        
        return expressions
    
    def export_results_to_txt(self, results, filepath):
        """
        Export analysis results to text file
        
        Args:
            results (list): List of result dictionaries
            filepath (str): Output file path
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("LEXICAL ANALYZER AND PARSER - BATCH ANALYSIS RESULTS\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total expressions: {len(results)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Write each result
                for i, result in enumerate(results, 1):
                    f.write(f"\n{'='*80}\n")
                    f.write(f"EXPRESSION #{i}\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"Input: {result['expression']}\n")
                    
                    if result.get('line_number'):
                        f.write(f"Source Line: {result['line_number']}\n")
                    
                    f.write(f"Status: {result['status']}\n")
                    
                    if result['status'] == 'ACCEPTED':
                        f.write(f"Result: {result.get('result', 'N/A')}\n")
                        f.write(f"Tokens: {result.get('token_count', 0)}\n")
                        f.write(f"\nLexical Analysis:\n{'-'*40}\n")
                        f.write(result.get('lexical_analysis', 'N/A'))
                        f.write(f"\n\nSymbol Table:\n{'-'*40}\n")
                        f.write(result.get('symbol_table', 'N/A'))
                        f.write(f"\n\nParse Tree:\n{'-'*40}\n")
                        f.write(result.get('parse_tree', 'N/A'))
                    else:
                        f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                    
                    f.write("\n")
                
                # Write summary
                accepted = sum(1 for r in results if r['status'] == 'ACCEPTED')
                rejected = len(results) - accepted
                
                f.write(f"\n{'='*80}\n")
                f.write("SUMMARY\n")
                f.write(f"{'='*80}\n")
                f.write(f"Total expressions: {len(results)}\n")
                f.write(f"Accepted: {accepted} ({accepted/len(results)*100:.1f}%)\n")
                f.write(f"Rejected: {rejected} ({rejected/len(results)*100:.1f}%)\n")
                
        except Exception as e:
            raise IOError(f"Error writing to file: {str(e)}")
    
    def export_results_to_csv(self, results, filepath):
        """
        Export analysis results to CSV file
        
        Args:
            results (list): List of result dictionaries
            filepath (str): Output file path
        """
        try:
            import csv
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Expression', 'Line Number', 'Status', 'Result', 
                    'Token Count', 'Unique Tokens', 'Error'
                ])
                
                # Write data
                for result in results:
                    writer.writerow([
                        result['expression'],
                        result.get('line_number', ''),
                        result['status'],
                        result.get('result', ''),
                        result.get('token_count', ''),
                        result.get('unique_tokens', ''),
                        result.get('error', '')
                    ])
                
        except Exception as e:
            raise IOError(f"Error writing CSV file: {str(e)}")
    
    def export_results_to_json(self, results, filepath):
        """
        Export analysis results to JSON file
        
        Args:
            results (list): List of result dictionaries
            filepath (str): Output file path
        """
        try:
            import json
            
            output = {
                'metadata': {
                    'generated': datetime.now().isoformat(),
                    'total_expressions': len(results),
                    'accepted': sum(1 for r in results if r['status'] == 'ACCEPTED'),
                    'rejected': sum(1 for r in results if r['status'] == 'REJECTED')
                },
                'results': results
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise IOError(f"Error writing JSON file: {str(e)}")
    
    def export_results(self, results, filepath, format='txt'):
        """
        Export results to file in specified format
        
        Args:
            results (list): List of result dictionaries
            filepath (str): Output file path
            format (str): Output format ('txt', 'csv', or 'json')
        """
        format = format.lower()
        
        if format == 'txt':
            self.export_results_to_txt(results, filepath)
        elif format == 'csv':
            self.export_results_to_csv(results, filepath)
        elif format == 'json':
            self.export_results_to_json(results, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def create_sample_input_file(self, filepath):
        """
        Create a sample input file with test expressions
        
        Args:
            filepath (str): Path where sample file will be created
        """
        sample_expressions = [
            "# Valid expressions",
            "3+4*5",
            "a+b",
            "(1+2)*3",
            "x",
            "(a+b)*(c+d)",
            "1*2*3*4",
            "((1+2)+(3+4))*5",
            "",
            "# Invalid expressions (for testing error handling)",
            "3+",
            "3**4",
            "(1+2",
            ")",
            "+3"
        ]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Sample Input File for Lexical Analyzer and Parser\n")
                f.write("# Lines starting with # are comments and will be ignored\n")
                f.write("# Each line should contain one expression\n\n")
                f.write("\n".join(sample_expressions))
        except Exception as e:
            raise IOError(f"Error creating sample file: {str(e)}")
    
    def validate_file_path(self, filepath, mode='r'):
        """
        Validate file path for reading or writing
        
        Args:
            filepath (str): File path to validate
            mode (str): 'r' for reading, 'w' for writing
            
        Returns:
            bool: True if valid, raises exception otherwise
        """
        if mode == 'r':
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            if not os.path.isfile(filepath):
                raise ValueError(f"Not a file: {filepath}")
        elif mode == 'w':
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                raise FileNotFoundError(f"Directory not found: {directory}")
        
        return True
    
    def get_file_info(self, filepath):
        """
        Get information about a file
        
        Args:
            filepath (str): Path to file
            
        Returns:
            dict: File information
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        stat = os.stat(filepath)
        
        return {
            'path': filepath,
            'name': os.path.basename(filepath),
            'size': stat.st_size,
            'size_readable': self._format_file_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'extension': os.path.splitext(filepath)[1]
        }
    
    @staticmethod
    def _format_file_size(size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"