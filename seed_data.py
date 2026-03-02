from main import SessionLocal
from db_setup import Socio, EstadoCuenta
from datetime import date

db = SessionLocal()

try:
    print("Iniciando la inserción masiva de 10 registros de prueba...")

    socios_data = [
        {"dni": "12208100", "nombre": "Kevin Francisco", "apellido": "Cossio Mercado", "usuario": "kcossio"},
        {"dni": "21311002", "nombre": "Andres Daniel", "apellido": "Mendizabal Martinez", "usuario": "amendizabal"},
        {"dni": "19307937", "nombre": "Ruben Ernesto", "apellido": "Meza Fernandez", "usuario": "rmeza"},
        {"dni": "20304103", "nombre": "Renzo Daniel", "apellido": "Minaya Cahuana", "usuario": "rminaya"},
        {"dni": "14129300", "nombre": "Ivan Leandro", "apellido": "Surichaque Espinoza", "usuario": "isurichaque"},
        {"dni": "70000001", "nombre": "Sofia", "apellido": "Serquen", "usuario": "sserquen"},
        {"dni": "70000002", "nombre": "Alexandro", "apellido": "Valderrama", "usuario": "avalderrama"},
        {"dni": "70000003", "nombre": "Maria", "apellido": "Quiroz", "usuario": "mquiroz"},
        {"dni": "70000004", "nombre": "Abigail", "apellido": "Torres", "usuario": "atorres"},
        {"dni": "70000005", "nombre": "Miguel", "apellido": "Sanchez", "usuario": "msanchez"}
    ]

    socios_insertados = []

    for i, data in enumerate(socios_data):
        nuevo_socio = Socio(
            dni=data["dni"],
            nombre=data["nombre"],
            apellido=data["apellido"],
            fecha_ingreso=date(2023 + (i % 3), (i % 12) + 1, 15), 
            estado_actual="Activo",
            usuario=data["usuario"],
            password="password123", 
            activo_sn=1
        )
        db.add(nuevo_socio)
        db.commit()
        db.refresh(nuevo_socio)
        socios_insertados.append(nuevo_socio)
        print(f"Socio registrado: {nuevo_socio.usuario} (ID: {nuevo_socio.id_socio})")


    periodos = ["Enero 2026", "Febrero 2026", "Marzo 2026"]
    estados = ["Pagado", "Pendiente", "Vencido"]
    
    for i, socio in enumerate(socios_insertados):
    
        cuenta_principal = EstadoCuenta(
            id_socio=socio.id_socio,
            monto_aporte=250.00 if i % 2 == 0 else 300.00,
            periodo=periodos[i % 3],
            estado_pago=estados[i % 3],
            u_modifica="admin_sistema"
        )
        db.add(cuenta_principal)
        
   
        if i % 3 == 0:
             cuenta_secundaria = EstadoCuenta(
                id_socio=socio.id_socio,
                monto_aporte=250.00,
                periodo=periodos[(i + 1) % 3],
                estado_pago="Pendiente",
                u_modifica="admin_sistema"
            )
             db.add(cuenta_secundaria)

    db.commit()
    print("\n¡Éxito total! Se insertaron los 10 socios y sus respectivos estados de cuenta en la nube.")

except Exception as e:
    print("Hubo un error durante la inserción:", e)
    db.rollback()
finally:
    db.close()