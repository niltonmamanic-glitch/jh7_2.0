from datetime import datetime

from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import (
    Cliente,
    Servicio,
    Tecnico,
    Solicitud,
    OrdenTrabajo,
    Seguimiento
)


# CONFIGURACION GENERAL DE LAS VISTAS
class BaseJH7View(ModelView):
    page_size = 20
    can_export = True


# GESTION DE CLIENTES
class ClienteView(BaseJH7View):

    list_title = 'Lista de clientes'
    add_title = 'Registrar cliente'
    edit_title = 'Editar cliente'
    show_title = 'Detalle del cliente'
    datamodel = SQLAInterface(Cliente)

    list_columns = [
        'nombre',
        'empresa',
        'telefono',
        'email',
        'activo'
    ]

    show_columns = [
        'nombre',
        'empresa',
        'telefono',
        'email',
        'direccion',
        'activo'
    ]

    add_columns = edit_columns = [
        'nombre',
        'empresa',
        'telefono',
        'email',
        'direccion',
        'activo'
    ]

    search_columns = [
        'nombre',
        'empresa',
        'telefono'
    ]


# GESTION DE SERVICIOS
class ServicioView(BaseJH7View):

    list_title = 'Lista de servicios'
    add_title = 'Registrar servicio'
    edit_title = 'Editar servicio'
    show_title = 'Detalle del servicio'
    datamodel = SQLAInterface(Servicio)
    

    list_columns = [
        'nombre',
        'descripcion',
        'activo'
    ]

    add_columns = edit_columns = [
        'nombre',
        'descripcion',
        'activo'
    ]

    search_columns = ['nombre']


# GESTION DE TECNICOS
class TecnicoView(BaseJH7View):

    list_title = 'Lista de técnicos'
    add_title = 'Registrar técnico'
    edit_title = 'Editar técnico'
    show_title = 'Detalle del técnico'
    datamodel = SQLAInterface(Tecnico)

    list_columns = [
        'nombre',
        'especialidad',
        'telefono',
        'activo'
    ]

    add_columns = edit_columns = [
        'nombre',
        'especialidad',
        'telefono',
        'activo'
    ]

    search_columns = [
        'nombre',
        'especialidad'
    ]


# GESTION DE SOLICITUDES
class SolicitudView(BaseJH7View):
    datamodel = SQLAInterface(Solicitud)

    list_columns = [
        'id',
        'cliente',
        'servicio',
        'asunto',
        'prioridad',
        'estado',
        'fecha'
    ]

    add_columns = edit_columns = [
        'cliente',
        'servicio',
        'asunto',
        'descripcion',
        'prioridad',
        'estado'
    ]

    show_columns = [
        'id',
        'cliente',
        'servicio',
        'asunto',
        'descripcion',
        'prioridad',
        'estado',
        'fecha'
    ]

    search_columns = [
        'asunto',
        'estado',
        'prioridad'
    ]

    label_columns = {
        'id': 'N.º',
        'cliente': 'Cliente',
        'servicio': 'Servicio',
        'asunto': 'Asunto',
        'fecha': 'Fecha'
    }


# GESTION DE ORDENES DE TRABAJO
class OrdenTrabajoView(BaseJH7View):
    datamodel = SQLAInterface(OrdenTrabajo)

    list_columns = [
        'id',
        'solicitud',
        'tecnico',
        'estado',
        'fecha_asignacion',
        'fecha_cierre'
    ]

    # Formulario para crear una orden
    add_columns = [
        'solicitud',
        'tecnico',
        'detalle',
        'estado'
    ]

    # Formulario para modificar una orden
    edit_columns = [
        'solicitud',
        'tecnico',
        'detalle',
        'estado'
    ]

    # Informacion visible al consultar
    show_columns = [
        'id',
        'solicitud',
        'tecnico',
        'detalle',
        'estado',
        'fecha_asignacion',
        'fecha_cierre'
    ]

    search_columns = [
        'estado'
    ]

    label_columns = {
        'id': 'N.º',
        'solicitud': 'Solicitud',
        'tecnico': 'Tecnico',
        'detalle': 'Detalle',
        'estado': 'Estado',
        'fecha_asignacion': 'Fecha de asignacion',
        'fecha_cierre': 'Fecha de cierre'
    }

    # Generar automaticamente la fecha
    # al registrar una nueva orden
    def pre_add(self, item):
        item.fecha_asignacion = datetime.now().replace(
            microsecond=0
        )

        item.fecha_cierre = None


# GESTION DE SEGUIMIENTOS
class SeguimientoView(BaseJH7View):
    datamodel = SQLAInterface(Seguimiento)

    list_columns = [
        'id',
        'orden',
        'fecha',
        'estado_reportado',
        'observacion'
    ]

    add_columns = edit_columns = [
        'orden',
        'observacion',
        'estado_reportado'
    ]

    search_columns = [
        'estado_reportado'
    ]


# REGISTRO DE LOS MODULOS
def register_views(appbuilder):

    # INICIO - PANEL ADMINISTRATIVO
    appbuilder.add_link(
        name='Inicio',
        href='/panel',
        icon='fa-home',
        category='Gestión JH7'
    )

    for view, name, icon in [

        (
            ClienteView,
            'Clientes',
            'fa-users'
        ),

        (
            ServicioView,
            'Servicios',
            'fa-wifi'
        ),

        (
            TecnicoView,
            'Técnicos',
            'fa-wrench'
        ),

        (
            SolicitudView,
            'Solicitudes',
            'fa-clipboard'
        ),

        (
            OrdenTrabajoView,
            'Órdenes de trabajo',
            'fa-tasks'
        ),

        (
            SeguimientoView,
            'Seguimientos',
            'fa-history'
        )

    ]:

        appbuilder.add_view(
            view,
            name,
            icon=icon,
            category='Gestión JH7'
        )