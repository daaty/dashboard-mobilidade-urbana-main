from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from backend.services.import_service import ImportService
import logging
logger = logging.getLogger(__name__)

bp = Blueprint('data_import', __name__)

# Inicializar serviço de importação
import_service = ImportService()

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivos"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        import_type = request.form.get('import_type', 'corridas')
        
        # Validar arquivo
        validation = import_service.validate_file(file)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # Salvar arquivo
        filename = validation['filename']
        filepath = import_service.save_uploaded_file(file, filename)
        
        # Gerar preview
        preview = import_service.preview_import(filepath, import_type)
        
        if not preview['success']:
            # Remover arquivo se houve erro
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': False,
                'error': preview['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'filepath': filepath,
                'file_size': validation['size'],
                'import_type': import_type,
                'preview': preview
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no upload de arquivo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/preview', methods=['POST'])
def preview_import():
    """Endpoint para preview de importação"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        import_type = data.get('import_type', 'corridas')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado'
            }), 400
        
        preview = import_service.preview_import(filepath, import_type)
        
        return jsonify({
            'success': True,
            'data': preview
        })
        
    except Exception as e:
        logger.error(f"Erro no preview de importação: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/execute', methods=['POST'])
def execute_import():
    """Endpoint para executar importação"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        import_type = data.get('import_type', 'corridas')
        column_mapping = data.get('column_mapping', {})
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado'
            }), 400
        
        if not column_mapping:
            return jsonify({
                'success': False,
                'error': 'Mapeamento de colunas é obrigatório'
            }), 400
        
        # Executar importação baseado no tipo
        if import_type == 'corridas':
            result = import_service.import_corridas(filepath, column_mapping)
        elif import_type == 'motoristas':
            # TODO: Implementar importação de motoristas
            result = {'success': False, 'error': 'Importação de motoristas não implementada ainda'}
        elif import_type == 'metas':
            # TODO: Implementar importação de metas
            result = {'success': False, 'error': 'Importação de metas não implementada ainda'}
        else:
            result = {'success': False, 'error': f'Tipo de importação não suportado: {import_type}'}
        
        # Remover arquivo após importação (sucesso ou erro)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.warning(f"Não foi possível remover arquivo temporário: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na execução de importação: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/history', methods=['GET'])
def get_import_history():
    """Endpoint para buscar histórico de importações"""
    try:
        limit = int(request.args.get('limit', 50))
        
        history = import_service.get_import_history(limit)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de importações: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Endpoint para listar formatos suportados"""
    return jsonify({
        'success': True,
        'data': {
            'formats': import_service.SUPPORTED_FORMATS,
            'max_file_size_mb': import_service.MAX_FILE_SIZE // (1024 * 1024),
            'import_types': ['corridas', 'motoristas', 'metas']
        }
    })

@bp.route('/validate-mapping', methods=['POST'])
def validate_mapping():
    """Endpoint para validar mapeamento de colunas"""
    try:
        data = request.get_json()
        import_type = data.get('import_type', 'corridas')
        column_mapping = data.get('column_mapping', {})
        
        # Obter configuração de mapeamento para o tipo
        mapping_config = import_service.get_column_mapping(import_type)
        
        # Validar campos obrigatórios
        missing_required = []
        for field in mapping_config['required'].keys():
            if field not in column_mapping or not column_mapping[field]:
                missing_required.append(field)
        
        # Validar se as colunas mapeadas existem no arquivo
        # (Isso seria feito com dados reais do arquivo)
        
        validation_result = {
            'valid': len(missing_required) == 0,
            'missing_required_fields': missing_required,
            'mapped_fields': list(column_mapping.keys()),
            'required_fields': list(mapping_config['required'].keys()),
            'optional_fields': list(mapping_config['optional'].keys())
        }
        
        return jsonify({
            'success': True,
            'data': validation_result
        })
        
    except Exception as e:
        logger.error(f"Erro na validação de mapeamento: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Endpoint para limpeza de arquivos antigos"""
    try:
        days = int(request.get_json().get('days', 7))
        
        import_service.cleanup_old_files(days)
        
        return jsonify({
            'success': True,
            'message': f'Limpeza de arquivos com mais de {days} dias executada'
        })
        
    except Exception as e:
        logger.error(f"Erro na limpeza de arquivos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/template/<template_type>', methods=['GET'])
def download_template(template_type):
    """Endpoint para download de templates"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        templates = {
            'corridas': {
                'data': ['2025-01-15', '2025-01-16'],
                'usuario_nome': ['João Silva', 'Maria Santos'],
                'usuario_telefone': ['(11) 99999-9999', '(11) 88888-8888'],
                'motorista_nome': ['Pedro Costa', 'Ana Lima'],
                'municipio': ['São Paulo', 'Rio de Janeiro'],
                'status': ['concluida', 'concluida'],
                'valor': [25.50, 18.75],
                'distancia': [8.2, 5.6],
                'tempo_corrida': [25, 18],
                'avaliacao': [5, 4],
                'motivo_cancelamento': ['', '']
            },
            'motoristas': {
                'nome': ['Carlos Silva', 'Ana Santos'],
                'municipio': ['São Paulo', 'Rio de Janeiro'],
                'telefone': ['(11) 99999-9999', '(21) 88888-8888'],
                'status': ['ativo', 'ativo'],
                'data_cadastro': ['2025-01-01', '2025-01-02']
            },
            'metas': {
                'municipio': ['São Paulo', 'Rio de Janeiro'],
                'mes': ['2025-01', '2025-01'],
                'meta_corridas': [1000, 800],
                'meta_receita': [25000.00, 20000.00],
                'meta_motoristas': [50, 40]
            }
        }
        
        if template_type not in templates:
            return jsonify({
                'success': False,
                'error': 'Tipo de template não encontrado'
            }), 404
        
        # Criar DataFrame com dados de exemplo
        df = pd.DataFrame(templates[template_type])
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=template_type.capitalize())
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'template_{template_type}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
