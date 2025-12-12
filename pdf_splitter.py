#!/usr/bin/env python3
"""
Módulo para dividir arquivos PDF em tamanhos menores.
"""

import os
from typing import List
from PyPDF2 import PdfReader, PdfWriter


class PDFSplitter:
    """Classe para dividir arquivos PDF em partes menores."""
    
    def __init__(self, input_pdf: str):
        """
        Inicializa o divisor de PDF.
        
        Args:
            input_pdf: Caminho para o arquivo PDF de entrada
        """
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_pdf}")
        
        self.input_pdf = input_pdf
        self.reader = PdfReader(input_pdf)
        self.total_pages = len(self.reader.pages)
    
    def split_by_pages(self, pages_per_file: int, output_dir: str = "output") -> List[str]:
        """
        Divide o PDF em arquivos menores por número de páginas.
        
        Args:
            pages_per_file: Número de páginas por arquivo
            output_dir: Diretório de saída para os arquivos divididos
        
        Returns:
            Lista com os caminhos dos arquivos criados
        """
        if pages_per_file <= 0:
            raise ValueError("Número de páginas por arquivo deve ser maior que zero")
        
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        created_files = []
        base_name = os.path.splitext(os.path.basename(self.input_pdf))[0]
        
        # Calcula número de arquivos necessários
        num_files = (self.total_pages + pages_per_file - 1) // pages_per_file
        
        for i in range(num_files):
            writer = PdfWriter()
            start_page = i * pages_per_file
            end_page = min((i + 1) * pages_per_file, self.total_pages)
            
            # Adiciona páginas ao novo PDF
            for page_num in range(start_page, end_page):
                writer.add_page(self.reader.pages[page_num])
            
            # Salva o arquivo
            output_file = os.path.join(
                output_dir, 
                f"{base_name}_parte_{i+1:03d}_paginas_{start_page+1}-{end_page}.pdf"
            )
            
            with open(output_file, 'wb') as output:
                writer.write(output)
            
            created_files.append(output_file)
            print(f"Criado: {output_file} ({end_page - start_page} páginas)")
        
        return created_files
    
    def split_by_size(self, max_size_mb: float, output_dir: str = "output") -> List[str]:
        """
        Divide o PDF em arquivos menores por tamanho máximo.
        
        Args:
            max_size_mb: Tamanho máximo em MB para cada arquivo
            output_dir: Diretório de saída para os arquivos divididos
        
        Returns:
            Lista com os caminhos dos arquivos criados
        """
        if max_size_mb <= 0:
            raise ValueError("Tamanho máximo deve ser maior que zero")
        
        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        created_files = []
        base_name = os.path.splitext(os.path.basename(self.input_pdf))[0]
        max_size_bytes = max_size_mb * 1024 * 1024
        
        file_num = 1
        current_writer = PdfWriter()
        current_start_page = 0
        current_page = 0
        
        while current_page < self.total_pages:
            # Adiciona página ao writer atual
            current_writer.add_page(self.reader.pages[current_page])
            current_page += 1
            
            # Verifica o tamanho temporário
            temp_file = os.path.join(output_dir, f"temp_{file_num}.pdf")
            with open(temp_file, 'wb') as temp:
                current_writer.write(temp)
            
            temp_size = os.path.getsize(temp_file)
            
            # Se excedeu o tamanho ou é a última página
            if temp_size > max_size_bytes or current_page == self.total_pages:
                # Se excedeu e tem mais de uma página, remove a última e salva
                if temp_size > max_size_bytes and current_page - current_start_page > 1:
                    current_page -= 1
                    current_writer = PdfWriter()
                    for page_num in range(current_start_page, current_page):
                        current_writer.add_page(self.reader.pages[page_num])
                
                # Salva o arquivo final
                output_file = os.path.join(
                    output_dir,
                    f"{base_name}_parte_{file_num:03d}_paginas_{current_start_page+1}-{current_page}.pdf"
                )
                
                with open(output_file, 'wb') as output:
                    current_writer.write(output)
                
                file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                created_files.append(output_file)
                print(f"Criado: {output_file} ({current_page - current_start_page} páginas, {file_size_mb:.2f} MB)")
                
                # Limpa arquivo temporário
                os.remove(temp_file)
                
                # Reinicia para o próximo arquivo
                file_num += 1
                current_writer = PdfWriter()
                current_start_page = current_page
            else:
                # Remove arquivo temporário
                os.remove(temp_file)
        
        return created_files
    
    def get_info(self) -> dict:
        """
        Retorna informações sobre o PDF.
        
        Returns:
            Dicionário com informações do PDF
        """
        file_size = os.path.getsize(self.input_pdf)
        file_size_mb = file_size / (1024 * 1024)
        
        return {
            'arquivo': self.input_pdf,
            'total_paginas': self.total_pages,
            'tamanho_bytes': file_size,
            'tamanho_mb': round(file_size_mb, 2)
        }


def main():
    """Função principal para teste."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python pdf_splitter.py <arquivo.pdf>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    splitter = PDFSplitter(pdf_file)
    
    # Mostra informações
    info = splitter.get_info()
    print(f"\nInformações do PDF:")
    print(f"  Arquivo: {info['arquivo']}")
    print(f"  Total de páginas: {info['total_paginas']}")
    print(f"  Tamanho: {info['tamanho_mb']} MB")
    
    # Divide por páginas (exemplo: 50 páginas por arquivo)
    print(f"\nDividindo em arquivos de 50 páginas cada...")
    files = splitter.split_by_pages(50)
    print(f"\nTotal de arquivos criados: {len(files)}")


if __name__ == '__main__':
    main()
