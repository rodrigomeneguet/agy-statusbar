# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

---

## [1.3.0] — 2026-06-01

### ✅ Corrigido
- **Bug crítico de renderização:** todos os itens da barra sumiam exceto o último. Causa: `current_line = to_add` substituía a linha acumulada a cada iteração em vez de concatenar (`current_line += to_add`).
- **Quota reset não detectava o processo agy:** a implementação anterior usava `/proc/{pid}/cmdline` que falhava silenciosamente. Portada a solução do [AndyAWD](https://github.com/AndyAWD/antigravity-cli-statusline) usando `ps auxww`.
- **Portas TCP não detectadas:** substituída leitura de `/proc/{pid}/net/tcp` (sujeita a problemas de namespace) por `lsof -iTCP -sTCP:LISTEN` diretamente.
- **Loop recursivo no daemon de quota:** adicionado guard `DISABLE_QUOTA_HOOK=1` no ambiente do processo filho para evitar que o daemon se reinvoque.
- **Definição duplicada de `term_width`:** removida a primeira definição redundante com `-20` que era sobrescrita mais adiante.

### 🎨 Melhorado
- **Espaçamento das cápsulas reduzido:** separador entre itens de `"  "` (2 espaços) para `" "` (1 espaço); padding interno das cápsulas de `"( icon "` para `"(icon "` — layout mais compacto sem perder legibilidade.
- **Regex de detecção de processo mais preciso:** `"agy " in lower` substituído por `\bagy(\s|$)` para evitar falso-positivos com nomes de processo que contêm "agy" como substring.
- **Margem de `term_width` ajustada:** de `-15` (copiado do Andy) para `-4` — desconto mínimo que evita overflow sem desperdiçar colunas.

### ⬆️ Dependências / Referências
- Implementação de `find_agy_processes()` portada de [AndyAWD/antigravity-cli-statusline/scripts/fetch-local-quota.mjs](https://github.com/AndyAWD/antigravity-cli-statusline/blob/main/scripts/fetch-local-quota.mjs)

---

## [1.2.0] — 2026-05-30

### ✅ Adicionado
- Detecção de quota real por modelo via daemon local (gRPC `GetUserStatus`)
- Cache de quota em `~/.gemini/tmp/real_quota_cache.json` com TTL de 30s
- Countdown de reset de quota (`refreshes_in`)
- Cache de contexto por conversa (`ctx_{conversation_id}.json`) para evitar "contador zerado"
- Suporte a Nerd Fonts (ícones  em vez de emojis)
- Tema `retro` com bordas `╔╗` e separadores `═══`
- Tema `minimal` sem decoração
- Detecção de cor por provedor de modelo (Gemini 🔵, Claude 🟠, GPT 🟢)
- Match fuzzy de modelo no cache (exato → substring → família → menor quota)
- Suporte multilíngue: `pt`, `us`, `zh-tw`, `jp`

### 🎨 Melhorado
- Barra de progresso com 3 variantes: `capsule`, `retro`, `minimal`
- Cores semânticas 4 estágios: Verde ≥75% / Amarelo ≥50% / Laranja ≥25% / Vermelho <25%
- `get_display_width()` com suporte correto a emojis, PUA (Nerd Fonts) e caracteres East Asian

---

## [1.1.0] — 2026-05-27

### ✅ Adicionado
- Sistema de items configuráveis via `ui.footer.items` no `settings.json`
- Items disponíveis: `project-path`, `git-branch`, `model-name`, `context-used`, `token-count`, `quota`, `quota-reset-countdown`, `memory-usage`
- Smart line-wrapping automático baseado na largura real do terminal
- Instalador automático `install.py` com verificação de dependências

### 🎨 Melhorado
- Paleta Catppuccin Macchiato completa (Verde, Amarelo, Laranja, Vermelho, Azul, Magenta, Ciano)
- RAM lida do processo pai (`ppid`) para refletir o consumo real do Agy CLI

---

## [1.0.0] — 2026-05-26

### ✅ Adicionado
- Versão inicial da statusbar em Python puro
- Exibição de: workspace, Git branch, modelo ativo, contexto, quota (estática 100%), memória
- Integração com `statusLine.command` do Agy CLI
- Paleta de cores ANSI com tema Cyberpunk Neon
