# 🔄 COMO FORÇAR ATUALIZAÇÃO DO FRONTEND

## ✅ **Backend está retornando 304 passageiros corretamente!**

O problema é cache no navegador. Tente estas soluções:

### 🔥 **SOLUÇÃO 1: Hard Reload no Navegador**
1. Abra o DevTools (F12)
2. Clique com botão direito no ícone de reload
3. Selecione "**Esvaziar cache e recarregar forçadamente**" (ou "Empty Cache and Hard Reload")

OU use o atalho:
- **Windows/Linux:** `Ctrl + Shift + R` ou `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`

---

### 🔥 **SOLUÇÃO 2: Limpar Cache do Navegador**
1. Abra DevTools (F12)
2. Vá em "Application" (Chrome) ou "Storage" (Firefox)
3. Clique em "Clear storage" ou "Clear site data"
4. Recarregue a página

---

### 🔥 **SOLUÇÃO 3: Modo Anônimo**
Abra o dashboard em uma aba anônima/privada para testar sem cache

---

### 🔥 **SOLUÇÃO 4: Verificar Network**
1. Abra DevTools (F12)
2. Vá na aba "Network"
3. Marque "Disable cache"
4. Recarregue a página
5. Procure pela requisição `/api/passengers/kpis`
6. Clique nela e veja a resposta - deve mostrar `"total_passengers":304`

---

## ✅ **CONFIRMAÇÃO:**

Execute no navegador (Console do DevTools):
```javascript
fetch('http://localhost:8000/api/passengers/kpis?period=3_months')
  .then(r => r.json())
  .then(d => console.log('Total de passageiros:', d.total_passengers))
```

**Deve retornar: 304**

---

## 🎯 **SE AINDA NÃO FUNCIONAR:**

O componente `PassengersOverview.jsx` pode ter o período hardcoded. 
Verifique se ele está usando `period=3_months` na URL.
