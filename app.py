from llm_prompting_gen.generators import PromptEngineeringGenerator
from llm_prompting_gen.models.prompt_engineering import PromptElements
from langchain_community.chat_models import ChatOpenAI
import logging
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import pandas as pd
import os

class PDFExtractorApp:
    def __init__(self, root):
        self.root = root
        self.initialize_ui()

    def initialize_ui(self):
        self.root.title("PDF Extractor")
        self.root.geometry("400x200")
        upload_button = tk.Button(self.root, text="Upload PDF", command=self.upload_pdf)
        upload_button.pack(pady=20)
        self.keywords_entry = tk.Entry(self.root)
        self.keywords_entry.pack(pady=10)
        extract_button = tk.Button(self.root, text="Extract Data", command=self.extract_data)
        extract_button.pack(pady=10)

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            tk.messagebox.showinfo("PDF Upload", "PDF successfully uploaded.")

    def extract_data(self):
        keywords = self.keywords_entry.get().split(',')
        if not hasattr(self, 'pdf_path'):
            tk.messagebox.showerror("Error", "Please upload a PDF first.")
            return
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except PyPDF2.errors.PdfReadError as e:
            tk.messagebox.showerror("PDF Error", "Failed to read the PDF file. It might be corrupted or not in a supported format.")
            logging.error(f"PDF read error: {e}")
            return
        # Extracting important lines based on multiple keywords
        if keywords:
            data = {'Keyword': [], 'Important Lines': []}
            found_keywords = set()
            for keyword in keywords:
                for line in text.split('\n'):
                    if keyword.lower() in line.lower():
                        data['Keyword'].append(keyword)
                        data['Important Lines'].append(line)
                if keyword:
                    found_keywords.add(keyword)
            # Display all found keywords
            if found_keywords:
                tk.messagebox.showinfo("Keywords Found", "Keywords found in the PDF: " + ", ".join(found_keywords))
            else:
                tk.messagebox.showinfo("No Keywords Found", "No keywords were found in the PDF.")
            if data['Important Lines']:
                self.save_data_to_excel(data)
            else:
                tk.messagebox.showinfo("No Matches", "No important lines found based on the provided keywords.")
        else:
            # Generate summary using ChatOpenAI
            summary = self.generate_summary(text)
            tk.messagebox.showinfo("PDF Summary", summary)

    def generate_summary(self, text):
        # Initialize the ChatOpenAI model
        chat_model = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0.7)
        # Generate the summary
        summary = chat_model(text)
        return summary

    def save_data_to_excel(self, data):
        # Creating a DataFrame with each keyword and its corresponding lines in separate rows
        df = pd.DataFrame(data)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = os.path.join(desktop_path, 'extracted_data.xlsx')
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracted Data')
                workbook = writer.book
                worksheet = writer.sheets['Extracted Data']
                for col in worksheet.columns:
                    max_length = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column].width = adjusted_width
            tk.messagebox.showinfo("Success", f"Data extracted and saved to {filename}.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save data to Excel. Error: {e}")
            logging.error(f"Failed to save data to Excel. Error: {e}")
def initialize():
    root = tk.Tk()
    app = PDFExtractorApp(root)
    root.mainloop()
