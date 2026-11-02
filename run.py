import click
from app import create_app, db
from app.models import Cliente, Servicio, Tecnico, Solicitud, OrdenTrabajo, Seguimiento

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Crear las tablas del proyecto y de seguridad (sin borrar datos)."""
    db.create_all()
    click.echo('Tablas verificadas/creadas. Ejecuta: flask --app run fab create-admin')

@app.cli.command('seed-demo')
def seed_demo():
    """Insertar ejemplos para practicar (solo si no existen)."""
    db.create_all()
    if Servicio.query.first():
        click.echo('Ya hay servicios. No se duplicaron registros.')
        return
    servicios=[Servicio(nombre=n,descripcion=d) for n,d in [
      ('Fibra Óptica','Instalación y mantenimiento FTTH'),
      ('Radio Bases','Estaciones BTS'),
      ('Radio Enlaces','Enlaces inalámbricos'),
      ('Planta Externa','Redes exteriores')]]
    clientes=[Cliente(nombre=n,empresa=e,telefono='70000000') for n,e in [('Ana Vargas','Constructora Andina'),('Luis Rojas','Minera Sur'),('Carmen Soto','Valle Digital'),('Pedro Pérez','Red Norte')]]
    tecnicos=[Tecnico(nombre=n,especialidad=e) for n,e in [('Técnico Uno','Fibra'),('Técnico Dos','Radio'),('Técnico Tres','Planta externa')]]
    db.session.add_all(servicios+clientes+tecnicos)
    db.session.flush()
    estados=['En proceso','Pendiente','En proceso','Finalizado']
    solicitudes=[Solicitud(cliente_id=clientes[i].id,servicio_id=servicios[i].id,asunto=['Instalación FTTH','Mantenimiento BTS','Revisión de radioenlace','Ampliación de red'][i],prioridad=['Alta','Media','Alta','Baja'][i],estado=estados[i]) for i in range(4)]
    db.session.add_all(solicitudes)
    db.session.flush()
    ordenes=[OrdenTrabajo(solicitud_id=s.id,tecnico_id=tecnicos[i%3].id,estado=estados[i],detalle=s.asunto) for i,s in enumerate(solicitudes)]
    db.session.add_all(ordenes)
    db.session.flush()
    db.session.add_all([Seguimiento(orden_id=o.id,observacion='Registro inicial de avance',estado_reportado=o.estado) for o in ordenes])
    db.session.commit()
    click.echo('Datos DEMO creados. Son ficticios, reemplázalos para la defensa.')

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8080,debug=True)
