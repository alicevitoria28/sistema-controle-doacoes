import sqlite3
from datetime import datetime
import os
import sys

class BancoDoacoes:
    def __init__(self, db_nome="doacoes.db"):
        self.db_nome = db_nome
        self.conn = sqlite3.connect(self.db_nome, timeout=5)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    def criar_tabela(self):
        self.cursor.execute("""
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
        self.conn.commit()

        try:
            existing = [col[1] for col in self.cursor.execute("PRAGMA table_info(doacoes)").fetchall()]
            extras = {"nome":"TEXT","cor":"TEXT","tamanho":"TEXT","observacoes":"TEXT","data":"TEXT"}
            for col, typ in extras.items():
                if col not in existing:
                    try:
                        self.cursor.execute(f"ALTER TABLE doacoes ADD COLUMN {col} {typ}")
                        self.conn.commit()
                    except Exception:
                        pass
        except Exception:
            pass

    def inserir_dado(self, item, quantidade, origem, nome="", cor="", tamanho="", observacoes=""):
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cursor.execute("""
            INSERT INTO doacoes (item, quantidade, data, origem, nome, cor, tamanho, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item, quantidade, data, origem, nome, cor, tamanho, observacoes))
        self.conn.commit()

    def ler_dados(self):
        self.cursor.execute("""
            SELECT id, item, quantidade, data, origem, nome, cor, tamanho, observacoes
            FROM doacoes
            ORDER BY id DESC
        """)
        return self.cursor.fetchall()

    def atualizar_dado(self, id_item, item, quantidade, origem, nome="", cor="", tamanho="", observacoes=""):
        self.cursor.execute("""
            UPDATE doacoes
            SET item=?, quantidade=?, origem=?, nome=?, cor=?, tamanho=?, observacoes=?
            WHERE id=?
        """, (item, quantidade, origem, nome, cor, tamanho, observacoes, id_item))
        self.conn.commit()

    def excluir_dado(self, id_item):
        self.cursor.execute("DELETE FROM doacoes WHERE id = ?", (id_item,))
        self.conn.commit()

    def exportar_para_excel(self, caminho=None):
        dados = self.ler_dados()
        if not dados:
            return False

        try:
            import pandas as pd
        except Exception as e:
            print("Exportar para Excel: pandas não disponível ou falhou ao importar:", e)
            return False

        if caminho is None:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                try:
                    os.makedirs(desktop)
                except Exception:
                    desktop = os.path.expanduser("~")
            caminho = os.path.join(desktop, "doacoes_exportadas.xlsx")

        colunas = ["Nome do Doador", "Item", "Quantidade", "Cor", "Tamanho", "Origem", "Data", "Observações"]
        df_dados = []
        for row in dados:
            try:
                nome = row[5]
                item = row[1]
                quantidade = row[2]
                cor = row[6]
                tamanho = row[7]
                origem = row[4]
                data = row[3]
                observacoes = row[8]
            except Exception:
                vals = list(row)
                nome = vals[5] if len(vals) > 5 else ""
                item = vals[1] if len(vals) > 1 else ""
                quantidade = vals[2] if len(vals) > 2 else ""
                cor = vals[6] if len(vals) > 6 else ""
                tamanho = vals[7] if len(vals) > 7 else ""
                origem = vals[4] if len(vals) > 4 else ""
                data = vals[3] if len(vals) > 3 else ""
                observacoes = vals[8] if len(vals) > 8 else ""
            df_dados.append([nome, item, quantidade, cor, tamanho, origem, data, observacoes])

        try:
            df = pd.DataFrame(df_dados, columns=colunas)
            df.to_excel(caminho, index=False)
        except Exception as e:
            print("Erro ao gerar arquivo Excel:", e)
            return False

        try:
            if sys.platform.startswith("win"):
                os.startfile(caminho)
        except Exception:
            pass

        return True

    def fechar(self):
        try:
            self.conn.close()
        except Exception:
            pass
