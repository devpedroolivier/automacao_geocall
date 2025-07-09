from sqlalchemy import create_engine, text

def test_banco_tem_dados():
    # Conectar ao banco SQLite
    engine = create_engine("sqlite:///./dados/database.db")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM manobras"))
        count = result.scalar()
        assert count > 0, "A tabela 'manobras' está vazia!"
