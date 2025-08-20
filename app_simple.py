from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import io
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
            'nombre1': self.nombre1,
            'nombre2': self.nombre2,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
            'agencia': self.agencia,
            'empresa': self.empresa,
            'observaciones': self.observaciones,
            'estado': self.estado,
            'fecha_entrega': self.fecha_entrega.strftime('%Y-%m-%d %H:%M') if self.fecha_entrega else '',
            'usuario_entrega': self.usuario_entrega,
            'nombre_completo': f"{self.nombre1} {self.nombre2} {self.apellido1} {self.apellido2}".strip()
        }

# Inicializar base de datos
def inicializar_db():
    db.create_all()
    if Asociado.query.count() == 0:
        # Datos de ejemplo
        datos_ejemplo = [
            {
                'cedula': '12345678', 'nombre1': 'JUAN', 'nombre2': 'CARLOS',
                'apellido1': 'GARCIA', 'apellido2': 'PEREZ',
                'agencia': 'PRINCIPAL', 'empresa': 'EMPRESA A'
            },
            {
                'cedula': '87654321', 'nombre1': 'MARIA', 'nombre2': 'ELENA',
                'apellido1': 'MARTINEZ', 'apellido2': 'GONZALEZ',
                'agencia': 'ZONA NORTE', 'empresa': 'EMPRESA B',
                'observaciones': 'Contactar antes de entregar'
            }
        ]
        
        for datos in datos_ejemplo:
            asociado = Asociado(**datos)
            db.session.add(asociado)
        db.session.commit()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Cooperenka</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-12 text-center">
                    <h1 class="text-success">🎁 Sistema de Entrega de Regalos</h1>
                    <h3>Cooperenka</h3>
                    <p class="lead">Sistema funcionando correctamente</p>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">📊 Ver Asociados</h5>
                            <p class="card-text">Lista completa de asociados</p>
                            <a href="/asociados" class="btn btn-primary">Ver Lista</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">📈 API</h5>
                            <p class="card-text">Acceso a datos JSON</p>
                            <a href="/api/asociados" class="btn btn-success">Ver API</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert alert-info">
                        <strong>✅ Sistema Online:</strong> Base de datos funcionando, 
                        API disponible, interfaz responsive.
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/asociados')
def lista_asociados():
    asociados = Asociado.query.all()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lista de Asociados - Cooperenka</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h2>📋 Lista de Asociados</h2>
            <a href="/" class="btn btn-secondary mb-3">← Volver</a>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>Cédula</th>
                            <th>Nombre Completo</th>
                            <th>Agencia</th>
                            <th>Empresa</th>
                            <th>Estado</th>
                            <th>Observaciones</th>
                        </tr>
                    </thead>
                    <tbody>
    '''
    
    for asociado in asociados:
        estado_color = 'success' if asociado.estado == 'ENTREGADO' else 'warning'
        html += f'''
                        <tr>
                            <td>{asociado.cedula}</td>
                            <td>{asociado.nombre_completo}</td>
                            <td>{asociado.agencia}</td>
                            <td>{asociado.empresa}</td>
                            <td><span class="badge bg-{estado_color}">{asociado.estado}</span></td>
                            <td>{asociado.observaciones}</td>
                        </tr>
        '''
    
    html += '''
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/api/asociados')
def api_asociados():
    asociados = Asociado.query.all()
    return jsonify([asociado.to_dict() for asociado in asociados])

@app.route('/api/estadisticas')
def api_estadisticas():
    total = Asociado.query.count()
    entregados = Asociado.query.filter_by(estado='ENTREGADO').count()
    pendientes = total - entregados
    
    return jsonify({
        'total': total,
        'entregados': entregados,
        'pendientes': pendientes
    })

if __name__ == '__main__':
    with app.app_context():
        inicializar_db()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
