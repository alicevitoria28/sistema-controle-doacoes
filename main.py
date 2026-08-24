import sys
import os
import tkinter as tk
import importlib
import sqlite3
import traceback
import threading
import time
import math

sys.path.insert(0, os.path.dirname(__file__) or ".")

def garantir_banco():
    try:
        conn = sqlite3.connect("doacoes.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                quantidade TEXT,
                origem TEXT,
                nome TEXT,
                cor TEXT,
                tamanho TEXT,
                observacoes TEXT,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Erro ao inicializar banco:", e)

class FullscreenSplash:
    def __init__(self, root, text="Carregando..."):
        self.root = root
        # cria toplevel fullscreen e sem bordas
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#ffffff")

        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        self.win.geometry(f"{sw}x{sh}+0+0")

        # conteúdo central
        self.frame = tk.Frame(self.win, bg="#ffffff")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.frame, text=text, font=("Segoe UI", 18, "bold"),
                 bg="#ffffff", fg="#03384d").pack(pady=(0, 12))

        self.canvas = tk.Canvas(self.frame, width=80, height=80, bg="#ffffff", highlightthickness=0)
        self.canvas.pack()
        self._create_spinner()
        self._running = False

        self.win.update_idletasks()
        self.win.update()

    def _create_spinner(self):
        cx, cy = 40, 40
        r = 22
        self.points = []
        colors = ["#0078d7"] * 8
        for i in range(8):
            ang = (i * 360 / 8) * (math.pi / 180.0)  # ✅ usando math
            x = cx + r * (0.8 * math.cos(ang))
            y = cy + r * (0.8 * math.sin(ang))
            p = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=colors[i], outline="")
            self.points.append(p)
        self._angle = 0

    def _step(self):
        n = len(self.points)
        active = int((self._angle / 15)) % n
        for i, p in enumerate(self.points):
            col = "#0078d7" if i == active else "#c6e0ff"
            try:
                self.canvas.itemconfig(p, fill=col)
            except Exception:
                pass
        self._angle += 15
        if self._running:
            self.win.after(60, self._step)

    def start(self):
        self._running = True
        self._step()

    def stop(self):
        self._running = False
        try:
            self.win.destroy()
        except Exception:
            pass

def criar_root_pronto():
    root = tk.Tk()
    root.withdraw()
    root.title("Sistema de Doações")
    try:
        root.configure(bg="#f4faff")
    except Exception:
        pass

    try:
        root.state("zoomed")
    except Exception:
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{sw}x{sh}+0+0")

    return root

def limpar_root_widgets(root):
    for w in list(root.winfo_children()):
        try:
            w.destroy()
        except Exception:
            pass

def carregar_modulos_e_iniciar(root, user_arg=None):
    try:
        garantir_banco()
    except:
        pass

    login_mod = None
    interface_mod = None
    try:
        login_mod = importlib.import_module("login")
        importlib.reload(login_mod)
    except Exception:
        login_mod = None

    try:
        interface_mod = importlib.import_module("interface")
        importlib.reload(interface_mod)
    except Exception:
        interface_mod = None

    def finalizar():
        limpar_root_widgets(root)

        if user_arg:
            if interface_mod:
                try:
                    InterfaceDoacoes = getattr(interface_mod, "InterfaceDoacoes")
                    try:
                        InterfaceDoacoes(root, usuario=user_arg)
                    except TypeError:
                        InterfaceDoacoes(root, usuario=user_arg, ao_sair=None)
                    root.deiconify()
                    root.lift()
                    root.focus_force()
                    return
                except Exception:
                    traceback.print_exc()
            tk.Label(root, text="Erro ao abrir interface.", fg="red", bg="#f4faff").pack(padx=20, pady=20)
            root.deiconify()
            return

        if login_mod:
            try:
                TelaLogin = getattr(login_mod, "TelaLogin")
                def ao_logar(usuario):
                    limpar_root_widgets(root)
                    try:
                        importlib.reload(interface_mod if interface_mod else importlib.import_module("interface"))
                        interface_mod_local = importlib.import_module("interface")
                        InterfaceDoacoes = getattr(interface_mod_local, "InterfaceDoacoes")
                        try:
                            InterfaceDoacoes(root, usuario=usuario)
                        except TypeError:
                            InterfaceDoacoes(root, usuario=usuario, ao_sair=None)
                        root.deiconify()
                        root.lift()
                        root.focus_force()
                        return
                    except Exception:
                        traceback.print_exc()
                        tk.Label(root, text="Erro ao abrir interface após login.", fg="red", bg="#f4faff").pack(padx=20, pady=20)
                        root.deiconify()
                        return

                TelaLogin(root, ao_logar=ao_logar)
                root.deiconify()
                root.lift()
                root.focus_force()
                return
            except Exception:
                traceback.print_exc()

        tk.Label(root, text="Erro ao carregar módulos (login/interface).", fg="red", bg="#f4faff").pack(padx=20, pady=20)
        root.deiconify()
        root.lift()
        root.focus_force()

    root.after(10, finalizar)

def main_entry(user_arg=None):
    root = criar_root_pronto()

    splash = FullscreenSplash(root, text="Aguarde...")
    splash.start()

    def worker():
        try:
            time.sleep(0.8)
            root.after(0, lambda: carregar_modulos_e_iniciar(root, user_arg=user_arg))
        except Exception:
            traceback.print_exc()
        finally:
            time.sleep(0.6)
            root.after(0, splash.stop)

    threading.Thread(target=worker, daemon=True).start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        try:
            root.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    user = None
    if "--user" in sys.argv:
        try:
            idx = sys.argv.index("--user")
            user = sys.argv[idx + 1]
        except Exception:
            user = None

    garantir_banco()
    main_entry(user_arg=user)
