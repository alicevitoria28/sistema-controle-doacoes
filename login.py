import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import bcrypt
from PIL import Image, ImageTk
import os
import random
import string
import smtplib
from email.message import EmailMessage
import ssl

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "sistemadecontrolededoacoes@gmail.com"
SMTP_PASSWORD = "ttwn spbk mcur mtgn"
EMAIL_FROM_NAME = "Sistema de Doações"

try:
    from banco_dados import BancoDoacoes
except Exception:
    BancoDoacoes = None

class TelaLogin(tk.Frame):
    def __init__(self, root, ao_logar):
        super().__init__(root)
        self.root = root
        self.ao_logar = ao_logar
        self.pack(fill="both", expand=True)

        try:
            self.root.configure(bg="#f4faff")
        except Exception:
            pass

        self.conn = sqlite3.connect("usuarios.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela_usuarios()

        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#f4faff")
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._criar_bolhas_animadas()

        card_w, card_h = 1000, 600
        sombra = tk.Frame(self, bg="#d0e9ff", width=card_w + 12, height=card_h + 12)
        sombra.place(relx=0.5 + 0.002, rely=0.5 + 0.002, anchor="center")

        self.card = tk.Frame(self, bg="#ffffff", width=card_w, height=card_h)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        left_w = card_w // 2
        self.frame_left = tk.Frame(self.card, bg="#e8f6ff", width=left_w, height=card_h)
        self.frame_right = tk.Frame(self.card, bg="#ffffff", width=card_w-left_w, height=card_h)
        self.frame_left.place(x=0, y=0, width=left_w, height=card_h)
        self.frame_right.place(x=left_w, y=0, width=card_w-left_w, height=card_h)

        self._montar_tela_login_inicial()

        try:
            self.root.attributes("-alpha", 0.0)
            self._fade_in()
        except Exception:
            pass

    def _criar_botao_hover(self, parent, texto, cor, comando):
        def on_enter(btn): btn.config(bg=self._escurecer_cor(cor))
        def on_leave(btn): btn.config(bg=cor)
        btn = tk.Button(parent, text=texto, bg=cor, fg="white", font=("Segoe UI", 12, "bold"),
                        bd=0, cursor="hand2", command=comando, relief="flat",
                        activebackground=self._escurecer_cor(cor))
        btn.pack(fill="x", pady=6, ipady=10)
        btn.bind("<Enter>", lambda e: on_enter(btn))
        btn.bind("<Leave>", lambda e: on_leave(btn))
        return btn

    def _escurecer_cor(self, cor_hex):
        cor_hex = cor_hex.lstrip("#")
        r, g, b = [int(cor_hex[i:i+2], 16) for i in (0, 2, 4)]
        return f"#{max(0,int(r*0.85)):02x}{max(0,int(g*0.85)):02x}{max(0,int(b*0.85)):02x}"

    def _montar_tela_login_inicial(self):
        for w in self.frame_left.winfo_children(): w.destroy()
        for w in self.frame_right.winfo_children(): w.destroy()
        self._criar_form_login()
        self._criar_imagem_lateral()

    def _criar_form_login(self):
        form = tk.Frame(self.frame_left, bg="#e8f6ff", padx=60, pady=60)
        form.pack(expand=True)

        tk.Label(form, text="Bem-vindo(a)!", font=("Segoe UI", 26, "bold"),
                 bg="#e8f6ff", fg="#03384d").pack(anchor="w")
        tk.Label(form, text="Sistema de Doações", font=("Segoe UI", 14, "bold"),
                 bg="#e8f6ff", fg="#035268").pack(anchor="w", pady=(6, 20))

        def criar_entry(parent, placeholder, is_password=False):
            frame = tk.Frame(parent, bg="#e8f6ff")
            frame.pack(fill="x", pady=10)
            container = tk.Frame(frame, bg="white", highlightbackground="#6bbdef", highlightthickness=1)
            container.pack(fill="x")
            entry = tk.Entry(container, bd=0, bg="white", fg="#0f1720", font=("Segoe UI", 11))
            entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(8, 0))
            entry.insert(0, placeholder)
            def clear(ev): 
                if entry.get() == placeholder: entry.delete(0, "end")
            def restore(ev): 
                if not entry.get(): entry.insert(0, placeholder)
            entry.bind("<FocusIn>", clear)
            entry.bind("<FocusOut>", restore)
            if is_password:
                entry.config(show="*")
                self.mostrar = False
                def toggle():
                    self.mostrar = not self.mostrar
                    entry.config(show="" if self.mostrar else "*")
                    olho_btn.config(text="👁" if self.mostrar else "👁‍🗨")
                olho_btn = tk.Button(container, text="👁‍🗨", bd=0, bg="white", font=("Segoe UI", 11),
                                     cursor="hand2", command=toggle, relief="flat", activebackground="white")
                olho_btn.pack(side="right", padx=(0, 8))
            return entry

        self.usuario_entry = criar_entry(form, "Usuário")
        self.senha_entry = criar_entry(form, "Senha", is_password=True)

        opts = tk.Frame(form, bg="#e8f6ff")
        opts.pack(fill="x", pady=(6, 10))
        self.var_lembrar = tk.BooleanVar()
        tk.Checkbutton(opts, text="Lembrar-me", variable=self.var_lembrar,
                       bg="#e8f6ff", fg="#03384d", selectcolor="#e8f6ff").pack(side="left")
        esqueci = tk.Label(opts, text="Esqueci minha senha", bg="#e8f6ff", fg="#035268",
                           font=("Segoe UI", 9, "underline"), cursor="hand2")
        esqueci.pack(side="right")
        esqueci.bind("<Button-1>", lambda e: self._janela_recuperar_senha())

        self._criar_botao_hover(form, "Entrar", "#06d6a0", self.verificar_login)
        self._criar_botao_hover(form, "Criar Conta", "#4dabf7", lambda: self._montar_tela_cadastro())

        tk.Label(form, text="Gerencie suas doações com praticidade e segurança.",
                 bg="#e8f6ff", fg="#035268", font=("Segoe UI", 10)).pack(anchor="w", pady=(18, 0))

    def _montar_tela_cadastro(self):
        for w in self.frame_left.winfo_children(): w.destroy()
        self._criar_form_cadastro()

    def _criar_form_cadastro(self):
        form = tk.Frame(self.frame_left, bg="#e8f6ff", padx=60, pady=36)
        form.pack(expand=True, fill="both")

        tk.Label(form, text="Criar nova conta", font=("Segoe UI", 22, "bold"),
                 bg="#e8f6ff", fg="#03384d").pack(anchor="w", pady=(0,12))
        tk.Label(form, text="Preencha os campos abaixo", font=("Segoe UI", 11),
                 bg="#e8f6ff", fg="#035268").pack(anchor="w", pady=(0,12))

        def criar_entry_simples(parent, placeholder, is_password=False):
            frame = tk.Frame(parent, bg="#e8f6ff")
            frame.pack(fill="x", pady=8)
            container = tk.Frame(frame, bg="white", highlightbackground="#6bbdef", highlightthickness=1)
            container.pack(fill="x")
            entry = tk.Entry(container, bd=0, bg="white", fg="#0f1720", font=("Segoe UI", 11))
            entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(8,0))
            entry.insert(0, placeholder)
            def clear(ev):
                if entry.get() == placeholder: entry.delete(0, "end")
            def restore(ev):
                if not entry.get(): entry.insert(0, placeholder)
            entry.bind("<FocusIn>", clear)
            entry.bind("<FocusOut>", restore)
            if is_password:
                entry.config(show="*")
                def toggle_password():
                    if entry.cget("show") == "":
                        entry.config(show="*")
                        btn_olho.config(text="👁‍🗨")
                    else:
                        entry.config(show="")
                        btn_olho.config(text="👁")
                btn_olho = tk.Button(container, text="👁‍🗨", bd=0, bg="white", font=("Segoe UI", 11),
                                     command=toggle_password, cursor="hand2", relief="flat")
                btn_olho.pack(side="right", padx=(0,8))
            return entry

        self.novo_usuario_entry = criar_entry_simples(form, "Nome de usuário")
        self.email_entry = criar_entry_simples(form, "E-mail (ex: seu@email.com)")
        self.nova_senha_entry = criar_entry_simples(form, "Senha", is_password=True)
        self.nova_senha_conf_entry = criar_entry_simples(form, "Confirme a senha", is_password=True)

        tk.Button(form, text="Cadastrar", bg="#06d6a0", fg="white", bd=0,
                  font=("Segoe UI", 12, "bold"), command=self._processar_cadastro,
                  cursor="hand2").pack(fill="x", ipady=10, pady=(10,8))
        tk.Button(form, text="Voltar", bg="#ddd", fg="#222", bd=0,
                  font=("Segoe UI", 11), command=self._montar_tela_login_inicial,
                  cursor="hand2").pack(fill="x", ipady=8)

    def _processar_cadastro(self):
        usuario = self.novo_usuario_entry.get().strip()
        email = self.email_entry.get().strip()
        senha = self.nova_senha_entry.get().strip()
        senha_conf = self.nova_senha_conf_entry.get().strip()
        if not usuario or not email or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        if senha != senha_conf:
            messagebox.showwarning("Atenção", "As senhas não coincidem.")
            return

        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        try:
            self.cursor.execute("INSERT INTO usuarios (usuario, senha_hash, email) VALUES (?, ?, ?)",
                                (usuario, senha_hash, email))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Conta criada com sucesso! Voltando ao login.")
            self._montar_tela_login_inicial()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário ou e-mail já cadastrado.")

    def _janela_recuperar_senha(self):
        email = simpledialog.askstring("Recuperar senha", "Digite o e-mail cadastrado:", parent=self.root)
        if not email: return
        self.cursor.execute("SELECT usuario FROM usuarios WHERE email=?", (email,))
        row = self.cursor.fetchone()
        if not row:
            messagebox.showerror("Erro", "E-mail não encontrado.")
            return
        usuario = row[0]
        senha_temp = self._gerar_senha_temporaria(8)
        senha_hash = bcrypt.hashpw(senha_temp.encode("utf-8"), bcrypt.gensalt())
        self.cursor.execute("UPDATE usuarios SET senha_hash=? WHERE usuario=?", (senha_hash, usuario))
        self.conn.commit()
        if enviar_senha_temporaria_por_email(email, usuario, senha_temp):
            messagebox.showinfo("Recuperação", "Senha temporária enviada ao e-mail.")
        else:
            messagebox.showwarning("Aviso", f"Não foi possível enviar o e-mail. Senha: {senha_temp}")

    def _gerar_senha_temporaria(self, n=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(n))

    def _criar_imagem_lateral(self):
        for w in self.frame_right.winfo_children(): w.destroy()
        frame = tk.Frame(self.frame_right, bg="#ffffff", padx=24, pady=30)
        frame.pack(fill="both", expand=True)
        img_path = next((f for f in ["login_ilustracao.png", "imagem_lateral.png", "fundo_login.jpg"] if os.path.exists(f)), None)
        if img_path:
            img = Image.open(img_path).convert("RGBA")
            img.thumbnail((420, 420))
            self.img_tk = ImageTk.PhotoImage(img)
            tk.Label(frame, image=self.img_tk, bg="#ffffff").pack(pady=(10,8))
        frase = tk.Frame(frame, bg="#ffffff"); frase.pack(pady=(12,0))
        tk.Label(frase, text="Doe com amor", bg="#fff", fg="#444", font=("Segoe UI",11)).pack(side="left")
        tk.Label(frase, text="❤️", bg="#fff", fg="red").pack(side="left", padx=(4,4))
        tk.Label(frase, text="—", bg="#fff", fg="#666").pack(side="left", padx=(4,4))
        tk.Label(frase, text="✨", bg="#fff", fg="#ffb84d").pack(side="left", padx=(0,4))
        tk.Label(frase, text="Organize com propósito", bg="#fff", fg="#444").pack(side="left")

    def criar_tabela_usuarios(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                senha_hash BLOB,
                email TEXT
            )
        """)
        self.conn.commit()

    def verificar_login(self):
        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get().strip()
        self.cursor.execute("SELECT senha_hash FROM usuarios WHERE usuario=?", (usuario,))
        row = self.cursor.fetchone()
        if row and bcrypt.checkpw(senha.encode("utf-8"), row[0]):
            messagebox.showinfo("Login", f"Bem-vindo, {usuario}!")
            if self.ao_logar: self.ao_logar(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def _criar_bolhas_animadas(self):
        self.bolhas = []
        self._anim_id = None                       # <- guarda id do after
        self._fade_id = None                       # <- guarda id do fade (se usado)
        colors = ["#3fa3e2", "#0e7ec4", "#0a6fb6", "#4fb0e9", "#1f8fd6"]
        W = max(1200, self.root.winfo_screenwidth() or 1366)
        H = max(700, self.root.winfo_screenheight() or 768)
        for _ in range(36):
            r = random.randint(40, 140)
            x = random.randint(-300, W + 300)
            y = random.randint(-200, H + 200)
            color = random.choice(colors)
            velx = random.uniform(-2.2, 2.2)
            vely = random.uniform(-1.6, 1.6)
            oval = self.canvas.create_oval(x, y, x + r, y + r, fill=color, outline="")
            self.bolhas.append({"id": oval, "r": r, "x": x, "y": y, "vx": velx, "vy": vely})
        self._animar_bolhas()

    def _animar_bolhas(self):
        try:
            for b in self.bolhas:
                b["x"] += b["vx"]; b["y"] += b["vy"]
                self.canvas.coords(b["id"], b["x"], b["y"], b["x"] + b["r"], b["y"] + b["r"])
            self._anim_id = self.after(28, self._animar_bolhas)
        except Exception:
            self._anim_id = None

    def _fade_in(self):
        try:
            op = self.root.attributes("-alpha")
        except Exception:
            return
        if op < 1.0:
            try:
                self.root.attributes("-alpha", op + 0.05)
                self._fade_id = self.after(30, self._fade_in)
            except Exception:
                self._fade_id = None

    def stop(self):
        """
        Cancela animações pendentes (deve ser chamado antes de destruir o frame/root).
        """
        try:
            if getattr(self, "_anim_id", None):
                try:
                    self.after_cancel(self._anim_id)
                except Exception:
                    pass
                self._anim_id = None
        except Exception:
            pass
        try:
            if getattr(self, "_fade_id", None):
                try:
                    self.after_cancel(self._fade_id)
                except Exception:
                    pass
                self._fade_id = None
        except Exception:
            pass


def enviar_email_html(destinatario, assunto, html_body, text_body=None):
    try:
        msg = EmailMessage()
        msg["From"] = f"{EMAIL_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(text_body or "Versão em texto não disponível")
        msg.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return False

def gerar_html_recuperacao(usuario_nome, senha_temporaria, logo_url=None):
    logo_block = f'''
        <tr><td align="center" style="padding:18px 0 8px 0;">
        <img src="{logo_url}" alt="Logo" width="120" style="display:block;border:0;"/></td></tr>
    ''' if logo_url else ""
    html = f"""
    <html><body style="background:#f4f7fb;font-family:Segoe UI,Arial,sans-serif;">
    <table align="center" width="600" style="background:#fff;border-radius:8px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);padding:40px;">
    {logo_block}
    <tr><td>
    <h2 style="color:#073b51;">Recuperação de senha</h2>
    <p style="color:#586f7f;">Olá <strong>{usuario_nome}</strong>, sua senha temporária é:</p>
    <div style="background:#f1fbf7;border:1px solid #cbeee0;padding:16px;border-radius:6px;
    text-align:center;">
    <p style="font-size:22px;letter-spacing:2px;color:#065f46;"><strong>{senha_temporaria}</strong></p>
    </div>
    <p style="margin-top:18px;color:#586f7f;">Use essa senha para entrar e altere-a assim que possível.</p>
    <p style="font-size:13px;color:#94a6b0;margin-top:20px;">© Sistema de Doações — Não responda este e-mail.</p>
    </td></tr></table></body></html>
    """
    text = f"Sua senha temporária é: {senha_temporaria}\nUse-a para entrar e altere-a depois."
    return html, text

def enviar_senha_temporaria_por_email(email_destino, usuario, senha_temp):
    html, text = gerar_html_recuperacao(usuario, senha_temp)
    return enviar_email_html(email_destino, "Recuperação de senha — Sistema de Doações", html, text)


if __name__ == "__main__":
    def ao_logar(usuario): print("DEBUG login ->", usuario)
    root = tk.Tk()
    root.title("Login Teste")
    root.geometry("1200x800")
    app = TelaLogin(root, ao_logar)
    root.mainloop()
