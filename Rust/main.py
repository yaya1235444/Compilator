import argparse
import sys
import re
import os
import shutil
import glob
import subprocess

VERSION = "neburust 5.1.0 (Bilingual Global Build Suite)"

# Couleurs ANSI / ANSI Colors
C_WHITE = "\033[0m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"

# =====================================================================
# SYSTEM LOGS (FRANÇAIS / ENGLISH)
# =====================================================================
def log_step(action, details_fr, details_en):
    """ Affiche les étapes de débug bilingues / Displays bilingual debug steps """
    print(f"[DEBUG] {action:<18} | FR: {details_fr} / EN: {details_en}")

def log_success(msg_fr, msg_en):
    """ Succès en VERT / Success in GREEN """
    print(f"{C_GREEN}✔ SUCCESS | FR: {msg_fr} | EN: {msg_en}{C_WHITE}")

def log_warning(msg_fr, msg_en):
    """ Alerte en JAUNE / Warning in YELLOW """
    print(f"{C_YELLOW}⚠ WARNING | FR: {msg_fr} | EN: {msg_en}{C_WHITE}")

def log_error(err_type, msg_fr, msg_en, help_fr=None, help_en=None):
    """ Erreurs en ROUGE avec aide / Errors in RED with helpful tips """
    print(f"{C_RED}🛑 error[{err_type}]: FR: {msg_fr} / EN: {msg_en}{C_WHITE}")
    if help_fr and help_en:
        print(f"   | {C_GREEN}help/aide: FR: {help_fr} / EN: {help_en}{C_WHITE}")
    sys.exit(1)

# =====================================================================
# SÉCURITÉ & LOGISTIQUE / SECURITY & LOGISTICS
# =====================================================================
def verify_parent_folder(file_path):
    absolute_file = os.path.abspath(file_path)
    parent_dir = os.path.dirname(absolute_file)
    user_home = os.path.abspath(os.path.expanduser("~"))
    
    log_step("Security Check", 
             f"Analyse du fichier: {absolute_file}", 
             f"Analyzing file: {absolute_file}")

    if not parent_dir.startswith(user_home):
        log_error("SECURITY_VIOLATION", 
                  "Dossier parent hors de la zone utilisateur.", 
                  "Parent directory outside the authorized user zone.",
                  f"Le fichier doit être sous : {user_home}", 
                  f"The file must reside under: {user_home}")
        
    log_success("Dossier parent sécurisé et validé.", "Parent directory secured and validated.")
    return absolute_file, parent_dir

def find_and_copy_dependency(dep_name, search_root, target_dir):
    if not dep_name or dep_name in ["C", '"C"']:
        return None
    
    log_step("Linker (Search)", 
             f"Recherche locale de '{dep_name}'...", 
             f"Searching locally for '{dep_name}'...")
             
    search_pattern = os.path.join(search_root, "**", dep_name)
    found_files = glob.glob(search_pattern, recursive=True)

    if not found_files:
        log_warning(f"Fichier '{dep_name}' introuvable. Liaison virtuelle.", 
                    f"File '{dep_name}' not found. Virtual linking applied.")
        return dep_name

    src_file = found_files[0]
    dest_file = os.path.join(target_dir, os.path.basename(src_file))
    
    try:
        shutil.copy2(src_file, dest_file)
        log_success(f"Dépendance '{os.path.basename(src_file)}' copiée dans le build.", 
                    f"Dependency '{os.path.basename(src_file)}' copied into the build.")
        return os.path.basename(src_file)
    except Exception as e:
        log_warning(f"Échec de la copie physique : {e}", f"Physical copy failed: {e}")
        return dep_name

# =====================================================================
# LEXER & PARSER
# =====================================================================
TOKEN_TYPES = [
    ("KW_EXTERN", r"\bextern\b"), ("KW_MOD", r"\bmod\b"), ("KW_FN", r"\bfn\b"),
    ("KW_LET", r"\blet\b"), ("KW_MUT", r"\bmut\b"), ("KW_IF", r"\bif\b"),
    ("KW_ELSE", r"\belse\b"), ("STR_LIT", r'"[^"]*"'),
    ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"), ("ASSIGN", r"="),
    ("COMP", r"==|!=|<=|>=|<|>"), ("NUM", r"\b\d+\b"), ("OP", r"[\+\-\*\/]"),
    ("LBRACE", r"\{"), ("RBRACE", r"\}"), ("LPAREN", r"\("), ("RPAREN", r"\)"),
    ("COLON", r":"), ("SEMI", r";"), ("SKIP", r"[ \t\n]+"), ("ANY", r"."),
]

def parse_and_compile(code, search_root, target_dir):
    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES)
    tokens = []
    
    log_step("Lexer", "Initialisation du scanneur.", "Initializing scanner tokenization.")
    for mo in re.finditer(regex, code):
        if mo.lastgroup != "SKIP": 
            tokens.append((mo.lastgroup, mo.group(mo.lastgroup)))
            
    pos, external_includes, ast_nodes = 0, [], []
    log_step("Parser", "Analyse syntaxique des blocs.", "Parsing syntax structural blocks.")
    
    while pos < len(tokens):
        token_type, token_val = tokens[pos]
        
        if token_type in ["KW_EXTERN", "KW_MOD"]:
            is_mod = (token_type == "KW_MOD")
            pos += 1
            if pos < len(tokens) and tokens[pos][0] in ["STR_LIT", "IDENT"]:
                raw_name = tokens[pos][1].strip('"')
                dep_file_name = f"{raw_name}.py" if is_mod and not raw_name.endswith((".py", ".rs", ".c")) else raw_name
                copied_name = find_and_copy_dependency(dep_file_name, search_root, target_dir)
                if copied_name: external_includes.append(copied_name)
                pos += 1
            if pos < len(tokens) and tokens[pos][0] == "LBRACE":
                pos += 1
                while pos < len(tokens) and tokens[pos][0] != "RBRACE": pos += 1
                pos += 1
            continue
            
        elif token_type == "KW_FN":
            pos += 1
            while pos < len(tokens) and tokens[pos][0] != "LBRACE": pos += 1
            pos += 1
            continue
            
        elif token_type == "KW_LET":
            pos += 1
            if tokens[pos][0] == "KW_MUT": pos += 1
            var_name = tokens[pos][1]
            pos += 2
            val = tokens[pos][1]
            pos += 1
            expr = val
            if pos < len(tokens) and tokens[pos][0] == "OP":
                expr += f" {tokens[pos][1]} {tokens[pos+1][1]}"
                pos += 2
            ast_nodes.append({"type": "let", "var": var_name, "expr": expr})
            while pos < len(tokens) and tokens[pos][0] != "SEMI": pos += 1
            pos += 1
            continue
            
        elif token_type == "KW_IF":
            pos += 1
            cond_expr = f"{tokens[pos][1]} {tokens[pos+1][1]} {tokens[pos+2][1]}"
            pos += 3
            ast_nodes.append({"type": "if", "cond": cond_expr})
            if pos < len(tokens) and tokens[pos][0] == "LBRACE": pos += 1
            continue
            
        elif token_type == "RBRACE":
            ast_nodes.append({"type": "end_block"})
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == "KW_ELSE":
                pos += 1
                ast_nodes.append({"type": "else"})
                if pos < len(tokens) and tokens[pos][0] == "LBRACE": pos += 1
            continue
        else:
            pos += 1
            
    return ast_nodes, external_includes

# =====================================================================
# BUILD ENGINE / MOTEUR DE PRODUCTION
# =====================================================================
def build_native_exe(ast, includes, parent_dir, icon_path=None, no_console=False):
    log_step("Compiler (Build)", "Génération du code source intermédiaire.", "Generating intermediate source code.")
    
    temp_c_file = os.path.join(parent_dir, "temp_build.c")
    temp_rc_file = os.path.join(parent_dir, "temp_icon.rc")
    temp_res_file = os.path.join(parent_dir, "temp_icon.o")
    output_exe_file = os.path.join(parent_dir, "final_program.exe" if os.name == 'nt' else "final_program")
    
    c_content = ["#include <stdio.h>"]
    if no_console and os.name == 'nt':
        c_content.append("#include <windows.h>")
        
    for inc in includes:
        if inc.endswith(".h"): c_content.append(f'#include "{inc}"')
        
    c_content.append("\nint main() {")
    indent = "    "
    for node in ast:
        if node["type"] == "let": c_content.append(f"{indent}int {node['var']} = {node['expr']};")
        elif node["type"] == "if":
            c_content.append(f"{indent}if ({node['cond']}) {{")
            indent += "    "
        elif node["type"] == "else":
            c_content.append(f"{indent}else {{")
            indent += "    "
        elif node["type"] == "end_block":
            if len(indent) > 4: indent = indent[:-4]
            c_content.append(f"{indent}}")
            
    if not no_console:
        c_content.append("    printf(\"[Neburust Console Process Executed Successfully]\\n\");")
    else:
        c_content.append("    MessageBox(NULL, \"Application lancée en mode Fenêtre / Window GUI Mode!\", \"Neburust System\", MB_OK);")
        
    c_content.append("    return 0;\n}")
    
    with open(temp_c_file, "w", encoding="utf-8") as f:
        f.write("\n".join(c_content))

    use_resource = False
    if icon_path and os.name == 'nt':
        if os.path.exists(icon_path):
            log_step("Compiler (Icon)", f"Intégration de l'icône: {icon_path}", f"Binding icon file: {icon_path}")
            with open(temp_rc_file, "w") as rc:
                rc.write(f'MAINICON ICON "{icon_path.replace("\\", "/")}"')
            try:
                subprocess.run(["windres", temp_rc_file, "-o", temp_res_file], check=True)
                use_resource = True
            except Exception:
                log_warning("L'outil de ressource 'windres' est introuvable.", "Resource linker 'windres' not found.")
        else:
            log_warning(f"L'icône n'existe pas : {icon_path}", f"Icon file missing: {icon_path}")

    gcc_cmd = ["gcc", temp_c_file]
    if use_resource: gcc_cmd.append(temp_res_file)
    gcc_cmd.extend(["-o", output_exe_file])
    
    if no_console and os.name == 'nt':
        log_step("Compiler (GUI)", "Application du mode fenêtre sans console.", "Applying window subsystem mode.")
        gcc_cmd.append("-mwindows")

    try:
        log_step("Compiler (GCC)", "Lancement du compilateur natif.", "Invoking native compiler backend.")
        result = subprocess.run(gcc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for tmp in [temp_c_file, temp_rc_file, temp_res_file]:
            if os.path.exists(tmp): os.remove(tmp)
            
        if result.returncode == 0:
            log_success(f"Exécutable créé avec succès -> {output_exe_file}", f"Executable built successfully -> {output_exe_file}")
        else:
            log_error("BUILD_FAILED", "GCC a renvoyé une erreur de compilation.", "GCC compilation backend failed.", result.stderr, result.stderr)
    except FileNotFoundError:
        log_error("MISSING_GCC", "GCC introuvable.", "GCC compiler not found in environmental PATH.")

# =====================================================================
# TRANSPILATION TRADITIONNELLE / CLASSIC TRANSPILATION
# =====================================================================
def generate_python(ast, includes, output_path):
    log_warning("La transpilation Python est en bêtacar.", "Python transpilation is currently in beta phase.")
    content = ["# Generated by neburust", "import sys, os", "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"]
    for inc in includes:
        if inc.endswith(".py"): content.append(f"import {inc.replace('.py', '')}")
    content.append("\ndef main():")
    indent = "    "
    for node in ast:
        if node["type"] == "let": content.append(f"{indent}{node['var']} = {node['expr']}")
        elif node["type"] == "if": content.append(f"{indent}if {node['cond']}:"); indent += "    "
        elif node["type"] == "else": content.append(f"{indent}else:"); indent += "    "
        elif node["type"] == "end_block": 
            if len(indent) > 4: indent = indent[:-4]
    content.append("    print('[Neburust Python Native Execution Completed]')\nmain()")
    with open(output_path, "w", encoding="utf-8") as f: f.write("\n".join(content))
    log_success(f"Fichier écrit : {output_path}", f"File generated: {output_path}")

def generate_c(ast, includes, output_path):
    log_warning("La transpilation C est en bêtacar.", "C transpilation is currently in beta phase.")
    content = ["// Generated by neburust", "#include <stdio.h>"]
    for inc in includes:
        if inc.endswith(".h"): content.append(f'#include "{inc}"')
    content.append("\nint main() {")
    indent = "    "
    for node in ast:
        if node["type"] == "let": content.append(f"{indent}int {node['var']} = {node['expr']};")
        elif node["type"] == "if": content.append(f"{indent}if ({node['cond']}) {{"); indent += "    "
        elif node["type"] == "else": content.append(f"{indent}else {{"); indent += "    "
        elif node["type"] == "end_block":
            if len(indent) > 4: indent = indent[:-4]
            content.append(f"{indent}}")
    content.append("    printf(\"[Neburust C Native Execution Completed]\\n\");\n    return 0;\n}")
    with open(output_path, "w", encoding="utf-8") as f: f.write("\n".join(content))
    log_success(f"Fichier écrit : {output_path}", f"File generated: {output_path}")

# =====================================================================
# CLI BILINGUE ENTRÉE / BILINGUAL CLI ENTRYPOINT
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="neburust compiler", add_help=False)
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--exe", action="store_true")
    parser.add_argument("--python", action="store_true")
    parser.add_argument("--c", action="store_true")
    parser.add_argument("--icon", type=str)
    parser.add_argument("--console", action="store_true")
    parser.add_argument("--noconsole", action="store_true")
    parser.add_argument("--window", action="store_true")
    parser.add_argument("path", nargs="?", type=str)

    args = parser.parse_args()

    if args.version:
        print(VERSION); return
        
    if args.help or not args.path:
        print(f"{C_BOLD}🦀 NEBURUST BILINGUAL COMPILER ENGINE v5.1.0{C_WHITE}\n")
        print(f"{C_BOLD}[FR] Usage:{C_WHITE} neburust --exe [OPTIONS-GRAPHIC] <CHEMIN_FICHIER>")
        print(f"{C_BOLD}[EN] Usage:{C_WHITE} neburust --exe [GRAPHIC-OPTIONS] <FILE_PATH>\n")
        print(C_BOLD + "Options / Flags:" + C_WHITE)
        print("  --exe            [FR] Génère un binaire .exe direct  / [EN] Generates a native binary executable")
        print("  --python         [FR] Transpile vers du script .py   / [EN] Transpiles source into structural Python")
        print("  --c              [FR] Transpile vers du code .c brut / [EN] Transpiles source into clean raw C code")
        print("  --icon <path>    [FR] Injecte une icône (.ico)       / [EN] Injects a custom application icon (.ico)")
        print("  --noconsole      [FR] Masque l'invite de commande     / [EN] Hides the background terminal window")
        print("  --window         [FR] Identique à --noconsole         / [EN] Identical to --noconsole (GUI mode)")
        print("  -v, --version    [FR] Affiche la version             / [EN] Displays current software version")
        print("  -h, --help       [FR] Menu d'aide bilingue           / [EN] Show this bilingual help menu")
        return

    target = "exe" if args.exe else "python" if args.python else "c" if args.c else None
    if not target:
        log_warning("Aucune cible spécifiée. Analyse structurelle seule.", "No target specified. Code checking only.")

    validated_file, parent_dir = verify_parent_folder(args.path)
    user_home = os.path.abspath(os.path.expanduser("~"))

    with open(validated_file, "r", encoding="utf-8") as f:
        code = f.read()

    ast, includes = parse_and_compile(code, user_home, parent_dir)
    print("-" * 80)

    if target == "exe":
        hide_console = args.noconsole or args.window
        build_native_exe(ast, includes, parent_dir, icon_path=args.icon, no_console=hide_console)
    elif target == "python":
        generate_python(ast, includes, os.path.join(parent_dir, "output.py"))
    elif target == "c":
        generate_c(ast, includes, os.path.join(parent_dir, "output.c"))

if __name__ == "__main__":
    main()
