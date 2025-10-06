"""
Enhanced Recursive Descent Parser with ACTUAL Parse Tree Construction
Implements top-down parsing with real tree building and evaluation
Grammar: E → TE', E' → +TE'|ε, T → FT', T' → *FT'|ε, F → (E)|id
"""

from core.token import TokenType
from utils.errors import ParserSyntaxError, SemanticError, UnexpectedEndOfInputError

class ParseTreeNode:
    """Node for representing parse tree"""
    
    def __init__(self, rule, children=None, token=None, value=None):
        """
        Initialize parse tree node
        
        Args:
            rule (str): Grammar rule or non-terminal
            children (list): Child nodes
            token: Associated token (for terminals)
            value: Evaluated value (for evaluation)
        """
        self.rule = rule
        self.children = children or []
        self.token = token
        self.value = value
        self.depth = 0
        self.node_id = None  # For graphical display
    
    def add_child(self, child):
        """Add child node"""
        if child:
            self.children.append(child)
            child.depth = self.depth + 1
    
    def get_tree_string(self, prefix="", is_last=True):
        """Get tree as formatted string with lines"""
        connector = "└── " if is_last else "├── "
        
        if self.token:
            result = f"{prefix}{connector}{self.rule}: '{self.token.value}'"
            if self.value is not None:
                result += f" = {self.value}"
        else:
            result = f"{prefix}{connector}{self.rule}"
            if self.value is not None:
                result += f" = {self.value}"
        
        result += "\n"
        
        # Add children
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            result += child.get_tree_string(child_prefix, is_last_child)
        
        return result
    
    def evaluate(self):
        """Evaluate the expression represented by this subtree"""
        # Terminals (identifiers)
        if self.token and self.token.type == TokenType.ID:
            if self.token.value.isdigit():
                self.value = int(self.token.value)
            else:
                # For variables, assign value 1 for demonstration
                self.value = 1
            return self.value
        
        # Non-terminals
        if self.rule == "E":
            # E → TE'
            if len(self.children) >= 2:
                t_val = self.children[0].evaluate()
                e_prime_val = self.children[1].evaluate()
                self.value = t_val + e_prime_val if e_prime_val is not None else t_val
            return self.value
        
        elif self.rule == "E'":
            # E' → +TE' | ε
            if len(self.children) == 0:
                # Epsilon - contributes 0 to addition
                self.value = 0
            elif len(self.children) >= 2:
                # +TE'
                t_val = self.children[1].evaluate()  # Skip + token
                if len(self.children) > 2:
                    e_prime_val = self.children[2].evaluate()
                    self.value = t_val + e_prime_val if e_prime_val is not None else t_val
                else:
                    self.value = t_val
            return self.value
        
        elif self.rule == "T":
            # T → FT'
            if len(self.children) >= 2:
                f_val = self.children[0].evaluate()
                t_prime_val = self.children[1].evaluate()
                self.value = f_val * t_prime_val if t_prime_val is not None and t_prime_val != 1 else f_val
            return self.value
        
        elif self.rule == "T'":
            # T' → *FT' | ε
            if len(self.children) == 0:
                # Epsilon - contributes 1 to multiplication
                self.value = 1
            elif len(self.children) >= 2:
                # *FT'
                f_val = self.children[1].evaluate()  # Skip * token
                if len(self.children) > 2:
                    t_prime_val = self.children[2].evaluate()
                    self.value = f_val * t_prime_val if t_prime_val is not None else f_val
                else:
                    self.value = f_val
            return self.value
        
        elif self.rule == "F":
            # F → (E) | id
            if len(self.children) == 1:
                # id
                self.value = self.children[0].evaluate()
            elif len(self.children) >= 3:
                # (E)
                self.value = self.children[1].evaluate()  # Middle child is E
            return self.value
        
        return self.value

class Parser:
    """Recursive descent parser with real parse tree construction"""
    
    def __init__(self):
        """Initialize parser"""
        self.tokens = []
        self.current_index = 0
        self.current_token = None
        self.parse_tree_root = None
        self.parse_steps = []
        self.errors = []
        self.warnings = []
        self.node_counter = 0
    
    def parse(self, tokens):
        """
        Parse the list of tokens and build parse tree
        
        Args:
            tokens (list): List of tokens to parse
            
        Returns:
            bool: True if parsing successful, False otherwise
        """
        # Initialize parser state
        self.tokens = tokens
        self.current_index = 0
        self.parse_steps = []
        self.errors = []
        self.warnings = []
        self.node_counter = 0
        
        # Check for empty token list
        if not tokens:
            raise UnexpectedEndOfInputError("expression")
        
        # Set current token
        self.current_token = tokens[0] if tokens else None
        
        # Semantic check
        self._perform_semantic_analysis()
        
        try:
            # Start parsing with the start symbol E
            self._add_parse_step("Starting parse with grammar rule: E")
            self.parse_tree_root = self._parse_E()
            
            # Check if all tokens consumed
            if self.current_index < len(self.tokens):
                remaining_tokens = [t.value for t in self.tokens[self.current_index:]]
                raise ParserSyntaxError(
                    f"Unexpected tokens at end of input: {', '.join(remaining_tokens)}",
                    self.current_token.position if self.current_token else None,
                    self.current_token
                )
            
            self._add_parse_step("✓ Parsing completed successfully")
            
            # Evaluate the expression
            if self.parse_tree_root:
                result = self.parse_tree_root.evaluate()
                self._add_parse_step(f"✓ Expression evaluates to: {result}")
            
            return True
            
        except (ParserSyntaxError, SemanticError) as e:
            self._add_parse_step(f"✗ {e.get_detailed_message()}")
            raise
        except Exception as e:
            error = SyntaxError(f"Unexpected parsing error: {str(e)}")
            self._add_parse_step(f"✗ {error.get_detailed_message()}")
            raise error
    
    def _perform_semantic_analysis(self):
        """Perform semantic checks on token sequence"""
        if not self.tokens:
            return
        
        # Check for consecutive operators
        for i in range(len(self.tokens) - 1):
            current = self.tokens[i]
            next_token = self.tokens[i + 1]
            
            if (current.type in [TokenType.PLUS, TokenType.MULTIPLY] and
                next_token.type in [TokenType.PLUS, TokenType.MULTIPLY]):
                raise SemanticError(
                    f"Consecutive operators '{current.value}' and '{next_token.value}' are not allowed",
                    current.position,
                    current,
                    "operator sequence"
                )
        
        # Check for operator at start
        if self.tokens[0].type in [TokenType.PLUS, TokenType.MULTIPLY]:
            raise SemanticError(
                f"Expression cannot start with operator '{self.tokens[0].value}'",
                self.tokens[0].position,
                self.tokens[0],
                "expression start"
            )
        
        # Check for operator at end
        if self.tokens[-1].type in [TokenType.PLUS, TokenType.MULTIPLY]:
            raise SemanticError(
                f"Expression cannot end with operator '{self.tokens[-1].value}'",
                self.tokens[-1].position,
                self.tokens[-1],
                "expression end"
            )
        
        # Check parentheses balance
        paren_count = 0
        for token in self.tokens:
            if token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count < 0:
                    raise SemanticError(
                        "Unmatched closing parenthesis",
                        token.position,
                        token,
                        "parentheses balance"
                    )
        
        if paren_count > 0:
            raise SemanticError(
                f"{paren_count} unmatched opening parenthesis(es)",
                None,
                None,
                "parentheses balance"
            )
    
    def _parse_E(self):
        """Parse E → TE' and return node"""
        self._add_parse_step("E → TE'")
        node = ParseTreeNode("E")
        node.node_id = self._get_node_id()
        
        t_node = self._parse_T()
        node.add_child(t_node)
        
        e_prime_node = self._parse_E_prime()
        node.add_child(e_prime_node)
        
        return node
    
    def _parse_E_prime(self):
        """Parse E' → +TE' | ε and return node"""
        node = ParseTreeNode("E'")
        node.node_id = self._get_node_id()
        
        if self.current_token and self.current_token.type == TokenType.PLUS:
            self._add_parse_step("E' → +TE'")
            
            # Add + token as child
            plus_node = ParseTreeNode("+", token=self.current_token)
            plus_node.node_id = self._get_node_id()
            node.add_child(plus_node)
            
            self._consume_token(TokenType.PLUS)
            
            t_node = self._parse_T()
            node.add_child(t_node)
            
            e_prime_node = self._parse_E_prime()
            node.add_child(e_prime_node)
        else:
            self._add_parse_step("E' → ε (epsilon)")
            # Epsilon - no children
        
        return node
    
    def _parse_T(self):
        """Parse T → FT' and return node"""
        self._add_parse_step("T → FT'")
        node = ParseTreeNode("T")
        node.node_id = self._get_node_id()
        
        f_node = self._parse_F()
        node.add_child(f_node)
        
        t_prime_node = self._parse_T_prime()
        node.add_child(t_prime_node)
        
        return node
    
    def _parse_T_prime(self):
        """Parse T' → *FT' | ε and return node"""
        node = ParseTreeNode("T'")
        node.node_id = self._get_node_id()
        
        if self.current_token and self.current_token.type == TokenType.MULTIPLY:
            self._add_parse_step("T' → *FT'")
            
            # Add * token as child
            mult_node = ParseTreeNode("*", token=self.current_token)
            mult_node.node_id = self._get_node_id()
            node.add_child(mult_node)
            
            self._consume_token(TokenType.MULTIPLY)
            
            f_node = self._parse_F()
            node.add_child(f_node)
            
            t_prime_node = self._parse_T_prime()
            node.add_child(t_prime_node)
        else:
            self._add_parse_step("T' → ε (epsilon)")
            # Epsilon - no children
        
        return node
    
    def _parse_F(self):
        """Parse F → (E) | id and return node"""
        if not self.current_token:
            raise UnexpectedEndOfInputError("'(' or identifier")
        
        node = ParseTreeNode("F")
        node.node_id = self._get_node_id()
        
        if self.current_token.type == TokenType.LPAREN:
            self._add_parse_step("F → (E)")
            
            # Add ( token
            lparen_node = ParseTreeNode("(", token=self.current_token)
            lparen_node.node_id = self._get_node_id()
            node.add_child(lparen_node)
            
            self._consume_token(TokenType.LPAREN)
            
            # Parse E
            e_node = self._parse_E()
            node.add_child(e_node)
            
            # Add ) token
            rparen_node = ParseTreeNode(")", token=self.current_token)
            rparen_node.node_id = self._get_node_id()
            node.add_child(rparen_node)
            
            self._consume_token(TokenType.RPAREN)
            
        elif self.current_token.type == TokenType.ID:
            self._add_parse_step(f"F → id ('{self.current_token.value}')")
            
            # Add id token
            id_node = ParseTreeNode("id", token=self.current_token)
            id_node.node_id = self._get_node_id()
            node.add_child(id_node)
            
            self._consume_token(TokenType.ID)
        else:
            raise ParserSyntaxError(
                f"Expected '(' or identifier",
                self.current_token.position,
                self.current_token,
                "'(' or identifier"
            )
        
        return node
    
    def _consume_token(self, expected_type):
        """Consume current token and move to next"""
        if not self.current_token:
            raise UnexpectedEndOfInputError(expected_type)
        
        if self.current_token.type != expected_type:
            raise ParserSyntaxError(
                f"Expected {expected_type}",
                self.current_token.position,
                self.current_token,
                expected_type
            )
        
        self._add_parse_step(f"✓ Consumed: {self.current_token}")
        
        # Move to next token
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = None
    
    def _add_parse_step(self, step):
        """Add step to parse steps list"""
        self.parse_steps.append(step)
    
    def _get_node_id(self):
        """Get unique node ID for tree visualization"""
        self.node_counter += 1
        return self.node_counter
    
    def get_parse_tree(self):
        """Get parse tree as formatted string"""
        if not self.parse_tree_root:
            return "No parse tree generated"
        
        result = "PARSE TREE (Hierarchical Structure)\n"
        result += "=" * 70 + "\n\n"
        result += self.parse_tree_root.get_tree_string()
        
        return result
    
    def get_parse_steps(self):
        """Get parse steps as formatted string"""
        if not self.parse_steps:
            return "No parse steps recorded"
        
        result = "PARSE STEPS (Derivation Sequence)\n"
        result += "=" * 70 + "\n"
        
        for i, step in enumerate(self.parse_steps, 1):
            indent = ""
            if "→" in step and not step.startswith("✓") and not step.startswith("✗"):
                indent = "  "
            elif step.startswith("✓ Consumed"):
                indent = "    "
            
            result += f"{i:2d}. {indent}{step}\n"
        
        return result
    
    def get_evaluation_result(self):
        """Get the evaluated result of the expression"""
        if not self.parse_tree_root:
            return None
        try:
            return self.parse_tree_root.evaluate()
        except:
            return None
    
    def has_errors(self):
        """Check if parser has errors"""
        return len(self.errors) > 0
    
    def reset(self):
        """Reset parser state"""
        self.tokens = []
        self.current_index = 0
        self.current_token = None
        self.parse_tree_root = None
        self.parse_steps = []
        self.errors = []
        self.warnings = []
        self.node_counter = 0