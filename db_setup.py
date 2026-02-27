import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Numeric, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL # <-- Importación nueva y salvadora

# 1. Cargar credenciales del archivo .env
load_dotenv()

# Limpiamos cualquier comilla (') o espacio invisible que se haya colado
host = os.getenv("DB_HOST").strip("'\" ")
port = int(os.getenv("DB_PORT").strip("'\" "))
user = os.getenv("DB_USERNAME").strip("'\" ")
password = os.getenv("DB_PASSWORD").strip("'\" ")
database = os.getenv("DB_DATABASE").strip("'\" ")

# 2. Cadena de conexión usando el armador nativo de SQLAlchemy (A prueba de errores)
url_object = URL.create(
    drivername="mysql+pymysql",
    username=user,
    password=password,
    host=host,
    port=port,
    database=database,
    query={"ssl_verify_cert": "true", "ssl_verify_identity": "true"}
)

# 3. Iniciar el motor de SQLAlchemy
engine = create_engine(url_object, echo=True)
Base = declarative_base()

# --- MODELO: Dominio Servicio de Socios ---
class Socio(Base):
    __tablename__ = "t_socios"
    
    id_socio = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    estado_actual = Column(String(20), nullable=False)
    usuario = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, server_default=text('NOW()'))
    fecha_modifica = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    activo_sn = Column(TINYINT(1), server_default=text('1'))

# --- MODELO: Dominio Servicio de Estado de Cuenta ---
class EstadoCuenta(Base):
    __tablename__ = "t_estado_cuenta"
    
    id_cuenta = Column(Integer, primary_key=True, autoincrement=True)
    id_socio = Column(Integer, nullable=False, index=True) # Puntero Lógico
    monto_aporte = Column(Numeric(10, 2), nullable=False, server_default=text('0'))
    periodo = Column(String(20), nullable=False)
    estado_pago = Column(String(20), nullable=False)
    u_actualizacion = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    u_modifica = Column(String(50))

# --- FUNCIÓN PARA CREAR TABLAS ---
def crear_tablas():
    print("Conectando a TiDB Serverless de forma segura...")
    Base.metadata.create_all(bind=engine)
    print("¡Éxito! Tablas t_socios y t_estado_cuenta creadas en la nube.")

if __name__ == "__main__":
    crear_tablas()

    # (Pon esto al final de db_setup.py)
class Reserva(Base):
    __tablename__ = "t_reservas"
    id_reserva = Column(Integer, primary_key=True, index=True)
    id_socio = Column(Integer, nullable=False)
    sede = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    horario = Column(String(20), nullable=False)
    estado = Column(String(20), default='Confirmado')