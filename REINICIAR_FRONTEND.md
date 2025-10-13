# 🔄 REINICIAR FRONTEND

## PASSOS:

1. **No terminal "esbuild"** (ou terminal do frontend):
   - Pressione `Ctrl + C` para parar
   - Execute: `npm run dev`

OU

2. **Em um novo terminal PowerShell:**
   ```powershell
   cd frontend
   npm run dev
   ```

---

## ✅ DEPOIS DE REINICIAR:

1. Abra o navegador em `http://localhost:5173`
2. Pressione `Ctrl + Shift + R` (hard reload)
3. Verifique se mostra **304 passageiros**

---

## 🧪 TESTE NO CONSOLE DO NAVEGADOR:

Abra o DevTools (F12) > Console e execute:

```javascript
fetch('http://localhost:8000/api/passengers/kpis?period=3_months')
  .then(r => r.json())
  .then(d => {
    console.log('='.repeat(50))
    console.log('TESTE DO ENDPOINT:')
    console.log('Total de passageiros:', d.total_passengers)
    console.log('Passageiros ativos:', d.active_passengers)
    console.log('Total de corridas:', d.total_rides)
    console.log('Receita total:', d.total_revenue)
    console.log('='.repeat(50))
  })
```

**Deve mostrar: `Total de passageiros: 304`**

Se mostrar 304 no console mas 271 na tela, é cache do React/componente.
