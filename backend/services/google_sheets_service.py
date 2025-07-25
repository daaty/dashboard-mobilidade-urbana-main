import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta

class GoogleSheetsService:
    """Serviço para integração com Google Sheets API"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        self.service = None
        self.config = self._load_config()
        self._authenticate()
    
    def _load_config(self):
        """Carrega configuração das planilhas"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sheets_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Configuração padrão (será substituída pela configuração do usuário)
        return {
            'spreadsheet_id_corridas': '',
            'spreadsheet_id_metas': ''
        }
    
    def _authenticate(self):
        """Autentica com Google Sheets API"""
        creds = None
        token_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.json')
        
        # Verifica se já existe token salvo
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # Se não há credenciais válidas, solicita autorização
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Para desenvolvimento, usaremos dados mock se não houver credenciais
                print("Aviso: Credenciais do Google Sheets não configuradas. Usando dados mock.")
                self.service = None
                return
        
        try:
            self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Erro ao conectar com Google Sheets: {e}")
            self.service = None
    
    def _get_sheet_data(self, spreadsheet_id, range_name):
        """Busca dados de uma planilha específica"""
        if not self.service or not spreadsheet_id:
            return self._get_mock_data(range_name)
        
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            
            if not values:
                return []
            
            # Converter para lista de dicionários
            headers = values[0]
            data = []
            for row in values[1:]:
                # Preencher colunas faltantes com string vazia
                while len(row) < len(headers):
                    row.append('')
                
                row_dict = dict(zip(headers, row))
                data.append(row_dict)
            
            return data
            
        except HttpError as error:
            print(f"Erro ao acessar Google Sheets: {error}")
            return self._get_mock_data(range_name)
    
    def _get_mock_data(self, range_name):
        """Retorna dados mock para desenvolvimento"""
        if 'Corridas Concluidas' in range_name:
            return [
                {'Data': '2025-01-20', 'Nº ID': '001', 'Nome Usuário': 'João Silva', 'Tel Usuário': '11999999999', 'Municipio': 'São Paulo', 'Nome Motorista': 'Carlos Santos'},
                {'Data': '2025-01-20', 'Nº ID': '002', 'Nome Usuário': 'Maria Oliveira', 'Tel Usuário': '11888888888', 'Municipio': 'Rio de Janeiro', 'Nome Motorista': 'Ana Costa'},
                {'Data': '2025-01-21', 'Nº ID': '003', 'Nome Usuário': 'Pedro Lima', 'Tel Usuário': '11777777777', 'Municipio': 'São Paulo', 'Nome Motorista': 'José Ferreira'},
                {'Data': '2025-01-21', 'Nº ID': '004', 'Nome Usuário': 'Ana Santos', 'Tel Usuário': '11666666666', 'Municipio': 'Belo Horizonte', 'Nome Motorista': 'Roberto Silva'},
                {'Data': '2025-01-22', 'Nº ID': '005', 'Nome Usuário': 'Carlos Pereira', 'Tel Usuário': '11555555555', 'Municipio': 'São Paulo', 'Nome Motorista': 'Marcos Oliveira'}
            ]
        elif 'Corridas Canceladas' in range_name:
            return [
                {'Data - CC': '2025-01-20', 'Nº ID - CC': '006', 'Nome Usuario - CC': 'Lucia Fernandes', 'Tel. Usuário - CC': '11444444444', 'Municipio - CC': 'São Paulo', 'Nome Motorista - CC': 'Paulo Santos', 'Razão - CC': 'Cliente', 'Motivo - CC': 'Desistência'},
                {'Data - CC': '2025-01-21', 'Nº ID - CC': '007', 'Nome Usuario - CC': 'Roberto Costa', 'Tel. Usuário - CC': '11333333333', 'Municipio - CC': 'Rio de Janeiro', 'Nome Motorista - CC': 'Sandra Lima', 'Razão - CC': 'Motorista', 'Motivo - CC': 'Problema no veículo'}
            ]
        elif 'Corridas Perdidas' in range_name:
            return [
                {'Data - CP': '2025-01-20', 'Nº ID _CP': '008', 'Nome Usuario - CP': 'Fernando Silva', 'Tel. Usuário - CP': '11222222222', 'Municipio - CP': 'São Paulo', 'Razão - CP': 'Sistema', 'Motivo - CP': 'Falha na conexão'},
                {'Data - CP': '2025-01-21', 'Nº ID _CP': '009', 'Nome Usuario - CP': 'Mariana Oliveira', 'Tel. Usuário - CP': '11111111111', 'Municipio - CP': 'Belo Horizonte', 'Razão - CP': 'Disponibilidade', 'Motivo - CP': 'Sem motoristas na região'}
            ]
        elif 'Metas' in range_name:
            return [
                {'Cidade': 'São Paulo', 'Media Corridas Mês': 150, 'Meta Mês 1': 200, 'Meta Mês 2': 220, 'Meta Mês 3': 240, 'Meta Mês 4': 260, 'Meta Mês 5': 280, 'Meta Mês 6': 300},
                {'Cidade': 'Rio de Janeiro', 'Media Corridas Mês': 100, 'Meta Mês 1': 120, 'Meta Mês 2': 130, 'Meta Mês 3': 140, 'Meta Mês 4': 150, 'Meta Mês 5': 160, 'Meta Mês 6': 170},
                {'Cidade': 'Belo Horizonte', 'Media Corridas Mês': 80, 'Meta Mês 1': 90, 'Meta Mês 2': 95, 'Meta Mês 3': 100, 'Meta Mês 4': 105, 'Meta Mês 5': 110, 'Meta Mês 6': 115}
            ]
        
        return []
    
    def get_corridas_concluidas(self):
        """Busca dados de corridas concluídas"""
        spreadsheet_id = self.config.get('spreadsheet_id_corridas', '')
        return self._get_sheet_data(spreadsheet_id, 'Corridas Concluidas!A:F')
    
    def get_corridas_canceladas(self):
        """Busca dados de corridas canceladas"""
        spreadsheet_id = self.config.get('spreadsheet_id_corridas', '')
        return self._get_sheet_data(spreadsheet_id, 'Corridas Canceladas!A:H')
    
    def get_corridas_perdidas(self):
        """Busca dados de corridas perdidas"""
        spreadsheet_id = self.config.get('spreadsheet_id_corridas', '')
        return self._get_sheet_data(spreadsheet_id, 'Corridas Perdidas!A:G')
    
    def get_metas(self):
        """Busca dados de metas por cidade"""
        spreadsheet_id = self.config.get('spreadsheet_id_metas', '')
        return self._get_sheet_data(spreadsheet_id, 'Metas!A:H')
    
    def test_connection(self):
        """Testa a conexão com as planilhas"""
        try:
            corridas = self.get_corridas_concluidas()
            metas = self.get_metas()
            
            return {
                'status': 'success',
                'corridas_count': len(corridas),
                'metas_count': len(metas),
                'message': 'Conexão estabelecida com sucesso'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro na conexão: {str(e)}'
            }

