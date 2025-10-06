"""
Enhanced GUI with File I/O, Graphical Tree, History, Evaluation, and Theme Toggle
Complete implementation with all bonus features + Dark/Light mode
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter.font import Font
import os
from datetime import datetime

from core.lexer import Lexer
from core.parser import Parser
from core.symbol_table import SymbolTable
from utils.errors import ParseError, LexicalError, ParserSyntaxError, SemanticError
from utils.file_handler import FileHandler
from utils.tree_visualizer import TreeVisualizerWindow

class ParserGUI:
    """Enhanced GUI with all bonus features and theme toggle"""
    
    def __init__(self, root):
        """Initialize the enhanced GUI"""
        self.root = root
        self.root.title("Lexical Analyzer & Parser")
        self.root.geometry("1400x900")
        
        # Theme state (True = dark, False = light)
        self.is_dark_mode = True
        
        # Initialize components
        self.lexer = Lexer()
        self.parser = Parser()
        self.symbol_table = SymbolTable()
        self.file_handler = FileHandler()
        
        # History management
        self.expression_history = []
        self.current_parse_tree = None
        self.current_expression = ""
        self.batch_results = []
        
        # Setup GUI
        self.setup_color_schemes()
        self.setup_fonts()
        self.apply_theme()
        self.create_menu_bar()
        self.create_widgets()
        self.setup_layout()
        self.center_window()
    
    def setup_color_schemes(self):
        """Setup color schemes for both themes"""
        # DARK MODE
        self.dark_colors = {
            'primary': '#0f3460',
            'secondary': '#16213e',
            'accent': '#e94560',
            'accent2': '#00d4ff',
            'success': '#00ff88',
            'danger': '#ff4757',
            'warning': '#ffa502',
            'bg': '#1a1a2e',
            'panel': '#16213e',
            'input_bg': '#0f3460',
            'text': '#eaeaea',
            'text_dim': '#a8a8b8',
            'border': '#2d3561',
            'error_bg': '#2a1a1f'
        }
        
        # LIGHT MODE
        self.light_colors = {
            'primary': '#ffffff',
            'secondary': '#f8f9fa',
            'accent': '#e94560',
            'accent2': '#0077b6',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'bg': '#f0f2f5',
            'panel': '#ffffff',
            'input_bg': '#ffffff',
            'text': '#212529',
            'text_dim': '#6c757d',
            'border': '#dee2e6',
            'error_bg': '#fff5f5'
        }
        
        # Start with dark mode
        self.colors = self.dark_colors.copy()
    
    def setup_fonts(self):
        """Setup custom fonts"""
        self.fonts = {
            'title': Font(family='Segoe UI', size=18, weight='bold'),
            'subtitle': Font(family='Segoe UI', size=12, weight='bold'),
            'normal': Font(family='Segoe UI', size=10),
            'code': Font(family='Consolas', size=10),
            'small': Font(family='Segoe UI', size=9)
        }
    
    def apply_theme(self):
        """Apply the current theme to styles"""
        self.root.configure(bg=self.colors['bg'])
        
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass
        
        # Button styles
        self.style.configure("Primary.TButton", background=self.colors['accent'], foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#d63447")])
        
        self.style.configure("Success.TButton", background=self.colors['accent2'], 
                           foreground="white" if self.is_dark_mode else "white")
        self.style.map("Success.TButton", background=[("active", "#00b8d4" if self.is_dark_mode else "#005f8a")])
        
        self.style.configure("Danger.TButton", background=self.colors['danger'], foreground="white")
        self.style.map("Danger.TButton", background=[("active", "#c82333" if not self.is_dark_mode else "#ee5a6f")])
        
        self.style.configure("Dark.TButton", background=self.colors['secondary'], foreground=self.colors['text'])
        self.style.map("Dark.TButton", background=[("active", self.colors['border'])])
        
        # Theme toggle button
        self.style.configure("Toggle.TButton", background=self.colors['accent2'], foreground="white")
        self.style.map("Toggle.TButton", background=[("active", "#005f8a" if not self.is_dark_mode else "#00b8d4")])
        
        # Notebook styling
        self.style.configure("TNotebook", background=self.colors['bg'], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.colors['secondary'], 
                           foreground=self.colors['text_dim'], padding=[20, 10])
        self.style.map("TNotebook.Tab",
            background=[("selected", self.colors['primary'])],
            foreground=[("selected", self.colors['accent2'])])
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.colors = self.dark_colors.copy() if self.is_dark_mode else self.light_colors.copy()
        
        # Reapply theme
        self.apply_theme()
        
        # Update all widgets
        self.update_widget_colors()
        
        # Update toggle button text
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.configure(text="☀ LIGHT" if self.is_dark_mode else "🌙 DARK")
    
    def update_widget_colors(self):
        """Update all widget colors after theme change"""
        # Main frame
        self.main_frame.configure(bg=self.colors['bg'])
        
        # Header
        self.header_frame.configure(bg=self.colors['primary'])
        self.accent_line.configure(bg=self.colors['accent'])
        self.content_frame.configure(bg=self.colors['primary'])
        self.title_label.configure(bg=self.colors['primary'], fg=self.colors['accent2'])
        self.features_label.configure(bg=self.colors['primary'], fg=self.colors['success'])
        
        # Input section
        self.input_frame.configure(bg=self.colors['bg'])
        self.label.configure(bg=self.colors['bg'], fg=self.colors['text'])
        self.input_container.configure(bg=self.colors['border'])
        self.input_inner.configure(bg=self.colors['input_bg'])
        self.input_entry.configure(
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent2'],
            selectbackground=self.colors['accent']
        )
        
        # Test buttons area
        self.test_frame.configure(bg=self.colors['bg'])
        self.valid_frame.configure(bg=self.colors['bg'])
        self.valid_label.configure(bg=self.colors['bg'], fg=self.colors['accent2'])
        self.invalid_frame.configure(bg=self.colors['bg'])
        self.invalid_label.configure(bg=self.colors['bg'], fg=self.colors['danger'])
        
        # Results section
        self.results_frame.configure(bg=self.colors['bg'])
        
        # Text widgets
        for widget in [self.summary_text, self.eval_text, self.lexical_text, 
                      self.symbol_text, self.parse_text, self.steps_text]:
            widget.configure(
                bg=self.colors['panel'],
                fg=self.colors['text'],
                insertbackground=self.colors['accent2'],
                selectbackground=self.colors['accent']
            )
        
        # Error text widget
        self.error_text.configure(
            bg=self.colors['error_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['danger'],
            selectbackground=self.colors['danger']
        )
        
        # Status bar
        self.status_bar.configure(bg=self.colors['secondary'])
        self.status_label.configure(bg=self.colors['secondary'], fg=self.colors['text_dim'])
    
    def create_menu_bar(self):
        """Create menu bar with file operations"""
        menubar = tk.Menu(self.root, bg=self.colors['secondary'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['secondary'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Batch Process...", command=self.batch_process)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_command(label="Create Sample File...", command=self.create_sample_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['secondary'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Graphical Tree", command=self.show_graphical_tree, accelerator="Ctrl+T")
        view_menu.add_command(label="View History", command=self.show_history, accelerator="Ctrl+H")
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme, accelerator="Ctrl+M")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['secondary'], fg=self.colors['text'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Grammar Rules", command=self.show_grammar)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-t>', lambda e: self.show_graphical_tree())
        self.root.bind('<Control-h>', lambda e: self.show_history())
        self.root.bind('<Control-m>', lambda e: self.toggle_theme())
    
    def create_widgets(self):
        """Create all GUI widgets"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        
        self.create_header()
        self.create_input_section()
        self.create_results_section()
        self.create_status_bar()
    
    def create_header(self):
        """Create application header"""
        self.header_frame = tk.Frame(self.main_frame, bg=self.colors['primary'], height=100)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        self.accent_line = tk.Frame(self.header_frame, bg=self.colors['accent'], height=4)
        self.accent_line.pack(fill=tk.X)
        
        self.content_frame = tk.Frame(self.header_frame, bg=self.colors['primary'])
        self.content_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        self.title_label = tk.Label(
            self.content_frame,
            text="⚡ LEXICAL ANALYZER & PARSER FOR ARITHMETIC EXPRESSIONS",
            font=self.fonts['title'],
            fg=self.colors['accent2'],
            bg=self.colors['primary']
        )
        self.title_label.pack(pady=(0, 4))
        
        self.features_label = tk.Label(
            self.content_frame,
            text="✓ File I/O  ✓ Graphical Trees  ✓ Expression Evaluation  ✓ History  ✓ Batch Processing  ✓ Dark/Light Mode",
            font=self.fonts['small'],
            fg=self.colors['success'],
            bg=self.colors['primary']
        )
        self.features_label.pack(pady=(2, 0))
        
        # Theme toggle button (top right)
        self.theme_toggle_btn = ttk.Button(
            self.header_frame,
            text="☀ LIGHT",
            command=self.toggle_theme,
            style="Toggle.TButton",
            width=10
        )
        self.theme_toggle_btn.place(relx=0.98, rely=0.5, anchor='e')
    
    def create_input_section(self):
        """Create input section"""
        self.input_frame = tk.Frame(self.main_frame, bg=self.colors['bg'], padx=16, pady=16)
        self.input_frame.pack(fill=tk.X)
        
        self.label = tk.Label(
            self.input_frame,
            text="INPUT EXPRESSION",
            font=self.fonts['subtitle'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.label.pack(fill=tk.X, pady=(0, 8))
        
        # Input container
        self.input_container = tk.Frame(self.input_frame, bg=self.colors['border'], padx=2, pady=2)
        self.input_container.pack(fill=tk.X, pady=(0, 12))
        
        self.input_inner = tk.Frame(self.input_container, bg=self.colors['input_bg'])
        self.input_inner.pack(fill=tk.BOTH, expand=True)
        
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            self.input_inner,
            textvariable=self.input_var,
            font=self.fonts['code'],
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            relief='flat',
            insertbackground=self.colors['accent2'],
            selectbackground=self.colors['accent'],
            selectforeground='white'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.input_entry.bind('<Return>', lambda e: self.analyze_expression())
        
        # Buttons
        self.analyze_btn = ttk.Button(
            self.input_inner,
            text="▶ ANALYZE",
            command=self.analyze_expression,
            style="Primary.TButton"
        )
        self.analyze_btn.pack(side=tk.RIGHT, padx=8, pady=6)
        
        self.tree_btn = ttk.Button(
            self.input_inner,
            text="🌳 TREE",
            command=self.show_graphical_tree,
            style="Success.TButton"
        )
        self.tree_btn.pack(side=tk.RIGHT, padx=3, pady=6)
        
        # Test buttons
        self.create_test_buttons(self.input_frame)
    
    def create_test_buttons(self, parent):
        """Create test buttons"""
        self.test_frame = tk.Frame(parent, bg=self.colors['bg'])
        self.test_frame.pack(fill=tk.X)
        
        # Valid tests
        self.valid_frame = tk.Frame(self.test_frame, bg=self.colors['bg'])
        self.valid_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.valid_label = tk.Label(
            self.valid_frame,
            text="✓ VALID",
            font=self.fonts['small'],
            bg=self.colors['bg'],
            fg=self.colors['accent2']
        )
        self.valid_label.pack(side=tk.LEFT, padx=(0, 10))
        
        valid_tests = ["3+4*5", "a+b", "(1+2)*3", "x", "(a+b)*(c+d)"]
        for test in valid_tests:
            ttk.Button(
                self.valid_frame,
                text=test,
                command=lambda t=test: self.set_input_and_analyze(t),
                style="Success.TButton"
            ).pack(side=tk.LEFT, padx=3)
        
        # Invalid tests
        self.invalid_frame = tk.Frame(self.test_frame, bg=self.colors['bg'])
        self.invalid_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        self.invalid_label = tk.Label(
            self.invalid_frame,
            text="✗ ERROR",
            font=self.fonts['small'],
            bg=self.colors['bg'],
            fg=self.colors['danger']
        )
        self.invalid_label.pack(side=tk.LEFT, padx=(0, 10))
        
        invalid_tests = ["3+", "3**4", "(1+2", ")", "+3"]
        for test in invalid_tests:
            ttk.Button(
                self.invalid_frame,
                text=test,
                command=lambda t=test: self.set_input_and_analyze(t),
                style="Danger.TButton"
            ).pack(side=tk.LEFT, padx=3)
        
        # Control buttons
        ttk.Button(
            self.test_frame,
            text="📁 LOAD",
            command=self.open_file,
            style="Dark.TButton"
        ).pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(
            self.test_frame,
            text="⟲ CLEAR",
            command=self.clear_all,
            style="Dark.TButton"
        ).pack(side=tk.RIGHT, padx=3)
    
    def create_results_section(self):
        """Create results section with tabs"""
        self.results_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_result_tabs()
    
    def create_result_tabs(self):
        """Create result display tabs"""
        # Summary tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📋 Summary")
        self.summary_text = self._create_text_widget(summary_frame)
        
        # Evaluation tab
        eval_frame = ttk.Frame(self.notebook)
        self.notebook.add(eval_frame, text="🔢 Evaluation")
        self.eval_text = self._create_text_widget(eval_frame)
        
        # Lexical tab
        lexical_frame = ttk.Frame(self.notebook)
        self.notebook.add(lexical_frame, text="🔤 Lexical")
        self.lexical_text = self._create_text_widget(lexical_frame)
        
        # Symbol table tab
        symbol_frame = ttk.Frame(self.notebook)
        self.notebook.add(symbol_frame, text="📊 Symbols")
        self.symbol_text = self._create_text_widget(symbol_frame)
        
        # Parse tree tab
        parse_frame = ttk.Frame(self.notebook)
        self.notebook.add(parse_frame, text="🌳 Parse Tree")
        self.parse_text = self._create_text_widget(parse_frame)
        
        # Parse steps tab
        steps_frame = ttk.Frame(self.notebook)
        self.notebook.add(steps_frame, text="📝 Steps")
        self.steps_text = self._create_text_widget(steps_frame)
        
        # Errors tab
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text="⚠️ Errors")
        self.error_text = self._create_text_widget(error_frame, bg=self.colors['error_bg'])
    
    def _create_text_widget(self, parent, bg=None):
        """Helper to create text widget"""
        widget = scrolledtext.ScrolledText(
            parent,
            font=self.fonts['code'],
            wrap=tk.WORD,
            bg=bg or self.colors['panel'],
            fg=self.colors['text'],
            state=tk.DISABLED,
            relief='flat',
            padx=16,
            pady=16,
            insertbackground=self.colors['accent2'],
            selectbackground=self.colors['accent'],
            selectforeground='white'
        )
        widget.pack(fill=tk.BOTH, expand=True)
        return widget
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("● Ready - Enter an expression or load a file")
        
        self.status_bar = tk.Frame(self.main_frame, bg=self.colors['secondary'], height=36)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_var,
            anchor=tk.W,
            bg=self.colors['secondary'],
            fg=self.colors['text_dim'],
            font=self.fonts['small'],
            padx=16
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
    
    def setup_layout(self):
        """Setup main layout"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def set_input_and_analyze(self, text):
        """Set input and analyze"""
        self.input_var.set(text)
        self.analyze_expression()
    
    def analyze_expression(self):
        """Main analysis function"""
        expression = self.input_var.get().strip()
        
        if not expression:
            messagebox.showwarning("Warning", "Please enter an expression!")
            return
        
        self.current_expression = expression
        self.status_var.set(f"⟳ Analyzing: '{expression}'...")
        self.root.update()
        
        try:
            self.clear_results()
            
            # Lexical analysis
            tokens = self.lexer.tokenize(expression)
            
            # Build symbol table
            self.symbol_table.clear()
            for token in tokens:
                self.symbol_table.add_token(token)
            
            # Parse expression
            parse_success = self.parser.parse(tokens)
            
            # Store parse tree
            self.current_parse_tree = self.parser.parse_tree_root
            
            # Get evaluation result
            eval_result = self.parser.get_evaluation_result()
            
            # Display results
            self.display_results(expression, tokens, parse_success, eval_result)
            
            # Add to history
            self.add_to_history(expression, parse_success, eval_result)
            
            # Update status
            if parse_success:
                result_str = f" = {eval_result}" if eval_result is not None else ""
                self.status_var.set(f"✓ '{expression}'{result_str} - ACCEPTED")
            else:
                self.status_var.set(f"✗ '{expression}' - REJECTED")
        
        except ParseError as e:
            self.handle_parse_error(expression, e)
        except Exception as e:
            self.handle_unexpected_error(expression, e)
    
    def display_results(self, expression, tokens, parse_success, eval_result):
        """Display analysis results"""
        # Summary
        summary = self.generate_summary(expression, tokens, parse_success, eval_result)
        self.update_text_widget(self.summary_text, summary)
        
        # Evaluation
        eval_info = self.generate_evaluation_info(expression, eval_result)
        self.update_text_widget(self.eval_text, eval_info)
        
        # Lexical
        lexical_info = self.generate_lexical_info(tokens)
        self.update_text_widget(self.lexical_text, lexical_info)
        
        # Symbol table
        symbol_info = self.symbol_table.get_formatted_table()
        self.update_text_widget(self.symbol_text, symbol_info)
        
        # Parse tree
        parse_info = self.parser.get_parse_tree()
        self.update_text_widget(self.parse_text, parse_info)
        
        # Parse steps
        steps_info = self.parser.get_parse_steps()
        self.update_text_widget(self.steps_text, steps_info)
        
        # Errors
        if parse_success:
            self.update_text_widget(self.error_text, "✓ No errors found!")
        
        # Switch to summary tab
        self.notebook.select(0)
    
    def generate_summary(self, expression, tokens, parse_success, eval_result):
        """Generate analysis summary"""
        summary = "ANALYSIS SUMMARY\n"
        summary += "=" * 70 + "\n"
        summary += f"Expression: '{expression}'\n"
        summary += f"Result: {'ACCEPTED ✓' if parse_success else 'REJECTED ✗'}\n"
        
        if eval_result is not None:
            summary += f"Evaluated Result: {eval_result}\n"
        
        summary += f"Total characters: {len(expression)}\n"
        summary += f"Total tokens: {len(tokens)}\n\n"
        
        stats = self.symbol_table.get_statistics()
        summary += "TOKEN BREAKDOWN:\n"
        summary += "-" * 30 + "\n"
        summary += f"Identifiers: {stats['identifier_count']}\n"
        summary += f"Operators: {stats['operator_count']}\n"
        summary += f"Delimiters: {stats['delimiter_count']}\n"
        summary += f"Unique tokens: {stats['unique_tokens']}\n\n"
        
        if parse_success:
            summary += "ANALYSIS STATUS:\n"
            summary += "-" * 20 + "\n"
            summary += "✓ Lexical analysis: PASSED\n"
            summary += "✓ Syntax analysis: PASSED\n"
            summary += "✓ Semantic analysis: PASSED\n"
            summary += "✓ Parse tree: CONSTRUCTED\n"
        
        return summary
    
    def generate_evaluation_info(self, expression, result):
        """Generate evaluation information"""
        info = "EXPRESSION EVALUATION\n"
        info += "=" * 70 + "\n\n"
        info += f"Input Expression: {expression}\n"
        
        if result is not None:
            info += f"\n{'='*70}\n"
            info += f"RESULT: {result}\n"
            info += f"{'='*70}\n\n"
            
            info += "EVALUATION PROCESS:\n"
            info += "-" * 40 + "\n"
            info += "The expression was evaluated using the parse tree structure.\n"
            info += "Operator precedence is enforced by the grammar:\n"
            info += "  * (multiply) has higher precedence than + (plus)\n"
            info += "  Parentheses override default precedence\n\n"
            
            info += "NOTE: Non-numeric identifiers (variables) are assigned value 1\n"
            info += "      for demonstration purposes.\n\n"
            
            info += f"Example: 3+4*5 = 3+(4*5) = 3+20 = 23\n"
            info += f"         (1+2)*3 = (3)*3 = 9\n"
        else:
            info += "\nResult: Cannot evaluate (parsing failed)\n"
        
        return info
    
    def generate_lexical_info(self, tokens):
        """Generate lexical analysis information"""
        info = "LEXICAL ANALYSIS RESULTS\n"
        info += "=" * 70 + "\n\n"
        info += "TOKENS FOUND:\n"
        info += "-" * 20 + "\n"
        
        for i, token in enumerate(tokens, 1):
            info += f"{i:2d}. {token}\n"
        
        info += f"\nTotal tokens: {len(tokens)}\n"
        
        return info
    
    def handle_parse_error(self, expression, error):
        """Handle parsing errors"""
        self.clear_results()
        
        error_summary = f"ANALYSIS FAILED\n"
        error_summary += "=" * 70 + "\n"
        error_summary += f"Expression: '{expression}'\n"
        error_summary += f"Result: REJECTED\n\n"
        error_summary += f"Error Type: {error.error_type}\n"
        error_summary += f"Message: {error.message}\n"
        
        self.update_text_widget(self.summary_text, error_summary)
        
        detailed_error = f"DETAILED ERROR INFORMATION\n"
        detailed_error += "=" * 70 + "\n"
        detailed_error += error.get_detailed_message() + "\n"
        
        self.update_text_widget(self.error_text, detailed_error)
        self.notebook.select(6)
        
        self.status_var.set(f"✗ '{expression}' - {error.error_type}")
        self.add_to_history(expression, False, None, str(error))
    
    def handle_unexpected_error(self, expression, error):
        """Handle unexpected errors"""
        error_msg = f"Unexpected error: {str(error)}"
        self.update_text_widget(self.summary_text, f"UNEXPECTED ERROR\n{error_msg}")
        self.status_var.set("✗ Unexpected error")
        messagebox.showerror("Error", error_msg)
    
    def update_text_widget(self, widget, text):
        """Update text widget"""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, text)
        widget.config(state=tk.DISABLED)
    
    def clear_results(self):
        """Clear all results"""
        for widget in [self.summary_text, self.eval_text, self.lexical_text, 
                      self.symbol_text, self.parse_text, self.steps_text, self.error_text]:
            self.update_text_widget(widget, "")
    
    def clear_all(self):
        """Clear everything"""
        self.input_var.set("")
        self.clear_results()
        self.current_parse_tree = None
        self.current_expression = ""
        self.status_var.set("● Ready - Enter an expression or load a file")
    
    # FILE I/O METHODS
    
    def open_file(self):
        """Open and process single file"""
        filename = filedialog.askopenfilename(
            title="Select Expression File",
            filetypes=[("Text files", "*.txt"), ("Expression files", "*.expr"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                expressions = self.file_handler.read_expressions_from_file(filename)
                
                if expressions:
                    first_expr = expressions[0]['expression']
                    self.input_var.set(first_expr)
                    self.analyze_expression()
                    
                    messagebox.showinfo("File Loaded", 
                                      f"Loaded {len(expressions)} expression(s) from file.\n"
                                      f"Showing first expression: '{first_expr}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def batch_process(self):
        """Batch process multiple expressions from file"""
        filename = filedialog.askopenfilename(
            title="Select File for Batch Processing",
            filetypes=[("Text files", "*.txt"), ("Expression files", "*.expr"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            expressions = self.file_handler.read_expressions_from_file(filename)
            
            if not expressions:
                messagebox.showwarning("Warning", "No expressions found in file!")
                return
            
            self.batch_results = []
            progress_window = self.create_progress_window(len(expressions))
            
            for i, expr_data in enumerate(expressions):
                expr = expr_data['expression']
                self.update_progress(progress_window, i+1, len(expressions), expr)
                
                result = self.process_single_expression(expr, expr_data.get('line_number'))
                self.batch_results.append(result)
            
            progress_window.destroy()
            self.show_batch_summary()
            
        except Exception as e:
            messagebox.showerror("Error", f"Batch processing failed:\n{str(e)}")
    
    def process_single_expression(self, expression, line_number=None):
        """Process single expression and return result"""
        result = {
            'expression': expression,
            'line_number': line_number,
            'status': 'REJECTED',
            'error': None
        }
        
        try:
            tokens = self.lexer.tokenize(expression)
            
            self.symbol_table.clear()
            for token in tokens:
                self.symbol_table.add_token(token)
            
            parse_success = self.parser.parse(tokens)
            eval_result = self.parser.get_evaluation_result()
            
            if parse_success:
                result['status'] = 'ACCEPTED'
                result['result'] = eval_result
                result['token_count'] = len(tokens)
                result['unique_tokens'] = self.symbol_table.get_statistics()['unique_tokens']
                result['lexical_analysis'] = self.generate_lexical_info(tokens)
                result['symbol_table'] = self.symbol_table.get_formatted_table()
                result['parse_tree'] = self.parser.get_parse_tree()
        
        except ParseError as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def create_progress_window(self, total):
        """Create progress window"""
        window = tk.Toplevel(self.root)
        window.title("Batch Processing")
        window.geometry("400x150")
        window.configure(bg=self.colors['bg'])
        
        tk.Label(
            window,
            text="Processing expressions...",
            font=self.fonts['subtitle'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        window.progress_label = tk.Label(
            window,
            text="",
            font=self.fonts['normal'],
            bg=self.colors['bg'],
            fg=self.colors['text_dim']
        )
        window.progress_label.pack(pady=10)
        
        window.progress_bar = ttk.Progressbar(
            window,
            length=300,
            mode='determinate',
            maximum=total
        )
        window.progress_bar.pack(pady=10)
        
        return window
    
    def update_progress(self, window, current, total, expression):
        """Update progress window"""
        window.progress_label.config(text=f"Processing {current}/{total}: {expression[:30]}...")
        window.progress_bar['value'] = current
        window.update()
    
    def show_batch_summary(self):
        """Show batch processing summary"""
        if not self.batch_results:
            return
        
        accepted = sum(1 for r in self.batch_results if r['status'] == 'ACCEPTED')
        rejected = len(self.batch_results) - accepted
        
        summary = f"BATCH PROCESSING COMPLETE\n"
        summary += "=" * 70 + "\n\n"
        summary += f"Total expressions: {len(self.batch_results)}\n"
        summary += f"Accepted: {accepted} ({accepted/len(self.batch_results)*100:.1f}%)\n"
        summary += f"Rejected: {rejected} ({rejected/len(self.batch_results)*100:.1f}%)\n\n"
        
        summary += "RESULTS:\n"
        summary += "-" * 70 + "\n"
        
        for i, result in enumerate(self.batch_results, 1):
            status_icon = "✓" if result['status'] == 'ACCEPTED' else "✗"
            summary += f"{i:2d}. {status_icon} '{result['expression']}'"
            
            if result['status'] == 'ACCEPTED' and result.get('result') is not None:
                summary += f" = {result['result']}"
            elif result.get('error'):
                summary += f" - {result['error'][:50]}"
            
            summary += "\n"
        
        self.update_text_widget(self.summary_text, summary)
        self.notebook.select(0)
        
        messagebox.showinfo("Batch Processing Complete",
                          f"Processed {len(self.batch_results)} expressions\n"
                          f"Accepted: {accepted}\nRejected: {rejected}")
    
    def export_results(self):
        """Export current or batch results"""
        if not self.batch_results and not self.current_expression:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        format_window = tk.Toplevel(self.root)
        format_window.title("Export Results")
        format_window.geometry("300x200")
        format_window.configure(bg=self.colors['bg'])
        
        tk.Label(
            format_window,
            text="Select Export Format",
            font=self.fonts['subtitle'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        format_var = tk.StringVar(value='txt')
        
        for fmt, label in [('txt', 'Text File (.txt)'), 
                          ('csv', 'CSV File (.csv)'), 
                          ('json', 'JSON File (.json)')]:
            tk.Radiobutton(
                format_window,
                text=label,
                variable=format_var,
                value=fmt,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['primary']
            ).pack(anchor=tk.W, padx=40)
        
        def do_export():
            fmt = format_var.get()
            format_window.destroy()
            
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{fmt}",
                filetypes=[(f"{fmt.upper()} files", f"*.{fmt}"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    results = self.batch_results if self.batch_results else [
                        self.process_single_expression(self.current_expression)
                    ]
                    
                    self.file_handler.export_results(results, filename, fmt)
                    messagebox.showinfo("Success", f"Results exported to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed:\n{str(e)}")
        
        tk.Button(
            format_window,
            text="Export",
            command=do_export,
            bg=self.colors['accent2'],
            fg=self.colors['bg'] if self.is_dark_mode else "white",
            font=self.fonts['normal'],
            relief='flat',
            padx=20,
            pady=5
        ).pack(pady=20)
    
    def create_sample_file(self):
        """Create sample input file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="sample_expressions.txt"
        )
        
        if filename:
            try:
                self.file_handler.create_sample_input_file(filename)
                messagebox.showinfo("Success", 
                                  f"Sample file created: {filename}\n"
                                  "You can now open this file for batch processing.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create sample file:\n{str(e)}")
    
    # VISUALIZATION METHODS
    
    def show_graphical_tree(self):
        """Show graphical parse tree"""
        if not self.current_parse_tree:
            messagebox.showwarning("Warning", "No parse tree available!\nAnalyze an expression first.")
            return
        
        try:
            TreeVisualizerWindow(self.root, self.current_parse_tree, self.current_expression)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display tree:\n{str(e)}")
    
    def show_history(self):
        """Show expression history"""
        if not self.expression_history:
            messagebox.showinfo("History", "No expressions in history yet!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Expression History")
        history_window.geometry("600x400")
        history_window.configure(bg=self.colors['bg'])
        
        tk.Label(
            history_window,
            text="Expression History",
            font=self.fonts['subtitle'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        frame = tk.Frame(history_window, bg=self.colors['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=self.fonts['code'],
            selectbackground=self.colors['accent']
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for entry in reversed(self.expression_history):
            status = "✓" if entry['accepted'] else "✗"
            result = f" = {entry['result']}" if entry.get('result') is not None else ""
            listbox.insert(tk.END, f"{status} {entry['expression']}{result} ({entry['timestamp']})")
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                index = len(self.expression_history) - 1 - selection[0]
                expr = self.expression_history[index]['expression']
                self.input_var.set(expr)
                history_window.destroy()
                self.analyze_expression()
        
        tk.Button(
            history_window,
            text="Load Selected",
            command=load_selected,
            bg=self.colors['accent2'],
            fg="white",
            font=self.fonts['normal'],
            relief='flat',
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def add_to_history(self, expression, accepted, result=None, error=None):
        """Add expression to history"""
        self.expression_history.append({
            'expression': expression,
            'accepted': accepted,
            'result': result,
            'error': error,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        if len(self.expression_history) > 50:
            self.expression_history = self.expression_history[-50:]
    
    # HELP METHODS
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
ENHANCED LEXICAL ANALYZER & PARSER
Version 2.0

Features:
• Lexical Analysis with error detection
• Top-Down Recursive Descent Parsing
• Symbol Table Management
• Parse Tree Construction & Visualization
• Expression Evaluation
• File Input/Output
• Batch Processing
• Graphical Tree Display
• Expression History
• Dark/Light Theme Toggle

Grammar:
E  → TE'
E' → +TE' | ε
T  → FT'
T' → *FT' | ε
F  → (E) | id
id → 0-9, a-z, A-Z

Developed for Compiler Design Course
        """
        messagebox.showinfo("About", about_text)
    
    def show_grammar(self):
        """Show grammar rules"""
        grammar_text = """
GRAMMAR RULES

Production Rules:
────────────────
E  → TE'
E' → +TE' | ε
T  → FT'
T' → *FT' | ε
F  → (E) | id

Terminals:
──────────
+ : Addition operator
* : Multiplication operator
( : Left parenthesis
) : Right parenthesis
id : Identifier (0-9, a-z, A-Z)

Non-Terminals:
──────────────
E  : Expression
E' : Expression prime (handles addition)
T  : Term
T' : Term prime (handles multiplication)
F  : Factor

Operator Precedence:
────────────────────
* (multiply) has higher precedence than + (plus)
Parentheses override default precedence

Examples:
─────────
Valid:   3+4*5, a+b, (1+2)*3, x
Invalid: 3+, 3**4, (1+2, ), +3
        """
        
        window = tk.Toplevel(self.root)
        window.title("Grammar Rules")
        window.geometry("500x600")
        window.configure(bg=self.colors['bg'])
        
        text = tk.Text(
            window,
            font=self.fonts['code'],
            bg=self.colors['panel'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(1.0, grammar_text)
        text.config(state=tk.DISABLED)


def main():
    """Main function"""
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()