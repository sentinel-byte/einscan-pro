import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.database import engine, Base, get_db
from backend.auth import create_access_token, verify_password, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.models.config import AppConfig

# Importar otros modelos para que Base los reconozca al crear tablas
from backend.models.exam import Exam, AnswerKey
from backend.models.student import Student
from backend.models.result import Scan, Result

load_dotenv()

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EinScan Pro API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Login endpoint
@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    if form_data.username != "admin" or not verify_password(form_data.password, get_password_hash(admin_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Inclusión de routers
from backend.routers import exams, generator, scanner, results
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(generator.router, prefix="/api/generator", tags=["Generator"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["Scanner"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])

# Servir Frontend
frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "EinScan Pro Backend activo. Frontend no encontrado o no compilado."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
