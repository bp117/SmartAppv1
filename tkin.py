import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import json
import fitz  # PyMuPDF for handling PDF files
from datetime import datetime

class PDFValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('PDF and JSON Validator')
        self.root.geometry('900x600')

        # Directory selection UI
        ttk.Label(root, text="PDF Directory:").grid(row=0, column=0, padx=10, pady=10)
        self.pdf_dir = tk.StringVar()
        ttk.Entry(root, textvariable=self.pdf_dir, width=70).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(root, text="Browse", command=lambda: self.load_directory(self.pdf_dir)).grid(row=0, column=2)

        ttk.Label(root, text="JSON Directory:").grid(row=1, column=0, padx=10, pady=10)
        self.json_dir = tk.StringVar()
        ttk.Entry(root, textvariable=self.json_dir, width=70).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(root, text="Browse", command=lambda: self.load_directory(self.json_dir)).grid(row=1, column=2)

        # Frame for Treeview
        frame = ttk.Frame(root)
        frame.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # Scrollbars for Treeview
        tree_scroll_x = ttk.Scrollbar(frame, orient="horizontal")
        tree_scroll_x.pack(side='bottom', fill='x')
        tree_scroll_y = ttk.Scrollbar(frame, orient="vertical")
        tree_scroll_y.pack(side='right', fill='y')

        # Treeview Widget
        self.tree = ttk.Treeview(frame, columns=("File", "Is PDF Tampered", "Is Spans Tampered"), xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)
        self.tree.heading("File", text="File")
        self.tree.heading("Is PDF Tampered", text="Is PDF Tampered")
        self.tree.heading("Is Spans Tampered", text="Is Spans Tampered")
        self.tree['show'] = 'headings'
        self.tree.pack(expand=True, fill='both')

        tree_scroll_x.config(command=self.tree.xview)
        tree_scroll_y.config(command=self.tree.yview)

        # Button to start validation
        ttk.Button(root, text="Start Validation", command=self.start_validation).grid(row=3, column=1, pady=10)

    def load_directory(self, directory_var):
        directory = filedialog.askdirectory()
        if directory:
            directory_var.set(directory)

    def start_validation(self):
        pdf_dir = self.pdf_dir.get()
        json_dir = self.json_dir.get()

        if not pdf_dir or not json_dir:
            messagebox.showerror("Error", "Please select both directories")
            return

        if not os.path.exists(pdf_dir) or not os.path.exists(json_dir):
            messagebox.showerror("Error", "One or both directories do not exist")
            return

        self.validate_files(pdf_dir, json_dir)

    def validate_files(self, pdf_dir, json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(json_dir, filename)
                pdf_filename = filename.replace('.json', '.pdf')
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                if os.path.exists(pdf_path):
                    tampered_pdf, tampered_spans = self.check_pdf(pdf_path)
                    self.tree.insert("", "end", values=(pdf_filename, "Yes" if tampered_pdf else "No", "Yes" if tampered_spans else "No"))

    def check_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        trailer = doc.pdf_trailer()

        tampered_pdf = self.check_pdf_tampering(metadata, trailer)
        tampered_spans = False  # Placeholder, integrate spans validation logic

        return tampered_pdf, tampered_spans

    def check_pdf_tampering(self, metadata, trailer):
        mod_date_str = metadata.get("modDate", "").replace('D:', '')[:14]
        creation_date_str = metadata.get("creationDate", "").replace('D:', '')[:14]

        try:
            mod_date = datetime.strptime(mod_date_str, "%Y%m%d%H%M%S")
            creation_date = datetime.strptime(creation_date_str, "%Y%m%d%H%M%S")
            if mod_date != creation_date:
                return True
        except ValueError:
            return False

        if "/Index" in str(trailer) or "/XRefStm" in str(trailer):
            return True

        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFValidatorApp(root)
    root.mainloop()
