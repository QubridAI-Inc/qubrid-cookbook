from fpdf import FPDF
import datetime
from typing import List, Dict, Any

class SchedulePDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(154, 27, 116) # Brand Color #9a1b74
        self.cell(0, 10, 'Personalized Medication Schedule', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150)
        self.multi_cell(0, 5, 'DISCLAIMER: This schedule is AI-generated based on a prescription image. It is NOT a medical prescription or professional advice. Always verify with your doctor or pharmacist before taking medication.', 0, 'C')
        self.set_y(-10)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_schedule_pdf(schedule_data: List[Dict[str, Any]]) -> bytes:
    """
    Generates a PDF bytes object from schedule data.
    """
    pdf = SchedulePDF()
    pdf.add_page()
    
    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    col_widths = [50, 30, 20, 20, 20, 30]
    headers = ['Medicine', 'Dosage', 'Morn.', 'Aft.', 'Night', 'Duration']
    
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], 1, 0, 'C', fill=True)
    pdf.ln()
    
    # Table Content
    pdf.set_font('helvetica', '', 9)
    for item in schedule_data:
        # Medicine + Instructions (Multi-line handle)
        med_text = f"{item.get('medicine')}\n({item.get('instructions', 'N/A')})"
        
        # Calculate height needed
        lines = len(med_text.split('\n'))
        h = 10 * lines if lines > 1 else 10
        
        x = pdf.get_x()
        y = pdf.get_y()
        
        pdf.multi_cell(col_widths[0], 10 if lines == 1 else 5, med_text, 1, 'L')
        pdf.set_xy(x + col_widths[0], y)
        
        pdf.cell(col_widths[1], h, str(item.get('dosage')), 1, 0, 'C')
        pdf.cell(col_widths[2], h, 'Yes' if item.get('morning') else '-', 1, 0, 'C')
        pdf.cell(col_widths[3], h, 'Yes' if item.get('afternoon') else '-', 1, 0, 'C')
        pdf.cell(col_widths[4], h, 'Yes' if item.get('night') else '-', 1, 0, 'C')
        pdf.cell(col_widths[5], h, f"{item.get('duration_days')} days", 1, 1, 'C')
    
    return bytes(pdf.output())
