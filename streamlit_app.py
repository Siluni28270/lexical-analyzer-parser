"""
Streamlit Web Application for Lexical Analyzer and Parser
Complete working version for deployment
"""

import streamlit as st
from core.lexer import Lexer
from core.parser import Parser
from core.symbol_table import SymbolTable
from utils.errors import ParseError, LexicalError, ParserSyntaxError, SemanticError

# Page configuration
st.set_page_config(
    page_title="Lexical Analyzer & Parser",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #00D9FF;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

def main():
    # Header
    st.markdown('<h1 class="main-header">⚡ LEXICAL ANALYZER & PARSER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Grammar: E → TE\', E\' → +TE\'|ε, T → FT\', T\' → *FT\'|ε, F → (E)|id</p>', unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        expression = st.text_input(
            "Enter Expression:",
            placeholder="e.g., 3+4*5, a+b, (1+2)*3",
            key="input",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Quick test buttons
    st.markdown("**Quick Tests:**")
    cols = st.columns(9)
    
    test_buttons = [
        ("3+4*5", True),
        ("a+b", True),
        ("(1+2)*3", True),
        ("x", True),
        ("3+", False),
        ("3**4", False),
        ("(1+2", False),
        ("+3", False),
        ("CLEAR", None)
    ]
    
    for i, (test, is_valid) in enumerate(test_buttons):
        with cols[i]:
            if test == "CLEAR":
                if st.button(test, key=f"btn_{i}"):
                    st.session_state.history = []
                    st.rerun()
            else:
                if st.button(test, key=f"btn_{i}"):
                    st.session_state.input = test
                    expression = test
                    analyze_btn = True
    
    st.divider()
    
    # Analyze expression
    if (analyze_btn or expression) and expression:
        analyze_expression(expression)
    
    # Sidebar - History
    with st.sidebar:
        st.header("📜 History")
        if st.session_state.history:
            for i, item in enumerate(st.session_state.history[:10]):
                status = "✅" if item['valid'] else "❌"
                with st.expander(f"{status} {item['expression']}", expanded=(i==0)):
                    st.write(f"**Status:** {'Valid' if item['valid'] else 'Invalid'}")
                    st.write(f"**Tokens:** {len(item.get('tokens', []))}")
                    if item.get('result'):
                        st.write(f"**Result:** {item['result']}")
                    if st.button(f"Load", key=f"load_{i}"):
                        st.session_state.input = item['expression']
                        st.rerun()
        else:
            st.info("No history yet. Analyze an expression to start!")

def analyze_expression(expression):
    """Analyze the expression and display results"""
    try:
        # Initialize components
        lexer = Lexer()
        parser = Parser()
        symbol_table = SymbolTable()
        
        # Lexical Analysis
        with st.spinner("Analyzing..."):
            tokens = lexer.tokenize(expression)
            
            # Build Symbol Table
            for token in tokens:
                symbol_table.add_token(token)
            
            # Parse
            is_valid = parser.parse(tokens)
            
            # Get evaluation result
            eval_result = parser.get_evaluation_result() if hasattr(parser, 'get_evaluation_result') else None
        
        # Add to history
        st.session_state.history.insert(0, {
            'expression': expression,
            'valid': is_valid,
            'tokens': tokens,
            'result': eval_result
        })
        
        # Display Results
        if is_valid:
            result_text = f" = {eval_result}" if eval_result is not None else ""
            st.markdown(f'<div class="success-box"><h2>✅ VALID EXPRESSION</h2><p>Expression "{expression}"{result_text} is syntactically correct!</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box"><h2>❌ INVALID EXPRESSION</h2><p>Expression "{expression}" contains errors.</p></div>', unsafe_allow_html=True)
        
        # Metrics
        stats = symbol_table.get_statistics()
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Status", "✅ Valid" if is_valid else "❌ Invalid")
        col2.metric("Total Tokens", len(tokens))
        col3.metric("Unique Tokens", stats['unique_tokens'])
        col4.metric("Operators", stats['operator_count'])
        
        # Tabs for detailed results
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary", 
            "🔤 Lexical Analysis", 
            "📊 Symbol Table", 
            "🌳 Parse Tree", 
            "⚠️ Errors"
        ])
        
        with tab1:
            st.subheader("Analysis Summary")
            st.write(f"**Input Expression:** `{expression}`")
            st.write(f"**Result:** {'ACCEPTED ✓' if is_valid else 'REJECTED ✗'}")
            if eval_result is not None:
                st.write(f"**Evaluated Result:** `{eval_result}`")
            st.write(f"**Total Tokens:** {len(tokens)}")
            st.write(f"**Unique Tokens:** {stats['unique_tokens']}")
            
            st.write("**Grammar Rules:**")
            st.code("""E  → TE'
E' → +TE' | ε
T  → FT'
T' → *FT' | ε
F  → (E) | id""", language="text")
        
        with tab2:
            st.subheader("Token Analysis")
            if tokens:
                st.write(f"**Found {len(tokens)} tokens:**")
                for i, token in enumerate(tokens, 1):
                    st.text(f"{i}. {token}")
            else:
                st.warning("No tokens found.")
        
        with tab3:
            st.subheader("Symbol Table")
            st.code(symbol_table.get_formatted_table(), language="text")
        
        with tab4:
            st.subheader("Parse Tree")
            if hasattr(parser, 'get_parse_tree'):
                st.code(parser.get_parse_tree(), language="text")
            else:
                st.info("Parse tree not available.")
        
        with tab5:
            st.subheader("Error Details")
            if hasattr(parser, 'errors') and parser.errors:
                for error in parser.errors:
                    st.error(error)
            elif not is_valid:
                st.error("Expression is invalid but no specific error details available.")
            else:
                st.success("No errors found! Expression is valid.")
    
    except (ParseError, LexicalError, ParserSyntaxError, SemanticError) as e:
        st.error(f"**Error during analysis:** {e.message if hasattr(e, 'message') else str(e)}")
        
        # Add to history as failed
        st.session_state.history.insert(0, {
            'expression': expression,
            'valid': False,
            'tokens': [],
            'error': str(e)
        })
        
    except Exception as e:
        st.error(f"**Unexpected error:** {str(e)}")
        st.exception(e)

# Footer
st.divider()
st.markdown("""
<p style='text-align: center; color: #888; font-size: 0.9rem;'>
    Created for Educational Purposes | Lexical Analyzer & Parser Project
</p>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
