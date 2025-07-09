from .database import engine
from . import models

def create_database():
    # Cria todas as tabelas definidas em models
    models.Base.metadata.create_all(bind=engine)
    print("🚀 Banco de dados e tabelas criados com sucesso!")

if __name__ == "__main__":
    create_database()
