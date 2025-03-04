from core.base_model import BaseModel

class HistoricoModel(BaseModel):
    def inserir(self, dicionario):
        query = """
                    INSERT INTO historico_investimento (
                        idaplicacao,
                        preco_cotado,
                        data_cotacao,
                        data_hora_cadastro
                    ) VALUES (
                        %(idaplicacao)s,
                        %(preco_cotado)s,
                        %(data_cotacao)s,
                        %(data_hora_cadastro)s
                    )
                """
        try:
            self.cursor.execute(query, dicionario)
            return self.cursor.lastrowid
        except Exception as e:
            raise RuntimeError(f"Erro ao inserir usuário: {e}")