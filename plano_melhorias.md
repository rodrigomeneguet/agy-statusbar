# Plano de Melhorias UX/UI: 3 Propostas de Design para a Statusline Agy

Agradeço imensamente pelo seu excelente apontamento. Correção justa: a versão portada do repositório realmente não possuía a barra gráfica de progresso, diferentemente do script antigo que servia de base. 

Este plano foi totalmente reformulado sob a ótica de **experiência do usuário (UX/UI)** em interfaces de terminal (TUI). O foco aqui é otimizar a carga cognitiva, melhorar o contraste visual e fornecer a melhor representação de dados a cada tecla pressionada.

Abaixo, apresentamos **3 propostas estéticas completamente diferentes** para você escolher a que melhor se adapta ao seu estilo de trabalho.

---

## 🎨 Princípios UX/UI de Cores Aplicados

Para evitar poluição visual ("efeito árvore de natal"), adotamos as seguintes regras de cores e contraste:
*   **Cores Semânticas Dinâmicas (Alertas):** Elementos numéricos cruciais (Contexto de Tokens e Quotas) utilizam cores semânticas atreladas a limiares de integridade:
    *   `Verde Pastel (Saudável)` [≥ 75%] ➔ Carga cognitiva leve.
    *   `Amarelo Quente (Atenção)` [50% - 74%] ➔ Chamar atenção de forma sutil.
    *   `Laranja Vibrante (Alerta)` [25% - 49%] ➔ Alerta moderado.
    *   `Vermelho Neon (Crítico)` [< 25%] ➔ Alerta máximo.
*   **Cores de Marca (Identidade):** O modelo ativo recebe cor com base na sua marca oficial (Claude: Laranja, Gemini: Azul, GPT: Verde), facilitando a identificação imediata do cérebro sem precisar ler o texto por inteiro.
*   **Hierarquia de Brilho:** Rótulos como "RAM:" ou "Tokens:" ficam em cinza frio de baixo brilho, mantendo os dados de fato (ex: `4MB`, `100%`) em alto brilho para destaque.

---

## 📂 Proposta 1: "Minimalista Moderno" (The Minimalist Powerhouse)
*Inspirado no visual padrão do editor de texto Zed, GitHub CLI e Starship minimal.*

*   **Filosofia:** Design limpo, focado em alta legibilidade com o menor número possível de caracteres de separação. Ideal para quem prefere que o terminal chame pouca atenção, mas forneça dados claros.
*   **Elementos Gráficos:** Sem pílulas espessas. Usa pontos centrais (`·`) e barras verticais ultra-finas (`│`).
*   **Representação da Barra de Progresso:** Um **ponto semântico indicador** (`●`) muda de cor conforme a pressão do contexto.
*   **Paleta de Cores:** Cores em tons pastel de baixo contraste.

### 🖥️ Amostra Visual (Resultado Esperado)

#### Com Nerd Fonts (Recomendado):
```text
  agy-statusbar ·  main*  │  󰚩 Gemini 3.5 Flash  │  ● 4.8% (295k/1.0M)  │  󰓅 Quota: 100%  │   4MB
```

#### Com Unicode Padrão (Fallback):
```text
 [ ◆ agy-statusbar · ◇ main* ]  |  ✦ Gemini 3.5 Flash  |  ● 4.8% (295k/1.0M)  |  Quota: 100%  |  RAM: 4MB
```

---

## 📂 Proposta 2: "Cyberpunk Capsule Grid" (Rounded Bubble UI)
*Inspirado nos temas avançados do Tmux Catppuccin e Powerline.*

*   **Filosofia:** Alta intensidade visual com blocos encapsulados bem definidos. Excelente para quem gosta de um terminal extremamente moderno e que se assemelhe a uma IDE premium.
*   **Elementos Gráficos:** Utiliza separadores arredondados (`` e ``) para criar pílulas/cápsulas flutuantes independentes que dividem os blocos de dados.
*   **Representação da Barra de Progresso:** Um micro-medidor elegante de barras de gradiente vertical (`▂▄▆█`) ou pílula de progresso horizontal moderna (`[▕████░░░░▏]`).
*   **Paleta de Cores:** Alto contraste baseado em tons de neon (Neon Blue, Neon Purple, Emerald Green).

### 🖥️ Amostra Visual (Resultado Esperado)

#### Com Nerd Fonts (Recomendado):
```text
   agy-statusbar   main*     󰚩 Gemini 3.5 Flash     󰓅 ▕██░░░░░░░░▏ 4.8% (295k/1M)      4MB 
```

#### Com Unicode Padrão (Fallback):
```text
 ( ◆ agy-statusbar | ◇ main* )  ( ✦ Gemini 3.5 Flash )  ( ▕██░░░░░░░░▏ 4.8% [295k/1M] )  ( RAM: 4MB )
```

---

## 📂 Proposta 3: "TUI Retro Dashboard" (Technical Grid)
*Inspirado em ferramentas clássicas de sistema como htop, btop e terminais retro.*

*   **Filosofia:** Um visual altamente técnico, estruturado como se fosse o painel de controle de um sistema operacional clássico ou mainframe hacker dos anos 80.
*   **Elementos Gráficos:** Utiliza colchetes robustos (`[` e `]`), linhas de conexão (`──`) e medidores técnicos com caracteres de bloco quadrado (`■` e `□`).
*   **Representação da Barra de Progresso:** Um medidor de blocos quadrados de alta precisão (`[■■■□□□□□]`).
*   **Paleta de Cores:** Monocromático cinza e âmbar/laranja clássico com destaques apenas nos alertas críticos.

### 🖥️ Amostra Visual (Resultado Esperado)

#### Com Nerd Fonts (Recomendado):
```text
 ╔[  agy-statusbar ⎇ main* ]═══[ 󰚩 Gemini 3.5 Flash ]═══[  [■□□□□□□□] 4.8% ]═══[  4MB ]╗
```

#### Com Unicode Padrão (Fallback):
```text
 [◆ agy-statusbar | branch: main*]──[model: Gemini 3.5 Flash]──[ctx: [■□□□□□□□] 4.8%]──[mem: 4MB]
```

---

## ⚙️ Configurações Recomendadas no `settings.json`

Para suportar esta alta customização sem precisar reescrever o script do zero futuramente, introduziremos as seguintes opções de controle visual na seção `"ui"` do `settings.json`:

```json
"ui": {
  "language": "pt",
  "statusline": {
    "theme": "capsule",      // Opções: "minimal", "capsule", "retro"
    "nerdFonts": true,       // Opções: true (com ícones) ou false (classico)
    "progressBarWidth": 10   // Largura visual das barras de progresso
  }
}
```

---

## 🏁 Próximos Passos
Qual das 3 propostas estéticas mais lhe agrada?
1.  **Opção 1:** Minimalista Moderno (foco em clean e no texto)
2.  **Opção 2:** Cyberpunk Capsule Grid (foco em pílulas e gráficos neon)
3.  **Opção 3:** TUI Retro Dashboard (foco técnico, estilo htop)

Assim que você escolher a sua favorita, reescreverei a lógica do nosso script principal para renderizar a interface correspondente.
