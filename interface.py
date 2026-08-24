import os
import sys
import importlib
import traceback
import subprocess
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from banco_dados import BancoDoacoes
import bcrypt
import time
import math

SPAWN_WAIT_MS = 800
CALLBACK_DELAY_MS = 1

def _spawn_login_window():
    script = os.path.join(os.path.dirname(__file__), "login_window.py")
    python_exe = sys.executable
    if not os.path.exists(script):
        return False
    try:
        if sys.platform.startswith("win"):
            CREATE_NO_WINDOW = 0x08000000
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            flags = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
            subprocess.Popen([python_exe, script], creationflags=flags, shell=False)
        else:
            subprocess.Popen([python_exe, script])
        return True
    except Exception:
        traceback.print_exc()
        return False

def _create_fullscreen_overlay(root, text="Aguarde", spinner_radius=30):

    try:
        overlay = tk.Toplevel(root)
        try:
            overlay.overrideredirect(True)
        except Exception:
            pass
        try:
            overlay.attributes("-topmost", True)
        except Exception:
            pass
        try:
            overlay.attributes("-fullscreen", True)
        except Exception:
            try:
                sw = overlay.winfo_screenwidth()
                sh = overlay.winfo_screenheight()
                overlay.geometry(f"{sw}x{sh}+0+0")
            except Exception:
                pass

        try:
            overlay.configure(bg="#000000")
        except Exception:
            pass

        try:
            overlay.lift()
            overlay.update_idletasks()
        except Exception:
            pass

        container = tk.Frame(overlay, bg="#000000")
        container.place(relx=0.5, rely=0.5, anchor="center")

        lbl = tk.Label(container, text=text, font=("Segoe UI", 20, "bold"), bg="#000000", fg="#00a2ff")
        lbl.pack(pady=(0, 12))

        spinner_size = max(120, spinner_radius * 4)
        canvas = tk.Canvas(container, width=spinner_size, height=spinner_size, bg="#000000", highlightthickness=0, bd=0)
        canvas.pack()

        cx = spinner_size // 2
        cy = spinner_size // 2
        bola_r = 8
        bx = cx + spinner_radius
        by = cy
        bola = canvas.create_oval(bx - bola_r, by - bola_r, bx + bola_r, by + bola_r, fill="#00a2ff", outline="")

        estado = {
            "angulo": 0,
            "rodando": True,
            "after_id": None,
            "overlay": overlay,
            "canvas": canvas,
            "bola": bola,
            "cx": cx,
            "cy": cy,
            "r": spinner_radius
        }

        def animar():
            if not overlay.winfo_exists() or not estado.get("rodando", False):
                return
            estado["angulo"] = (estado["angulo"] + 20) % 360
            rad = math.radians(estado["angulo"])
            x = estado["cx"] + estado["r"] * math.cos(rad)
            y = estado["cy"] + estado["r"] * math.sin(rad)
            try:
                canvas.coords(estado["bola"], x - bola_r, y - bola_r, x + bola_r, y + bola_r)
            except Exception:
                pass
            try:
                aid = overlay.after(18, animar)
                estado["after_id"] = aid
            except Exception:
                estado["after_id"] = None

        animar()
        try:
            overlay.update_idletasks()
            overlay.update()
        except Exception:
            pass

        return overlay, estado
    except Exception:
        traceback.print_exc()
        return None, None

def _destroy_overlay_safe(estado):
    try:
        if not estado:
            return
        estado["rodando"] = False
        overlay = estado.get("overlay")
        aid = estado.get("after_id")
        if overlay and aid:
            try:
                overlay.after_cancel(aid)
            except Exception:
                pass
        if overlay and overlay.winfo_exists():
            try:
                overlay.destroy()
            except Exception:
                try:
                    overlay.withdraw()
                except Exception:
                    pass
                try:
                    overlay.destroy()
                except Exception:
                    pass
    except Exception:
        pass

class InterfaceDoacoes(ttk.Frame):
    def __init__(self, root, usuario=None, ao_sair=None):
        super().__init__(root)
        self.root = root
        self.usuario = usuario
        self.ao_sair = ao_sair
        self.pack(fill="both", expand=True)

        if usuario:
            self.db = BancoDoacoes(db_nome=f"doacoes_{usuario}.db")
        else:
            self.db = BancoDoacoes()

        try:
            self.style = ttk.Style("darkly")
        except Exception:
            self.style = None
        self._criar_widgets()
        self._atualizar_tabela()

    def _criar_widgets(self):
        self.frame_principal = ttk.Frame(self.root, padding=20)
        self.frame_principal.pack(fill=BOTH, expand=True)

        header = ttk.Frame(self.frame_principal)
        header.pack(fill=X, pady=(0, 6))

        cfg_btn = ttk.Button(header, text="⚙", width=6, bootstyle="link", command=self._abrir_menu_config)
        cfg_btn.pack(side=LEFT, padx=(0, 10))

        self.titulo_label = ttk.Label(
            self.frame_principal,
            text="📦 Controle de Doações",
            font=("Segoe UI", 22, "bold"),
            anchor="center",
        )
        self.titulo_label.pack(pady=(0, 20))

        self.tema_switch = ttk.Checkbutton(
            self.frame_principal,
            text="🌞 / 🌙",
            bootstyle="round-toggle",
            command=self._alternar_tema,
        )
        try:
            self.tema_switch.place(x=1020, y=20)
        except Exception:
            self.tema_switch.pack(anchor="ne")

        self.frame_campos = ttk.Frame(self.frame_principal)
        self.frame_campos.pack(pady=10)

        self.nome_entry = self._criar_campo("Nome do Doador:")
        self.item_cb = self._criar_combo("Item:", ["Roupas", "Sapatos", "Móveis", "Dinheiro", "Outros"])
        self.quantidade_entry = self._criar_campo("Quantidade:")
        self.cor_entry = self._criar_campo("Cor:")
        self.tamanho_entry = self._criar_campo("Tamanho:")
        self.origem_entry = self._criar_campo("Origem:")
        self.observacoes_entry = self._criar_campo("Observações:")

        self.frame_botoes = ttk.Frame(self.frame_principal)
        self.frame_botoes.pack(pady=15)

        self._criar_botao("➕ Adicionar", "info-outline", self._adicionar_dado)
        self._criar_botao("✏️ Editar", "warning-outline", self._editar_dado)
        self._criar_botao("🗑️ Excluir", "danger-outline", self._excluir_item)
        self._criar_botao("📤 Exportar Excel", "success-outline", self._exportar_excel)

        self._criar_tabela()

    def _criar_campo(self, texto):
        frame = ttk.Frame(self.frame_campos)
        frame.pack(fill=X, pady=5)
        ttk.Label(frame, text=texto, width=18, anchor=W).pack(side=LEFT)
        entry = ttk.Entry(frame, width=60)
        entry.pack(side=LEFT, padx=5)
        return entry

    def _criar_combo(self, texto, valores):
        frame = ttk.Frame(self.frame_campos)
        frame.pack(fill=X, pady=5)
        ttk.Label(frame, text=texto, width=18, anchor=W).pack(side=LEFT)
        cb = ttk.Combobox(frame, values=valores, width=58)
        cb.pack(side=LEFT, padx=5)
        return cb

    def _criar_botao(self, texto, estilo, comando):
        btn = ttk.Button(self.frame_botoes, text=texto, bootstyle=estilo, command=comando)
        btn.pack(side=LEFT, padx=10, ipadx=5, ipady=3)
        return btn

    def _criar_tabela(self):
        colunas = ["Nome do Doador", "Item", "Quantidade", "Cor", "Tamanho", "Origem", "Data", "Observações"]
        self.tree = ttk.Treeview(self.frame_principal, columns=colunas, show="headings", height=12)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor=CENTER)
        self.tree.pack(fill=BOTH, expand=True, pady=10)
        self.tree.bind("<ButtonRelease-1>", self._selecionar_item)

    def _atualizar_tabela(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        dados = self.db.ler_dados()
        for item in dados:
            try:
                self.tree.insert("", "end", values=[item[5], item[1], item[2], item[6], item[7], item[4], item[3], item[8]])
            except Exception:
                pass

    def _abrir_menu_config(self):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Editar perfil", command=self._menu_editar_perfil)
        menu.add_command(label="Alterar senha", command=self._menu_alterar_senha)
        menu.add_separator()
        menu.add_command(label="Sair da conta", command=self._sair_para_login)
        x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _menu_editar_perfil(self):
        if not self.usuario:
            messagebox.showwarning("Atenção", "Nenhum usuário está logado no momento.")
            return

        novo_usuario = simpledialog.askstring("Editar Usuário", "Digite o novo nome de usuário:", initialvalue=self.usuario)
        novo_email = simpledialog.askstring("Editar E-mail", "Digite o novo e-mail:")
        if not novo_usuario or not novo_email:
            return

        conn = sqlite3.connect("usuarios.db")
        cur = conn.cursor()
        try:
            if novo_usuario == self.usuario:
                cur.execute("UPDATE usuarios SET email=? WHERE usuario=?", (novo_email, self.usuario))
                conn.commit()
                messagebox.showinfo("Sucesso", "Seu e-mail foi atualizado com sucesso!")
                conn.close()
                return

            cur.execute("SELECT 1 FROM usuarios WHERE usuario=? COLLATE NOCASE", (novo_usuario,))
            existe = cur.fetchone()
            if existe:
                messagebox.showerror("Erro", "Já existe um usuário com esse nome. Escolha outro nome de usuário.")
                conn.close()
                return

            cur.execute("UPDATE usuarios SET usuario=?, email=? WHERE usuario=?", (novo_usuario, novo_email, self.usuario))
            conn.commit()
            self.usuario = novo_usuario
            messagebox.showinfo("Sucesso", "Seus dados foram atualizados com sucesso!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Não foi possível atualizar o perfil. Esse nome de usuário já está sendo usado.")
            traceback.print_exc()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o perfil:\n{e}")
            traceback.print_exc()
        finally:
            conn.close()


    def _menu_alterar_senha(self):
        if not self.usuario:
            messagebox.showwarning("Atenção", "Nenhum usuário logado.")
            return
        atual = simpledialog.askstring("Senha atual", "Digite a senha atual:", show="*")
        nova = simpledialog.askstring("Nova senha", "Digite a nova senha:", show="*")
        conf = simpledialog.askstring("Confirmar", "Confirme a nova senha:", show="*")
        if not atual or not nova or not conf:
            return
        if nova != conf:
            messagebox.showerror("Erro", "Senhas não coincidem.")
            return
        conn = sqlite3.connect("usuarios.db")
        cur = conn.cursor()
        cur.execute("SELECT senha_hash FROM usuarios WHERE usuario=?", (self.usuario,))
        row = cur.fetchone()
        if not row or not bcrypt.checkpw(atual.encode(), row[0]):
            messagebox.showerror("Erro", "Senha atual incorreta.")
            conn.close()
            return
        cur.execute("UPDATE usuarios SET senha_hash=? WHERE usuario=?", (bcrypt.hashpw(nova.encode(), bcrypt.gensalt()), self.usuario))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")

    def _sair_para_login(self):
        try:
            overlay, estado = None, None
            try:
                overlay, estado = _create_fullscreen_overlay(self.root, text="Aguarde", spinner_radius=30)
            except Exception:
                overlay, estado = None, None

            if callable(self.ao_sair):
                def _do_return():
                    try:
                        try:
                            self.destroy()
                        except Exception:
                            pass
                        self.ao_sair()
                    except Exception:
                        traceback.print_exc()
                    finally:
                        try:
                            _destroy_overlay_safe(estado)
                        except Exception:
                            pass

                try:
                    if overlay:
                        overlay.after(CALLBACK_DELAY_MS, _do_return)
                    else:
                        _do_return()
                except Exception:
                    _do_return()
                return

            if _spawn_login_window():
                def _after_spawn():
                    try:
                        _destroy_overlay_safe(estado)
                    except Exception:
                        pass
                    self._encerrar_janela_segura()

                try:
                    if overlay:
                        overlay.after(SPAWN_WAIT_MS, _after_spawn)
                    else:
                        _after_spawn()
                except Exception:
                    _after_spawn()
                return

            for w in self.root.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass
            self.root.configure(bg="#f4faff")
            try:
                self.root.state("zoomed")
            except Exception:
                sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
            try:
                _destroy_overlay_safe(estado)
            except Exception:
                pass
            try:
                importlib.reload(importlib.import_module("login")).TelaLogin(self.root, ao_logar=lambda u: None)
            except Exception:
                traceback.print_exc()

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao sair: {e}")

    def _start_fade_out(self, duration_ms=150):
        try:
            try:
                current = self.root.attributes("-alpha")
            except Exception:
                self._encerrar_janela_segura()
                return
            steps = max(4, int(duration_ms / 25))
            delta = (current) / steps if current > 0 else 1.0 / steps
            self._fade_step(steps, delta)
        except Exception:
            self._encerrar_janela_segura()

    def _fade_step(self, remaining_steps, delta):
        if remaining_steps <= 0:
            try:
                self.root.attributes("-alpha", 1.0)
            except Exception:
                pass
            self._encerrar_janela_segura()
            return
        try:
            try:
                cur = self.root.attributes("-alpha")
            except Exception:
                cur = 1.0
            new_alpha = max(0.0, cur - delta)
            try:
                self.root.attributes("-alpha", new_alpha)
            except Exception:
                pass
            self.root.after(25, lambda: self._fade_step(remaining_steps - 1, delta))
        except Exception:
            self._encerrar_janela_segura()

    def _encerrar_janela_segura(self):
        try:
            try:
                self.root.update_idletasks()
                self.root.withdraw()
                self.root.update()
            except Exception:
                pass
            try:
                os._exit(0)
            except Exception:
                try:
                    self.root.destroy()
                except Exception:
                    pass
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass

    def _adicionar_dado(self):
        nome = self.nome_entry.get()
        item = self.item_cb.get()
        quantidade = self.quantidade_entry.get()
        cor = self.cor_entry.get()
        tamanho = self.tamanho_entry.get()
        origem = self.origem_entry.get()
        obs = self.observacoes_entry.get()
        if not nome or not item or not quantidade:
            messagebox.showwarning("Atenção", "Preencha Nome, Item e Quantidade!")
            return
        self.db.inserir_dado(item, quantidade, origem, nome, cor, tamanho, obs)
        self._limpar_campos()
        self._atualizar_tabela()

    def _editar_dado(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um item para editar.")
            return
        valores = self.tree.item(sel)["values"]
        if not valores:
            return
        nome, item, quantidade, cor, tamanho, origem, data, obs = valores
        self.db.cursor.execute("SELECT id FROM doacoes WHERE nome=? AND item=? AND data=?", (nome, item, data))
        r = self.db.cursor.fetchone()
        if not r:
            return
        id_item = r[0]
        novo_nome = self.nome_entry.get().strip()
        novo_item = self.item_cb.get().strip()
        nova_qtd = self.quantidade_entry.get().strip()
        novo_cor = self.cor_entry.get().strip()
        novo_tam = self.tamanho_entry.get().strip()
        novo_origem = self.origem_entry.get().strip()
        novo_obs = self.observacoes_entry.get().strip()
        self.db.atualizar_dado(id_item, novo_item, nova_qtd, novo_origem, novo_nome, novo_cor, novo_tam, novo_obs)
        self._atualizar_tabela()
        messagebox.showinfo("Sucesso", "Doação atualizada com sucesso!")

    def _excluir_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um item para excluir.")
            return
        valores = self.tree.item(sel, "values")
        nome, item, qtd, cor, tam, origem, data, obs = valores
        if not messagebox.askyesno("Confirmar", "Deseja excluir esta doação?"):
            return
        self.db.cursor.execute("DELETE FROM doacoes WHERE nome=? AND item=? AND data=?", (nome, item, data))
        self.db.conn.commit()
        self._atualizar_tabela()
        messagebox.showinfo("Sucesso", "Item excluído com sucesso!")

    def _exportar_excel(self):
        caminho = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho", "doacoes.xlsx")
        if self.db.exportar_para_excel(caminho):
            messagebox.showinfo("Exportação", f"Arquivo salvo em:\n{caminho}")
        else:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")

    def _limpar_campos(self):
        for e in [self.nome_entry, self.item_cb, self.quantidade_entry, self.cor_entry, self.tamanho_entry,
                  self.origem_entry, self.observacoes_entry]:
            try:
                e.delete(0, "end")
            except Exception:
                pass

    def _selecionar_item(self, event):
        sel = self.tree.focus()
        if not sel:
            return
        valores = self.tree.item(sel)["values"]
        if not valores:
            return
        try:
            self.nome_entry.delete(0, "end")
            self.item_cb.delete(0, "end")
            self.quantidade_entry.delete(0, "end")
            self.cor_entry.delete(0, "end")
            self.tamanho_entry.delete(0, "end")
            self.origem_entry.delete(0, "end")
            self.observacoes_entry.delete(0, "end")
        except Exception:
            pass
        try:
            self.nome_entry.insert(0, valores[0])
            self.item_cb.insert(0, valores[1])
            self.quantidade_entry.insert(0, valores[2])
            self.cor_entry.insert(0, valores[3])
            self.tamanho_entry.insert(0, valores[4])
            self.origem_entry.insert(0, valores[5])
            self.observacoes_entry.insert(0, valores[7])
        except Exception:
            pass

    def _alternar_tema(self):
        self.modo_escuro = not getattr(self, "modo_escuro", True)
        tema = "darkly" if self.modo_escuro else "flatly"
        try:
            if self.style:
                self.style.theme_use(tema)
            else:
                ttk.Style(theme=tema)
        except Exception:
            pass


if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    InterfaceDoacoes(app, usuario="teste")
    app.mainloop()
