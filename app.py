"""
Streamlit Web Application for Lexical Analyzer and Parser
"""

import streamlit as st
from core.lexer import Lexer
from core.parser import Parser
from core.symbol_table import SymbolTable
from utils.errors import ParseError, LexicalError, SyntaxError, SemanticError

# Page configuration
st.set_page_config(
    page_title="Lexical Analyzer & Parser",
    page_icon="⚡",
    layout="wide"
)

# Initialize session state
if 'lexer' not in st.session_state:
    st.session_state.lexer = Lexer()
if 'parser' not in st.session_state:
    st.session_state.parser = Parser()
if 'symbol_table' not in st.session_state:
    st.session_state.symbol_table = SymbolTable()

def main():
    # Header
    st.title("⚡ LEXICAL ANALYZER & PARSER")
    st.markdown("---")
    
    # Input section
    st.subheader("📝 Enter Expression")
    expression = st.text_input("", placeholder="e.g., 3+4*5 or a+b")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyze = st.button("🔍 Analyze", type="primary")
    with col2:
        clear = st.button("🗑 Clear")
    
    if clear:
        st.rerun()
    
    # Quick test buttons
    st.markdown("### 🧪 Quick Tests")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("3+4*5"):
            expression = "3+4*5"
            analyze = True
    with col2:
        if st.button("a+b"):
            expression = "a+b"
            analyze = True
    with col3:
        if st.button("(1+2)*3"):
            expression = "(1+2)*3"
            analyze = True
    with col4:
        if st.button("3+ (Error)"):
            expression = "3+"
            analyze = True
    with col5:
        if st.button("3**4 (Error)"):
            expression = "3**4"
            analyze = True
    
    # Analysis
    if analyze and expression:
        analyze_expression(expression)

def analyze_expression(expression):
    try:
        # Lexical Analysis
        with st.spinner("Analyzing..."):
            tokens = st.session_state.lexer.tokenize(expression)
            
            # Build Symbol Table
            st.session_state.symbol_table.clear()
            for token in tokens:
                st.session_state.symbol_table.add_token(token)
            
            # Parse
            parse_success = st.session_state.parser.parse(tokens)
        
        # Results
        if parse_success:
            st.success(f"✅ ACCEPTED: '{expression}' is valid!")
        else:
            st.error(f"❌ REJECTED: '{expression}' is invalid!")
        
        # Stats
        stats = st.session_state.symbol_table.get_statistics()
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Tokens", len(tokens))
        col2.metric("Identifiers", stats['identifier_count'])
        col3.metric("Operators", stats['operator_count'])
        col4.metric("Unique Tokens", stats['unique_tokens'])
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🔤 Tokens", "📊 Symbol Table", "🌳 Parse Tree"])
        
        with tab1:
            st.text(f"Expression: '{expression}'")
            st.text(f"Result: {'ACCEPTED ✓' if parse_success else 'REJECTED ✗'}")
            st.text(f"Total Tokens: {len(tokens)}")
        
        with tab2:
            for i, token in enumerate(tokens, 1):
                st.text(f"{i}. {token}")
        
        with tab3:
            st.code(st.session_state.symbol_table.get_formatted_table())
        
        with tab4:
            st.code(st.session_state.parser.get_parse_tree())
    
    except (ParseError, LexicalError, SyntaxError, SemanticError) as e:
        st.error(f"❌ Error: {e.message}")
        with st.expander("See details"):
            st.code(e.get_detailed_message())
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

if _name_ == "_main_":
    main()