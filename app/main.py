from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

app = FastAPI()

# Dependência para abrir e fechar conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"msg": "API do projeto rodando!"}

@app.get("/manobras/")
def get_manobras(db: Session = Depends(get_db)):
    manobras = db.query(models.Manobra).all()
    return [
        {
            "id": m.id,
            "unidade_executante": m.unidade_executante,
            "municipio": m.municipio,
            "num_os_solicitante": m.num_os_solicitante,
            "endereco_os_solicitante": m.endereco_os_solicitante,
            "data_criacao": m.data_criacao,
            "data_fechamento": m.data_fechamento,
            "data_abertura": m.data_abertura,
            "qtde_pdes_afetados": m.qtde_pdes_afetados,
            "notas": m.notas,
            "total_economias": m.total_economias,
            "residencial": m.residencial,
            "comercial": m.comercial,
            "industrial": m.industrial,
            "publico": m.publico
        }
        for m in manobras
    ]

@app.get("/manobras/{manobra_id}")
def get_manobra_by_id(manobra_id: int, db: Session = Depends(get_db)):
    manobra = db.query(models.Manobra).filter(models.Manobra.id == manobra_id).first()
    if not manobra:
        raise HTTPException(status_code=404, detail="Manobra não encontrada")
    return {
        "id": manobra.id,
        "unidade_executante": manobra.unidade_executante,
        "municipio": manobra.municipio,
        "num_os_solicitante": manobra.num_os_solicitante,
        "endereco_os_solicitante": manobra.endereco_os_solicitante,
        "data_criacao": manobra.data_criacao,
        "data_fechamento": manobra.data_fechamento,
        "data_abertura": manobra.data_abertura,
        "qtde_pdes_afetados": manobra.qtde_pdes_afetados,
        "notas": manobra.notas,
        "total_economias": manobra.total_economias,
        "residencial": manobra.residencial,
        "comercial": manobra.comercial,
        "industrial": manobra.industrial,
        "publico": manobra.publico
    }
