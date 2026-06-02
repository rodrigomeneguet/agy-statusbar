# Contribuindo para agy-statusbar

Obrigado por interessar-se em contribuir! Este guia explica como configurar o ambiente de desenvolvimento, executar testes e enviar mudanças.

## Pré-requisitos

- Python 3.10+
- Git
- (Opcional) [Nerd Fonts](https://www.nerdfonts.com/) para desenvolvimento de ícones

## Configuração do Ambiente

```bash
# Clonar o repositório
git clone https://github.com/rodrigomeneguet/agy-statusbar.git
cd agy-statusbar

# Criar ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências de desenvolvimento
# Nota: requer pyproject.toml (PR #8). Se não existir, instale manualmente:
pip install pytest pytest-cov ruff mypy
```

## Executando Testes

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar com cobertura
pytest --cov=statusline --cov-report=term-missing

# Executar testes lentos (integração)
pytest -m "not slow"
```

## Linting e Formatação

```bash
# Verificar erros de lint
ruff check .

# Formatar código
ruff format .

# Verificar tipos
mypy statusline.py install.py --ignore-missing-imports
```

## Estrutura do Projeto

```
agy-statusbar/
├── statusline.py          # Script principal da statusline
├── install.py             # Instalador interativo
├── install.sh             # Wrapper shell para install.py
├── tests/
│   ├── test_statusline.py # Testes do statusline.py
│   └── test_install.py    # Testes do install.py
├── pyproject.toml         # Configuração do projeto
├── README.md              # Documentação principal
├── CHANGELOG.md           # Histórico de versões
└── CONTRIBUTING.md        # Este arquivo
```

## Enviando Mudanças

1. Crie uma branch para sua feature/fix:
   ```bash
   git checkout -b feat/minha-feature
   ```

2. Faça suas alterações e execute os testes:
   ```bash
   pytest
   ruff check .
   ```

3. Faça commit com mensagem descritiva seguindo [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: adiciona novo recurso X"
   ```

4. Push e crie um Pull Request:
   ```bash
   git push -u origin feat/minha-feature
   ```

## Convenções de Commit

| Prefixo | Descrição |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Alteração de documentação |
| `test:` | Adição/correção de testes |
| `refactor:` | Refatoração sem mudança de comportamento |
| `chore:` | Tarefas de manutenção (CI, dependências, etc.) |

## Reportando Bugs

Ao reportar um bug, por favor inclua:
- Versão do Python
- Sistema operacional
- Passos para reproduzir
- Comportamento esperado vs atual
- Logs de erro (se houver)

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [MIT License](LICENSE).
