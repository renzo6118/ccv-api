import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import URL
from db_setup import Socio, EstadoCuenta  # Importamos los modelos que creaste
from db_setup import Socio, EstadoCuenta, Reserva  # <--- Agrega Reserva aquí

# --- 1. CONFIGURACIÓN DE BASE DE DATOS ---
load_dotenv()
host = os.getenv("DB_HOST").strip("'\" ")
port = int(os.getenv("DB_PORT").strip("'\" "))
user = os.getenv("DB_USERNAME").strip("'\" ")
password = os.getenv("DB_PASSWORD").strip("'\" ")
database = os.getenv("DB_DATABASE").strip("'\" ")

url_object = URL.create(
    drivername="mysql+pymysql",
    username=user,
    password=password,
    host=host,
    port=port,
    database=database,
    query={"ssl_verify_cert": "true", "ssl_verify_identity": "true"}
)

engine = create_engine(url_object)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. INICIALIZAR FASTAPI ---
from fastapi.middleware.cors import CORSMiddleware  # <-- Importante agregar esto

app = FastAPI(
    title="CCV API - Arquitectura SOA",
    description="Implementación de servicios REST para Gestión de procesos del Country Club de Villa.",
    version="1.0.0"
)

# --- CONFIGURACIÓN DE CORS (El permiso para tu web) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # El asterisco permite que cualquier web entre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. DTOs (Modelos de Entrada y Salida para Swagger) ---
class CredencialesDTO(BaseModel):
    usuario: str
    password: str

class ReservaDTO(BaseModel):
    idSocio: int
    idInstalacion: int
    fecha: str
    horaInicio: str
    horaFin: str

class ResetPasswordDTO(BaseModel):
    usuario: str
    nuevaPassword: str

# --- 4. SERVICIOS (ENDPOINTS) ---

@app.post("/autenticacion/autenticarSocio", tags=["Servicio: Autenticación"])
def autenticar_socio(credenciales: CredencialesDTO, db: Session = Depends(get_db)):
    """ Valida las credenciales del socio en la base de datos """
    socio = db.query(Socio).filter(Socio.usuario == credenciales.usuario).first()
    
    if not socio or socio.password != credenciales.password:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    if socio.activo_sn == 0 or socio.estado_actual != 'Activo':
        raise HTTPException(status_code=403, detail="El socio no se encuentra activo")

    return {
        "mensaje": "Autenticación exitosa",
        "tokenAutorizacion": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...",
        "datosSocio": {
            "id_socio": socio.id_socio,
            "nombres": f"{socio.nombre} {socio.apellido}",
            "dni": socio.dni
        }
    }

@app.get("/finanzas/consultarEstadoCuenta/{id_socio}", tags=["Servicio: Estado Financiero"])
def consultar_estado_cuenta(id_socio: int, db: Session = Depends(get_db)):
    """ Consulta la deuda y pagos del socio en la base de datos """
    cuentas = db.query(EstadoCuenta).filter(EstadoCuenta.id_socio == id_socio).all()
    
    if not cuentas:
        return {"mensaje": "El socio no tiene estados de cuenta registrados", "deuda_total": 0, "detalle": []}
    
    detalle = []
    deuda_total = 0
    for c in cuentas:
        detalle.append({
            "id_cuenta": c.id_cuenta,
            "periodo": c.periodo,
            "monto": c.monto_aporte,
            "estado": c.estado_pago
        })
        if c.estado_pago == 'Pendiente':
            deuda_total += c.monto_aporte
            
    return {
        "id_socio": id_socio,
        "deuda_total": deuda_total,
        "detalle_cuentas": detalle
    }

@app.post("/reservas/registrarReserva", tags=["Servicio: Reservas"])
def registrar_reserva(reserva: ReservaDTO, db: Session = Depends(get_db)):
    """ Registra una nueva reserva de instalación en la Base de Datos """
    
    # Validar si el socio existe
    socio = db.query(Socio).filter(Socio.id_socio == reserva.idSocio).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    # Crear la nueva reserva
    nueva_reserva = Reserva(
        id_socio=reserva.idSocio,
        sede=f"Sede ID: {reserva.idInstalacion}", 
        fecha=reserva.fecha,
        horario=reserva.horaInicio
    )
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    
    return {
        "codigoReserva": f"RES-2026-0{nueva_reserva.id_reserva}",
        "estado": "Confirmado",
        "mensaje": "¡Reserva registrada exitosamente!"
    }

@app.put("/autenticacion/actualizarPassword", tags=["Servicio: Autenticación"])
def actualizar_password(datos: ResetPasswordDTO, db: Session = Depends(get_db)):
    """ Actualiza la contraseña de un socio en la base de datos """
    socio = db.query(Socio).filter(Socio.usuario == datos.usuario).first()
    
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    socio.password = datos.nuevaPassword
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}