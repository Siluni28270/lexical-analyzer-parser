"""
Lexical Analyzer and Parser - Main Entry Point
Grammar: E → TE', E' → +TE'|ε, T → FT', T' → *FT'|ε, F → (E)|id
"""

import tkinter as tk
from ui.gui import ParserGUI

def main():
    """Main function to start the application"""
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = ParserGUI(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()