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

# Cargar variables de entorno al inicio
load_dotenv()

from backend.database import engine, Base, get_db
from backend.models.config import AppConfig, License

# Importar otros modelos
from backend.models.exam import Exam, AnswerKey
from backend.models.student import Student
from backend.models.result import Scan, Result

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EinScan Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_admin(password: str):
    """Verifica la contraseña de admin de forma ultra-robusta."""
    # Obtenemos la clave de Render, si no existe usamos la de por defecto
    master = os.environ.get("ADMIN_PASSWORD") or os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Limpiamos espacios y pasamos a minúsculas para evitar errores humanos
    master = str(master).strip().lower()
    provided = str(password).strip().lower()
    
    return provided == master

# Middleware de seguridad
@app.middleware("http")
async def license_check_middleware(request: Request, call_next):
    path = request.url.path
    
    # Permitir TODAS las rutas que no sean de la API (frontend, assets)
    if not path.startswith("/api"):
        return await call_next(request)
        
    # Rutas de la API que NO requieren licencia (públicas)
    public_api_paths = [
        "/api/license/validate",
        "/api/license/generate",
        "/api/license/list",
        "/api/scanner/view",
        "/api/export/pdf-boletas",
        "/api/export/excel"
    ]

    if any(path.startswith(p) for p in public_api_paths):
        return await call_next(request)
    
    # El resto requiere Key
    license_key = request.headers.get("X-License-Key")
    if not license_key:
        return JSONResponse(status_code=403, content={"detail": "LICENSE_REQUIRED"})
    
    db = next(get_db())
    valid_license = db.query(License).filter(
        License.key == license_key.strip(),
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).first()
    
    if not valid_license:
        return JSONResponse(status_code=403, content={"detail": "LICENSE_INVALID"})
    
    return await call_next(request)

# --- ENDPOINTS ---
class LicenseCreate(BaseModel):
    days: int
    admin_pass: str

class LicenseValidate(BaseModel):
    key: str

@app.post("/api/license/validate")
def validate_key(data: LicenseValidate, db: Session = Depends(get_db)):
    lic = db.query(License).filter(
        License.key == data.key.strip(),
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).first()
    if lic:
        return {"valid": True, "expires_at": lic.expires_at}
    raise HTTPException(status_code=403, detail="Clave no válida")

@app.post("/api/license/generate")
def generate_license(data: LicenseCreate, db: Session = Depends(get_db)):
    if not verify_admin(data.admin_pass):
        raise HTTPException(status_code=401, detail="Error de autenticación")
    
    new_key = "EINSTEIN-" + str(uuid.uuid4()).upper()[:8]
    expires = datetime.utcnow() + timedelta(days=data.days)
    db_license = License(key=new_key, expires_at=expires)
    db.add(db_license)
    db.commit()
    return {"key": new_key, "expires_at": expires}

@app.get("/api/license/list")
def list_licenses(admin_pass: str, db: Session = Depends(get_db)):
    if not verify_admin(admin_pass):
        raise HTTPException(status_code=401, detail="Acceso denegado")
    return db.query(License).all()

# Routers de la App
from backend.routers import exams, generator, scanner, results, export
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(generator.router, prefix="/api/generator", tags=["Generator"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["Scanner"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Servir Frontend
frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"): raise HTTPException(status_code=404)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def read_root(): return {"status": "running"}
