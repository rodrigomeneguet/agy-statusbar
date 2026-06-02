#!/usr/bin/env python3
import os
import sys
import json
import shutil
import platform
import subprocess
import urllib.request
import urllib.error

# Cores globais para UX premium
C_BLUE = '\033[38;2;137;180;250m'
C_GREEN = '\033[38;2;166;227;161m'
C_YELLOW = '\033[38;2;249;226;175m'
C_CYAN = '\033[38;2;137;220;235m'
C_RED = '\033[38;2;243;139;168m'
C_RESET = '\033[0m'

def detect_nerd_fonts():
    """Detecta se há alguma Nerd Font instalada no sistema."""
    system = platform.system()
    
    if system == "Linux" or system == "Darwin":
        # 1. Tentar fc-list se disponível
        if shutil.which("fc-list"):
            try:
                proc = subprocess.run(
                    ["fc-list", ":", "family"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=2.0
                )
                if proc.returncode == 0:
                    families = proc.stdout.lower()
                    if "nerd font" in families or " nf" in families:
                        return True
            except Exception:
                pass
        
        # 2. Varredura manual de pastas de fontes locais e globais
        home = os.path.expanduser("~")
        search_dirs = [
            os.path.join(home, ".local/share/fonts"),
            os.path.join(home, ".fonts"),
            os.path.join(home, "Library/Fonts"),
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/Library/Fonts"
        ]
        for sdir in search_dirs:
            if os.path.exists(sdir):
                for root, _, files in os.walk(sdir):
                    for file in files:
                        lower_file = file.lower()
                        if lower_file.endswith((".ttf", ".otf")):
                            if "nerd" in lower_file or " nf" in lower_file:
                                return True
                                
    elif system == "Windows":
        # 1. Verificar registros do Windows (HKCU e HKLM)
        try:
            import winreg
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
            ]
            for hkey_root, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey_root, subkey) as key:
                        i = 0
                        while True:
                            val_name, _, _ = winreg.EnumValue(key, i)
                            if "nerd" in val_name.lower() or " nf" in val_name.lower():
                                return True
                            i += 1
                except OSError:
                    pass
        except Exception:
            pass
            
        # 2. Escaneamento do diretório do usuário local e de fontes global
        home = os.path.expanduser("~")
        search_dirs = [
            os.path.join(home, "AppData/Local/Microsoft/Windows/Fonts"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        ]
        for sdir in search_dirs:
            if os.path.exists(sdir):
                for root, _, files in os.walk(sdir):
                    for file in files:
                        lower_file = file.lower()
                        if lower_file.endswith((".ttf", ".otf")):
                            if "nerd" in lower_file or " nf" in lower_file:
                                return True
                                
    return False

def download_font_with_progress(url, dest_path):
    """Baixa um arquivo de fonte exibindo uma barra de progresso estilizada."""
    print(f"{C_CYAN}Baixando: {os.path.basename(dest_path)}...{C_RESET}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.info().get('Content-Length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    f.write(buffer)
                    
                    # Desenhar barra de progresso visual
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        filled_length = int(40 * downloaded // total_size)
                        bar = '█' * filled_length + '░' * (40 - filled_length)
                        # Imprimir barra sem pular linha
                        sys.stdout.write(f"\r{C_BLUE}[{bar}]{C_RESET} {percent:.1f}% ({downloaded/(1024*1024):.1f}MB / {total_size/(1024*1024):.1f}MB)")
                        sys.stdout.flush()
            print(f"\n{C_GREEN}✔ Download concluído!{C_RESET}")
            return True
    except Exception as e:
        print(f"\n{C_RED}❌ Falha ao baixar a fonte: {e}{C_RESET}")
        return False

def install_nerd_fonts():
    """Baixa e instala JetBrains Mono Nerd Font no sistema de forma local (sem admin)."""
    system = platform.system()
    home = os.path.expanduser("~")
    
    # Definir diretório de destino
    if system == "Linux":
        font_dir = os.path.join(home, ".local/share/fonts/NerdFonts")
    elif system == "Darwin":
        font_dir = os.path.join(home, "Library/Fonts")
    elif system == "Windows":
        font_dir = os.path.join(home, "AppData/Local/Microsoft/Windows/Fonts")
    else:
        print(f"{C_YELLOW}Aviso: Instalação automática não suportada para o sistema {system}.{C_RESET}")
        return False
        
    try:
        os.makedirs(font_dir, exist_ok=True)
    except Exception as e:
        print(f"{C_RED}Erro ao criar diretório de fontes {font_dir}: {e}{C_RESET}")
        return False
        
    # URLs oficiais da JetBrains Mono Nerd Font
    fonts_to_download = {
        "JetBrainsMonoNerdFont-Regular.ttf": "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/Regular/JetBrainsMonoNerdFont-Regular.ttf",
        "JetBrainsMonoNerdFont-Bold.ttf": "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/Bold/JetBrainsMonoNerdFont-Bold.ttf"
    }
    
    for name, url in fonts_to_download.items():
        dest_path = os.path.join(font_dir, name)
        success = download_font_with_progress(url, dest_path)
        if not success:
            return False
        
    # Procedimento pós-instalação
    if system == "Linux":
        print(f"{C_CYAN}Atualizando cache de fontes do sistema (fc-cache)...{C_RESET}")
        try:
            if shutil.which("fc-cache"):
                subprocess.run(["fc-cache", "-f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{C_GREEN}✔ Cache de fontes atualizado com sucesso!{C_RESET}")
            else:
                print(f"{C_YELLOW}Aviso: Utilitário fc-cache não encontrado. As fontes estarão disponíveis após reiniciar.{C_RESET}")
        except Exception:
            pass
    elif system == "Darwin":
        print(f"{C_GREEN}✔ Fontes instaladas com sucesso em ~/Library/Fonts!{C_RESET}")
            
    elif system == "Windows":
        print(f"{C_CYAN}Registrando fontes no Registro do Windows (HKCU)...{C_RESET}")
        try:
            import winreg
            # HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Fonts
            reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                # Registrar Regular
                winreg.SetValueEx(
                    key, 
                    "JetBrainsMono Nerd Font Regular (TrueType)", 
                    0, 
                    winreg.REG_SZ, 
                    "JetBrainsMonoNerdFont-Regular.ttf"
                )
                # Registrar Bold
                winreg.SetValueEx(
                    key, 
                    "JetBrainsMono Nerd Font Bold (TrueType)", 
                    0, 
                    winreg.REG_SZ, 
                    "JetBrainsMonoNerdFont-Bold.ttf"
                )
            print(f"{C_GREEN}✔ Fontes registradas com sucesso no Registro do Windows!{C_RESET}")
            print(f"{C_YELLOW}Importante: Lembre-se de reiniciar o seu terminal para ativar a nova fonte.{C_RESET}")
        except Exception as e:
            print(f"{C_RED}Erro ao registrar fontes no Registro: {e}{C_RESET}")
            
    return True

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
    
    # Criar diretórios automaticamente se não existirem
    if not os.path.exists(gemini_dir):
        try:
            os.makedirs(gemini_dir, exist_ok=True)
            print(f"{C_YELLOW}Aviso: Diretório ~/.gemini não existia e foi criado automaticamente.{C_RESET}")
        except Exception as e:
            print(f"\033[31mErro ao criar ~/.gemini: {e}{C_RESET}")
            sys.exit(1)
            
    if not os.path.exists(cli_dir):
        try:
            os.makedirs(cli_dir, exist_ok=True)
            print(f"{C_YELLOW}Aviso: Diretório ~/.gemini/antigravity-cli não existia e foi criado automaticamente.{C_RESET}")
        except Exception:
            pass

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
            print(f"\n{C_CYAN}Verificando suporte a ícones...{C_RESET}")
            has_fonts = detect_nerd_fonts()
            
            if has_fonts:
                print(f"{C_GREEN}✔ Nerd Fonts detectadas com sucesso no sistema!{C_RESET}")
                nerd_choice = input("Deseja ativar o suporte a Nerd Fonts por padrão? (S/N): ").strip().lower()
                enable_nerdfonts = nerd_choice in ['s', 'sim', 'y', 'yes', '']  # enter padrão Sim
            else:
                print(f"{C_YELLOW}⚠ Nenhuma Nerd Font foi encontrada no sistema.{C_RESET}")
                print("O agy-statusbar utiliza Nerd Fonts para exibir ícones cyberpunk elegantes.")
                install_choice = input("Deseja baixar e instalar a JetBrainsMono Nerd Font recomendada agora? (S/N): ").strip().lower()
                
                if install_choice in ['s', 'sim', 'y', 'yes', '']:  # enter padrão Sim
                    print(f"\n{C_BLUE}Iniciando a instalação automática de fontes...{C_RESET}")
                    if install_nerd_fonts():
                        print(f"{C_GREEN}✔ JetBrainsMono Nerd Font instalada com sucesso!{C_RESET}")
                        enable_nerdfonts = True
                    else:
                        print(f"{C_RED}❌ Falha na instalação de fontes. O instalador prosseguirá com ícones Unicode normais.{C_RESET}")
                        enable_nerdfonts = False
                else:
                    print(f"{C_YELLOW}Entendido. Prosseguindo com ícones Unicode normais (sem Nerd Fonts).{C_RESET}")
                    enable_nerdfonts = False
        except EOFError:
            print(f"{C_YELLOW}Instalação não interativa detectada (EOF). Mantendo Nerd Fonts desativadas por padrão.{C_RESET}")
    else:
        print(f"{C_YELLOW}Instalação não interativa detectada. Mantendo Nerd Fonts desativadas por padrão.{C_RESET}")

    configured = False
    for spath in settings_paths:
        try:
            # Inicializar settings.json vazio se não existir mas a pasta pai sim
            if not os.path.exists(spath):
                parent_dir = os.path.dirname(spath)
                if os.path.exists(parent_dir):
                    with open(spath, "w", encoding="utf-8") as f:
                        json.dump({}, f)
                        
            if os.path.exists(spath):
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
    
    # Escrever também no arquivo de configuração dedicado para evitar que o Agy limpe as chaves
    statusline_cfg_path = os.path.join(gemini_dir, "statusline_config.json")
    try:
        cfg_data = {}
        if os.path.exists(statusline_cfg_path):
            with open(statusline_cfg_path, "r", encoding="utf-8") as f:
                cfg_data = json.load(f)
        
        if "statusline" not in cfg_data:
            cfg_data["statusline"] = {}
        cfg_data["statusline"]["nerdFonts"] = enable_nerdfonts
        
        with open(statusline_cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2, ensure_ascii=False)
        print(f"{C_GREEN}✔ statusline_config.json atualizado com sucesso em: {statusline_cfg_path}{C_RESET}")
    except Exception as e:
        print(f"{C_YELLOW}Aviso: Não foi possível gravar o arquivo dedicado {statusline_cfg_path}: {e}{C_RESET}")
        
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
