#!/usr/bin/env python3
"""
Script para criar um PDF de teste para demonstração.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def create_test_pdf(filename, num_pages=100):
    """
    Cria um PDF de teste com várias páginas.
    
    Args:
        filename: Nome do arquivo a ser criado
        num_pages: Número de páginas a criar
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    for page_num in range(1, num_pages + 1):
        # Título
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1*inch, height - 1*inch, f"Documento de Teste")
        
        # Número da página
        c.setFont("Helvetica-Bold", 36)
        c.drawString(1*inch, height - 2*inch, f"Página {page_num} de {num_pages}")
        
        # Conteúdo de exemplo
        c.setFont("Helvetica", 12)
        y = height - 3*inch
        
        c.drawString(1*inch, y, f"Este é um documento de teste criado para demonstrar")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"o funcionamento do Rodovalho PDF Splitter.")
        y -= 0.5*inch
        
        c.drawString(1*inch, y, f"O PDF Splitter permite:")
        y -= 0.3*inch
        c.drawString(1.5*inch, y, f"• Dividir PDFs por número de páginas")
        y -= 0.3*inch
        c.drawString(1.5*inch, y, f"• Dividir PDFs por tamanho máximo (MB)")
        y -= 0.3*inch
        c.drawString(1.5*inch, y, f"• Visualizar informações do arquivo")
        y -= 0.5*inch
        
        c.drawString(1*inch, y, f"Ideal para protocolar documentos em sistemas jurídicos")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"que têm limites de tamanho de arquivo.")
        
        # Rodapé
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(1*inch, 0.5*inch, f"Rodovalho PDF Splitter - Página {page_num}")
        
        c.showPage()
    
    c.save()
    print(f"PDF de teste criado: {filename}")
    print(f"Total de páginas: {num_pages}")


if __name__ == '__main__':
    create_test_pdf('test_document.pdf', 100)
