import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel

from backend.database import engine, Base, get_db
from backend.models.config import AppConfig, License

# Importar otros modelos para creación de tablas
from backend.models.exam import Exam, AnswerKey
from backend.models.student import Student
from backend.models.result import Scan, Result

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EinScan Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para validar Licencia por KEY
@app.middleware("http")
async def license_check_middleware(request: Request, call_next):
    path = request.url.path
    
    # Rutas públicas (estáticos, assets, login de licencia, y vista de imágenes para miniaturas)
    if (not path.startswith("/api") or 
        path.startswith("/api/license/validate") or 
        path.startswith("/api/license/generate") or
        path.startswith("/api/scanner/view")):
        return await call_next(request)
    
    # Obtener Key del Header
    license_key = request.headers.get("X-License-Key")
    
    if not license_key:
        return JSONResponse(status_code=403, content={"detail": "MISSING_KEY"})
    
    db = next(get_db())
    valid_license = db.query(License).filter(
        License.key == license_key,
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).first()
    
    if not valid_license:
        return JSONResponse(status_code=403, content={"detail": "INVALID_OR_EXPIRED_KEY"})
    
    return await call_next(request)

# --- ENDPOINTS DE LICENCIA ---
class LicenseCreate(BaseModel):
    days: int
    admin_pass: str

class LicenseValidate(BaseModel):
    key: str

@app.post("/api/license/validate")
def validate_key(data: LicenseValidate, db: Session = Depends(get_db)):
    lic = db.query(License).filter(
        License.key == data.key,
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).first()
    if lic:
        return {"valid": True, "expires_at": lic.expires_at}
    raise HTTPException(status_code=403, detail="Licencia no válida o expirada")

@app.post("/api/license/generate")
def generate_license(data: LicenseCreate, db: Session = Depends(get_db)):
    master_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    if data.admin_pass != master_pass:
        raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta")
    
    new_key = "EINSTEIN-" + str(uuid.uuid4()).upper()[:8]
    expires = datetime.utcnow() + timedelta(days=data.days)
    
    db_license = License(key=new_key, expires_at=expires)
    db.add(db_license)
    db.commit()
    return {"key": new_key, "expires_at": expires}

@app.get("/api/license/list")
def list_licenses(admin_pass: str, db: Session = Depends(get_db)):
    master_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    if admin_pass != master_pass:
        raise HTTPException(status_code=401)
    return db.query(License).all()

# --- INCLUSIÓN DE ROUTERS ---
from backend.routers import exams, generator, scanner, results, export
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(generator.router, prefix="/api/generator", tags=["Generator"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["Scanner"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# --- SERVIR FRONTEND (CATCH-ALL) ---
frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "EinScan Pro Backend activo."}
