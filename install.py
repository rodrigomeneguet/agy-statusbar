#!/usr/bin/env python3
import os
import sys
import json
import shutil

def main():
    # Cores no terminal
    C_BLUE = '\033[38;2;137;180;250m'
    C_GREEN = '\033[38;2;166;227;161m'
    C_YELLOW = '\033[38;2;249;226;175m'
    C_CYAN = '\033[38;2;137;220;235m'
    C_RESET = '\033[0m'

    print(f"{C_BLUE}=================================================={C_RESET}")
    print(f"{C_GREEN}   Instalador: Cyberpunk statusline para Agy{C_RESET}")
    print(f"{C_BLUE}=================================================={C_RESET}\n")

    home = os.path.expanduser("~")
    gemini_dir = os.path.join(home, ".gemini")
    cli_dir = os.path.join(gemini_dir, "antigravity-cli")
    
    if not os.path.exists(gemini_dir):
        print(f"\033[31mErro: Diretório ~/.gemini não encontrado. O Agy está instalado?{C_RESET}")
        sys.exit(1)

    # 1. Copiar o script
    dest_script = os.path.join(gemini_dir, "statusline.py")
    try:
        shutil.copy("statusline.py", dest_script)
        os.chmod(dest_script, 0o755)
        print(f"{C_GREEN}✔ statusline.py copiado para {dest_script} e marcado como executável.{C_RESET}")
    except Exception as e:
        print(f"\033[31mFalha ao copiar statusline.py: {e}{C_RESET}")
        sys.exit(1)

    # 2. Configurar settings.json do antigravity-cli e do gemini
    settings_paths = [
        os.path.join(cli_dir, "settings.json"),
        os.path.join(gemini_dir, "settings.json")
    ]
    
    # Configuração de Nerd Fonts
    enable_nerdfonts = False
    
    # 1. Verificar argumentos de linha de comando
    if "--nerd-fonts" in sys.argv:
        enable_nerdfonts = True
    elif "--no-nerd-fonts" in sys.argv:
        enable_nerdfonts = False
    # 2. Verificar variável de ambiente
    elif os.environ.get("ENABLE_NERDFONTS") is not None:
        enable_nerdfonts = os.environ.get("ENABLE_NERDFONTS").lower() in ['true', '1', 'yes', 'y']
    # 3. Perguntar interativamente se for um TTY
    elif sys.stdin.isatty():
        try:
            print(f"\n{C_CYAN}Configuração Visual:{C_RESET}")
            print("O agy-statusbar suporta ícones tradicionais de Nerd Fonts de forma compacta.")
            nerd_choice = input("Deseja ativar o suporte a Nerd Fonts? [s/N]: ").strip().lower()
            enable_nerdfonts = nerd_choice in ['s', 'sim', 'y', 'yes']
        except EOFError:
            print(f"{C_YELLOW}Instalação não interativa detectada (EOF). Mantendo Nerd Fonts desativadas por padrão.{C_RESET}")
    else:
        print(f"{C_YELLOW}Instalação não interativa detectada. Mantendo Nerd Fonts desativadas por padrão.{C_RESET}")

    configured = False
    for spath in settings_paths:
        if os.path.exists(spath):
            try:
                with open(spath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                data["statusLine"] = {
                    "type": "command",
                    "command": f"python3 {dest_script}",
                    "enabled": True
                }
                
                # Configurar Nerd Fonts no settings.json
                if "ui" not in data:
                    data["ui"] = {}
                if "statusline" not in data["ui"]:
                    data["ui"]["statusline"] = {}
                data["ui"]["statusline"]["nerdFonts"] = enable_nerdfonts
                
                with open(spath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"{C_GREEN}✔ settings.json atualizado com sucesso em: {spath}{C_RESET}")
                configured = True
            except Exception as e:
                print(f"{C_YELLOW}Aviso: Não foi possível atualizar {spath}: {e}{C_RESET}")
    
    if not configured:
        print(f"{C_YELLOW}Aviso: Nenhum settings.json encontrado para atualizar automaticamente.{C_RESET}")
        print("Crie a configuração manualmente em ~/.gemini/antigravity-cli/settings.json:")
        print(json.dumps({
            "statusLine": {
                "type": "command",
                "command": f"python3 {dest_script}",
                "enabled": True
            }
        }, indent=2))

    print(f"\n{C_GREEN}🚀 Instalação concluída com sucesso!{C_RESET}")
    print(f"{C_YELLOW}Para ativar a barra de status no Agy, digite o seguinte comando dentro da CLI:{C_RESET}")
    print(f"{C_CYAN}   /statusline on{C_RESET}\n")

if __name__ == "__main__":
    main()
