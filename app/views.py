from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from wtforms.validators import DataRequired
from .models import Cliente, Servicio, Tecnico, Solicitud, OrdenTrabajo, Seguimiento

class BaseJH7View(ModelView):
    page_size = 20
    can_export = True

class ClienteView(BaseJH7View):
    datamodel = SQLAInterface(Cliente)
    list_columns = ['nombre', 'empresa', 'telefono', 'email', 'activo']
    show_columns = ['nombre', 'empresa', 'telefono', 'email', 'direccion', 'activo']
    add_columns = edit_columns = ['nombre', 'empresa', 'telefono', 'email', 'direccion', 'activo']
    search_columns = ['nombre','empresa','telefono']

class ServicioView(BaseJH7View):
    datamodel = SQLAInterface(Servicio)
    list_columns = ['nombre','descripcion','activo']
    add_columns = edit_columns = ['nombre','descripcion','activo']
    search_columns = ['nombre']

class TecnicoView(BaseJH7View):
    datamodel = SQLAInterface(Tecnico)
    list_columns = ['nombre','especialidad','telefono','activo']
    add_columns = edit_columns = ['nombre','especialidad','telefono','activo']
    search_columns = ['nombre','especialidad']

class SolicitudView(BaseJH7View):
    datamodel = SQLAInterface(Solicitud)
    list_columns = ['id','cliente','servicio','asunto','prioridad','estado','fecha']
    add_columns = edit_columns = ['cliente','servicio','asunto','descripcion','prioridad','estado']
    show_columns = ['id','cliente','servicio','asunto','descripcion','prioridad','estado','fecha']
    search_columns = ['asunto','estado','prioridad']
    label_columns = {'id':'N.º','cliente':'Cliente','servicio':'Servicio','asunto':'Asunto', 'fecha':'Fecha'}

class OrdenTrabajoView(BaseJH7View):
    datamodel = SQLAInterface(OrdenTrabajo)
    list_columns = ['id','solicitud','tecnico','estado','fecha_asignacion','fecha_cierre']
    add_columns = edit_columns = ['solicitud','tecnico','detalle','estado','fecha_asignacion','fecha_cierre']
    show_columns = ['id','solicitud','tecnico','detalle','estado','fecha_asignacion','fecha_cierre']
    search_columns = ['estado']

class SeguimientoView(BaseJH7View):
    datamodel = SQLAInterface(Seguimiento)
    list_columns = ['id','orden','fecha','estado_reportado','observacion']
    add_columns = edit_columns = ['orden','observacion','estado_reportado']
    search_columns = ['estado_reportado']

def register_views(appbuilder):
    for view,name,icon in [
        (ClienteView,'Clientes','fa-users'),
        (ServicioView,'Servicios','fa-wifi'),
        (TecnicoView,'Técnicos','fa-wrench'),
        (SolicitudView,'Solicitudes','fa-clipboard'),
        (OrdenTrabajoView,'Órdenes de trabajo','fa-tasks'),
        (SeguimientoView,'Seguimientos','fa-history'),
    ]:
        appbuilder.add_view(view, name, icon=icon, category='Gestión JH7')
