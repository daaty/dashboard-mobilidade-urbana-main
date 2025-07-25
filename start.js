const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Iniciando Dashboard de Mobilidade Urbana...');
console.log('================================================');

// Função para limpar processos ao sair
const processes = [];

function cleanup() {
    console.log('\n🛑 Parando serviços...');
    processes.forEach(proc => {
        if (proc && !proc.killed) {
            proc.kill('SIGTERM');
        }
    });
    console.log('✅ Serviços parados');
    process.exit(0);
}

// Registra a função de limpeza
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
process.on('exit', cleanup);

// Inicia o servidor Flask
console.log('🐍 Iniciando servidor Flask (Backend) na porta 5000...');
const flaskProcess = spawn('python3', ['main.py'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
});

flaskProcess.stdout.on('data', (data) => {
    console.log(`[FLASK] ${data.toString().trim()}`);
});

flaskProcess.stderr.on('data', (data) => {
    console.log(`[FLASK ERROR] ${data.toString().trim()}`);
});

processes.push(flaskProcess);

// Aguarda um pouco antes de iniciar o Vite
setTimeout(() => {
    console.log('⚡ Iniciando servidor Vite (Frontend) na porta 3000...');
    const viteProcess = spawn('npm', ['run', 'dev'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: process.cwd(),
        shell: true
    });

    viteProcess.stdout.on('data', (data) => {
        console.log(`[VITE] ${data.toString().trim()}`);
    });

    viteProcess.stderr.on('data', (data) => {
        console.log(`[VITE ERROR] ${data.toString().trim()}`);
    });

    processes.push(viteProcess);

    console.log('================================================');
    console.log('✅ Serviços iniciados com sucesso!');
    console.log('📊 Dashboard (Produção): http://localhost:5000');
    console.log('🔧 Dashboard (Desenvolvimento): http://localhost:3000');
    console.log('================================================');
    console.log('💡 Pressione Ctrl+C para parar todos os serviços');
    console.log('');
}, 2000);

// Mantém o processo rodando
process.stdin.resume();
