import os
import csv
import io
from collections import Counter
from flask import Blueprint, render_template, request, jsonify, Response, current_app
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, CSRFError
from sqlalchemy import func
from . import db
from .models import Cliente, Servicio, Tecnico, Solicitud, OrdenTrabajo, Seguimiento

bp = Blueprint('jh7', __name__)

def is_authorized():
    return current_user.is_authenticated and any(r.name in ('Admin','Tecnico','Gerencia') for r in current_user.roles)

def blocked():
    return jsonify({'error':'Sin permisos para esta operación'}), 403

@bp.route('/')
def inicio():
    return render_template('inicio.html')

@bp.route('/panel')
@login_required
def panel():
    if not is_authorized(): return 'Acceso no autorizado', 403
    stats = {
       'solicitudes': db.session.query(func.count(Solicitud.id)).scalar() or 0,
       'ordenes': db.session.query(func.count(OrdenTrabajo.id)).filter(OrdenTrabajo.estado=='En proceso').scalar() or 0,
       'pendientes': db.session.query(func.count(OrdenTrabajo.id)).filter(OrdenTrabajo.estado=='Pendiente').scalar() or 0,
       'finalizados': db.session.query(func.count(OrdenTrabajo.id)).filter(OrdenTrabajo.estado=='Finalizado').scalar() or 0
    }
    ultimas = Solicitud.query.order_by(Solicitud.fecha.desc()).limit(8).all()
    return render_template('panel.html', stats=stats, ultimas=ultimas)

@bp.route('/reportes')
@login_required
def reportes():
    if not is_authorized(): return 'Acceso no autorizado', 403
    tipo = request.args.get('tipo','servicios')
    if tipo not in ('servicios','estados','tecnicos'): tipo='servicios'
    fecha_desde=request.args.get('desde','')
    fecha_hasta=request.args.get('hasta','')
    filtros=[]
    try:
        from datetime import datetime, timedelta
        if fecha_desde: filtros.append(Solicitud.fecha >= datetime.strptime(fecha_desde,'%Y-%m-%d'))
        if fecha_hasta: filtros.append(Solicitud.fecha < datetime.strptime(fecha_hasta,'%Y-%m-%d')+timedelta(days=1))
    except ValueError:
        return 'Fecha inválida (use AAAA-MM-DD)', 400
    if tipo == 'servicios':
        q = db.session.query(Servicio.nombre,func.count(Solicitud.id)).join(Solicitud, Solicitud.servicio_id==Servicio.id).filter(*filtros).group_by(Servicio.id,Servicio.nombre).order_by(Servicio.nombre)
        columnas=['Servicio','Solicitudes']
    elif tipo == 'estados':
        q = db.session.query(OrdenTrabajo.estado,func.count(OrdenTrabajo.id)).join(Solicitud, OrdenTrabajo.solicitud_id==Solicitud.id).filter(*filtros).group_by(OrdenTrabajo.estado).order_by(OrdenTrabajo.estado)
        columnas=['Estado','Órdenes']
    else:
        q = db.session.query(Tecnico.nombre,func.count(OrdenTrabajo.id)).join(OrdenTrabajo, OrdenTrabajo.tecnico_id==Tecnico.id).join(Solicitud, OrdenTrabajo.solicitud_id==Solicitud.id).filter(*filtros).group_by(Tecnico.id,Tecnico.nombre).order_by(Tecnico.nombre)
        columnas=['Técnico','Trabajos asignados']
    datos=[(str(a),int(b)) for a,b in q.all()]
    if request.args.get('exportar')=='csv':
        output=io.StringIO()
        writer=csv.writer(output)
        writer.writerow(columnas)
        writer.writerows(datos)
        return Response('﻿'+output.getvalue(), mimetype='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename=reporte_{tipo}.csv'})
    return render_template('reportes.html', tipo=tipo, datos=datos, columnas=columnas, desde=fecha_desde, hasta=fecha_hasta)

@bp.route('/asistente')
@login_required
def asistente():
    if not is_authorized(): return 'Acceso no autorizado',403
    return render_template('asistente.html')

@bp.route('/api/asistente',methods=['POST'])
@login_required
def api_asistente():
    if not is_authorized(): return blocked()
    payload=request.get_json(silent=True) or {}
    mensaje=payload.get('mensaje','')
    if not isinstance(mensaje,str) or not 1 <= len(mensaje.strip()) <= 1500:
        return jsonify({'error':'La consulta debe tener entre 1 y 1500 caracteres.'}),400
    raw_hist=payload.get('historial',[])
    if not isinstance(raw_hist,list): raw_hist=[]
    historial=[]
    for item in raw_hist[-8:]:
        if isinstance(item,dict) and item.get('role') in ('user','assistant') and isinstance(item.get('content'),str):
            historial.append({'role':item['role'],'content':item['content'][:1500]})
    key=os.getenv('GROQ_API_KEY','').strip()
    if not key:
        return jsonify({'error':'Falta GROQ_API_KEY en el archivo .env.'}),503
    # Datos reales, agregados y no personales; no compartimos información identificable de clientes.
    por_servicio=db.session.query(Servicio.nombre,func.count(Solicitud.id)).outerjoin(Solicitud).group_by(Servicio.id, Servicio.nombre).all()
    por_estado=db.session.query(OrdenTrabajo.estado,func.count(OrdenTrabajo.id)).group_by(OrdenTrabajo.estado).all()
    contexto='Servicios y solicitudes: '+', '.join(f'{n}: {c}' for n,c in por_servicio)
    contexto+='\nÓrdenes según estado: '+', '.join(f'{n}: {c}' for n,c in por_estado)
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=os.getenv('GROQ_BASE_URL','https://api.groq.com/openai/v1'),timeout=25.0)
        system=('Eres un asistente de diagnóstico técnico de telecomunicaciones para JH7 SRL TELECOM. '
                'Responde en español, con recomendaciones prudentes para fibra óptica, BTS, radioenlaces y planta externa. '
                'No inventes órdenes, datos de clientes, mediciones ni reparaciones ejecutadas. '
                'Si hay riesgos eléctricos o trabajos en altura, indica que actúe personal cualificado. '
                'Utiliza únicamente estas estadísticas como contexto real del sistema:\n'+contexto)
        resp=client.chat.completions.create(model=os.getenv('GROQ_MODEL','openai/gpt-oss-20b'),messages=[{'role':'system','content':system}]+historial+[{'role':'user','content':mensaje.strip()}],temperature=0.3,max_tokens=650)
        respuesta=(resp.choices[0].message.content or '').strip()
        if not respuesta: raise ValueError('El modelo devolvió una respuesta vacía')
        return jsonify({'respuesta':respuesta})
    except Exception as exc:
        current_app.logger.exception('Error consultando Groq')
        return jsonify({'error':'No se pudo consultar la IA. Revisa la conexión, el modelo y la API key; consulta el terminal.'}),502
