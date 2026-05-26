# ⚡ Cyberpunk Neon Status Bar for Gemini/Agy CLI

Uma barra de status ultra-moderna, minimalista e altamente reativa (estilo *Cyberpunk Neon*) projetada exclusivamente para o novo **Agy CLI (programado em Go)**. 

Ela se integra de forma 100% nativa e assíncrona com os servidores da Google para exibir as suas quotas e consumo em tempo real com excelente fidelidade visual.

---

## 🎨 Principais Recursos (UX/UI Premium)

* **⌥ Workspace & Git (Esquerda):** Caminho compactado (com redução inteligente `~`) + branch e status Git `⎇` (Verde se limpo, Âmbar com asterisco se houver alterações pendentes).
* **Emojis Dinâmicos de Estado (Centro-Esquerdo):** Transição de emojis e cores baseando-se na atividade da IA:
  * `💤 IDLE` (verde) — Quando a IA está aguardando instruções.
  * `🔥 BUSY` (ciano) — Quando a IA está processando ativamente tarefas.
* **ctx: [Barra] (Centro):** Barra de progresso gráfica em blocos (`█░░░░░░░`) mostrando reativamente o consumo da sua janela de contexto (Tokens Usados / Totais), com alertas de cores de segurança (Verde ➜ Amarelo ➜ Magenta).
* **[Quota: [Barra] X%] (Centro-Direito):** Adicionada uma barra gráfica de progresso também para a **Quota real de requisições restante do modelo ativo** nos servidores da Google via renovação de token OAuth automática e assíncrona!
* **◈ Modelo (Direita):** Nome do modelo ativo destacado com símbolo `◈` em ciano.

---

## 📸 Demonstração Visual (No Terminal)

Durante a execução ativa de tarefas:
```text
⌥ tmp                                    🔥 BUSY                                   ctx: ██░░░░░░ 357.5k/1.0M (34.1%)                                   [Quota: ████████ 100%]                                   ◈ Gemini 3.5 Flash (Medium)
```

---

## 🚀 Instalação Rápida (One-Liner)

Basta clonar o repositório e rodar o instalador automatizado no seu terminal (Linux ou macOS):

```bash
git clone https://github.com/rodrigomeneguet/agy-statusbar.git /tmp/agy-statusbar && cd /tmp/agy-statusbar && chmod +x install.sh && ./install.sh && rm -rf /tmp/agy-statusbar
```

---

## 🛠️ Configuração Manual

Se preferir não usar o instalador automático, siga estes passos simples:

1. Baixe o script [statusline.py](statusline.py) e salve-o em `~/.gemini/statusline.py`.
2. Torne-o executável no seu terminal:
   ```bash
   chmod +x ~/.gemini/statusline.py
   ```
3. Abra o arquivo de configurações da CLI em `~/.gemini/antigravity-cli/settings.json` e adicione a seguinte configuração:
   ```json
   "statusLine": {
     "type": "command",
     "command": "python3 /home/SEU_USUARIO/.gemini/statusline.py",
     "enabled": true
   }
   ```
   *(Substitua `SEU_USUARIO` pelo seu usuário correspondente no sistema).*

---

## 💡 Como Ativar na CLI
Após a instalação, inicie a sua sessão do `agy` e digite o seguinte comando diretamente no prompt de conversação para ativá-la:

```bash
/statusline on
```
*(Para desativar a qualquer momento, basta usar `/statusline off`).*

---

## 🔧 Personalização

Você pode abrir o script `~/.gemini/statusline.py` e ajustar facilmente as cores ANSI no topo do arquivo para combinar com o tema do seu terminal (Catppuccin, Nord, Dracula, etc.):

```python
C_BLUE = '\033[38;2;137;180;250m'      # Cor do Workspace
C_GREEN = '\033[38;2;166;227;161m'     # Alerta Seguro
C_YELLOW = '\033[38;2;249;226;175m'    # Alerta de Atenção
C_MAGENTA = '\033[38;2;203;166;247m'   # Alerta Crítico
C_CYAN = '\033[38;2;137;220;235m'      # Cor do Modelo
```
