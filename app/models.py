from sqlalchemy import Column, Integer, String, DateTime
from .database import Base  # Corrigido

class Manobra(Base):
    __tablename__ = "manobras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    unidade_executante = Column(String)
    municipio = Column(String)
    num_os_solicitante = Column(String)
    endereco_os_solicitante = Column(String)
    data_criacao = Column(DateTime)
    data_fechamento = Column(DateTime)
    data_abertura = Column(DateTime)
    qtde_pdes_afetados = Column(Integer)
    notas = Column(String)
    total_economias = Column(Integer)
    residencial = Column(Integer)
    comercial = Column(Integer)
    industrial = Column(Integer)
    publico = Column(Integer)
