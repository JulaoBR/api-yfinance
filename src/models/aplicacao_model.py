from core.base_model import BaseModel

class AplicacaoModel(BaseModel):
    def consultrar(self):
        query = """
                    SELECT 
                        aplicacao.idaplicacao,
                        aplicacao.idcategoria_aplicacao,
                        aplicacao.descricao
                    FROM aplicacao
                    WHERE aplicacao.idcategoria_aplicacao IN (9, 10)
                    AND aplicacao.status = '1'
                    ORDER BY idaplicacao ASC
                """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Erro ao buscar aplicacoes: {e}")