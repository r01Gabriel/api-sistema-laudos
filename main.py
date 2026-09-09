from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Seu link do banco de dados no Render
DATABASE_URL = "postgresql://db_gabriel_zem6_user:Sz1ZpuHPCV2N7wAe3AtzU0wCjevVvdpT@dpg-dagt95tbedkc73855c60-a/db_gabriel_zem6"

# Configuração de conexão do banco
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DEFINIÇÃO DAS TABELAS (MULTI-TENANT) ---

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String, nullable=False)
    url_logo = Column(String, nullable=True) # Ex: link da imagem da Solução

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    email = Column(String, unique=True, index=True)
    senha = Column(String) # No futuro, vamos criptografar isso

class Laudo(Base):
    __tablename__ = "laudos"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id")) # Garante que o laudo pertence só a uma empresa
    os_numero = Column(String)
    cliente = Column(String)
    dados_inspecao = Column(Text) # Aqui salvaremos o JSON com as peças e status

# Cria as tabelas no banco de dados lá no Render
Base.metadata.create_all(bind=engine)

# --- INICIALIZAÇÃO DA API ---
app = FastAPI(title="API Sistema de Laudos")

@app.get("/")
def home():
    return {"mensagem": "API de Laudos do Gabriel está online e conectada ao banco!"}