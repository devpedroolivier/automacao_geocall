from sqlalchemy import create_engine, text

def test_banco_mock():
    # Conecta a um banco SQLite em memória (não precisa de arquivo físico)
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        # Cria tabela fake só pra testar
        conn.execute(text("""
            CREATE TABLE manobras (
                id INTEGER PRIMARY KEY,
                municipio TEXT
            )
        """))
        # Insere um registro
        conn.execute(text("INSERT INTO manobras (id, municipio) VALUES (1, 'GUARULHOS')"))
        # Testa se consegue ler
        result = conn.execute(text("SELECT COUNT(*) FROM manobras"))
        count = result.scalar()
        assert count == 1, "Banco em memória não retornou registros."
