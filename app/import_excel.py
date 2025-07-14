import sys
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from datetime import datetime

def parse_date(x):
    if pd.isna(x):
        return None
    try:
        return pd.to_datetime(x, dayfirst=True, format="%d/%m/%Y %H:%M")
    except Exception as e:
        print(f"[WARN] Não foi possível converter '{x}' para data: {e}")
        return None

def main(arquivo):
    models.Base.metadata.create_all(bind=engine)
    print(f"[INFO] Importando {arquivo}...")

    try:
        df = pd.read_excel(arquivo)
    except Exception as e:
        print(f"[ERRO] Falha ao ler {arquivo}: {e}")
        return

    df.rename(columns={
        "Id. da Manobra": "id",
        "Unidade Executante": "unidade_executante",
        "Município": "municipio",
        "Num OS solicitante": "num_os_solicitante",
        "Endereço OS solicitante": "endereco_os_solicitante",
        "Data de Criação": "data_criacao",
        "Data de Fechamento": "data_fechamento",
        "Data de Abertura": "data_abertura",
        "Qtde PDE's Afetados": "qtde_pdes_afetados",
        "Notas": "notas",
        "Total de Economias": "total_economias",
        "Residencial": "residencial",
        "Comercial": "comercial",
        "Industrial": "industrial",
        "Público": "publico",
        "Motivo da Manobra": "motivo_da_manobra"
    }, inplace=True)

    for col in ["data_criacao", "data_fechamento", "data_abertura"]:
        df[col] = df[col].apply(parse_date)

    db: Session = SessionLocal()
    for _, row in df.iterrows():
        manobra = models.Manobra(
            id=int(row['id']),
            unidade_executante=row['unidade_executante'],
            municipio=row['municipio'],
            num_os_solicitante=str(int(row['num_os_solicitante'])) if pd.notna(row['num_os_solicitante']) else None,
            endereco_os_solicitante=row['endereco_os_solicitante'],
            data_criacao=row['data_criacao'],
            data_fechamento=row['data_fechamento'],
            data_abertura=row['data_abertura'],
            qtde_pdes_afetados=int(row['qtde_pdes_afetados']) if pd.notna(row['qtde_pdes_afetados']) else None,
            notas=str(row['notas']) if pd.notna(row['notas']) else None,
            total_economias=int(row['total_economias']) if pd.notna(row['total_economias']) else None,
            residencial=int(row['residencial']) if pd.notna(row['residencial']) else None,
            comercial=int(row['comercial']) if pd.notna(row['comercial']) else None,
            industrial=int(row['industrial']) if pd.notna(row['industrial']) else None,
            publico=int(row['publico']) if pd.notna(row['publico']) else None,
            motivo_da_manobra=row['motivo_da_manobra'] if pd.notna(row['motivo_da_manobra']) else None
        )
        db.merge(manobra)
    db.commit()
    db.close()

    print(f"🚀 Dados do arquivo {arquivo} importados com sucesso!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m app.import_excel <arquivo.xlsx>")
        sys.exit(1)
    main(sys.argv[1])
