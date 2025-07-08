import tkinter as tk
from tkinter import ttk, scrolledtext
import pandas as pd
import csv

class ChessViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Move Analysis Viewer")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create moves frame
        self.moves_frame = ttk.LabelFrame(self.main_frame, text="Moves")
        self.moves_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Create moves list with specific size
        self.moves_list = tk.Listbox(self.moves_frame, width=30, height=20)
        self.moves_list.pack(side='left', fill='both', expand=True)
        
        # Create scrollbar
        self.moves_scroll = ttk.Scrollbar(self.moves_frame, orient='vertical', command=self.moves_list.yview)
        self.moves_scroll.pack(side='right', fill='y')
        self.moves_list.configure(yscrollcommand=self.moves_scroll.set)
        
        # Create details frame
        self.details_frame = ttk.LabelFrame(self.main_frame, text="Move Details")
        self.details_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Create text widget for move details
        self.details_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, width=40, height=20)
        self.details_text.pack(fill='both', expand=True)
        
        # Bind selection event
        self.moves_list.bind('<<ListboxSelect>>', self.show_move_details)
        
        # Add file loading button
        self.load_button = ttk.Button(root, text="Load CSV File", command=self.load_file)
        self.load_button.pack(pady=5)
        
        self.data = None
        # Store move type information
        self.move_types = {}  # Will store 'white' or 'black' for each index

    def load_file(self):
        try:
            self.data = pd.read_csv('R3.csv')
            self.moves_list.delete(0, tk.END)
            self.move_types.clear()  # Clear previous move types
            
            # Get played moves for display in the list
            played_moves = self.data[self.data['is_played'] == 1].copy()
            
            # Group by movenumber to get white and black moves
            current_index = 0
            for movenumber in played_moves['movenumber'].unique():
                moves = played_moves[played_moves['movenumber'] == movenumber]
                
                # Get white (.) and black (...) moves
                white_moves = moves[moves['white_or_black'] == '.']
                black_moves = moves[moves['white_or_black'] == '...']
                
                white_move = white_moves['prediction'].iloc[0] if not white_moves.empty else "..."
                black_move = black_moves['prediction'].iloc[0] if not black_moves.empty else "..."
                
                # Add white move
                white_text = f"{movenumber}. {white_move}"
                self.moves_list.insert(tk.END, white_text)
                self.move_types[current_index] = 'white'
                current_index += 1
                
                # Add black move if it exists
                if black_move != "...":
                    black_text = f"{movenumber}... {black_move}"
                    self.moves_list.insert(tk.END, black_text)
                    self.move_types[current_index] = 'black'
                    current_index += 1
                
        except Exception as e:
            print(f"Error in load_file: {str(e)}")
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error loading file: {str(e)}")

    def show_move_details(self, event):
        if not self.moves_list.curselection():
            return
            
        selection = self.moves_list.curselection()[0]
        selected_text = self.moves_list.get(selection)
        
        try:
            # Get move type from stored dictionary
            is_black = self.move_types[selection] == 'black'
            movenumber = int(selected_text.split('.')[0])
            
            # Clear previous details
            self.details_text.delete(1.0, tk.END)
            
            # Get all moves for this movenumber and color
            color_marker = '...' if is_black else '.'
            moves_data = self.data[
                (self.data['movenumber'] == movenumber) & 
                (self.data['white_or_black'] == color_marker)
            ].sort_values(by='new_norm_prob', ascending=False)
            
            # Create table headers
            color_name = "Black" if is_black else "White"
            self.details_text.insert(tk.END, f"Move {movenumber} {color_name}\n\n")
            
            headers = ["#", "Move", "Likelihood", "Evaluation"]
            header_line = f"{headers[0]:<3} {headers[1]:<15} {headers[2]:<12} {headers[3]:<12}\n"
            self.details_text.insert(tk.END, header_line)
            self.details_text.insert(tk.END, "-" * 45 + "\n")
            
            # Add each move to the table
            for idx, move in enumerate(moves_data.itertuples(), 1):
                move_text = f"{move.prediction}"
                likelihood = f"{move.new_norm_prob:.2f}%"
                evaluation = f"{move.win_percentage:.2f}%"
                
                # Add a marker (*) for the played move
                if move.is_played == 1:
                    move_text = f"{move_text} *"
                
                row = f"#{idx:<2} {move_text:<15} {likelihood:<12} {evaluation:<12}\n"
                self.details_text.insert(tk.END, row)
                
        except Exception as e:
            print(f"Error in show_move_details: {str(e)}")
            import traceback
            traceback.print_exc()
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error showing move details: {str(e)}")

def main():
    root = tk.Tk()
    app = ChessViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
