# Scripts de Inicialização - Dashboard de Mobilidade Urbana

Este documento explica como usar os diferentes scripts de inicialização disponíveis para o Dashboard de Mobilidade Urbana.

## 🚀 Opções de Inicialização

### 1. **NPM Start (Recomendado)**
```bash
npm start
```
- **Plataformas**: Linux, macOS, Windows
- **Dependências**: Node.js, npm, Python3
- **Vantagens**: 
  - Mais simples de usar
  - Logs coloridos e organizados
  - Para automaticamente se um serviço falha
  - Prefixos visuais para distinguir Flask e Vite

### 2. **Script Bash (Linux/macOS)**
```bash
./start.sh
```
- **Plataformas**: Linux, macOS
- **Dependências**: Bash, Python3, npm
- **Vantagens**:
  - Controle nativo do sistema
  - Limpeza automática de processos
  - Verificação de dependências
  - Instalação automática se necessário

### 3. **Script Batch (Windows)**
```cmd
start.bat
```
- **Plataformas**: Windows
- **Dependências**: Python, npm
- **Vantagens**:
  - Abre terminais separados
  - Interface familiar do Windows
  - Fácil de parar (fechar janelas)

### 4. **Script Node.js**
```bash
node start.js
```
- **Plataformas**: Linux, macOS, Windows
- **Dependências**: Node.js, Python3
- **Vantagens**:
  - Multiplataforma
  - Logs organizados por serviço
  - Controle programático

## 📊 Serviços Iniciados

Todos os scripts iniciam dois serviços simultaneamente:

| Serviço | Porta | Descrição | URL |
|---------|-------|-----------|-----|
| **Flask Backend** | 5000 | API e Dashboard de Produção | http://localhost:5000 |
| **Vite Frontend** | 3000 | Servidor de Desenvolvimento | http://localhost:3000 |

## 🛠️ Configuração Inicial

### Pré-requisitos
- **Python 3.7+** com pip
- **Node.js 16+** com npm
- **Git** (para clonagem)

### Primeira Execução
1. Clone o repositório:
   ```bash
   git clone <repositorio>
   cd dashboard-mobilidade-urbana
   ```

2. Instale dependências Python:
   ```bash
   pip3 install -r backend/requirements.txt
   ```

3. Instale dependências Node.js:
   ```bash
   npm install
   ```

4. Execute um dos scripts de inicialização

## 🎯 Qual Script Usar?

### Para Desenvolvimento Diário
```bash
npm start
```
**Motivo**: Mais prático, logs organizados, para automaticamente se algo der errado.

### Para Demonstração/Produção
```bash
./start.sh  # Linux/macOS
start.bat   # Windows
```
**Motivo**: Mais controle, verificação de sistema, melhor para apresentações.

### Para Debugging/Análise
```bash
node start.js
```
**Motivo**: Logs detalhados, controle programático, fácil de modificar.

## 🔧 Personalização

### Modificar Portas
Edite os arquivos de configuração:
- **Flask**: `main.py` - linha com `app.run()`
- **Vite**: `vite.config.js` - propriedade `server.port`

### Adicionar Serviços
Modifique o script desejado para incluir comandos adicionais:
```bash
# Exemplo para start.sh
echo "🗄️ Iniciando Redis..."
redis-server &
```

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```
GOOGLE_API_KEY=sua_chave_aqui
FLASK_ENV=development
VITE_API_URL=http://localhost:5000
```

## 🚨 Solução de Problemas

### Porta em Uso
```bash
# Verificar o que está usando a porta
lsof -i :5000
lsof -i :3000

# Matar processo específico
kill -9 <PID>
```

### Dependências em Falta
```bash
# Reinstalar dependências Python
pip3 install -r backend/requirements.txt --force-reinstall

# Reinstalar dependências Node.js
rm -rf node_modules
npm install
```

### Scripts Não Executam
```bash
# Linux/macOS: dar permissão
chmod +x start.sh

# Windows: executar como administrador
# Right-click → "Run as administrator"
```

## 📝 Logs e Debugging

### Ver Logs em Tempo Real
```bash
# Flask logs
tail -f flask.log

# Vite logs (terminal separado)
npm run dev
```

### Debug Mode
Para habilitar modo debug, modifique o `main.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🔄 Parar os Serviços

### NPM Start
Pressione `Ctrl+C` no terminal

### Script Bash
Pressione `Ctrl+C` no terminal

### Script Batch (Windows)
Feche as janelas dos terminais

### Script Node.js
Pressione `Ctrl+C` no terminal

## 📞 Suporte

Para problemas específicos:
1. Verifique os logs de cada serviço
2. Confirme que todas as dependências estão instaladas
3. Teste cada serviço individualmente
4. Consulte a documentação do projeto principal
