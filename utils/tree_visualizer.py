"""
Graphical Parse Tree Visualizer using Tkinter Canvas
Creates visual representation of parse trees
"""

import tkinter as tk
from tkinter import ttk

class TreeVisualizer:
    """Visualizes parse trees graphically using Tkinter Canvas"""
    
    def __init__(self, parent, width=800, height=600):
        """
        Initialize tree visualizer
        
        Args:
            parent: Parent widget
            width: Canvas width
            height: Canvas height
        """
        self.parent = parent
        self.width = width
        self.height = height
        
        # Visual settings
        self.node_radius = 25
        self.node_color = '#0f3460'
        self.node_border = '#00d4ff'
        self.text_color = '#eaeaea'
        self.line_color = '#2d3561'
        self.terminal_color = '#e94560'
        self.epsilon_color = '#ffa502'
        
        self.horizontal_spacing = 80
        self.vertical_spacing = 100
        
        # Node positions cache
        self.node_positions = {}
        
        # Create canvas
        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
    
    def draw_tree(self, root_node):
        """
        Draw the parse tree
        
        Args:
            root_node: Root node of parse tree
        """
        # Clear canvas
        self.canvas.delete('all')
        self.node_positions.clear()
        
        if not root_node:
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="No parse tree to display",
                fill=self.text_color,
                font=('Segoe UI', 12)
            )
            return
        
        # Calculate tree layout
        self._calculate_positions(root_node)
        
        # Draw edges first (so they appear behind nodes)
        self._draw_edges(root_node)
        
        # Draw nodes
        self._draw_nodes(root_node)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _calculate_positions(self, node, depth=0, left_bound=0):
        """
        Calculate positions for all nodes using a compact tree layout
        
        Args:
            node: Current node
            depth: Current depth in tree
            left_bound: Left boundary for positioning
            
        Returns:
            tuple: (left_extent, right_extent)
        """
        if not node:
            return left_bound, left_bound
        
        y = 50 + depth * self.vertical_spacing
        
        if not node.children:
            # Leaf node
            x = left_bound + self.horizontal_spacing
            self.node_positions[id(node)] = (x, y)
            return left_bound, x
        
        # Process children
        current_left = left_bound
        children_positions = []
        
        for child in node.children:
            child_left, child_right = self._calculate_positions(child, depth + 1, current_left)
            children_positions.append((child_left, child_right))
            current_left = child_right
        
        # Position this node centered over its children
        if children_positions:
            first_child_x = self.node_positions[id(node.children[0])][0]
            last_child_x = self.node_positions[id(node.children[-1])][0]
            x = (first_child_x + last_child_x) // 2
        else:
            x = left_bound + self.horizontal_spacing
        
        self.node_positions[id(node)] = (x, y)
        
        return left_bound, current_left
    
    def _draw_edges(self, node):
        """Draw edges connecting nodes"""
        if not node or id(node) not in self.node_positions:
            return
        
        parent_x, parent_y = self.node_positions[id(node)]
        
        for child in node.children:
            if id(child) in self.node_positions:
                child_x, child_y = self.node_positions[id(child)]
                
                # Draw line from parent to child
                self.canvas.create_line(
                    parent_x, parent_y + self.node_radius,
                    child_x, child_y - self.node_radius,
                    fill=self.line_color,
                    width=2,
                    smooth=True
                )
                
                # Recursively draw edges for children
                self._draw_edges(child)
    
    def _draw_nodes(self, node):
        """Draw all nodes"""
        if not node or id(node) not in self.node_positions:
            return
        
        x, y = self.node_positions[id(node)]
        
        # Determine node color
        if node.token:
            # Terminal node
            if node.rule == 'id':
                color = self.terminal_color
            else:
                color = self.node_color
        elif not node.children:
            # Epsilon node
            color = self.epsilon_color
        else:
            # Non-terminal node
            color = self.node_color
        
        # Draw node circle
        self.canvas.create_oval(
            x - self.node_radius, y - self.node_radius,
            x + self.node_radius, y + self.node_radius,
            fill=color,
            outline=self.node_border,
            width=2
        )
        
        # Draw node label
        if node.token:
            label = node.token.value
        elif not node.children:
            label = 'ε'
        else:
            label = node.rule
        
        self.canvas.create_text(
            x, y,
            text=label,
            fill=self.text_color,
            font=('Consolas', 10, 'bold')
        )
        
        # Draw value if available (for evaluation)
        if node.value is not None and not node.token:
            self.canvas.create_text(
                x, y + self.node_radius + 15,
                text=f"= {node.value}",
                fill='#00ff88',
                font=('Consolas', 9)
            )
        
        # Recursively draw child nodes
        for child in node.children:
            self._draw_nodes(child)
    
    def save_as_image(self, filename):
        """
        Save tree as PostScript file (can be converted to image)
        
        Args:
            filename: Output filename
        """
        try:
            # Generate PostScript
            ps = self.canvas.postscript(colormode='color')
            
            # Save to file
            with open(filename, 'w') as f:
                f.write(ps)
            
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def clear(self):
        """Clear the canvas"""
        self.canvas.delete('all')
        self.node_positions.clear()


class TreeVisualizerWindow:
    """Standalone window for tree visualization"""
    
    def __init__(self, parent, parse_tree_root, expression):
        """
        Create tree visualizer window
        
        Args:
            parent: Parent window
            parse_tree_root: Root node of parse tree
            expression: The expression being visualized
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"Parse Tree Visualization - {expression}")
        self.window.geometry("900x700")
        self.window.configure(bg='#1a1a2e')
        
        # Header
        header = tk.Frame(self.window, bg='#0f3460', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text=f"Parse Tree: {expression}",
            font=('Segoe UI', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f3460'
        )
        title.pack(pady=15)
        
        # Canvas frame
        canvas_frame = tk.Frame(self.window, bg='#1a1a2e')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create visualizer
        self.visualizer = TreeVisualizer(canvas_frame, width=880, height=600)
        
        # Draw tree
        self.visualizer.draw_tree(parse_tree_root)
        
        # Button frame
        button_frame = tk.Frame(self.window, bg='#1a1a2e')
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Export button
        export_btn = tk.Button(
            button_frame,
            text="Export as PostScript",
            command=self.export_tree,
            bg='#00d4ff',
            fg='#1a1a2e',
            font=('Segoe UI', 10),
            relief='flat',
            padx=15,
            pady=5
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            bg='#16213e',
            fg='#eaeaea',
            font=('Segoe UI', 10),
            relief='flat',
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Legend
        self.create_legend(canvas_frame)
    
    def create_legend(self, parent):
        """Create legend for tree visualization"""
        legend_frame = tk.Frame(parent, bg='#16213e', padx=10, pady=8)
        legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        tk.Label(
            legend_frame,
            text="Legend:",
            font=('Segoe UI', 9, 'bold'),
            fg='#eaeaea',
            bg='#16213e'
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Non-terminal
        self._add_legend_item(legend_frame, '#0f3460', "Non-terminal")
        
        # Terminal
        self._add_legend_item(legend_frame, '#e94560', "Terminal (id)")
        
        # Epsilon
        self._add_legend_item(legend_frame, '#ffa502', "Epsilon (ε)")
    
    def _add_legend_item(self, parent, color, label):
        """Add legend item"""
        frame = tk.Frame(parent, bg='#16213e')
        frame.pack(side=tk.LEFT, padx=10)
        
        canvas = tk.Canvas(frame, width=20, height=20, bg='#16213e', highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=(0, 5))
        canvas.create_oval(2, 2, 18, 18, fill=color, outline='#00d4ff')
        
        tk.Label(
            frame,
            text=label,
            font=('Segoe UI', 9),
            fg='#a8a8b8',
            bg='#16213e'
        ).pack(side=tk.LEFT)
    
    def export_tree(self):
        """Export tree to file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[("PostScript", "*.ps"), ("All Files", "*.*")]
        )
        
        if filename:
            if self.visualizer.save_as_image(filename):
                from tkinter import messagebox
                messagebox.showinfo("Success", f"Tree saved to {filename}")