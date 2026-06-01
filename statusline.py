#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import urllib.request
import urllib.parse
import re
import ssl
import time

# Configuração de codificação UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Efeitos ANSI Macchiato / Cyberpunk Neon
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[38;2;147;153;178m"      # Cinza Frio
GREEN = "\033[38;2;166;227;161m"     # Verde Macchiato
YELLOW = "\033[38;2;249;226;175m"    # Amarelo Macchiato
ORANGE = "\033[38;2;250;179;135m"    # Laranja Macchiato
RED = "\033[38;2;243;139;168m"       # Vermelho Macchiato
BLUE = "\033[38;2;137;180;250m"      # Azul Céu
MAGENTA = "\033[38;2;203;166;247m"   # Lavanda/Magenta
CYAN = "\033[38;2;137;220;235m"      # Ciano Elétrico

def format_tokens(n):
    if n is None:
        return "0"
    if n >= 1000000:
        return f"{n / 1000000:.1f}M"
    elif n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)

def get_git_branch(lang):
    try:
        # Obter a branch atual
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=0.8
        )
        if branch_proc.returncode == 0:
            branch = branch_proc.stdout.strip()
            # Verificar se há modificações
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=0.8
            )
            is_dirty = bool(status_proc.stdout.strip())
            return f"{branch}*" if is_dirty else branch
    except Exception:
        pass
    
    if lang == 'zh-tw':
        return '無版本控制'
    elif lang == 'jp':
        return 'バージョン管理なし'
    elif lang == 'pt':
        return 'Sem controle de versão'
    return 'No VC'

def get_cli_memory_mb():
    try:
        ppid = os.getppid()
        if os.path.exists(f"/proc/{ppid}/status"):
            with open(f"/proc/{ppid}/status", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return int(parts[1]) // 1024
    except Exception:
        pass
    try:
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return int(parts[1]) // 1024
    except Exception:
        pass
    return 0

# ==================== IMPLEMENTAÇÃO DO ANDY (ps auxww + lsof) ====================

def find_agy_processes():
    """Encontra processos agy/language_server usando 'ps auxww' (método do Andy)."""
    candidates = []
    try:
        result = subprocess.run(
            ["ps", "auxww"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.0
        )
        lines = result.stdout.split("\n")
        for line in lines:
            lower = line.lower()
            # Regex preciso: \bagy(\s|$) evita falso-positivo com processos que contêm 'agy' no meio
            is_cli = bool(re.search(r'\bagy(\s|$)', lower)) or "antigravity" in lower
            is_lang = "language_server" in lower
            if not is_cli and not is_lang:
                continue
            parts = line.strip().split()
            if len(parts) < 11:
                continue
            try:
                pid = int(parts[1])
            except (IndexError, ValueError):
                continue

            csrf_token = ""
            token_match = re.search(r"--csrf_token(?:=|\s+)([^\s\"']+)", line)
            if token_match:
                csrf_token = token_match.group(1)

            # Penaliza app empacotado (macOS .app bundle)
            penalty = 10 if "/applications/antigravity.app" in lower else 0
            score = (40 if is_cli else 0) + (20 if is_lang else 0) + (10 if csrf_token else 0) - penalty

            candidates.append({
                "pid": pid,
                "csrf_token": csrf_token,
                "score": score,
                "kind": "cli" if is_cli else "language_server"
            })
    except Exception:
        pass

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates

def get_listening_ports(pid):
    """Usa lsof diretamente (método do Andy) — mais portável que /proc/net/tcp."""
    ports = []
    try:
        out = subprocess.check_output(
            ["lsof", "-nP", "-a", "-p", str(pid), "-iTCP", "-sTCP:LISTEN"],
            text=True,
            stderr=subprocess.PIPE,
            timeout=2.0
        )
        matches = re.findall(r":(\d+)\s+\(LISTEN\)", out)
        for m in matches:
            port = int(m)
            if port not in ports:
                ports.append(port)
    except Exception:
        pass
    return sorted(ports)

def request_user_status(port, csrf_token):
    url = f"https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
    payload = {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en"
        }
    }

    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Connect-Protocol-Version": "1",
            "X-Codeium-Csrf-Token": csrf_token
        },
        method="POST"
    )

    with urllib.request.urlopen(req, context=ctx, timeout=1.8) as res:
        return json.loads(res.read().decode("utf-8"))

def format_reset_time(reset_time_str):
    try:
        from datetime import datetime, timezone
        ts = reset_time_str.replace("Z", "+00:00")
        reset_dt = datetime.fromisoformat(ts)
        now_dt = datetime.now(timezone.utc)
        
        diff_seconds = int((reset_dt - now_dt).total_seconds())
        if diff_seconds <= 0:
            return "now"
            
        minutes = (diff_seconds + 59) // 60
        if minutes < 60:
            return f"{minutes}m"
            
        hours = minutes // 60
        mins = minutes % 60
        if hours >= 24:
            days = hours // 24
            rem_hours = hours % 24
            return f"{days}d {rem_hours}h" if rem_hours else f"{days}d"
            
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    except Exception:
        return ""

def fetch_live_quota():
    candidates = find_agy_processes()
    all_models = {}

    for info in candidates:
        ports = get_listening_ports(info["pid"])
        for port in ports:
            try:
                response = request_user_status(port, info["csrf_token"])
                user_status = response.get("userStatus") or {}
                cascade = user_status.get("cascadeModelConfigData") or {}

                for model_cfg in cascade.get("clientModelConfigs") or []:
                    quota_info = model_cfg.get("quotaInfo")
                    if not quota_info:
                        continue

                    fraction = 1.0
                    if "remainingFraction" in quota_info:
                        fraction = float(quota_info["remainingFraction"])
                    elif "resetTime" in quota_info:
                        # Se tiver resetTime mas não tiver remainingFraction, significa que o protobuf omitiu o 0
                        fraction = 0.0
                    else:
                        continue

                    model_obj = model_cfg.get("modelOrAlias") or {}
                    model_id = model_obj.get("model") or "Unknown"
                    label = model_cfg.get("label") or model_id

                    remaining_percentage = fraction * 100.0 if fraction <= 1.0 else fraction
                    remaining_percentage = max(0.0, min(100.0, remaining_percentage))

                    entry = {
                        "name": label,
                        "remaining_percentage": remaining_percentage
                    }

                    if "resetTime" in quota_info:
                        entry["reset_time"] = quota_info["resetTime"]
                        entry["refreshes_in"] = format_reset_time(quota_info["resetTime"])

                    norm_key = re.sub(r'[^a-z0-9]+', '', label.lower())

                    if norm_key not in all_models or remaining_percentage < all_models[norm_key]["remaining_percentage"]:
                        all_models[norm_key] = entry
            except Exception:
                continue

    if all_models:
        return {
            "models": all_models,
            "updatedAt": int(time.time() * 1000)
        }
    return None

# ========================================================================================

def get_semantic_color(pct, reverse=False):
    if reverse:
        # Alta porcentagem é saudável (Quota)
        if pct >= 75:
            return GREEN
        elif pct >= 50:
            return YELLOW
        elif pct >= 25:
            return ORANGE
        return RED
    else:
        # Baixa porcentagem é saudável (Contexto usado)
        if pct < 25:
            return GREEN
        elif pct < 50:
            return YELLOW
        elif pct < 75:
            return ORANGE
        return RED

def make_progress_bar(pct, theme="capsule", width=10, reverse=False):
    ratio = max(0.0, min(1.0, pct / 100.0))
    filled = int(ratio * width)
    empty = width - filled
    color = get_semantic_color(pct, reverse)
    
    if theme == "retro":
        return f"{color}[" + "■" * filled + "□" * empty + f"]{RESET}"
    elif theme == "capsule":
        return f"{color}▕" + "█" * filled + f"{GRAY}" + "░" * empty + f"{color}▏{RESET}"
    else: # minimal
        return f"{color}●{RESET}"

def get_model_color(name):
    lower = (name or "").lower()
    if "claude" in lower:
        return "\033[38;2;221;80;19m" # Laranja Claude
    if "gemini" in lower:
        return "\033[38;2;71;150;227m" # Azul Gemini
    if "gpt" in lower or "chatgpt" in lower:
        return "\033[38;2;116;170;156m" # Verde GPT
    return BLUE

def strip_ansi(s):
    return re.sub(r'[\u001b\u009b][\[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]', '', s)

def get_display_width(s):
    import unicodedata
    width = 0
    for char in s:
        cp = ord(char)
        # Private Use Area (PUA) e Supplementary PUA-A/B para Nerd Fonts / Powerline
        if (0xE000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0x10FFFD):
            width += 2
            continue
        # Emojis e Símbolos de alta definição/largos (2 colunas no terminal)
        if (0x1F300 <= cp <= 0x1F9FF) or (0x1F600 <= cp <= 0x1F64F) or (0x2600 <= cp <= 0x27BF) or (0x1F000 <= cp <= 0x1F9FF):
            width += 2
            continue
        w = unicodedata.east_asian_width(char)
        if w in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def get_settings():
    home = os.path.expanduser("~")
    global_path = os.path.join(home, ".gemini", "settings.json")
    cli_path = os.path.join(home, ".gemini", "antigravity-cli", "settings.json")
    project_path = os.path.join(os.getcwd(), ".gemini", "settings.json")
    
    settings = {}
    
    # Ler configurações globais
    for spath in [global_path, cli_path]:
        if os.path.exists(spath):
            try:
                with open(spath, "r", encoding="utf-8") as f:
                    settings.update(json.load(f))
            except Exception:
                pass
                
    # Ler configurações do projeto
    if os.path.exists(project_path):
        try:
            with open(project_path, "r", encoding="utf-8") as f:
                proj_settings = json.load(f)
                settings.update(proj_settings)
                # Fazer merge inteligente de ui.footer
                if "ui" in proj_settings:
                    if "ui" not in settings:
                        settings["ui"] = {}
                    settings["ui"].update(proj_settings["ui"])
        except Exception:
            pass
            
    return settings

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
        
        settings = get_settings()
        fallback_model = "Gemini 3.5 Flash (Medium)"
        model_obj = data.get("model") or {}
        if model_obj.get("display_name"):
            fallback_model = model_obj["display_name"]
        elif model_obj.get("id"):
            fallback_model = model_obj["id"]

        lang = "pt"
        if "ui" in settings and "language" in settings["ui"]:
            lang = settings["ui"]["language"]
            
        # Carregar configurações visuais
        ui_config = settings.get("ui", {})
        sl_config = ui_config.get("statusline", {})
        theme = sl_config.get("theme", "capsule")
        # nerdFonts padrão desabilitado para usar emojis nítidos se o usuário não possuir Nerd Fonts
        nerd_fonts = sl_config.get("nerdFonts", False)
        progressBarWidth = sl_config.get("progressBarWidth", 10)
        
        footer_items = None
        if "ui" in settings and "footer" in settings["ui"] and "items" in settings["ui"]["footer"]:
            footer_items = settings["ui"]["footer"]["items"]
            
        if not footer_items:
            footer_items = [
                "project-path",
                "git-branch",
                "model-name",
                "context-used",
                "token-count",
                "quota",
                "quota-reset-countdown",
                "memory-usage"
            ]
            
        # 1. Obter informações de Contexto com Cache para evitar "zerão"
        context_window = data.get("context_window") or {}
        conversation_id = data.get("conversation_id") or "default"
        cache_dir = os.path.expanduser("~/.gemini/tmp")
        ctx_cache_path = os.path.join(cache_dir, f"ctx_{conversation_id}.json")
        
        total_input = context_window.get("total_input_tokens") or 0
        total_output = context_window.get("total_output_tokens") or 0
        used_pct_num = context_window.get("used_percentage") or 0.0
        context_size = context_window.get("context_window_size") or 1048576
        
        if total_input == 0 and total_output == 0:
            try:
                if os.path.exists(ctx_cache_path):
                    with open(ctx_cache_path, "r", encoding="utf-8") as f:
                        cached_ctx = json.load(f)
                        total_input = cached_ctx.get("total_input_tokens") or 0
                        total_output = cached_ctx.get("total_output_tokens") or 0
                        if cached_ctx.get("used_percentage"):
                            used_pct_num = float(cached_ctx["used_percentage"])
            except Exception:
                pass
        else:
            try:
                os.makedirs(cache_dir, exist_ok=True)
                with open(ctx_cache_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "total_input_tokens": total_input,
                        "total_output_tokens": total_output,
                        "used_percentage": used_pct_num
                    }, f, indent=2)
            except Exception:
                pass
                
        if context_size > 0 and total_input > 0 and not used_pct_num:
            used_pct_num = (total_input / context_size) * 100.0
            
        remain_ctx = max(0.0, 100.0 - used_pct_num)
        context_color = get_semantic_color(used_pct_num, reverse=False)
        used_pct = f"{used_pct_num:.1f}%"
        total_tokens = total_input + total_output
 
        # 2. Obter informações de Quota Real a partir do cache local daemon
        cache_path = os.path.join(cache_dir, "real_quota_cache.json")
        need_update = True
        cache_data = None
        
        try:
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if int(time.time() * 1000) - cache_data.get("updatedAt", 0) < 30000:
                    need_update = False
        except Exception:
            pass
            
        if need_update:
            try:
                script_path = os.path.abspath(__file__)
                # Passa DISABLE_QUOTA_HOOK=1 para evitar loop recursivo (método Andy)
                env = os.environ.copy()
                env["DISABLE_QUOTA_HOOK"] = "1"
                subprocess.Popen(
                    [sys.executable, script_path, "--fetch-quota"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    env=env
                )
            except Exception:
                pass
                
        norm_model = re.sub(r'[^a-z0-9]+', '', fallback_model.lower())
        model_quota = None
        
        if cache_data and "models" in cache_data:
            models_cache = cache_data["models"]
            # 1. Match exato
            if norm_model in models_cache:
                model_quota = models_cache[norm_model]
            else:
                # 2. Substring fuzzy match
                for k, v in models_cache.items():
                    if norm_model in k or k in norm_model:
                        model_quota = v
                        break
            
            # 3. Match de família/provedor (Gemini, Claude, GPT)
            if not model_quota:
                for family in ["claude", "gemini", "gpt"]:
                    if family in norm_model:
                        for k, v in models_cache.items():
                            if family in k:
                                if not model_quota or v["remaining_percentage"] < model_quota["remaining_percentage"]:
                                    model_quota = v
            
            # 4. Fallback final: menor cota encontrada no cache
            if not model_quota:
                all_vals = list(models_cache.values())
                if all_vals:
                    model_quota = min(all_vals, key=lambda x: x["remaining_percentage"])
                    
        if not model_quota:
            model_quota = {"remaining_percentage": 100, "refreshes_in": ""}
            
        quota_pct = model_quota["remaining_percentage"]
        refreshes_in = model_quota.get("refreshes_in") or ""
        quota_color = get_semantic_color(quota_pct, reverse=True)
        quota_val = f"{int(quota_pct)}%"
        
        # 3. Obter outras telemetrias
        rss_mem = get_cli_memory_mb()
        token_count = f"{format_tokens(total_tokens)} / {format_tokens(context_size)}"
        
        na_label = {
            'zh-tw': '無',
            'jp': 'なし',
            'pt': 'N/D',
            'us': 'N/A'
        }.get(lang, 'N/D')
        
        countdown_val = refreshes_in or na_label
        git_branch = get_git_branch(lang)
        project_full_path = os.getcwd()
        project_name = os.path.basename(project_full_path)
        
        labels = {
            'pt': {
                'project-path': "Projeto",
                'git-branch': "Git",
                'model-name': "Modelo",
                'context-used': "Contexto",
                'token-count': "Tokens",
                'quota': "Disponibilidade",
                'quota-reset-countdown': "Reset Quota",
                'memory-usage': "RAM"
            },
            'us': {
                'project-path': "Project",
                'git-branch': "Git",
                'model-name': "Model",
                'context-used': "Context",
                'token-count': "Tokens",
                'quota': "API Available",
                'quota-reset-countdown': "API Reset in",
                'memory-usage': "RAM"
            },
            'zh-tw': {
                'project-path': "專案",
                'git-branch': "Git 分支",
                'model-name': "模型",
                'context-used': "Context",
                'token-count': "Token",
                'quota': "API 可用額度",
                'quota-reset-countdown': "API 重置倒數",
                'memory-usage': "記憶體"
            },
            'jp': {
                'project-path': "プロジェクト",
                'git-branch': "Gitブランチ",
                'model-name': "モデル",
                'context-used': "コンテキスト",
                'token-count': "トークン数",
                'quota': "API 利用可能枠",
                'quota-reset-countdown': "API リセットまで",
                'memory-usage': "メモリ"
            }
        }
        
        icons_nerd = {
            'project-path': "",                  # Pasta (classic)
            'git-branch': "",                    # Branch Git (classic)
            'model-name': "󰚩",                    # Modelo IA
            'context-used': "",                  # Pilha de Contexto / Lista (classic)
            'token-count': "",                   # Banco de Dados / Tokens (classic)
            'quota': "⚡",                         # Quota (Unicode)
            'quota-reset-countdown': "",         # Relógio / Reset (classic)
            'memory-usage': ""                   # Microchip / RAM (classic)
        }
        
        # Símbolos Unicode modernizados para Emojis nítidos, vibrantes e compatíveis por padrão
        icons_unicode = {
            'project-path': "📂",
            'git-branch': "🌿",
            'model-name': "🤖",
            'context-used': "📊",
            'token-count': "🪙",
            'quota': "⚡",
            'quota-reset-countdown': "⏳",
            'memory-usage': "💻"
        }
        
        values = {
            'project-path': project_name,
            'git-branch': git_branch,
            'model-name': f"{get_model_color(fallback_model)}{BOLD}{fallback_model}{RESET}",
            'context-used': f"{used_pct} {make_progress_bar(used_pct_num, theme, progressBarWidth, reverse=False)}",
            'token-count': token_count,
            'quota': f"{quota_val} {make_progress_bar(quota_pct, theme, progressBarWidth, reverse=True)}",
            'quota-reset-countdown': countdown_val,
            'memory-usage': f"{rss_mem}MB"
        }
        
        colors = {
            'project-path': BLUE,
            'git-branch': YELLOW if "*" in git_branch else GREEN,
            'model-name': get_model_color(fallback_model),
            'context-used': context_color,
            'token-count': GRAY,
            'quota': quota_color,
            'quota-reset-countdown': GRAY,
            'memory-usage': GRAY
        }
        
        # Renderizadores de temas com cores Macchiato
        BG_PILL = "\033[48;2;44;46;58m"
        FG_CAPS = "\033[38;2;44;46;58m"
        
        # Separadores específicos
        if theme == "capsule":
            separator = " "
        elif theme == "retro":
            separator = f"{GRAY}═══{RESET}"
        else: # minimal
            separator = f" {GRAY}│{RESET} "
            
        lang_labels = labels.get(lang) or labels['us']
        
        def render_item(item_id, value, color):
            label = lang_labels.get(item_id, "")
            icon = icons_nerd.get(item_id, "") if nerd_fonts else icons_unicode.get(item_id, "")
            
            content_str = f"{label}: {color}{BOLD}{value}{RESET}" if item_id != "model-name" else f"{label}: {value}"
            
            if theme == "capsule":
                pill_content = f"{BG_PILL}{color}{icon}{RESET}{BG_PILL} {content_str} "
                if nerd_fonts:
                    return f"{FG_CAPS}{RESET}{pill_content}{FG_CAPS}{RESET}"
                else:
                    return f"{FG_CAPS}({RESET}{pill_content}{FG_CAPS}){RESET}"
            elif theme == "retro":
                return f"{color}[{RESET} {color}{icon}{RESET} {content_str} {color}]{RESET}"
            else: # minimal
                return f"{color}{icon}{RESET} {content_str}"
                
        def get_item_width(item_id):
            rendered = render_item(item_id, values[item_id], colors[item_id])
            return get_display_width(strip_ansi(rendered))
            
        # Desconto de 4 colunas garante margem mínima sem desperdiçar espaço
        term_width = max(40, (data.get("terminal_width") or 80) - 4)
        
        lines = []
        current_line = ""
        sep_width = get_display_width(strip_ansi(separator))
        
        for item in footer_items:
            rendered = render_item(item, values[item], colors[item])
            item_width = get_display_width(strip_ansi(rendered))
            
            if current_line == "":
                to_add = rendered
            else:
                to_add = f"{separator}{rendered}"
                
            to_add_plain = strip_ansi(to_add)
            current_plain = strip_ansi(current_line)
            
            if current_line != "" and get_display_width(current_plain) + get_display_width(to_add_plain) > term_width:
                lines.append(current_line)
                current_line = rendered
            else:
                current_line += to_add
                
        if current_line != "":
            lines.append(current_line)
            
        # Margem de alinhamento com a linha anterior
        if theme == "retro":
            for line in lines:
                print(f"{GRAY}╔{RESET}{line}{GRAY}╗{RESET}")
        else:
            for line in lines:
                print(line)
            
        sys.stdout.flush()
        
    except Exception as e:
        sys.stderr.write(f"statusline: erro inesperado: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fetch-quota":
        # Guard contra loop recursivo (método Andy)
        if os.environ.get("DISABLE_QUOTA_HOOK"):
            sys.exit(0)
        try:
            cache = fetch_live_quota()
            if cache:
                cache_dir = os.path.expanduser("~/.gemini/tmp")
                os.makedirs(cache_dir, exist_ok=True)
                cache_path = os.path.join(cache_dir, "real_quota_cache.json")
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2)
        except Exception:
            pass
        sys.exit(0)
    else:
        main()
