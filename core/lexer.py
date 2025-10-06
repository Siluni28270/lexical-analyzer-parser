"""
Lexical Analyzer (Lexer)
Converts input string into tokens and detects lexical errors
"""

from core.token import Token, TokenType
from utils.errors import LexicalError, EmptyInputError

class Lexer:
    """Lexical Analyzer for converting input into tokens"""
    
    def __init__(self):
        """Initialize the lexer"""
        self.input_string = ""
        self.position = 0
        self.current_char = None
        self.tokens = []
        self.errors = []
    
    def tokenize(self, input_string):
        """
        Convert input string into list of tokens
        
        Args:
            input_string (str): Input expression to tokenize
            
        Returns:
            list: List of tokens
            
        Raises:
            EmptyInputError: If input is empty or whitespace only
            LexicalError: If invalid characters are found
        """
        # Reset state
        self.input_string = input_string.strip()
        self.position = 0
        self.tokens = []
        self.errors = []
        
        # Check for empty input
        if not self.input_string:
            raise EmptyInputError()
        
        # Initialize current character
        self.current_char = self.input_string[0] if self.input_string else None
        
        # Process each character
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self._skip_whitespace()
                continue
            
            # Identify and create tokens
            token = self._get_next_token()
            if token:
                self.tokens.append(token)
        
        # Check if any lexical errors occurred
        if self.errors:
            # Raise the first error found
            raise self.errors[0]
        
        return self.tokens
    
    def _get_next_token(self):
        """Get the next token from input"""
        char = self.current_char
        position = self.position
        
        # Plus operator
        if char == '+':
            self._advance()
            return Token(TokenType.PLUS, '+', position)
        
        # Multiply operator
        elif char == '*':
            self._advance()
            return Token(TokenType.MULTIPLY, '*', position)
        
        # Left parenthesis
        elif char == '(':
            self._advance()
            return Token(TokenType.LPAREN, '(', position)
        
        # Right parenthesis
        elif char == ')':
            self._advance()
            return Token(TokenType.RPAREN, ')', position)
        
        # Identifier (alphanumeric)
        elif char.isalnum():
            self._advance()
            return Token(TokenType.ID, char, position)
        
        # Invalid character
        else:
            error = LexicalError(
                f"Invalid character '{char}' found",
                position,
                char
            )
            self.errors.append(error)
            self._advance()
            return Token(TokenType.INVALID, char, position)
    
    def _advance(self):
        """Move to next character"""
        self.position += 1
        if self.position >= len(self.input_string):
            self.current_char = None
        else:
            self.current_char = self.input_string[self.position]
    
    def _skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char is not None and self.current_char.isspace():
            self._advance()
    
    def get_tokens_info(self):
        """
        Get formatted token information for display
        
        Returns:
            list: List of token information dictionaries
        """
        return [token.get_display_info() for token in self.tokens]
    
    def has_errors(self):
        """Check if lexical errors were found"""
        return len(self.errors) > 0
    
    def get_error_summary(self):
        """Get summary of lexical errors"""
        if not self.errors:
            return "No lexical errors found"
        
        summary = f"Found {len(self.errors)} lexical error(s):\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"{i}. {error.get_detailed_message()}\n"
        
        return summary.strip()
    
    def is_valid_character(self, char):
        """
        Check if character is valid in our grammar
        
        Args:
            char (str): Character to check
            
        Returns:
            bool: True if character is valid
        """
        return (char.isalnum() or 
                char in ['+', '*', '(', ')'] or 
                char.isspace())
    
    def get_token_statistics(self):
        """Get statistics about tokens found"""
        if not self.tokens:
            return {}
        
        stats = {}
        for token in self.tokens:
            if token.type in stats:
                stats[token.type] += 1
            else:
                stats[token.type] = 1
        
        return stats