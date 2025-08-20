from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cooperenka_regalos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Asociado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), nullable=False, unique=True)
    nombre1 = db.Column(db.String(50), nullable=False)
    nombre2 = db.Column(db.String(50), default='')
    apellido1 = db.Column(db.String(50), nullable=False)
    apellido2 = db.Column(db.String(50), default='')
    agencia = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    observaciones = db.Column(db.Text, default='')
    estado = db.Column(db.String(20), default='PENDIENTE')
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    usuario_entrega = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombre_completo': f"{self.nombre1} {self.nombre2} {self.apellido1} {self.apellido2}".strip(),
            'agencia': self.agencia,
            'empresa': self.empresa,
            'observaciones': self.observaciones or '',
            'estado': self.estado,
            'fecha_entrega': self.fecha_entrega.strftime('%Y-%m-%d %H:%M') if self.fecha_entrega else '',
            'usuario_entrega': self.usuario_entrega or ''
        }

# Inicializar base de datos con datos de ejemplo
def inicializar_db():
    db.create_all()
    if Asociado.query.count() == 0:
        datos_ejemplo = [
            Asociado(cedula='12345678', nombre1='JUAN', nombre2='CARLOS',
                    apellido1='GARCIA', apellido2='PEREZ',
                    agencia='PRINCIPAL', empresa='EMPRESA A'),
            Asociado(cedula='87654321', nombre1='MARIA', nombre2='ELENA',
                    apellido1='MARTINEZ', apellido2='GONZALEZ',
                    agencia='ZONA NORTE', empresa='EMPRESA B',
                    observaciones='Contactar antes de entregar'),
            Asociado(cedula='11223344', nombre1='CARLOS', nombre2='ALBERTO',
                    apellido1='RODRIGUEZ', apellido2='HERNANDEZ',
                    agencia='CENTRO', empresa='EMPRESA C',
                    estado='ENTREGADO', fecha_entrega=datetime.now(),
                    usuario_entrega='Sistema'),
            Asociado(cedula='99887766', nombre1='ANA', nombre2='SOFIA',
                    apellido1='LOPEZ', apellido2='DIAZ',
                    agencia='SUR', empresa='EMPRESA D',
                    observaciones='Verificar identidad')
        ]
        
        for asociado in datos_ejemplo:
            db.session.add(asociado)
        db.session.commit()

@app.route('/')
def index():
    total = Asociado.query.count()
    entregados = Asociado.query.filter_by(estado='ENTREGADO').count()
    pendientes = total - entregados
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema Cooperenka</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .header-gradient {{
                background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
                color: white;
                padding: 2rem 0;
            }}
            .stat-card {{
                background: white;
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="header-gradient">
            <div class="container">
                <h1 class="text-center"><i class="fas fa-gift"></i> Sistema de Entrega de Regalos</h1>
                <h3 class="text-center">Cooperenka - Sistema Online</h3>
            </div>
        </div>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-4">
                    <div class="stat-card text-center">
                        <h2 class="text-primary">{total}</h2>
                        <p class="mb-0">Total Asociados</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center">
                        <h2 class="text-success">{entregados}</h2>
                        <p class="mb-0">Entregados</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center">
                        <h2 class="text-warning">{pendientes}</h2>
                        <p class="mb-0">Pendientes</p>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Ver Asociados</h5>
                            <p class="card-text">Lista completa con opciones de entrega</p>
                            <a href="/asociados" class="btn btn-primary">
                                <i class="fas fa-list"></i> Ver Lista
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-search fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Buscar Asociado</h5>
                            <p class="card-text">Búsqueda rápida por cédula</p>
                            <a href="/buscar" class="btn btn-success">
                                <i class="fas fa-search"></i> Buscar
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-success mt-4">
                <h4><i class="fas fa-check-circle"></i> Sistema Funcionando Correctamente</h4>
                <p class="mb-0">✅ Base de datos activa ✅ {total} asociados cargados ✅ API funcionando</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/asociados')
def lista_asociados():
    asociados = Asociado.query.all()
    
    asociados_html = ''
    for asociado in asociados:
        estado_color = 'success' if asociado.estado == 'ENTREGADO' else 'warning'
        estado_icon = 'check-circle' if asociado.estado == 'ENTREGADO' else 'clock'
        
        btn_entregar = ''
        if asociado.estado == 'PENDIENTE':
            btn_entregar = f'<a href="/entregar/{asociado.id}" class="btn btn-success btn-sm"><i class="fas fa-check"></i> Entregar</a>'
        
        asociados_html += f'''
        <tr>
            <td><strong>{asociado.cedula}</strong></td>
            <td>{asociado.nombre_completo}</td>
            <td>{asociado.agencia}</td>
            <td>{asociado.empresa}</td>
            <td><span class="badge bg-{estado_color}"><i class="fas fa-{estado_icon}"></i> {asociado.estado}</span></td>
            <td>{asociado.observaciones}</td>
            <td>{btn_entregar}</td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lista de Asociados - Cooperenka</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-users"></i> Lista de Asociados</h2>
                <a href="/" class="btn btn-secondary"><i class="fas fa-home"></i> Inicio</a>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Cédula</th>
                            <th>Nombre Completo</th>
                            <th>Agencia</th>
                            <th>Empresa</th>
                            <th>Estado</th>
                            <th>Observaciones</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {asociados_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/buscar')
def buscar_form():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Buscar Asociado - Cooperenka</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <div class="row">
                <div class="col-md
