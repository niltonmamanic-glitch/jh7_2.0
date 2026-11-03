import os
import csv
import io

from pathlib import Path
from datetime import datetime, timedelta
from dotenv import dotenv_values

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    Response,
    current_app
)

from flask_login import login_required, current_user
from sqlalchemy import func

from . import db
from .models import Servicio, Tecnico, Solicitud, OrdenTrabajo


bp = Blueprint('jh7', __name__)


# Permisos de acceso
def is_authorized():
    if not current_user.is_authenticated:
        return False

    roles = ('Admin', 'Tecnico', 'Gerencia')

    return any(
        rol.name in roles for rol in current_user.roles
    )


def blocked():
    return jsonify({
        'error': 'Sin permisos para esta operación'
    }), 403


# Pagina principal
@bp.route('/')
def inicio():
    return render_template('inicio.html')


# Panel administrativo
@bp.route('/panel')
@login_required
def panel():
    if not is_authorized():
        return 'Acceso no autorizado', 403

    stats = {
        'solicitudes': db.session.query(
            func.count(Solicitud.id)
        ).scalar() or 0,

        'ordenes': db.session.query(
            func.count(OrdenTrabajo.id)
        ).filter(
            OrdenTrabajo.estado == 'En proceso'
        ).scalar() or 0,

        'pendientes': db.session.query(
            func.count(OrdenTrabajo.id)
        ).filter(
            OrdenTrabajo.estado == 'Pendiente'
        ).scalar() or 0,

        'finalizados': db.session.query(
            func.count(OrdenTrabajo.id)
        ).filter(
            OrdenTrabajo.estado == 'Finalizado'
        ).scalar() or 0
    }

    ultimas = db.session.query(Solicitud).order_by(
    Solicitud.fecha.desc()
).limit(8).all()

    return render_template(
        'panel.html',
        stats=stats,
        ultimas=ultimas
    )


# Reportes del sistema
@bp.route('/reportes')
@login_required
def reportes():
    if not is_authorized():
        return 'Acceso no autorizado', 403

    tipo = request.args.get('tipo', 'servicios')

    if tipo not in ('servicios', 'estados', 'tecnicos'):
        tipo = 'servicios'

    fecha_desde = request.args.get('desde', '')
    fecha_hasta = request.args.get('hasta', '')

    filtros = []

    try:
        if fecha_desde:
            inicio_fecha = datetime.strptime(
                fecha_desde, '%Y-%m-%d'
            )

            filtros.append(
                Solicitud.fecha >= inicio_fecha
            )

        if fecha_hasta:
            fin_fecha = datetime.strptime(
                fecha_hasta, '%Y-%m-%d'
            ) + timedelta(days=1)

            filtros.append(
                Solicitud.fecha < fin_fecha
            )

    except ValueError:
        return 'Fecha inválida (use AAAA-MM-DD)', 400

    # Solicitudes por servicio
    if tipo == 'servicios':
        consulta = db.session.query(
            Servicio.nombre,
            func.count(Solicitud.id)
        ).join(
            Solicitud,
            Solicitud.servicio_id == Servicio.id
        ).filter(
            *filtros
        ).group_by(
            Servicio.id,
            Servicio.nombre
        ).order_by(
            Servicio.nombre
        )

        columnas = ['Servicio', 'Solicitudes']

    # Ordenes por estado
    elif tipo == 'estados':
        consulta = db.session.query(
            OrdenTrabajo.estado,
            func.count(OrdenTrabajo.id)
        ).join(
            Solicitud,
            OrdenTrabajo.solicitud_id == Solicitud.id
        ).filter(
            *filtros
        ).group_by(
            OrdenTrabajo.estado
        ).order_by(
            OrdenTrabajo.estado
        )

        columnas = ['Estado', 'Órdenes']

    # Trabajos por tecnico
    else:
        consulta = db.session.query(
            Tecnico.nombre,
            func.count(OrdenTrabajo.id)
        ).join(
            OrdenTrabajo,
            OrdenTrabajo.tecnico_id == Tecnico.id
        ).join(
            Solicitud,
            OrdenTrabajo.solicitud_id == Solicitud.id
        ).filter(
            *filtros
        ).group_by(
            Tecnico.id,
            Tecnico.nombre
        ).order_by(
            Tecnico.nombre
        )

        columnas = ['Técnico', 'Trabajos asignados']

    datos = [
        (str(nombre), int(cantidad))
        for nombre, cantidad in consulta.all()
    ]

    # Exportacion a CSV
    if request.args.get('exportar') == 'csv':
        archivo = io.StringIO()
        escritor = csv.writer(archivo)

        escritor.writerow(columnas)
        escritor.writerows(datos)

        contenido = '\ufeff' + archivo.getvalue()

        return Response(
            contenido,
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition':
                f'attachment; filename=reporte_{tipo}.csv'
            }
        )

    return render_template(
        'reportes.html',
        tipo=tipo,
        datos=datos,
        columnas=columnas,
        desde=fecha_desde,
        hasta=fecha_hasta
    )


# Pagina del asistente
@bp.route('/asistente')
@login_required
def asistente():
    if not is_authorized():
        return 'Acceso no autorizado', 403

    return render_template('asistente.html')


# Asistente de inteligencia artificial
@bp.route('/api/asistente', methods=['POST'])
@login_required
def api_asistente():
    if not is_authorized():
        return blocked()

    datos = request.get_json(silent=True) or {}
    mensaje = datos.get('mensaje', '')

    if not isinstance(mensaje, str):
        return jsonify({
            'error': 'La consulta debe ser un texto.'
        }), 400

    mensaje = mensaje.strip()

    if not 1 <= len(mensaje) <= 1500:
        return jsonify({
            'error': 'La consulta debe tener entre 1 y 1500 caracteres.'
        }), 400

    # Historial de conversacion
    historial_recibido = datos.get('historial', [])

    if not isinstance(historial_recibido, list):
        historial_recibido = []

    historial = []

    for item in historial_recibido[-8:]:
        if not isinstance(item, dict):
            continue

        rol = item.get('role')
        contenido = item.get('content')

        if rol in ('user', 'assistant') and isinstance(contenido, str):
            historial.append({
                'role': rol,
                'content': contenido[:1500]
            })

    # Leer la clave desde el archivo .env
    ruta_env = Path(__file__).resolve().parent.parent / '.env'
    configuracion = dotenv_values(ruta_env)

    clave = (
        configuracion.get('GROQ_API_KEY')
        or current_app.config.get('GROQ_API_KEY')
        or os.getenv('GROQ_API_KEY')
        or ''
    ).strip()

    # Mostrar solo si la clave fue encontrada
    print('Archivo .env encontrado:', ruta_env.is_file(), flush=True)
    print('Clave Groq disponible:', bool(clave), flush=True)

    if not clave:
        return jsonify({
            'error': 'No se encontró la clave de Groq. Revisa el archivo .env.'
        }), 503

    modelo = (
        configuracion.get('GROQ_MODEL')
        or current_app.config.get('GROQ_MODEL')
        or 'openai/gpt-oss-20b'
    )

    url_groq = (
        configuracion.get('GROQ_BASE_URL')
        or current_app.config.get('GROQ_BASE_URL')
        or 'https://api.groq.com/openai/v1'
    )

    # Estadisticas de la base de datos
    servicios = db.session.query(
        Servicio.nombre,
        func.count(Solicitud.id)
    ).outerjoin(
        Solicitud
    ).group_by(
        Servicio.id,
        Servicio.nombre
    ).all()

    estados = db.session.query(
        OrdenTrabajo.estado,
        func.count(OrdenTrabajo.id)
    ).group_by(
        OrdenTrabajo.estado
    ).all()

    resumen_servicios = ', '.join(
        f'{nombre}: {cantidad}'
        for nombre, cantidad in servicios
    )

    resumen_estados = ', '.join(
        f'{estado}: {cantidad}'
        for estado, cantidad in estados
    )

    contexto = (
        'Servicios y solicitudes: '
        + resumen_servicios
        + '\nÓrdenes según estado: '
        + resumen_estados
    )

    # Instrucciones para la inteligencia artificial
    instrucciones = (
        'Eres un asistente de diagnóstico técnico de '
        'JH7 SRL TELECOM. '
        'Responde en español de forma clara y sencilla. '
        'Ayuda a diagnosticar problemas de fibra óptica, '
        'radioenlaces, BTS y redes de telecomunicaciones. '
        'Explica los pasos de solución de manera ordenada. '
        'No inventes información de clientes ni trabajos realizados. '
        'En actividades peligrosas recomienda personal capacitado. '
        'Estas son las estadísticas reales del sistema:\n'
        + contexto
    )

    # Conexion con Groq
    try:
        from openai import OpenAI

        cliente = OpenAI(
            api_key=clave,
            base_url=url_groq,
            timeout=25.0
        )

        mensajes = [
            {
                'role': 'system',
                'content': instrucciones
            }
        ]

        mensajes.extend(historial)

        mensajes.append({
            'role': 'user',
            'content': mensaje
        })

        resultado = cliente.chat.completions.create(
            model=modelo,
            messages=mensajes,
            temperature=0.3,
            max_tokens=650
        )

        respuesta = (
            resultado.choices[0].message.content or ''
        ).strip()

        if not respuesta:
            return jsonify({
                'error': 'La inteligencia artificial no devolvió una respuesta.'
            }), 502

        return jsonify({
            'respuesta': respuesta
        })

    except Exception:
        current_app.logger.exception(
            'Error al consultar Groq'
        )

        return jsonify({
            'error': 'No se pudo conectar con Groq. Revisa la terminal de VS Code.'
        }), 502