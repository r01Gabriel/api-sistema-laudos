from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Link do banco de dados no Render
DATABASE_URL = "postgresql://db_gabriel_zem6_user:Sz1ZpuHPCV2N7wAe3AtzU0wCjevVvdpT@dpg-dagt95tbedkc73855c60-a/db_gabriel_zem6"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABELAS DO BANCO DE DADOS ---
class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String, nullable=False)
    url_logo = Column(String, nullable=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    email = Column(String, unique=True, index=True)
    senha = Column(String)

class Laudo(Base):
    __tablename__ = "laudos"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    os_numero = Column(String)
    cliente = Column(String)
    dados_inspecao = Column(Text)

Base.metadata.create_all(bind=engine)

# --- INICIALIZAÇÃO DA API ---
app = FastAPI(title="API Sistema de Laudos Multi-Tenant")

# Permite que seu front-end acesse a API sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ESTRUTURAS DE DADOS (SCHEMAS) ---
class LoginRequest(BaseModel):
    email: str
    senha: str

class LaudoCreate(BaseModel.ConfigDict):
    empresa_id: int
    os_numero: str
    cliente: str
    dados_inspecao: str

# --- ROTAS DA API ---

@app.get("/")
def home():
    return {"mensagem": "API de Laudos do Gabriel está online e conectada ao banco!"}

# Rota de Login simples
@app.post("/login")
def fazer_login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email, Usuario.senha == dados.senha).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
    return {
        "mensagem": "Login realizado com sucesso",
        "usuario_id": usuario.id,
        "empresa_id": empresa.id,
        "nome_empresa": empresa.nome_fantasia,
        "url_logo": empresa.url_logo
    }

# Rota para salvar um laudo vinculado à empresa correta
@app.post("/laudos")
def salvar_laudo(laudo: dict, db: Session = Depends(get_db)):
    novo_laudo = Laudo(
        empresa_id=laudo.get("empresa_id"),
        os_numero=laudo.get("os_numero"),
        cliente=laudo.get("cliente"),
        dados_inspecao=laudo.get("dados_inspecao")
    )
    db.add(novo_laudo)
    db.commit()
    db.refresh(novo_laudo)
    return {"mensagem": "Laudo salvo com sucesso!", "id_laudo": novo_laudo.id}

# Rota para listar apenas os laudos da empresa logada
@app.get("/laudos/{empresa_id}")
def listar_laudos(empresa_id: int, db: Session = Depends(get_db)):
    laudos = db.query(Laudo).filter(Laudo.empresa_id == empresa_id).all()
    return laudos
