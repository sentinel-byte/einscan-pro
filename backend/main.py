import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime

from backend.database import engine, Base, get_db
from backend.models.config import AppConfig, License

# Importar otros modelos
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

# Middleware para validar Licencia (excepto rutas de activación y estáticos)
@app.middleware("http")
async def license_check_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/license") or not path.startswith("/api") or path.startswith("/api/scanner/view"):
        return await call_next(request)
    
    db = next(get_db())
    valid_license = db.query(License).filter(
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).first()
    
    if not valid_license:
        return JSONResponse(
            status_code=403,
            content={"detail": "LICENSE_EXPIRED", "message": "Tu licencia ha expirado o no tienes una activa."}
        )
    
    return await call_next(request)

# Router de Licencias
from pydantic import BaseModel
from datetime import timedelta
import uuid

class LicenseCreate(BaseModel):
    days: int
    admin_pass: str

@app.post("/api/license/generate")
def generate_license(data: LicenseCreate, db: Session = Depends(get_db)):
    master_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    if data.admin_pass != master_pass:
        raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta")
    
    new_key = str(uuid.uuid4()).upper()[:8]
    expires = datetime.utcnow() + timedelta(days=data.days)
    
    db_license = License(key=new_key, expires_at=expires)
    db.add(db_license)
    db.commit()
    return {"key": new_key, "expires_at": expires}

@app.get("/api/license/status")
def check_status(db: Session = Depends(get_db)):
    lic = db.query(License).filter(License.is_active == True, License.expires_at > datetime.utcnow()).first()
    if lic:
        return {"active": True, "expires_at": lic.expires_at}
    return {"active": False}

# Inclusión de routers existentes
from backend.routers import exams, generator, scanner, results, export
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(generator.router, prefix="/api/generator", tags=["Generator"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["Scanner"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Servir Frontend con CATCH-ALL para evitar el 404 al actualizar
frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_dist):
    # Servir archivos estáticos (js, css, etc)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Si la ruta empieza con api, no devolvemos el index
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "EinScan Pro Backend activo. Frontend no compilado."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
