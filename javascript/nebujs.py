# Hi, it's me. I'm the creator of this program for those struggling with JavaScript. 
# It translates from Python to JavaScript to add functions. I'll be commenting on tutorials.
# French Project / projet francais et oui baguette
# For your safety, please do not install Nebuljs from any source other than this one, as I analyze modified code to avoid the risk of malware, viruses, and Trojans.

import ast     # FR: Analyse l'arbre syntaxique du code / EN: Analyzes the code's syntax tree
import sys     # FR: Gère les arguments système et la console / EN: Handles system arguments and console
import os      # FR: Gère les dossiers système courants / EN: Handles current system directories
from pathlib import Path  # FR: Manipulation propre des chemins / EN: Clean file path manipulation

# FR: Version actuelle du compilateur / EN: Current version of the compiler
__version__ = "1.0.2"

class NebuJS:
    def __init__(self, file_path): 
        """
        FR: INITIALISATION - Prépare l'environnement de compilation et sécurise les dossiers de sortie.
        EN: INITIALIZATION - Prepares the compilation environment and secures output directories.
        """
        # FR: Recherche et localise le fichier Python cible / EN: Searches and localizes the target Python file
        self.source = self._find_file(file_path)
        
        # FR: Arrêt du programme si le fichier n'existe pas / EN: Stops the program if the file does not exist
        if not self.source:
            print(f"Erreur : Impossible de trouver le fichier '{file_path}'")
            sys.exit(1)
            
        # FR: Création du dossier 'output' juste à côté du fichier source / EN: Creates 'output' folder right next to the source file
        self.output_dir = self.source.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # FR: Initialisation des conteneurs de code / EN: Initialization of code containers
        self.js_lines = []
        self.html_lines = ["<!DOCTYPE html><html><body>"]
        
        print(f"--- Compilation de : {self.source.name} ---")

    def _find_file(self, file_path):
        """
        FR: RECHERCHE DE FICHIER - Empêche les crashs liés aux dossiers temporaires (Nuitka ONEFIL~1).
        EN: FILE SEARCH - Prevents crashes related to temporary extraction folders (Nuitka ONEFIL~1).
        """
        # FR: 1. Test si le chemin fourni est un chemin absolu valide / EN: 1. Test if the provided path is a valid absolute path
        p = Path(file_path).resolve()
        if p.exists() and p.is_file(): 
            return p
        
        # FR: 2. Test si le fichier est dans le dossier actuel de la console / EN: 2. Test if the file is in the current console directory
        cwd_path = Path(os.getcwd()) / file_path
        cwd_path = cwd_path.resolve()
        if cwd_path.exists() and cwd_path.is_file(): 
            return cwd_path
        
        return None # FR: Fichier introuvable / EN: File not found

    def debug(self, category, msg):
        """
        FR: LOG DE DÉBOGAGE - Formate et affiche les détections à l'écran.
        EN: DEBUG LOG - Formats and displays detections on screen.
        """
        print(f"[DEBUG] {category:<12} | {msg}")

    def transpile(self, node):
        """
        FR: TRANSPILEUR - Analyse chaque nœud AST Python pour générer du code Web (JS/HTML).
        EN: TRANSPILER - Analyzes each Python AST node to generate Web code (JS/HTML).
        """

        # --- FR: Détection Tkinter Tk() / EN: Tkinter Tk() Detection ---
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr == 'Tk':
                return # FR: Ignoré car le navigateur s'ouvre déjà / EN: Ignored because browser already opens


        # --- FR: Détection des appels de fonctions / EN: Detection of function calls ---
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            
            # FR: Détection 'print' -> 'console.log' / EN: 'print' detection -> 'console.log'
            if isinstance(func, ast.Name) and func.id == 'print':
                args = [arg.id if isinstance(arg, ast.Name) else f"'{arg.value}'" for arg in node.value.args]
                self.js_lines.append(f"console.log({', '.join(args)});")
                self.debug("Logique", f"print -> {args}")
            
            # FR: Détection Tkinter 'Label' -> Balise HTML <p> / EN: Tkinter 'Label' detection -> HTML <p> tag
            elif isinstance(func, ast.Attribute) and func.attr == 'Label':
                text = node.value.args[0].value if node.value.args else "Label"
                self.html_lines.append(f"<p>{text}</p>")
                self.debug("UI", f"Label -> {text}")
                
            # FR: Détection Tkinter 'mainloop' / EN: Tkinter 'mainloop' detection
            elif isinstance(func, ast.Attribute) and func.attr == 'mainloop':
                return

            # =========================================================================
            # 💡 FR: TUTORIEL 1 - AJOUTER UN COMPOSANT UI (Ex: Un Bouton HTML)
            # 💡 EN: TUTORIAL 1 - ADDING A UI COMPONENT (Ex: An HTML Button)
            # Python target: root.Button("Click me")
            # =========================================================================
            elif isinstance(func, ast.Attribute) and func.attr == 'Button':
                btn_text = node.value.args[0].value if node.value.args else "Bouton"
                self.html_lines.append(f"<button>{btn_text}</button>")
                self.debug("UI", f"Button -> {btn_text}")

            # =========================================================================
            # 💡 FR: TUTORIEL 2 - AJOUTER UNE FONCTION JS NATIVE (Ex: Alerte Pop-up)
            # 💡 EN: TUTORIAL 2 - ADDING A NATIVE JS FUNCTION (Ex: Pop-up Alert)
            # Python target: alert("Hello!")
            # =========================================================================
            elif isinstance(func, ast.Name) and func.id == 'alert':
                alert_text = node.value.args[0].value if node.value.args else ""
                self.js_lines.append(f"alert('{alert_text}');")
                self.debug("Logique", f"alert -> {alert_text}")


        # --- FR: Détection des Variables (=) / EN: Detection of Variables (=) ---
        elif isinstance(node, ast.Assign):
            var_name = node.targets[0].id 
            
            # FR: Détection 'input()' -> 'prompt()' / EN: 'input()' detection -> 'prompt()'
            if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', '') == 'input':
                prompt_txt = node.value.args[0].value if node.value.args else ""
                self.js_lines.append(f"let {var_name} = prompt('{prompt_txt}');")
            # FR: Assigantion de valeurs classiques / EN: Classic value assignment
            else:
                val = node.value.value if isinstance(node.value, ast.Constant) else "null"
                self.js_lines.append(f"let {var_name} = '{val}';")


        # --- FR: Détection des structures If / Else / EN: Detection of If / Else structures ---
        elif isinstance(node, ast.If):
            cond = ast.unparse(node.test)
            self.js_lines.append(f"if ({cond}) {{")
            # FR: Traduction récursive du contenu / EN: Recursive translation of content
            for n in node.body: self.transpile(n)
            self.js_lines.append("}")
            
            if node.orelse:
                self.js_lines.append("else {")
                for n in node.orelse: self.transpile(n)
                self.js_lines.append("}")


        # =========================================================================
        # 💡 FR: TUTORIEL 3 - TRADUIRE LES FONCTIONS PY THON (def MaFonction():)
        # 💡 EN: TUTORIAL 3 - TRANSLATING PYTHON FUNCTIONS (def MyFunction():)
        # Python target: def hello(): ...
        # =========================================================================
        elif isinstance(node, ast.FunctionDef):
            func_name = node.name 
            self.js_lines.append(f"function {func_name}() {{")
            
            # FR: Traduit tout le code à l'intérieur / EN: Translates all code inside
            for n in node.body: 
                self.transpile(n)
                
            self.js_lines.append("}") 
            self.debug("Structure", f"def {func_name}()")


    def run(self):
        """
        FR: EXÉCUTEUR - Parse le code source et génère les fichiers physiques finaux.
        EN: EXECUTER - Parses the source code and writes final physical files.
        """
        try:
            # FR: Parse le fichier Python complet en UTF-8 / EN: Parses the complete Python file in UTF-8
            tree = ast.parse(self.source.read_text(encoding='utf-8'))
            
            # FR: Lance la boucle de transpilation nœud par nœud / EN: Starts the transpilation loop node by node
            for node in tree.body:
                self.transpile(node)
            
            # FR: Lie le fichier JavaScript au fichier HTML / EN: Links the JavaScript file to the HTML file
            self.html_lines.append("<script src='script.js'></script></body></html>")

            # FR: Écriture finale sur le disque dur / EN: Final writing to hard drive
            (self.output_dir / "script.js").write_text("\n".join(self.js_lines), encoding='utf-8')
            (self.output_dir / "index.html").write_text("\n".join(self.html_lines), encoding='utf-8')
            print(f"--- Succès ! Fichiers générés dans : {self.output_dir} ---")
            
        except Exception as e:
            print(f"[ERREUR] : {e}")


# --- FR: ENTRÉE DU PROGRAMME / EN: PROGRAM ENTRY POINT ---
if __name__ == "__main__":
    print("nebujs by Astra")
    print("(C).Copyright Astra")
    
    # FR: Vérification des arguments de la ligne de commande / EN: Checking command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # FR: Menu d'aide (-h) / EN: Help Menu (-h)
        if arg in ("-h", "--help"):
            print("Compile file:  nebujs.exe <name_file.py>, or path the file exemple : nebujs.exe C:/User/Users/Downloads/test.py ")
            print("how to compiler proceed for compile file python File ---> Compiler ---> function detection ---> generator code for js File >>>> JS File")
            sys.exit(0)

        # FR: Menu de version / EN: Version Menu
        if arg in ("--version", "-v"):
            print(f"NebuJS Compiler Version {__version__}")
            sys.exit(0)
            
        # FR: Lancement du compilateur avec le fichier / EN: Launching the compiler with the file
        compiler = NebuJS(arg)
        compiler.run()
    else:
        print("Usage:")
        print("  nebujs.exe <nom_du_fichier.py>  (pour compiler / to compile)")
        print("  nebujs.exe --version            (pour voir la version / to see version)")
