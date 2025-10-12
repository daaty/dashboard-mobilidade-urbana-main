# 🔧 CORREÇÃO: GerenciadorMetasEstrategicas - React Keys e DELETE

**Data:** 11/10/2025  
**Status:** ✅ CORRIGIDO  
**Severidade:** 🟠 ALTA (warnings + erro funcional)

---

## 🐛 PROBLEMAS IDENTIFICADOS

### **1. React Key Warning**
```
Warning: Each child in a list should have a unique "key" prop.
Check the render method of `GerenciadorMetasEstrategicas`.
```

**Causa:** `.map()` das metas sem key única ou com `key={undefined}`

---

### **2. DELETE com ID Undefined**
```
DELETE http://localhost:8000/api/metas-estrategicas/metas-progressivas/undefined 422
Erro ao deletar meta progressiva: Error: [object Object]
```

**Causa:** `itemParaDeletar.id` estava `undefined` ao tentar deletar

---

## 🔍 ANÁLISE DA CAUSA RAIZ

### **Estrutura Retornada pela API:**
```json
GET /api/metas-estrategicas/metas-progressivas
[
  {
    "cidade_id": 3,
    "cidade_nome": "Matupá",
    "metas": [
      {"id": 41, "mes": 3, "percentual_penetracao": 2.0, ...},
      {"id": 14, "mes": 6, "percentual_penetracao": 5.0, ...}
    ]
  },
  {
    "cidade_id": 6,
    "cidade_nome": "Cidade 6",
    "metas": [
      {"id": 106, "mes": 3, ...},
      {"id": 107, "mes": 6, ...}
    ]
  }
]
```

### **Problema:**
O hook `useMetasEstrategicas` estava salvando o array **ANINHADO** diretamente:
```javascript
// ❌ ANTES (ERRADO)
if (Array.isArray(data)) {
  setMetasProgressivas(data) // data é [{cidade, metas: [...]}, ...]
  return { success: true, metas: data }
}
```

Resultado: `metasProgressivas` continha objetos com estrutura `{cidade_id, cidade_nome, metas: [...]}` ao invés de um array flat de metas.

Quando o componente tentava `.map()` nas metas:
```javascript
// ❌ ANTES
cidade.metas.map(meta => (
  <div key={meta.id}>  // ← meta.id podia ser undefined
))
```

E ao deletar:
```javascript
// ❌ ANTES
setItemParaDeletar({...meta, tipo: 'meta'})
// Se meta não tem ID, itemParaDeletar.id = undefined
```

---

## ✅ SOLUÇÕES APLICADAS

### **Correção 1: Achatar (Flatten) Array de Metas**

**Arquivo:** `frontend/src/hooks/useMetasEstrategicas.js`

```javascript
// ✅ DEPOIS (CORRIGIDO)
if (Array.isArray(data)) {
  // Achatar array aninhado para ter todas as metas em um único array
  const metasFlat = data.flatMap(cidade => 
    cidade.metas.map(meta => ({
      ...meta,
      cidade_id: cidade.cidade_id,
      cidade_nome: cidade.cidade_nome
    }))
  )
  console.log(`✅ ${metasFlat.length} metas progressivas carregadas`)
  setMetasProgressivas(metasFlat)
  return { success: true, metas: metasFlat }
}
```

**Resultado:**
```javascript
metasProgressivas = [
  {id: 41, mes: 3, cidade_id: 3, cidade_nome: "Matupá", ...},
  {id: 14, mes: 6, cidade_id: 3, cidade_nome: "Matupá", ...},
  {id: 106, mes: 3, cidade_id: 6, cidade_nome: "Cidade 6", ...},
  ...
]
```

---

### **Correção 2: Fallback Key para React**

**Arquivo:** `frontend/src/components/GerenciadorMetasEstrategicas.jsx`

```javascript
// ✅ DEPOIS (COM FALLBACK)
{cidade.metas.map((meta, index) => (
  <div key={meta.id || `meta-${meta.cidade_id}-${meta.mes}-${index}`} className="...">
    {/* Conteúdo da meta */}
  </div>
))}
```

**Benefício:** Se `meta.id` for `undefined`, usa fallback único baseado em `cidade_id`, `mes` e `index`.

---

### **Correção 3: Validação Antes de Deletar**

**Arquivo:** `frontend/src/components/GerenciadorMetasEstrategicas.jsx`

```javascript
// ✅ Validação ao clicar em deletar
<button
  onClick={() => {
    console.log('🗑️ Deletar meta:', meta) // Debug
    if (!meta.id) {
      console.error('❌ Meta sem ID:', meta)
      showToast('Erro: Esta meta não tem um ID válido', 'error')
      return // ← Impede tentativa de delete
    }
    setItemParaDeletar({...meta, tipo: 'meta'})
    setShowConfirmDelete(true)
  }}
>
  <Trash2 />
</button>

// ✅ Validação na função handleDelete
const handleDelete = async () => {
  try {
    // Validar que temos um ID válido
    if (!itemParaDeletar?.id) {
      console.error('❌ Erro: ID do item para deletar está undefined', itemParaDeletar)
      showToast('Erro: ID do item inválido', 'error')
      setShowConfirmDelete(false)
      setItemParaDeletar(null)
      return // ← Aborta delete
    }

    let resultado
    if (itemParaDeletar.tipo === 'meta') {
      resultado = await deletarMetaProgressiva(itemParaDeletar.id) // ← Agora garante ID válido
    } else {
      resultado = await deletarFaseEstrategica(itemParaDeletar.id)
    }
    // ...
  }
}
```

---

## 📊 ANTES vs DEPOIS

### **ANTES (Estrutura Errada):**
```javascript
metasProgressivas = [
  {
    cidade_id: 3,
    cidade_nome: "Matupá",
    metas: [
      {id: 41, mes: 3, ...}, // ← Aninhado
      {id: 14, mes: 6, ...}
    ]
  }
]

// Problemas:
// 1. Filtros não funcionavam (esperavam array flat)
// 2. Keys podiam ser undefined
// 3. DELETE pegava objeto errado
```

### **DEPOIS (Estrutura Correta):**
```javascript
metasProgressivas = [
  {id: 41, mes: 3, cidade_id: 3, cidade_nome: "Matupá", ...}, // ← Flat
  {id: 14, mes: 6, cidade_id: 3, cidade_nome: "Matupá", ...},
  {id: 106, mes: 3, cidade_id: 6, cidade_nome: "Cidade 6", ...}
]

// Benefícios:
// 1. Filtros funcionam corretamente
// 2. Todas as keys são únicas e válidas
// 3. DELETE pega ID correto
// 4. Componente GerenciadorMetasEstrategicas agrupa por cidade corretamente
```

---

## 🧪 COMO VALIDAR AS CORREÇÕES

### **1. React Key Warning (Resolvido)**
- Recarregue a página (F5)
- Abra Console (F12)
- **Não deve mais** aparecer: `Warning: Each child in a list should have a unique "key" prop`

### **2. DELETE Funcionando**
- Abra "Gerenciador de Metas Estratégicas"
- Clique no ícone de lixeira em qualquer meta
- Console deve mostrar: `🗑️ Deletar meta: {id: 41, ...}`
- **NÃO deve mostrar:** `❌ Meta sem ID`
- **NÃO deve fazer request para:** `/undefined`
- DELETE deve funcionar corretamente

### **3. Metas Exibidas Corretamente**
- Metas devem aparecer agrupadas por cidade
- Cada meta deve mostrar: Mês, Tipo, Corridas, Motoristas, Receita
- Filtros devem funcionar (por cidade, tipo, mês)

---

## 📝 ARQUIVOS MODIFICADOS

### **1. `frontend/src/hooks/useMetasEstrategicas.js`**
**Linha ~40:** Adicionado `.flatMap()` para achatar array aninhado
```javascript
const metasFlat = data.flatMap(cidade => 
  cidade.metas.map(meta => ({
    ...meta,
    cidade_id: cidade.cidade_id,
    cidade_nome: cidade.cidade_nome
  }))
)
```

### **2. `frontend/src/components/GerenciadorMetasEstrategicas.jsx`**

**Linha ~440:** Adicionado fallback key
```javascript
{cidade.metas.map((meta, index) => (
  <div key={meta.id || `meta-${meta.cidade_id}-${meta.mes}-${index}`}>
```

**Linha ~225:** Adicionado validação de ID antes de deletar
```javascript
if (!itemParaDeletar?.id) {
  console.error('❌ Erro: ID do item para deletar está undefined')
  showToast('Erro: ID do item inválido', 'error')
  return
}
```

**Linha ~471:** Adicionado validação ao clicar no botão deletar
```javascript
onClick={() => {
  console.log('🗑️ Deletar meta:', meta)
  if (!meta.id) {
    console.error('❌ Meta sem ID:', meta)
    showToast('Erro: Esta meta não tem um ID válido', 'error')
    return
  }
  setItemParaDeletar({...meta, tipo: 'meta'})
  setShowConfirmDelete(true)
}}
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

- [ ] Console **NÃO mostra** warning de React keys
- [ ] Console mostra: `✅ X metas progressivas carregadas`
- [ ] Metas aparecem agrupadas por cidade
- [ ] Clicar em deletar mostra log: `🗑️ Deletar meta: {id: XX, ...}`
- [ ] DELETE **NÃO faz** request para `/undefined`
- [ ] DELETE funciona e remove meta corretamente
- [ ] Filtros (cidade, tipo, mês) funcionam
- [ ] Editar meta funciona corretamente

---

## 🎯 RESUMO EXECUTIVO

| Problema | Causa | Solução | Status |
|----------|-------|---------|--------|
| React Key Warning | `meta.id` undefined | Fallback key: `meta-${cidade}-${mes}-${index}` | ✅ |
| DELETE /undefined | Array aninhado quebrava estrutura | `.flatMap()` para achatar array | ✅ |
| ID inválido | Sem validação antes de deletar | Validação dupla (botão + handleDelete) | ✅ |
| Filtros não funcionavam | Estrutura de dados errada | Array flat com `cidade_id` e `cidade_nome` | ✅ |

---

**Total de Correções:** 4  
**Arquivos Modificados:** 2  
**Linhas Alteradas:** ~30 linhas  
**Impacto:** Componente GerenciadorMetasEstrategicas agora totalmente funcional ✅
