# Rodovalho PDF Splitter

<p align="center">
  <strong>⚖️ RODOVALHO ADVOGADOS</strong>
</p>

<p align="center">
  <em>Desenvolvido por Calleva | RM SOFTWARES E TREINAMENTOS LTDA</em>
</p>

---

Aplicação Python para dividir arquivos PDF em tamanhos menores, facilitando o protocolo de documentos grandes em sistemas jurídicos.

## Características

- ✂️ **Divisão por Páginas**: Divide PDF em arquivos com número específico de páginas
- 📦 **Divisão por Tamanho**: Divide PDF em arquivos com tamanho máximo em MB
- 📊 **Informações do PDF**: Visualiza informações sobre o arquivo (páginas, tamanho)
- 🎯 **Interface Simples**: Linha de comando fácil de usar
- 🖥️ **Interface Web**: Interface gráfica moderna via navegador
- 📁 **Organização Automática**: Cria diretórios de saída automaticamente


## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/bodimfm/rodovalho_pdf_splitter.git
cd rodovalho_pdf_splitter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Interface Web (Recomendado)

A forma mais fácil de usar a aplicação é através da interface web:

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador para usar a interface gráfica.

### Interface de Linha de Comando (CLI)

#### Ver informações do PDF
```bash
python cli.py arquivo.pdf -i
```

#### Dividir por número de páginas
```bash
# Divide em arquivos de 50 páginas cada
python cli.py arquivo.pdf -p 50

# Especificando diretório de saída
python cli.py arquivo.pdf -p 50 -o meus_pdfs/
```

#### Dividir por tamanho
```bash
# Divide em arquivos de no máximo 5 MB cada
python cli.py arquivo.pdf -s 5

# Divide em arquivos de no máximo 10 MB
python cli.py arquivo.pdf -s 10 -o output_pdfs/
```

### Usando como Módulo Python

```python
from pdf_splitter import PDFSplitter

# Cria o divisor
splitter = PDFSplitter('meu_arquivo.pdf')

# Ver informações
info = splitter.get_info()
print(f"Total de páginas: {info['total_paginas']}")
print(f"Tamanho: {info['tamanho_mb']} MB")

# Dividir por páginas (50 páginas por arquivo)
arquivos = splitter.split_by_pages(50, output_dir='output')

# Ou dividir por tamanho (5 MB por arquivo)
arquivos = splitter.split_by_size(5, output_dir='output')
```

## Exemplos de Uso

### Caso de Uso: Sistema Jurídico

Muitos sistemas jurídicos têm limites de tamanho para upload de documentos. Por exemplo:

```bash
# Se o sistema aceita no máximo 10 MB por arquivo
python cli.py processo_completo.pdf -s 10 -o processo_dividido/

# Se prefere dividir em documentos de 30 páginas cada
python cli.py peticao_longa.pdf -p 30 -o peticao_partes/
```

## Opções do CLI

```
usage: cli.py [-h] [-p NUM] [-s MB] [-o DIR] [-i] pdf

Argumentos posicionais:
  pdf                   Arquivo PDF para dividir

Opções:
  -h, --help            Mostrar ajuda e sair
  -p NUM, --pages NUM   Número de páginas por arquivo
  -s MB, --size MB      Tamanho máximo em MB por arquivo
  -o DIR, --output DIR  Diretório de saída (padrão: output/)
  -i, --info            Mostrar apenas informações do PDF sem dividir
```

## Estrutura dos Arquivos de Saída

Os arquivos divididos são nomeados automaticamente seguindo o padrão:
```
<nome_original>_parte_001_paginas_1-50.pdf
<nome_original>_parte_002_paginas_51-100.pdf
<nome_original>_parte_003_paginas_101-150.pdf
...
```

## Requisitos

- Python 3.6+
- PyPDF2 >= 3.0.0
- Streamlit >= 1.28.0

## Estrutura do Projeto

```
rodovalho_pdf_splitter/
├── app.py              # Interface web (Streamlit)
├── cli.py              # Interface de linha de comando
├── pdf_splitter.py     # Módulo principal de divisão
├── demo.py             # Script de demonstração
├── create_test_pdf.py  # Criador de PDF de teste
├── public/             # Assets (logos)
├── requirements.txt    # Dependências Python
└── README.md           # Documentação
```

## Identidade Visual

O sistema utiliza a identidade visual do escritório **RODOVALHO ADVOGADOS**:

- **Azul Marinho** (#1a2744): Cor principal - transmite confiança e profissionalismo
- **Dourado** (#c9a227): Cor de destaque - transmite sofisticação
- **Azul Secundário** (#3d5a80): Elementos secundários

## Licença

Este projeto é de código aberto.

## Desenvolvido por

**Calleva** | RM SOFTWARES E TREINAMENTOS LTDA

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
