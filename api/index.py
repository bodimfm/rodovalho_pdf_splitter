"""
API Flask para divisão de PDFs - Versão Web para Vercel.
"""

import os
import io
import json
import zipfile
import tempfile
from flask import Flask, request, jsonify, send_file, render_template_string
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(_error):
    """Retorna erro amigável quando o upload excede o limite."""
    return jsonify({'error': 'Arquivo muito grande para processar nesta hospedagem.'}), 413


@app.after_request
def add_cors_headers(response):
    """Adiciona headers CORS a todas as respostas."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/info', methods=['OPTIONS'])
@app.route('/split', methods=['OPTIONS'])
@app.route('/api/info', methods=['OPTIONS'])
@app.route('/api/split', methods=['OPTIONS'])
def handle_options():
    """Trata requisições preflight OPTIONS."""
    return '', 204

# Preferências padrão por tribunal (em MB e páginas)
TRIBUNAIS_DEFAULTS = {
    "tjsp": {"max_size_mb": 5, "max_pages": None, "nome": "TJSP - Tribunal de Justiça de SP"},
    "tjrj": {"max_size_mb": 10, "max_pages": None, "nome": "TJRJ - Tribunal de Justiça do RJ"},
    "tjmg": {"max_size_mb": 8, "max_pages": None, "nome": "TJMG - Tribunal de Justiça de MG"},
    "tjpr": {"max_size_mb": 5, "max_pages": None, "nome": "TJPR - Tribunal de Justiça do PR"},
    "tjrs": {"max_size_mb": 10, "max_pages": None, "nome": "TJRS - Tribunal de Justiça do RS"},
    "tjsc": {"max_size_mb": 5, "max_pages": None, "nome": "TJSC - Tribunal de Justiça de SC"},
    "trf1": {"max_size_mb": 10, "max_pages": None, "nome": "TRF1 - Tribunal Regional Federal 1ª Região"},
    "trf2": {"max_size_mb": 10, "max_pages": None, "nome": "TRF2 - Tribunal Regional Federal 2ª Região"},
    "trf3": {"max_size_mb": 10, "max_pages": None, "nome": "TRF3 - Tribunal Regional Federal 3ª Região"},
    "trf4": {"max_size_mb": 10, "max_pages": None, "nome": "TRF4 - Tribunal Regional Federal 4ª Região"},
    "trf5": {"max_size_mb": 10, "max_pages": None, "nome": "TRF5 - Tribunal Regional Federal 5ª Região"},
    "stj": {"max_size_mb": 15, "max_pages": None, "nome": "STJ - Superior Tribunal de Justiça"},
    "stf": {"max_size_mb": 15, "max_pages": None, "nome": "STF - Supremo Tribunal Federal"},
    "tst": {"max_size_mb": 10, "max_pages": None, "nome": "TST - Tribunal Superior do Trabalho"},
    "pje": {"max_size_mb": 10, "max_pages": 200, "nome": "PJe - Processo Judicial Eletrônico"},
    "projudi": {"max_size_mb": 5, "max_pages": None, "nome": "Projudi"},
    "esaj": {"max_size_mb": 5, "max_pages": None, "nome": "e-SAJ"},
    "custom": {"max_size_mb": 5, "max_pages": 50, "nome": "Personalizado"}
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Divisor de PDF - Por Tribunal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .card-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px 15px 0 0 !important; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-primary:hover { background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%); transform: translateY(-2px); }
        .drop-zone { border: 3px dashed #667eea; border-radius: 15px; padding: 40px; text-align: center; transition: all 0.3s; cursor: pointer; }
        .drop-zone:hover, .drop-zone.dragover { background: rgba(102, 126, 234, 0.1); border-color: #764ba2; }
        .tribunal-card { cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
        .tribunal-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .tribunal-card.selected { border-color: #667eea; background: rgba(102, 126, 234, 0.1); }
        .progress { height: 25px; border-radius: 12px; }
        .progress-bar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .file-info { background: #f8f9fa; border-radius: 10px; padding: 15px; margin-top: 15px; }
        #customSettings { display: none; }
        .preference-badge { font-size: 0.75rem; }
        .saved-preferences { max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="card">
                    <div class="card-header text-white py-4">
                        <h2 class="mb-0 text-center">
                            <i class="bi bi-file-earmark-pdf me-2"></i>
                            Divisor de PDF por Tribunal
                        </h2>
                        <p class="mb-0 text-center mt-2 opacity-75">Divida seus PDFs conforme as regras de cada tribunal</p>
                    </div>
                    <div class="card-body p-4">
                        <!-- Seleção de Tribunal -->
                        <div class="mb-4">
                            <h5 class="mb-3"><i class="bi bi-bank me-2"></i>Selecione o Tribunal</h5>
                            <div class="row g-2" id="tribunalList">
                                <!-- Tribunais serão inseridos via JS -->
                            </div>
                        </div>

                        <!-- Configurações Personalizadas -->
                        <div id="customSettings" class="mb-4 p-3 bg-light rounded">
                            <h6 class="mb-3"><i class="bi bi-gear me-2"></i>Configurações Personalizadas</h6>
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Tamanho máximo (MB)</label>
                                    <input type="number" class="form-control" id="customSize" value="5" min="1" max="50" step="0.5">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Máximo de páginas (opcional)</label>
                                    <input type="number" class="form-control" id="customPages" placeholder="Sem limite" min="1">
                                </div>
                            </div>
                            <div class="mt-3">
                                <button class="btn btn-sm btn-outline-primary" onclick="saveCustomPreference()">
                                    <i class="bi bi-save me-1"></i>Salvar como preferência
                                </button>
                            </div>
                        </div>

                        <!-- Preferências Salvas -->
                        <div class="mb-4" id="savedPreferencesSection" style="display: none;">
                            <h6 class="mb-2">
                                <i class="bi bi-bookmark-star me-2"></i>Suas Preferências Salvas
                                <button class="btn btn-sm btn-link text-danger" onclick="clearAllPreferences()">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </h6>
                            <div class="saved-preferences" id="savedPreferencesList"></div>
                        </div>

                        <!-- Configuração Atual -->
                        <div class="alert alert-info" id="currentConfig">
                            <i class="bi bi-info-circle me-2"></i>
                            <span id="configText">Selecione um tribunal para ver as configurações</span>
                        </div>

                        <!-- Upload de PDF -->
                        <div class="drop-zone" id="dropZone" onclick="document.getElementById('pdfInput').click()">
                            <i class="bi bi-cloud-upload display-4 text-primary"></i>
                            <h5 class="mt-3">Arraste seu PDF aqui</h5>
                            <p class="text-muted">ou clique para selecionar</p>
                            <input type="file" id="pdfInput" accept=".pdf" class="d-none">
                        </div>

                        <!-- Informações do arquivo -->
                        <div class="file-info" id="fileInfo" style="display: none;">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <i class="bi bi-file-earmark-pdf text-danger me-2"></i>
                                    <strong id="fileName"></strong>
                                </div>
                                <button class="btn btn-sm btn-outline-danger" onclick="clearFile()">
                                    <i class="bi bi-x"></i>
                                </button>
                            </div>
                            <div class="row mt-2">
                                <div class="col-6">
                                    <small class="text-muted">Tamanho: <span id="fileSize"></span></small>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Páginas: <span id="pageCount">-</span></small>
                                </div>
                            </div>
                        </div>

                        <!-- Progresso -->
                        <div class="mt-4" id="progressSection" style="display: none;">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated"
                                     id="progressBar" style="width: 0%">0%</div>
                            </div>
                            <p class="text-center mt-2" id="progressText">Processando...</p>
                        </div>

                        <!-- Botão de Divisão -->
                        <div class="d-grid gap-2 mt-4">
                            <button class="btn btn-primary btn-lg" id="splitBtn" onclick="splitPDF()" disabled>
                                <i class="bi bi-scissors me-2"></i>Dividir PDF
                            </button>
                        </div>

                        <!-- Resultado -->
                        <div class="mt-4" id="resultSection" style="display: none;">
                            <div class="alert alert-success">
                                <h5><i class="bi bi-check-circle me-2"></i>PDF Dividido com Sucesso!</h5>
                                <p class="mb-2">Foram criados <strong id="filesCount"></strong> arquivos.</p>
                                <div id="filesList" class="small"></div>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer text-center text-muted py-3">
                        <small>
                            <i class="bi bi-shield-check me-1"></i>
                            Processamento seguro no servidor - seus arquivos não são armazenados
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Dados dos tribunais
        const TRIBUNAIS = ''' + json.dumps(TRIBUNAIS_DEFAULTS, ensure_ascii=False) + ''';

        let selectedTribunal = null;
        let selectedFile = null;
        let userPreferences = {};

        // Carrega preferências do localStorage
        function loadPreferences() {
            const saved = localStorage.getItem('pdfSplitter_preferences');
            if (saved) {
                userPreferences = JSON.parse(saved);
                updatePreferencesUI();
            }
        }

        // Salva preferências no localStorage
        function savePreferences() {
            localStorage.setItem('pdfSplitter_preferences', JSON.stringify(userPreferences));
            updatePreferencesUI();
        }

        // Atualiza UI de preferências
        function updatePreferencesUI() {
            const section = document.getElementById('savedPreferencesSection');
            const list = document.getElementById('savedPreferencesList');

            if (Object.keys(userPreferences).length === 0) {
                section.style.display = 'none';
                return;
            }

            section.style.display = 'block';
            list.innerHTML = '';

            for (const [key, pref] of Object.entries(userPreferences)) {
                const div = document.createElement('div');
                div.className = 'd-flex justify-content-between align-items-center p-2 bg-white rounded mb-1';
                div.innerHTML = `
                    <span>
                        <strong>${pref.nome || key.toUpperCase()}</strong>:
                        ${pref.max_size_mb}MB${pref.max_pages ? ', ' + pref.max_pages + ' páginas' : ''}
                    </span>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletePreference('${key}')">
                        <i class="bi bi-x"></i>
                    </button>
                `;
                list.appendChild(div);
            }

            // Atualiza badges nos tribunais
            document.querySelectorAll('.tribunal-card').forEach(card => {
                const key = card.dataset.tribunal;
                const badge = card.querySelector('.preference-badge');
                if (userPreferences[key]) {
                    badge.style.display = 'inline-block';
                    badge.textContent = `${userPreferences[key].max_size_mb}MB`;
                } else {
                    badge.style.display = 'none';
                }
            });
        }

        // Salvar preferência personalizada
        function saveCustomPreference() {
            if (!selectedTribunal) {
                alert('Selecione um tribunal primeiro');
                return;
            }

            const size = parseFloat(document.getElementById('customSize').value) || 5;
            const pages = parseInt(document.getElementById('customPages').value) || null;

            userPreferences[selectedTribunal] = {
                max_size_mb: size,
                max_pages: pages,
                nome: TRIBUNAIS[selectedTribunal]?.nome || selectedTribunal.toUpperCase()
            };

            savePreferences();
            updateConfigDisplay();
            alert('Preferência salva com sucesso!');
        }

        // Deletar preferência
        function deletePreference(key) {
            delete userPreferences[key];
            savePreferences();
        }

        // Limpar todas preferências
        function clearAllPreferences() {
            if (confirm('Deseja remover todas as preferências salvas?')) {
                userPreferences = {};
                savePreferences();
            }
        }

        // Renderiza lista de tribunais
        function renderTribunais() {
            const container = document.getElementById('tribunalList');
            container.innerHTML = '';

            for (const [key, data] of Object.entries(TRIBUNAIS)) {
                const col = document.createElement('div');
                col.className = 'col-6 col-md-4 col-lg-3';
                col.innerHTML = `
                    <div class="card tribunal-card h-100 p-2" data-tribunal="${key}" onclick="selectTribunal('${key}')">
                        <div class="text-center">
                            <small class="fw-bold">${key.toUpperCase()}</small>
                            <span class="badge bg-success preference-badge ms-1" style="display: none;"></span>
                            <br>
                            <small class="text-muted">${data.max_size_mb}MB</small>
                        </div>
                    </div>
                `;
                container.appendChild(col);
            }
        }

        // Seleciona tribunal
        function selectTribunal(key) {
            selectedTribunal = key;

            // Atualiza visual
            document.querySelectorAll('.tribunal-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-tribunal="${key}"]`).classList.add('selected');

            // Mostra/esconde configurações personalizadas
            const customSettings = document.getElementById('customSettings');
            if (key === 'custom') {
                customSettings.style.display = 'block';
            } else {
                customSettings.style.display = 'none';
            }

            updateConfigDisplay();
            updateSplitButton();
        }

        // Atualiza exibição da configuração
        function updateConfigDisplay() {
            if (!selectedTribunal) return;

            // Pega configuração (preferência do usuário ou padrão)
            const config = userPreferences[selectedTribunal] || TRIBUNAIS[selectedTribunal];
            const configText = document.getElementById('configText');

            let text = `<strong>${config.nome || selectedTribunal.toUpperCase()}</strong>: `;
            text += `Máximo ${config.max_size_mb} MB`;
            if (config.max_pages) {
                text += ` ou ${config.max_pages} páginas`;
            }

            if (userPreferences[selectedTribunal]) {
                text += ' <span class="badge bg-success">Personalizado</span>';
            }

            configText.innerHTML = text;
        }

        // Configuração de drag and drop
        const dropZone = document.getElementById('dropZone');
        const pdfInput = document.getElementById('pdfInput');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                handleFile(files[0]);
            }
        });

        pdfInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        async function readErrorMessage(response) {
            const contentType = response.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                try {
                    const data = await response.json();
                    if (data && typeof data === 'object') {
                        return data.error || JSON.stringify(data);
                    }
                } catch (_e) {
                    // ignora e tenta texto
                }
            }

            try {
                const text = await response.text();
                if (!text) return `HTTP ${response.status}`;
                return text.length > 300 ? text.slice(0, 300) + '…' : text;
            } catch (_e) {
                return `HTTP ${response.status}`;
            }
        }

        // Processa arquivo selecionado - usa API backend para obter informações
        async function handleFile(file) {
            selectedFile = file;
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('pageCount').textContent = 'Carregando...';

            // Usa a API backend para obter informações do PDF
            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/info', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const info = await response.json();
                    document.getElementById('pageCount').textContent = info.pages;
                } else {
                    const message = await readErrorMessage(response);
                    document.getElementById('pageCount').textContent = 'Erro: ' + message;
                }
            } catch (error) {
                console.error('Erro ao obter info:', error);
                document.getElementById('pageCount').textContent = 'Erro';
            }

            updateSplitButton();
        }

        // Limpa arquivo selecionado
        function clearFile() {
            selectedFile = null;
            pdfInput.value = '';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('resultSection').style.display = 'none';
            updateSplitButton();
        }

        // Atualiza estado do botão
        function updateSplitButton() {
            const btn = document.getElementById('splitBtn');
            btn.disabled = !selectedFile || !selectedTribunal;
        }

        // Formata tamanho do arquivo
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        }

        // Divide o PDF usando a API backend
        async function splitPDF() {
            if (!selectedFile || !selectedTribunal) return;

            const config = userPreferences[selectedTribunal] || TRIBUNAIS[selectedTribunal];

            const progressSection = document.getElementById('progressSection');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const resultSection = document.getElementById('resultSection');
            const splitBtn = document.getElementById('splitBtn');

            progressSection.style.display = 'block';
            resultSection.style.display = 'none';
            splitBtn.disabled = true;

            // Animação de progresso indeterminado
            progressBar.style.width = '30%';
            progressBar.textContent = 'Enviando...';
            progressText.textContent = 'Enviando arquivo para o servidor...';

            try {
                // Prepara FormData para enviar ao servidor
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('max_size_mb', config.max_size_mb);
                if (config.max_pages) {
                    formData.append('max_pages', config.max_pages);
                }

                progressBar.style.width = '50%';
                progressBar.textContent = 'Processando...';
                progressText.textContent = 'Servidor processando o PDF...';

                // Envia para a API backend
                const response = await fetch('/api/split', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const message = await readErrorMessage(response);
                    throw new Error(message || 'Erro ao processar PDF');
                }

                progressBar.style.width = '80%';
                progressBar.textContent = 'Baixando...';
                progressText.textContent = 'Preparando download...';

                // Recebe o ZIP e faz download
                const blob = await response.blob();
                const baseName = selectedFile.name.replace('.pdf', '');
                const downloadUrl = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `${baseName}_dividido.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);

                // Mostra resultado
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                progressText.textContent = 'Concluído!';

                document.getElementById('filesCount').textContent = 'vários';
                document.getElementById('filesList').innerHTML = '<div><i class="bi bi-file-earmark-zip text-warning me-1"></i>Arquivo ZIP baixado com sucesso!</div>';

                resultSection.style.display = 'block';

            } catch (error) {
                console.error('Erro:', error);
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-danger');
                progressText.textContent = 'Erro: ' + error.message;
                alert('Erro ao processar PDF: ' + error.message);
            } finally {
                splitBtn.disabled = false;
            }
        }

        // Inicialização
        document.addEventListener('DOMContentLoaded', () => {
            renderTribunais();
            loadPreferences();
        });
    </script>
</body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
    """Página principal com interface web."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/tribunais', methods=['GET'])
@app.route('/api/tribunais', methods=['GET'])
def get_tribunais():
    """Retorna lista de tribunais e suas configurações padrão."""
    return jsonify(TRIBUNAIS_DEFAULTS)


@app.route('/info', methods=['POST'])
@app.route('/api/info', methods=['POST'])
def get_pdf_info():
    """Retorna informações sobre um PDF enviado."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Arquivo deve ser PDF'}), 400
    
    try:
        pdf_bytes = file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        
        return jsonify({
            'filename': secure_filename(file.filename),
            'pages': len(reader.pages),
            'size_bytes': len(pdf_bytes),
            'size_mb': round(len(pdf_bytes) / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/split', methods=['POST'])
@app.route('/api/split', methods=['POST'])
def split_pdf():
    """Divide um PDF e retorna um ZIP com os arquivos."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    max_size_mb = float(request.form.get('max_size_mb', 5))
    max_pages = request.form.get('max_pages')
    max_pages = int(max_pages) if max_pages else None
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Arquivo deve ser PDF'}), 400
    
    try:
        pdf_bytes = file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        max_size_bytes = max_size_mb * 1024 * 1024
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        
        # Cria ZIP na memória
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            part_num = 1
            current_start = 0
            
            while current_start < total_pages:
                writer = PdfWriter()
                current_page = current_start
                
                while current_page < total_pages:
                    # Verifica limite de páginas
                    if max_pages and (current_page - current_start) >= max_pages:
                        break
                    
                    writer.add_page(reader.pages[current_page])
                    
                    # Verifica tamanho
                    temp_buffer = io.BytesIO()
                    writer.write(temp_buffer)
                    
                    if temp_buffer.tell() > max_size_bytes and current_page > current_start:
                        # Remove última página
                        writer = PdfWriter()
                        for i in range(current_start, current_page):
                            writer.add_page(reader.pages[i])
                        break
                    
                    current_page += 1
                
                # Salva parte no ZIP
                output_buffer = io.BytesIO()
                writer.write(output_buffer)
                
                filename = f"{base_name}_parte_{part_num:03d}_pag_{current_start + 1}-{current_page}.pdf"
                zip_file.writestr(filename, output_buffer.getvalue())
                
                current_start = current_page
                part_num += 1
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{base_name}_dividido.zip'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


# Para execução local
if __name__ == '__main__':
    app.run(debug=True, port=5000)
