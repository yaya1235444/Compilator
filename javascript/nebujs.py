import ast
import sys
import os
from pathlib import Path


__version__ = "1.0.1"

class NebuJS:
    def __init__(self, file_path):
        self.source = self._find_file(file_path)
        
        if not self.source:
            print(f"Erreur : Impossible de trouver le fichier '{file_path}'")
            sys.exit(1)
            
        # L'output va dans le vrai dossier du fichier test.py
        self.output_dir = self.source.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.js_lines = []
        self.html_lines = ["<!DOCTYPE html><html><body>"]
        print(f"--- Compilation de : {self.source.name} ---")

    def _find_file(self, file_path):

        p = Path(file_path).resolve()
        if p.exists() and p.is_file(): 
            return p
        

        cwd_path = Path(os.getcwd()) / file_path
        cwd_path = cwd_path.resolve()
        if cwd_path.exists() and cwd_path.is_file(): 
            return cwd_path
        
        return None

    def debug(self, category, msg):
        print(f"[DEBUG] {category:<12} | {msg}")

    def transpile(self, node):

        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr == 'Tk':
                return


        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            

            if isinstance(func, ast.Name) and func.id == 'print':
                args = [arg.id if isinstance(arg, ast.Name) else f"'{arg.value}'" for arg in node.value.args]
                self.js_lines.append(f"console.log({', '.join(args)});")
                self.debug("Logique", f"print -> {args}")
            

            elif isinstance(func, ast.Attribute) and func.attr == 'Label':
                text = node.value.args[0].value if node.value.args else "Label"
                self.html_lines.append(f"<p>{text}</p>")
                self.debug("UI", f"Label -> {text}")
                

            elif isinstance(func, ast.Attribute) and func.attr == 'mainloop':
                return

        elif isinstance(node, ast.Assign):
            var_name = node.targets[0].id
            if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', '') == 'input':
                prompt_txt = node.value.args[0].value if node.value.args else ""
                self.js_lines.append(f"let {var_name} = prompt('{prompt_txt}');")
            else:
                val = node.value.value if isinstance(node.value, ast.Constant) else "null"
                self.js_lines.append(f"let {var_name} = '{val}';")

        elif isinstance(node, ast.If):
            cond = ast.unparse(node.test)
            self.js_lines.append(f"if ({cond}) {{")
            for n in node.body: self.transpile(n)
            self.js_lines.append("}")
            if node.orelse:
                self.js_lines.append("else {")
                for n in node.orelse: self.transpile(n)
                self.js_lines.append("}")

    def run(self):
        try:

            tree = ast.parse(self.source.read_text(encoding='utf-8'))
            for node in tree.body:
                self.transpile(node)
            
            self.html_lines.append("<script src='script.js'></script></body></html>")

            (self.output_dir / "script.js").write_text("\n".join(self.js_lines), encoding='utf-8')
            (self.output_dir / "index.html").write_text("\n".join(self.html_lines), encoding='utf-8')
            print(f"--- Succès ! Fichiers générés dans : {self.output_dir} ---")
        except Exception as e:
            print(f"[ERREUR] : {e}")

if __name__ == "__main__":

    print("nebujs by Astra")
    print("(C).Copyright Astra")
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("-h", "--help"):
            print("Compile file:  nebujs.exe <name_file.py>, or path the file exemple : nebujs.exe C:/User/Users/Downloads/test.py ")
            print("how to compiler proceed for compile file python File ---> Compiler ---> function detection ---> generator code for js File >>>> JS File")
            sys.exit(0)

        if arg in ("--version", "-v"):
            print(f"NebuJS Compiler Version {__version__}")
            sys.exit(0)
            

        compiler = NebuJS(arg)
        compiler.run()
    else:
        print("Usage:")
        print("  nebujs.exe <nom_du_fichier.py>  (pour compiler)")
        print("  nebujs.exe --version            (pour voir la version)")
