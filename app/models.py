from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Cliente(Model):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    empresa = Column(String(120))
    telefono = Column(String(40))
    email = Column(String(120))
    direccion = Column(String(200))
    activo = Column(Boolean, default=True, nullable=False)

    solicitudes = relationship('Solicitud', back_populates='cliente')

    def __repr__(self):
        return self.nombre


class Servicio(Model):
    __tablename__ = 'servicios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(250))
    activo = Column(Boolean, default=True, nullable=False)

    solicitudes = relationship('Solicitud', back_populates='servicio')

    def __repr__(self):
        return self.nombre


class Tecnico(Model):
    __tablename__ = 'tecnicos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    especialidad = Column(String(100))
    telefono = Column(String(40))
    activo = Column(Boolean, default=True, nullable=False)

    ordenes = relationship('OrdenTrabajo', back_populates='tecnico')

    def __repr__(self):
        return self.nombre


class Solicitud(Model):
    __tablename__ = 'solicitudes'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    servicio_id = Column(Integer, ForeignKey('servicios.id'), nullable=False)
    asunto = Column(String(160), nullable=False)
    descripcion = Column(Text)
    prioridad = Column(String(20), default='Media', nullable=False)
    estado = Column(String(25), default='Pendiente', nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    cliente = relationship('Cliente', back_populates='solicitudes')
    servicio = relationship('Servicio', back_populates='solicitudes')
    ordenes = relationship('OrdenTrabajo', back_populates='solicitud')

    def __repr__(self):
        servicio = self.servicio.nombre if self.servicio else 'Sin servicio'
        return f'Solicitud #{self.id} - {servicio}'


class OrdenTrabajo(Model):
    __tablename__ = 'ordenes_trabajo'

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey('solicitudes.id'), nullable=False)
    tecnico_id = Column(Integer, ForeignKey('tecnicos.id'), nullable=False)
    detalle = Column(Text)
    estado = Column(String(25), default='Pendiente', nullable=False)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_cierre = Column(DateTime)

    solicitud = relationship('Solicitud', back_populates='ordenes')
    tecnico = relationship('Tecnico', back_populates='ordenes')
    seguimientos = relationship('Seguimiento', back_populates='orden')

    def __repr__(self):
        return f'Orden #{self.id}'


class Seguimiento(Model):
    __tablename__ = 'seguimientos'

    id = Column(Integer, primary_key=True)
    orden_id = Column(Integer, ForeignKey('ordenes_trabajo.id'), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    observacion = Column(Text, nullable=False)
    estado_reportado = Column(String(25), nullable=False, default='En proceso')

    orden = relationship('OrdenTrabajo', back_populates='seguimientos')

    def __repr__(self):
        return f'Seguimiento #{self.id}'