# Guia de Contribuição

Obrigado por considerar contribuir para o Analisador de Microfone com IA! Este documento fornece diretrizes e instruções para contribuir com o projeto.

## 🤝 Como Contribuir

### Reportando Bugs

Antes de criar relatórios de bugs, verifique a [lista de issues](../../issues) pois você pode descobrir que o problema já foi reportado.

**Ao reportar um bug, inclua:**

- **Título claro e descritivo**
- **Descrição exata do comportamento observado**
- **Comportamento esperado**
- **Passos para reproduzir** (com exemplos específicos)
- **Screenshots** (se relevante)
- **Seu ambiente**: SO, versão Python, modelo de Whisper usado
- **Logs** (veja `logs/app.log`)

### Sugerindo Melhorias

- Use um **título claro e descritivo**
- Forneça **descrição detalhada da sugestão**
- Explique **por que** essa melhoria seria útil
- Cite **exemplos** de como outras aplicações implementam isso

### Pull Requests

- Siga o **estilo de código Python** (PEP 8)
- Inclua **testes apropriados**
- Documente **novas funcionalidades**
- Use **mensagens de commit claras**

## 📝 Estilo de Código

### Python

```python
# Use docstrings descritivas
def process_audio(chunk: np.ndarray) -> np.ndarray:
    """
    Processa um chunk de áudio.
    
    Args:
        chunk: Array numpy com samples de áudio
        
    Returns:
        Array processado normalizado
        
    Raises:
        ValueError: Se chunk estiver vazio
    """
    if len(chunk) == 0:
        raise ValueError("Chunk não pode estar vazio")
    return normalize_audio(chunk)
```

```python
# Type hints são bem-vindas
def detect_keywords(text: str, keywords: List[Dict]) -> Optional[Dict]:
    pass
```

### JavaScript

```javascript
// Use JSDoc para funções
/**
 * Conecta ao servidor WebSocket
 * @param {string} url - URL do servidor
 * @param {Object} options - Opções de conexão
 * @returns {Promise<void>}
 */
async function connect(url, options = {}) {
    // implementação
}
```

### HTML/CSS

- Use **classes CSS semânticas**
- Mantenha **HTML estruturado**
- Use **variáveis CSS** para cores/espaçamento
- Certifique-se que é **responsivo**

## 🧪 Testes

### Executando Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_audio.py -v
pytest tests/test_ai.py::TestKeywordDetector::test_exact_match_found

# Com cobertura
pytest --cov=core --cov=audio --cov=ai --cov-report=html
```

### Criando Testes

- Novos recursos devem ter **testes unitários**
- Bugs corrigidos devem ter **testes que reproduzem o problema**
- Cobertura deve ser **≥80%** para código crítico

```python
def test_something():
    """Descrição clara do que está sendo testado"""
    # Arrange - Preparar dados
    audio = np.zeros(1000, dtype=np.float32)
    
    # Act - Executar função
    result = process_audio(audio)
    
    # Assert - Verificar resultado
    assert result.shape == audio.shape
```

## 📦 Dependências

Ao adicionar novas dependências:

1. Use `pip install pacote`
2. Execute `pip freeze > requirements_new.txt`
3. Verifique se é **necessária e não duplicada**
4. Adicione versão pinada: `pacote==1.2.3`
5. Atualize `requirements.txt`
6. Documente no Pull Request **por que** é necessária

## 🔄 Processo de Contribuição

1. **Fork** o repositório
2. **Crie uma branch** de feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra um Pull Request**

### Checklist para Pull Request

- [ ] Meu código segue o estilo do projeto
- [ ] Eu rodei `pytest` localmente e passou
- [ ] Eu adicionei testes que testam minha mudança
- [ ] Eu adicionei documentação apropriada
- [ ] Eu removi código comentado/debug
- [ ] Minhas mudanças não geram novos warnings

## 📚 Documentação

- Use **docstrings descritivas** (Google style)
- Atualize **README.md** se necessário
- Documente **comportamento complexo** com comentários
- Mantenha **DOCUMENTACAO_COMPLETA.md** atualizado

## 🚀 Releases

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (1.0.0)
- MAJOR: mudanças incompatíveis
- MINOR: novos recursos compatíveis
- PATCH: correções de bugs

## ⚖️ Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob o mesmo termo que o projeto.

## 📞 Perguntas?

Abra uma [discussion](../../discussions) ou issue com a tag `question`.

---

**Obrigado por contribuir!** 🎉
