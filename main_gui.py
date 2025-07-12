#!/usr/bin/env python3
"""
WeCare247 Churn Prediction GUI Automation
Simple GUI version with a single button to run everything
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
from datetime import datetime
import pathlib

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main automation function
from main import (
    fetch_google_sheet_data, 
    prepare_data, 
    train_models, 
    generate_predictions_file, 
    open_results,
    create_summary_report,
    PREDICTIONS_FILE,
    DATA_DIR
)

class WeCareAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WeCare247 Churn Prediction Automation")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_running = False
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏥 WeCare247 Churn Prediction Automation", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready to run automation", 
                                     font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Automation Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Main run button
        self.run_button = ttk.Button(button_frame, text="🚀 Run Automation", 
                                    command=self.run_automation, 
                                    style='Accent.TButton')
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open results button
        self.open_button = ttk.Button(button_frame, text="📂 Open Results", 
                                     command=self.open_results_folder,
                                     state=tk.DISABLED)
        self.open_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear log button
        self.clear_button = ttk.Button(button_frame, text="🧹 Clear Log", 
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT)
        
        # Configure button style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Initialize log
        self.log_message("🏥 WeCare247 Churn Prediction Automation Ready")
        self.log_message("📅 Click 'Run Automation' to start the process")
        self.log_message("=" * 60)
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def open_results_folder(self):
        """Open the results folder"""
        try:
            open_results()
            self.log_message("✅ Results folder opened")
        except Exception as e:
            self.log_message(f"❌ Error opening results: {e}")
    
    def run_automation_thread(self):
        """Run the automation in a separate thread"""
        try:
            self.is_running = True
            self.run_button.config(state=tk.DISABLED)
            self.progress.start()
            
            # Step 1: Fetch data
            self.update_status("📊 Fetching data from Google Sheets...")
            self.log_message("📊 Step 1: Fetching data from Google Sheets...")
            
            if not fetch_google_sheet_data():
                self.log_message("❌ Failed to fetch data from Google Sheets")
                self.show_error("Failed to fetch data from Google Sheets")
                return
            
            self.log_message("✅ Data fetched successfully")
            
            # Step 2: Prepare data
            self.update_status("🧹 Preparing data...")
            self.log_message("🧹 Step 2: Cleaning and preparing data...")
            
            if not prepare_data():
                self.log_message("❌ Failed to prepare data")
                self.show_error("Failed to prepare data")
                return
            
            self.log_message("✅ Data preparation completed")
            
            # Step 3: Train models
            self.update_status("🚀 Training models...")
            self.log_message("🚀 Step 3: Training prediction models...")
            
            if not train_models():
                self.log_message("❌ Failed to train models")
                self.show_error("Failed to train models")
                return
            
            self.log_message("✅ Models trained successfully")
            
            # Step 4: Generate predictions
            self.update_status("🔮 Generating predictions...")
            self.log_message("🔮 Step 4: Generating predictions...")
            
            if not generate_predictions_file():
                self.log_message("❌ Failed to generate predictions")
                self.show_error("Failed to generate predictions")
                return
            
            self.log_message("✅ Predictions generated successfully")
            
            # Step 5: Create summary
            self.update_status("📝 Creating summary report...")
            self.log_message("📝 Step 5: Creating summary report...")
            
            create_summary_report()
            self.log_message("✅ Summary report created")
            
            # Success
            self.update_status("🎉 Automation completed successfully!")
            self.log_message("=" * 60)
            self.log_message("🎉 AUTOMATION COMPLETED SUCCESSFULLY! 🎉")
            self.log_message(f"📊 Your predictions are ready in: {PREDICTIONS_FILE}")
            self.log_message(f"📁 All files are in: {DATA_DIR}")
            self.log_message("=" * 60)
            
            # Enable open results button
            self.open_button.config(state=tk.NORMAL)
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Automation completed successfully!\n\n"
                              f"Predictions saved to:\n{PREDICTIONS_FILE}\n\n"
                              f"Click 'Open Results' to view the files.")
            
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {e}")
            self.show_error(f"Unexpected error: {e}")
        
        finally:
            self.is_running = False
            self.run_button.config(state=tk.NORMAL)
            self.progress.stop()
            self.update_status("Ready to run automation")
    
    def run_automation(self):
        """Start the automation process"""
        if self.is_running:
            return
        
        # Clear previous log
        self.clear_log()
        self.log_message("🚀 Starting WeCare247 Churn Prediction Automation...")
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.run_automation_thread)
        thread.daemon = True
        thread.start()
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = WeCareAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()