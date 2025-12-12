#!/usr/bin/env python3
"""
Interface de linha de comando para o divisor de PDF.
Desenvolvido por Calleva | RM SOFTWARES E TREINAMENTOS LTDA
Cliente: RODOVALHO ADVOGADOS
"""

import argparse
import sys
from pdf_splitter import PDFSplitter


BANNER = """
╔═══════════════════════════════════════════════════════════════════════╗
║              ⚖️  RODOVALHO PDF SPLITTER  ⚖️                           ║
║                     RODOVALHO ADVOGADOS                               ║
║─────────────────────────────────────────────────────────────────────║
║           Desenvolvido por CALLEVA                                    ║
╚═══════════════════════════════════════════════════════════════════════╝
"""


def main():
    parser = argparse.ArgumentParser(
        description='Dividir arquivos PDF em tamanhos menores - RODOVALHO ADVOGADOS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Dividir por número de páginas (50 páginas por arquivo)
  python cli.py arquivo.pdf -p 50
  
  # Dividir por tamanho máximo (5 MB por arquivo)
  python cli.py arquivo.pdf -s 5
  
  # Especificar diretório de saída
  python cli.py arquivo.pdf -p 50 -o meus_pdfs/
  
  # Ver informações do PDF
  python cli.py arquivo.pdf -i
        """
    )
    
    parser.add_argument('pdf', help='Arquivo PDF para dividir')
    
    parser.add_argument(
        '-p', '--pages',
        type=int,
        metavar='NUM',
        help='Número de páginas por arquivo'
    )
    
    parser.add_argument(
        '-s', '--size',
        type=float,
        metavar='MB',
        help='Tamanho máximo em MB por arquivo'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output',
        metavar='DIR',
        help='Diretório de saída (padrão: output/)'
    )
    
    parser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Mostrar apenas informações do PDF sem dividir'
    )
    
    args = parser.parse_args()
    
    # Exibe banner
    print(BANNER)
    
    try:
        # Cria o divisor
        splitter = PDFSplitter(args.pdf)
        
        # Mostra informações
        info = splitter.get_info()
        print(f"\n{'='*60}")
        print(f"📄 INFORMAÇÕES DO PDF")
        print(f"{'='*60}")
        print(f"Arquivo: {info['arquivo']}")
        print(f"Total de páginas: {info['total_paginas']}")
        print(f"Tamanho: {info['tamanho_mb']} MB ({info['tamanho_bytes']:,} bytes)")
        print(f"{'='*60}\n")
        
        # Se for apenas informação, para aqui
        if args.info:
            return 0
        
        # Verifica se foi especificado um método de divisão
        if not args.pages and not args.size:
            print("Erro: Você deve especificar -p/--pages ou -s/--size para dividir o PDF")
            print("Use -h para ver ajuda")
            return 1
        
        # Verifica se ambos foram especificados
        if args.pages and args.size:
            print("Erro: Especifique apenas -p/--pages OU -s/--size, não ambos")
            return 1
        
        # Divide o PDF
        if args.pages:
            print(f"Dividindo por número de páginas ({args.pages} páginas por arquivo)...")
            print(f"Diretório de saída: {args.output}/\n")
            files = splitter.split_by_pages(args.pages, args.output)
        else:
            print(f"Dividindo por tamanho ({args.size} MB por arquivo)...")
            print(f"Diretório de saída: {args.output}/\n")
            files = splitter.split_by_size(args.size, args.output)
        
        # Resumo
        print(f"\n{'='*60}")
        print(f"✅ DIVISÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Total de arquivos criados: {len(files)}")
        print(f"Localização: {args.output}/")
        print(f"{'='*60}")
        print(f"\n📌 Desenvolvido por CALLEVA | RM SOFTWARES E TREINAMENTOS LTDA\n")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
