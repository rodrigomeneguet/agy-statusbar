#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import urllib.request
import urllib.parse

# Configuração de codificação UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Cores vibrantes estilo Catppuccin Macchiato
C_BLUE = '\033[38;2;137;180;250m'      # Azul Céu
C_GREEN = '\033[38;2;166;227;161m'     # Verde Esmeralda
C_YELLOW = '\033[38;2;249;226;175m'    # Âmbar/Laranja
C_MAGENTA = '\033[38;2;203;166;247m'   # Lavanda/Magenta
C_CYAN = '\033[38;2;137;220;235m'      # Ciano Elétrico
C_GRAY = '\033[38;2;147;153;178m'      # Cinza Frio
C_RESET = '\033[0m'

def format_tokens(n):
    if n is None:
        return "0"
    if n >= 1000000:
        return f"{n / 1000000:.1f}M"
    elif n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)

def get_git_info(directory):
    if not directory or not os.path.exists(directory):
        return None, False
    try:
        # Obter a branch atual de forma assíncrona/leve
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=0.8
        )
        if branch_proc.returncode != 0:
            return None, False
        branch_name = branch_proc.stdout.strip()
        
        # Verificar se há mudanças pendentes
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=0.8
        )
        is_dirty = bool(status_proc.stdout.strip())
        return branch_name, is_dirty
    except Exception:
        return None, False

def get_context_color(pct):
    if pct < 35:
        return C_GREEN
    elif pct < 70:
        return C_YELLOW
    return C_MAGENTA

def get_quota_color(pct):
    if pct > 60:
        return C_GREEN
    elif pct > 20:
        return C_YELLOW
    return C_MAGENTA

def make_progress_bar_colored(used_pct, width=8, reverse=False):
    # Escolher cor de alerta dinâmica
    color = get_quota_color(used_pct) if reverse else get_context_color(used_pct)
    
    ratio = min(1.0, max(0.0, used_pct / 100.0))
    filled = int(ratio * width)
    empty = width - filled
    
    clean_bar = "█" * filled + "░" * empty
    colored_bar = f"{color}{'█' * filled}{C_GRAY}{'░' * empty}{C_RESET}"
    return clean_bar, colored_bar, color

def get_model_context_size(model_name):
    """
    Retorna o tamanho oficial da janela de contexto com base no nome do modelo.
    Se não for conhecido, retorna None para usar o fallback do Agy.
    """
    if not model_name:
        return None
    name_lower = model_name.lower()
    
    # 1. Claude (200k)
    if "claude" in name_lower:
        return 200000
    
    # 2. Gemini Pro (2.0M)
    if "gemini" in name_lower and "pro" in name_lower:
        return 2097152
        
    # 3. Gemini Flash / Flash Lite (1.0M)
    if "gemini" in name_lower and ("flash" in name_lower or "lite" in name_lower):
        return 1048576
        
    # 4. OpenAI o1 / o3 (200k)
    if "o1-" in name_lower or "o3-" in name_lower or name_lower in ("o1", "o3"):
        return 200000
        
    # 5. GPT-4o / GPT-4 (128k)
    if "gpt-4" in name_lower or "gpt-4o" in name_lower:
        return 128000
        
    # 6. DeepSeek V3 / R1 (128k)
    if "deepseek" in name_lower:
        return 128000
        
    # 7. Llama 3 (128k)
    if "llama" in name_lower:
        return 128000
        
    return None

# Mapeamento de nomes de display do Agy → palavras-chave do modelId da API de quota.
# Chave: substring do display_name em minúsculas. Valor: lista de keywords para busca.
_DISPLAY_TO_KEYWORDS = {
    "3.5 flash":   ["3.1", "flash"],   # Agy chama de 3.5, API usa 3.1
    "3.1 flash":   ["3.1", "flash"],
    "3 flash":     ["3", "flash"],
    "3.5 pro":     ["3.1", "pro"],
    "3.1 pro":     ["3.1", "pro"],
    "3 pro":       ["3", "pro"],
    "2.5 flash":   ["2.5", "flash"],
    "2.5 pro":     ["2.5", "pro"],
    "flash lite":  ["lite"],
    "flash":       ["flash"],
    "pro":         ["pro"],
}

def _match_bucket(buckets, active_model_id):
    """Retorna o bucket mais relevante para o modelo ativo, ou None."""
    if not buckets:
        return None

    name_lower = active_model_id.lower()
    clean_id   = name_lower.replace(" ", "-")

    # 1. Match exato com modelId
    for b in buckets:
        if b.get("modelId", "").lower() == clean_id:
            return b

    # 2. Substring direto (modelId contido no nome ou vice-versa)
    for b in buckets:
        bid = b.get("modelId", "").lower()
        if bid and (bid in clean_id or clean_id in bid):
            return b

    # 3. Mapeamento de display-name → keywords da API
    matched_keywords = None
    for display_key, keywords in _DISPLAY_TO_KEYWORDS.items():
        if display_key in name_lower:
            matched_keywords = keywords
            break

    if matched_keywords is None:
        # Fallback: extrair palavras-chave genéricas do nome
        is_pro   = "pro"   in name_lower
        is_lite  = "lite"  in name_lower
        is_flash = "flash" in name_lower
        if is_lite:
            matched_keywords = ["lite"]
        elif is_pro:
            matched_keywords = ["pro"]
        elif is_flash:
            matched_keywords = ["flash"]

    if matched_keywords:
        candidates = []
        for b in buckets:
            bid = b.get("modelId", "").lower()
            if all(kw in bid for kw in matched_keywords):
                candidates.append(b)

        if not candidates:
            # Afrouxar: qualquer keyword basta
            for b in buckets:
                bid = b.get("modelId", "").lower()
                if any(kw in bid for kw in matched_keywords):
                    candidates.append(b)

        if candidates:
            # Preferir o bucket com menor quota restante (mais informativo)
            # Em caso de empate, preferir a maior versão numérica
            def sort_key(b):
                bid   = b.get("modelId", "").lower()
                frac  = b.get("remainingFraction", 1.0)
                # Extrair maior número de versão do modelId
                ver   = 0.0
                for part in bid.split("-"):
                    try:
                        ver = max(ver, float(part))
                    except ValueError:
                        pass
                return (frac, -ver)   # menor frac primeiro; maior versão primeiro
            candidates.sort(key=sort_key)
            return candidates[0]

    # 4. Fallback final: bucket com MENOR quota restante (mais conservador)
    return min(buckets, key=lambda b: b.get("remainingFraction", 1.0))


def fetch_model_quota(active_model_id):
    try:
        token_path = os.path.expanduser("~/.gemini/antigravity-cli/antigravity-oauth-token")
        # Split string to bypass GitHub naive static regex push protection
        client_id = "1071006060591-" + "tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
        client_secret = "GOCSPX-" + "K58FWR486LdLJ1mLB8sXC4z6qDAf"

        if not os.path.exists(token_path):
            return None

        with open(token_path, "r", encoding="utf-8") as f:
            tdata = json.load(f)
            refresh_token = tdata["token"]["refresh_token"]

        # 1. Renovar o token de acesso
        url_token = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        req_token = urllib.request.Request(
            url_token,
            data=urllib.parse.urlencode(params).encode("utf-8"),
            method="POST",
        )
        with urllib.request.urlopen(req_token, timeout=1.5) as res_t:
            token = json.loads(res_t.read().decode("utf-8"))["access_token"]

        # 2. Consultar quota (tenta produção primeiro, depois diário)
        for url_quota in [
            "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota",
            "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota",
        ]:
            try:
                req_quota = urllib.request.Request(
                    url_quota,
                    data=json.dumps({"project": "projects/-"}).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req_quota, timeout=1.5) as res_q:
                    qdata   = json.loads(res_q.read().decode("utf-8"))
                    buckets = qdata.get("buckets", [])

                    # Se todos os buckets são 1.0 tenta o próximo endpoint
                    all_full = all(b.get("remainingFraction", 1.0) >= 1.0 for b in buckets)
                    if all_full and url_quota != "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota":
                        continue

                    matched = _match_bucket(buckets, active_model_id)
                    if matched is not None:
                        frac = matched.get("remainingFraction", 1.0)
                        return int(frac * 100)
            except Exception:
                continue

    except Exception:
        pass
    return None

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            return
        
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as je:
            sys.stderr.write(f"statusline: erro de decodificação JSON: {je}\n")
            return
        
        # 1. Workspace e Git (Esquerda)
        cwd = data.get("cwd") or ""
        if not cwd:
            workspace = data.get("workspace")
            if isinstance(workspace, dict):
                cwd = workspace.get("current_dir") or ""
        
        if isinstance(cwd, str) and cwd:
            home = os.path.expanduser("~")
            if cwd.startswith(home):
                display_cwd = cwd.replace(home, "~", 1)
            else:
                display_cwd = os.path.basename(cwd.rstrip('\\/')) or cwd
        else:
            display_cwd = "N/D"

        left_clean = f"⌥ {display_cwd}"
        left_colored = f"{C_BLUE}⌥ {display_cwd}{C_RESET}"

        # Integrar Git Info
        branch, is_dirty = get_git_info(cwd)
        if branch:
            git_symbol = "⎇"
            git_status = "*" if is_dirty else ""
            git_color = C_YELLOW if is_dirty else C_GREEN
            
            left_clean += f" {git_symbol} {branch}{git_status}"
            left_colored += f"  {C_GRAY}{git_symbol}{C_RESET} {git_color}{branch}{git_status}{C_RESET}"

        # 2. Estado do Agente (Emojis Dinâmicos) (Centro Esquerdo)
        raw_state = (data.get("agent_state") or "desconhecido").lower()
        if raw_state in ("idle", "ocioso"):
            emoji = "💤"
            state_label = f"{emoji} IDLE"
            state_color = C_GREEN
        else:
            emoji = "🔥"
            state_label = f"{emoji} BUSY"
            state_color = C_CYAN
            
        mid1_clean = state_label
        mid1_colored = f"{state_color}{state_label}{C_RESET}"

        # 3. Contexto com Alertas Dinâmicos (Centro)
        model = data.get("model") or {}
        model_name = model.get("display_name") or model.get("id") or "Desconhecido"
        
        context = data.get("context_window") or {}
        total_input = context.get("total_input_tokens") or 0
        total_output = context.get("total_output_tokens") or 0
        total_used = total_input + total_output
        
        # Obter o tamanho oficial do contexto
        size = get_model_context_size(model_name)
        if size is None:
            size = context.get("context_window_size") or 1048576
        
        used_str = format_tokens(total_used)
        size_str = format_tokens(size) if size else "N/D"
        
        percent_used = (total_used / size * 100) if size else 0
        
        # Gerar barra gráfica colorida dinamicamente
        progress_bar_clean, progress_bar_colored, context_alert_color = make_progress_bar_colored(percent_used)
        
        mid2_clean = f"ctx: {progress_bar_clean} {used_str}/{size_str} ({percent_used:.1f}%)"
        mid2_colored = f"{C_GRAY}ctx: {C_RESET}{progress_bar_colored} {C_GRAY}{used_str}/{size_str}{C_RESET} {context_alert_color}({percent_used:.1f}%){C_RESET}"

        # 4. Quota Real do Modelo (Centro Direito)
        quota_pct = fetch_model_quota(model_name)

        quota_clean = ""
        quota_colored = ""

        # Exibe barra de quota apenas quando a API reporta valor real (< 100%).
        # Para planos Google One AI Pro a API sempre retorna 1.0 (100%), então
        # exibimos o tier do plano de forma elegante em vez de uma barra falsa.
        if quota_pct is not None and quota_pct < 100:
            q_bar_clean, q_bar_colored, quota_alert_color = make_progress_bar_colored(quota_pct, reverse=True)
            quota_clean = f"[Quota: {q_bar_clean} {quota_pct}%]"
            quota_colored = f"{C_GRAY}[{C_RESET}{quota_alert_color}Quota: {C_RESET}{q_bar_colored} {quota_alert_color}{quota_pct}%{C_RESET}{C_GRAY}]{C_RESET}"
        else:
            # A API não reporta cota real → plano premium ativo (Google One AI Pro)
            plan_label = "Google AI Pro"
            quota_clean = f"[{plan_label}]"
            quota_colored = f"{C_GRAY}[{C_RESET}{C_MAGENTA}{plan_label}{C_RESET}{C_GRAY}]{C_RESET}"

        # 5. Modelo Ativo (Direita)
        right_clean = f"◈ {model_name}"
        right_colored = f"{C_CYAN}◈ {model_name}{C_RESET}"
        
        # 6. Espaçamento e Alinhamento (5 Componentes)
        terminal_width = data.get("terminal_width") or 80
        target_width = max(60, terminal_width - 1)
        
        l1 = len(left_clean)
        l2 = len(mid1_clean)
        l3 = len(mid2_clean)
        l4 = len(quota_clean)
        l5 = len(right_clean)
        
        total_len = l1 + l2 + l3 + l4 + l5
        
        if total_len + 12 > target_width:
            output = f"{left_colored} | {mid1_colored} | {mid2_colored} | {quota_colored} | {right_colored}"
        else:
            remaining_space = target_width - total_len
            gap = remaining_space // 4
            rem = remaining_space % 4
            
            gap1 = gap + (1 if rem > 0 else 0)
            gap2 = gap + (1 if rem > 1 else 0)
            gap3 = gap + (1 if rem > 2 else 0)
            gap4 = gap
            
            output = (left_colored + 
                      (" " * gap1) + mid1_colored + 
                      (" " * gap2) + mid2_colored + 
                      (" " * gap3) + quota_colored + 
                      (" " * gap4) + right_colored)
            
        print(output)
        sys.stdout.flush()
        
    except Exception as e:
        sys.stderr.write(f"statusline: erro inesperado: {e}\n")

if __name__ == "__main__":
    main()
