#!/usr/bin/env python3
"""
Rodovalho PDF Splitter - Interface Web
Desenvolvido por Calleva (RM SOFTWARES E TREINAMENTOS LTDA)
Cliente: RODOVALHO ADVOGADOS
"""

import streamlit as st
import os
import tempfile
import zipfile
import io
from pdf_splitter import PDFSplitter

# Configuração da página
st.set_page_config(
    page_title="PDF Splitter | Rodovalho Advogados",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Customizado - Identidade Visual Rodovalho Advogados
# Paleta de cores baseada em escritório de advocacia:
# - Azul Marinho (#1a2744): cor principal, transmite confiança e profissionalismo
# - Dourado (#c9a227): cor de destaque, transmite sofisticação
# - Branco (#ffffff): fundo limpo
# - Cinza Escuro (#2d3436): textos
# - Azul Claro (#3d5a80): hover e elementos secundários
st.markdown("""
<style>
    /* Reset e variáveis de cor */
    :root {
        --color-primary: #1a2744;
        --color-secondary: #3d5a80;
        --color-accent: #c9a227;
        --color-accent-hover: #d4af37;
        --color-text: #2d3436;
        --color-text-light: #636e72;
        --color-background: #f8f9fa;
        --color-white: #ffffff;
        --color-border: #dfe6e9;
        --color-success: #00b894;
        --color-error: #d63031;
    }
    
    /* Fundo geral */
    .stApp {
        background: linear-gradient(180deg, var(--color-background) 0%, var(--color-white) 100%);
    }
    
    /* Container principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Header customizado */
    .header-container {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(26, 39, 68, 0.15);
    }
    
    .header-title {
        color: var(--color-white);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        color: var(--color-accent);
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 2px;
    }
    
    .header-client {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        text-align: center;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Cards de informação */
    .info-card {
        background: var(--color-white);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .info-card h4 {
        color: var(--color-primary);
        margin-bottom: 1rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--color-border);
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-label {
        color: var(--color-text-light);
        font-size: 0.9rem;
    }
    
    .info-value {
        color: var(--color-text);
        font-weight: 600;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: var(--color-white);
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(26, 39, 68, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(26, 39, 68, 0.3);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
        color: var(--color-primary);
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(201, 162, 39, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(201, 162, 39, 0.4);
    }
    
    /* Upload area */
    .stFileUploader {
        background: var(--color-white);
        border: 2px dashed var(--color-border);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stFileUploader:hover {
        border-color: var(--color-accent);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: var(--color-white);
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--color-text-light);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: var(--color-white);
    }
    
    /* Inputs */
    .stNumberInput input, .stTextInput input {
        border: 2px solid var(--color-border);
        border-radius: 8px;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(26, 39, 68, 0.1);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: var(--color-white);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Success e Warning messages */
    .stSuccess {
        background-color: rgba(0, 184, 148, 0.1);
        border-left: 4px solid var(--color-success);
    }
    
    .stWarning {
        background-color: rgba(201, 162, 39, 0.1);
        border-left: 4px solid var(--color-accent);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-accent) 100%);
    }
    
    /* Footer */
    .footer-container {
        background: var(--color-primary);
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 3rem;
        text-align: center;
    }
    
    .footer-developer {
        color: var(--color-accent);
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 1px;
    }
    
    .footer-company {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    .footer-version {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.7rem;
        margin-top: 0.5rem;
    }
    
    /* Divider customizado */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
        margin: 2rem 0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--color-white);
        border-radius: 8px;
        color: var(--color-primary);
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--color-primary);
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--color-text-light);
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--color-primary);
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Renderiza o cabeçalho da aplicação."""
    # Verifica se existem logos
    logo_rodovalho_path = "public/logo_rodovalho.png"
    logo_calleva_path = "public/logo_calleva.png"
    
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">⚖️ PDF SPLITTER</h1>
        <p class="header-subtitle">DIVISOR DE DOCUMENTOS PDF</p>
        <p class="header-client">RODOVALHO ADVOGADOS</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tenta exibir logo se existir
    if os.path.exists(logo_rodovalho_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo_rodovalho_path, width=200)


def render_footer():
    """Renderiza o rodapé da aplicação."""
    st.markdown("""
    <div class="footer-container">
        <p class="footer-developer">DESENVOLVIDO POR CALLEVA</p>
        <p class="footer-company">RM SOFTWARES E TREINAMENTOS LTDA</p>
        <p class="footer-version">v1.0.0 | 2024</p>
    </div>
    """, unsafe_allow_html=True)


def render_info_card(info: dict):
    """Renderiza card com informações do PDF."""
    st.markdown(f"""
    <div class="info-card">
        <h4>📄 Informações do Documento</h4>
        <div class="info-item">
            <span class="info-label">Arquivo</span>
            <span class="info-value">{info['arquivo']}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Total de Páginas</span>
            <span class="info-value">{info['total_paginas']}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Tamanho</span>
            <span class="info-value">{info['tamanho_mb']} MB</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_zip_from_files(files: list) -> bytes:
    """Cria um arquivo ZIP com os PDFs gerados."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in files:
            if os.path.exists(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def main():
    """Função principal da aplicação."""
    
    # Renderiza cabeçalho
    render_header()
    
    # Área de upload
    st.markdown("### 📤 Upload do Documento")
    uploaded_file = st.file_uploader(
        "Arraste e solte seu arquivo PDF ou clique para selecionar",
        type=['pdf'],
        help="Tamanho máximo: 200MB"
    )
    
    if uploaded_file is not None:
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Cria o divisor
            splitter = PDFSplitter(tmp_path)
            info = splitter.get_info()
            info['arquivo'] = uploaded_file.name
            
            # Mostra informações
            render_info_card(info)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            # Opções de divisão
            st.markdown("### ✂️ Configuração da Divisão")
            
            tab1, tab2 = st.tabs(["📄 Por Páginas", "📦 Por Tamanho"])
            
            with tab1:
                st.markdown("""
                <p style="color: #636e72; margin-bottom: 1rem;">
                    Divide o PDF em arquivos com número específico de páginas.
                    Ideal para sistemas que limitam número de páginas.
                </p>
                """, unsafe_allow_html=True)
                
                pages_per_file = st.number_input(
                    "Páginas por arquivo",
                    min_value=1,
                    max_value=info['total_paginas'],
                    value=min(50, info['total_paginas']),
                    step=1,
                    key="pages_input"
                )
                
                estimated_files = (info['total_paginas'] + pages_per_file - 1) // pages_per_file
                st.info(f"📊 Estimativa: {estimated_files} arquivo(s) serão gerados")
                
                if st.button("✂️ Dividir por Páginas", key="split_pages", use_container_width=True):
                    with st.spinner("Processando documento..."):
                        # Cria diretório temporário
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            files = splitter.split_by_pages(pages_per_file, tmp_dir)
                            
                            st.success(f"✅ {len(files)} arquivo(s) gerado(s) com sucesso!")
                            
                            # Cria ZIP para download
                            zip_data = create_zip_from_files(files)
                            
                            st.download_button(
                                label="📥 Baixar todos os arquivos (ZIP)",
                                data=zip_data,
                                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_dividido.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # Lista arquivos gerados
                            with st.expander("📁 Ver arquivos gerados"):
                                for f in files:
                                    fname = os.path.basename(f)
                                    fsize = os.path.getsize(f) / (1024 * 1024)
                                    st.markdown(f"- `{fname}` ({fsize:.2f} MB)")
            
            with tab2:
                st.markdown("""
                <p style="color: #636e72; margin-bottom: 1rem;">
                    Divide o PDF em arquivos com tamanho máximo especificado.
                    Ideal para sistemas com limite de tamanho de upload.
                </p>
                """, unsafe_allow_html=True)
                
                max_size_mb = st.number_input(
                    "Tamanho máximo por arquivo (MB)",
                    min_value=0.1,
                    max_value=100.0,
                    value=5.0,
                    step=0.5,
                    format="%.1f",
                    key="size_input"
                )
                
                if info['tamanho_mb'] <= max_size_mb:
                    st.warning(f"⚠️ O arquivo já é menor que {max_size_mb} MB. Não será necessário dividir.")
                else:
                    estimated_files_size = int(info['tamanho_mb'] / max_size_mb) + 1
                    st.info(f"📊 Estimativa: aproximadamente {estimated_files_size} arquivo(s)")
                
                if st.button("✂️ Dividir por Tamanho", key="split_size", use_container_width=True):
                    with st.spinner("Processando documento..."):
                        # Cria diretório temporário
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            files = splitter.split_by_size(max_size_mb, tmp_dir)
                            
                            st.success(f"✅ {len(files)} arquivo(s) gerado(s) com sucesso!")
                            
                            # Cria ZIP para download
                            zip_data = create_zip_from_files(files)
                            
                            st.download_button(
                                label="📥 Baixar todos os arquivos (ZIP)",
                                data=zip_data,
                                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_dividido.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # Lista arquivos gerados
                            with st.expander("📁 Ver arquivos gerados"):
                                for f in files:
                                    fname = os.path.basename(f)
                                    fsize = os.path.getsize(f) / (1024 * 1024)
                                    st.markdown(f"- `{fname}` ({fsize:.2f} MB)")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        
        finally:
            # Remove arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    else:
        # Estado vazio - instruções
        st.markdown("""
        <div class="info-card">
            <h4>📋 Como usar</h4>
            <div class="info-item">
                <span class="info-label">Passo 1</span>
                <span class="info-value">Faça upload do arquivo PDF</span>
            </div>
            <div class="info-item">
                <span class="info-label">Passo 2</span>
                <span class="info-value">Escolha o método de divisão</span>
            </div>
            <div class="info-item">
                <span class="info-label">Passo 3</span>
                <span class="info-value">Baixe os arquivos divididos</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recursos
        with st.expander("ℹ️ Recursos do Sistema"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Divisão por Páginas**
                - Define número exato de páginas
                - Ideal para sistemas jurídicos
                - Nomeação automática dos arquivos
                """)
            with col2:
                st.markdown("""
                **Divisão por Tamanho**
                - Define tamanho máximo em MB
                - Ideal para limits de upload
                - Compressão otimizada
                """)
    
    # Rodapé
    render_footer()


if __name__ == "__main__":
    main()
