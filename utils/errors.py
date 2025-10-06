"""
Custom error classes for the lexical analyzer and parser
Provides specific error types with detailed information
"""

class ParseError(Exception):
    """Base class for parsing errors"""
    
    def __init__(self, message, error_type="Parse Error", position=None, token=None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.position = position
        self.token = token
    
    def get_detailed_message(self):
        """Get detailed error message with position info"""
        details = f"{self.error_type}: {self.message}"
        if self.position is not None:
            details += f" at position {self.position}"
        if self.token:
            details += f" (found '{self.token.value}')"
        return details

class LexicalError(ParseError):
    """Error during lexical analysis"""
    
    def __init__(self, message, position=None, character=None):
        super().__init__(message, "Lexical Error", position)
        self.character = character
    
    def get_detailed_message(self):
        """Get detailed lexical error message"""
        details = f"{self.error_type}: {self.message}"
        if self.character:
            details += f" (character: '{self.character}')"
        if self.position is not None:
            details += f" at position {self.position}"
        return details

class ParserSyntaxError(ParseError):  # ← RENAMED from SyntaxError
    """Error during syntax analysis"""
    
    def __init__(self, message, position=None, token=None, expected=None):
        super().__init__(message, "Syntax Error", position, token)
        self.expected = expected
    
    def get_detailed_message(self):
        """Get detailed syntax error message"""
        details = f"{self.error_type}: {self.message}"
        if self.expected:
            details += f" (expected: {self.expected}"
            if self.token:
                details += f", found: '{self.token.value}'"
            details += ")"
        elif self.token:
            details += f" (found '{self.token.value}')"
        if self.position is not None:
            details += f" at position {self.position}"
        return details

class SemanticError(ParseError):
    """Error during semantic analysis"""
    
    def __init__(self, message, position=None, token=None, context=None):
        super().__init__(message, "Semantic Error", position, token)
        self.context = context
    
    def get_detailed_message(self):
        """Get detailed semantic error message"""
        details = f"{self.error_type}: {self.message}"
        if self.context:
            details += f" ({self.context})"
        if self.token:
            details += f" at token '{self.token.value}'"
        if self.position is not None:
            details += f" (position {self.position})"
        return details

class EmptyInputError(ParseError):
    """Error for empty or whitespace-only input"""
    
    def __init__(self):
        super().__init__(
            "Input string is empty or contains only whitespace",
            "Input Error"
        )

class UnexpectedEndOfInputError(ParserSyntaxError):  # ← Updated parent class
    """Error when input ends unexpectedly"""
    
    def __init__(self, expected=None):
        message = "Unexpected end of input"
        if expected:
            message += f", expected {expected}"
        super().__init__(message, expected=expected)