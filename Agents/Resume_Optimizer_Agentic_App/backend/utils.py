"""Utility functions for file processing."""

from pathlib import Path
import PyPDF2
import markdown
import re

# Data directories
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"


def parse_pdf(file_path: Path) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            return "\n\n".join(text_parts)
            
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def parse_text_file(file_path: Path) -> str:
    """
    Read text from .txt or .md file.
    
    Args:
        file_path: Path to text file
        
    Returns:
        File contents
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}")


def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of file
        allowed_extensions: List like ['.pdf', '.txt', '.md']
        
    Returns:
        True if valid, False otherwise
    """
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def save_markdown(content: str, filename: str) -> Path:
    """
    Save resume as markdown file.
    
    Args:
        content: Markdown text
        filename: Base filename (without extension)
        
    Returns:
        Path to saved file
    """
    output_path = OUTPUTS_DIR / f"{filename}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def convert_markdown_to_pdf(content: str, filename: str) -> Path:
    """
    Convert markdown to PDF using ReportLab (pure Python, no system dependencies).
    
    Args:
        content: Markdown text
        filename: Base filename (without extension)
        
    Returns:
        Path to generated PDF, or None if conversion fails
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
    except ImportError:
        raise ImportError(
            "ReportLab not installed. Install with:\n"
            "pip install reportlab\n"
            "Or skip PDF generation and use Markdown download only."
        )
    
    try:
        output_path = OUTPUTS_DIR / f"{filename}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for PDF elements
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#34495e',
            spaceAfter=6,
            spaceBefore=12,
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor='#333333',
        )
        
        # Parse markdown into simple text (basic formatting)
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.2 * inch))
                continue
            
            # Handle headers
            if line.startswith('# '):
                text = line[2:].strip()
                # Remove markdown from headers
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                story.append(Paragraph(text, title_style))
                
            elif line.startswith('## '):
                text = line[3:].strip()
                # Remove markdown from headers
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                story.append(Paragraph(text, heading_style))
                
            elif line.startswith('### '):
                text = line[4:].strip()
                # Remove markdown from headers
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                para_style = ParagraphStyle(
                    'Heading3',
                    parent=heading_style,
                    fontSize=12,
                )
                story.append(Paragraph(text, para_style))
                
            # Handle lists
            elif line.startswith('- ') or line.startswith('* '):
                text = '• ' + line[2:].strip()
                # Remove markdown from list items
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                text = re.sub(r'`(.+?)`', r'\1', text)
                story.append(Paragraph(text, normal_style))
                
            # Handle normal text - strip all markdown
            else:
                # Remove markdown formatting to avoid ReportLab parsing errors
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)  # Remove **bold**
                text = re.sub(r'\*(.+?)\*', r'\1', text)      # Remove *italic*
                text = re.sub(r'`(.+?)`', r'\1', text)        # Remove `code`
                text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Remove [links](url)
                story.append(Paragraph(text, normal_style))
        
        # Build PDF
        doc.build(story)
        
        return output_path
        
    except Exception as e:
        # Return None on failure - PDF is optional
        print(f"PDF generation failed: {str(e)}")
        return None