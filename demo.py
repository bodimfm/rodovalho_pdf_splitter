#!/usr/bin/env python3
"""
Script de demonstração do Rodovalho PDF Splitter.
"""

import os
import shlex
import subprocess
import sys


def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{'='*70}")
    print(f"DEMONSTRAÇÃO: {description}")
    print(f"{'='*70}")
    print(f"Comando: {cmd}\n")
    result = subprocess.run(shlex.split(cmd), shell=False)
    return result.returncode == 0


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                   RODOVALHO PDF SPLITTER                          ║
    ║          Demonstração de Funcionalidades                         ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Verifica se há PDF de teste
    if not os.path.exists('test_document.pdf'):
        print("Criando PDF de teste com 100 páginas...")
        if not run_command('python create_test_pdf.py', 'Criar PDF de Teste'):
            return 1
    
    # Demonstração 1: Ver informações
    if not run_command('python cli.py test_document.pdf -i', 
                      'Ver Informações do PDF'):
        return 1
    
    input("\n⏸️  Pressione ENTER para continuar...")
    
    # Demonstração 2: Dividir por páginas
    run_command('rm -rf output/*', 'Limpar diretório de saída')
    if not run_command('python cli.py test_document.pdf -p 25', 
                      'Dividir por Páginas (25 páginas por arquivo)'):
        return 1
    
    print("\n📁 Arquivos criados:")
    subprocess.run('ls -lh output/', shell=True)
    
    input("\n⏸️  Pressione ENTER para continuar...")
    
    # Demonstração 3: Dividir por tamanho
    run_command('rm -rf output/*', 'Limpar diretório de saída')
    if not run_command('python cli.py test_document.pdf -s 0.03', 
                      'Dividir por Tamanho (0.03 MB por arquivo)'):
        return 1
    
    print("\n📁 Arquivos criados:")
    subprocess.run('ls -lh output/', shell=True)
    
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                   DEMONSTRAÇÃO CONCLUÍDA!                         ║
    ║                                                                   ║
    ║  O Rodovalho PDF Splitter está pronto para uso.                  ║
    ║  Consulte o README.md para mais informações.                      ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
