# 🔠 Protótipos com Nerd Fonts — agy-statusbar

> **Pré-requisito:** Este arquivo deve ser visualizado em um terminal com uma
> [Nerd Font](https://www.nerdfonts.com/) configurada (ex: JetBrainsMono Nerd Font,
> FiraCode Nerd Font, Hack Nerd Font) para que os ícones renderizem corretamente.

**Modelo atual (emojis)** para comparação:
```
(📂 Projeto: agy-statusbar ) (🌿 Git: main* ) (🤖 Modelo: Claude Sonnet 4.6 (Thinking) )
(📊 Contexto: 5.2% ▕░░░░░░░░░░▏ ) (🪙 Tokens: 55.0k / 1.0M ) (⚡ Disponibilidade: 80% ▕████████░░▏ ) (⏳ Reset Quota: 3h 29m ) (💻 RAM: 4MB )
```

---

## Protótipo 1 — Powerline Arrows (Segmentado)

> **Conceito:** Estilo clássico das barras Powerline/Oh-My-Zsh. Cada segmento tem fundo sólido
> com cor própria e os separadores ``, `` criam um fluxo visual contínuo em "setas".
> Sem labels de texto — só ícone + valor. Ultra-compacto e profissional.

```
 agy-statusbar  main*  Claude Sonnet 4.6 (Thinking)  5.2% ▕░░░░░░░░░░▏  55.0k/1M ⚡ 80% ▕████████░░▏  3h29m  4MB 
```

**Paleta por segmento:**

| Segmento | Ícone | Fundo | Fonte |
|---|---|---|---|
| Projeto | ` ` | Azul escuro `#1e2030` | Branco |
| Git branch | ` ` | Verde `#40a02b` | Preto |
| Modelo | `󰚩 ` | Laranja Claude `#dd5013` | Branco |
| Contexto | ` ` | Cinza `#363a4f` | Verde/Amarelo/Vermelho |
| Tokens | ` ` | Cinza escuro `#2a2d3e` | Cinza claro |
| Quota | `⚡` | Verde → Vermelho dinâmico | Branco |
| Reset | ` ` | Cinza `#363a4f` | Cinza claro |
| RAM | ` ` | Azul escuro `#1e2030` | Ciano |

**Variação full-line (terminal largo ~200 cols):**
```
 agy-statusbar  main*  Claude Sonnet 4.6 (Thinking)   5.2% ▕░░░░░░░░░░▏   55.0k / 1.0M  ⚡ 80% ▕████████░░▏   3h 29m   4MB 
```

**Variação comprimida (terminal ~100 cols):**
```
 agy-statusbar  main*  Claude Sonnet 4.6  5.2%  80% 3h29m  4MB
```

---

## Protótipo 2 — Capsule Nerd (Refinado)

> **Conceito:** Evolução direta do tema atual. Mantém as cápsulas `(...)` mas troca emojis
> por ícones Nerd Fonts monocromáticos — resultado mais limpo, sem o "peso visual" dos emojis
> coloridos. Cada ícone usa a mesma cor semântica do valor que acompanha.

```
( agy-statusbar ) ( main* ) (󰚩 Claude Sonnet 4.6 (Thinking) )
( Contexto: 5.2% ▕░░░░░░░░░░▏ ) ( Tokens: 55.0k / 1.0M ) (⚡ Disponibilidade: 80% ▕████████░░▏ ) ( Reset: 3h 29m ) ( 4MB )
```

**Características:**
- Ícones monocromáticos — sem cor própria, herdam a cor do valor
- Cápsulas `(icon Label: Valor)` — mesma estrutura atual, só troca o ícone
- Ícone e texto ficam na mesma cor semântica (verde/amarelo/laranja/vermelho)
- Resultado: visual mais coeso e menos "festival de cores"

**Comparação direta:**

| Item | Emoji atual | Nerd Font |
|---|---|---|
| Projeto | `📂` | ` ` (nf-cod-folder) |
| Git | `🌿` | ` ` (nf-dev-git_branch) |
| Modelo | `🤖` | `󰚩 ` (nf-md-robot) |
| Contexto | `📊` | ` ` (nf-cod-layers) |
| Tokens | `🪙` | ` ` (nf-fa-database) |
| Quota | `⚡` | `⚡` (mantido — universal) |
| Reset | `⏳` | ` ` (nf-fa-clock_o) |
| RAM | `💻` | ` ` (nf-fa-microchip) |

---

## Protótipo 3 — Minimal Inline (Ultra-Compacto)

> **Conceito:** Sem cápsulas, sem labels. Apenas `ícone valor` separados por `│`.
> Maximiza o espaço disponível — ideal para terminais menores ou quem prefere
> uma statusbar mais discreta, estilo tmux/vim-airline.

**Linha única (terminal ~140 cols):**
```
 agy-statusbar │  main* │ 󰚩 Claude Sonnet 4.6 (Thinking) │  5.2% ▕░░░░░░░░░░▏ │  55.0k/1M │ ⚡ 80% ▕████████░░▏ │  3h29m │  4MB
```

**Com separadores coloridos (versão vibrante):**
```
 agy-statusbar  main*  󰚩 Claude Sonnet 4.6 (Thinking)   5.2% ▕░░░░░░░░░░▏   55.0k/1M  ⚡ 80% ▕████████░░▏   3h29m   4MB
```

**Características:**
- Zero overhead de cápsulas — cada item ocupa o mínimo possível
- Separador `│` fino e discreto (pode ser `·`, `╎` ou `` powerline)
- Labels completamente removidos — só ícone guia o significado
- 30–40% mais compacto que o modelo atual com cápsulas

**Adaptação automática por largura:**

| Largura | Itens exibidos |
|---|---|
| > 160 cols | Todos os 8 itens |
| 100–160 cols | 6 itens (remove Reset e Tokens) |
| < 100 cols | 4 itens ( projeto  git 󰚩 modelo ⚡ quota) |

---

## 📊 Comparativo Final

| Critério | Atual (Emojis) | P1 Powerline | P2 Capsule Nerd | P3 Minimal |
|---|---|---|---|---|
| **Espaço usado** | Médio | Alto | Médio | Mínimo |
| **Impacto visual** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Legibilidade** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Compatibilidade** | ✅ Universal | ⚠️ Só Nerd Fonts | ⚠️ Só Nerd Fonts | ⚠️ Só Nerd Fonts |
| **Curva de implementação** | — (já existe) | Alta (novo tema) | Baixa (troca ícones) | Média (remove labels) |

---

## 🔧 Como ativar Nerd Fonts no projeto atual

Adicione ao `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "ui": {
    "statusline": {
      "nerdFonts": true
    }
  }
}
```

Isso ativa imediatamente o **Protótipo 2 (Capsule Nerd)** — a troca de emojis por ícones
Nerd Fonts já está implementada no código atual via `icons_nerd`.

Os Protótipos 1 (Powerline) e 3 (Minimal) precisariam de novos temas implementados.
