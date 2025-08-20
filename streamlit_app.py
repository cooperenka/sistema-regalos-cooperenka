import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Configuración de la página
st.set_page_config(
    page_title="Sistema Cooperenka",
    page_icon="🎁",
    layout="wide"
)

# Crear/conectar base de datos
def init_db():
    conn = sqlite3.connect('cooperenka.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asociados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE NOT NULL,
        nombre1 TEXT NOT NULL,
        nombre2 TEXT,
        apellido1 TEXT NOT NULL,
        apellido2 TEXT,
        agencia TEXT NOT NULL,
        empresa TEXT NOT NULL,
        observaciones TEXT,
        estado TEXT DEFAULT 'PENDIENTE',
        fecha_entrega TEXT,
        usuario_entrega TEXT
    )
    ''')
    
    # Insertar datos de ejemplo si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM asociados')
    if cursor.fetchone()[0] == 0:
        datos_ejemplo = [
            ('12345678', 'JUAN', 'CARLOS', 'GARCIA', 'PEREZ', 'PRINCIPAL', 'EMPRESA A', '', 'PENDIENTE', '', ''),
            ('87654321', 'MARIA', 'ELENA', 'MARTINEZ', 'GONZALEZ', 'ZONA NORTE', 'EMPRESA B', 'Contactar antes de entregar', 'PENDIENTE', '', ''),
            ('11223344', 'CARLOS', 'ALBERTO', 'RODRIGUEZ', 'HERNANDEZ', 'CENTRO', 'EMPRESA C', '', 'ENTREGADO', '2024-12-15 10:30', 'Sistema'),
            ('99887766', 'ANA', 'SOFIA', 'LOPEZ', 'DIAZ', 'SUR', 'EMPRESA D', 'Verificar identidad', 'PENDIENTE', '', ''),
            ('55443322', 'LUIS', 'MIGUEL', 'HERNANDEZ', 'JIMENEZ', 'ORIENTE', 'EMPRESA E', '', 'PENDIENTE', '', '')
        ]
        
        cursor.executemany('''
        INSERT INTO asociados (cedula, nombre1, nombre2, apellido1, apellido2, agencia, empresa, observaciones, estado, fecha_entrega, usuario_entrega)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', datos_ejemplo)
    
    conn.commit()
    conn.close()

# Funciones de base de datos
def get_all_asociados():
    conn = sqlite3.connect('cooperenka.db')
    df = pd.read_sql_query('SELECT * FROM asociados ORDER BY apellido1, nombre1', conn)
    conn.close()
    return df

def get_estadisticas():
    conn = sqlite3.connect('cooperenka.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM asociados')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM asociados WHERE estado = 'ENTREGADO'")
    entregados = cursor.fetchone()[0]
    
    pendientes = total - entregados
    
    cursor.execute("SELECT COUNT(*) FROM asociados WHERE observaciones != '' AND observaciones IS NOT NULL")
    novedades = cursor.fetchone()[0]
    
    conn.close()
    
    return total, entregados, pendientes, novedades

def buscar_asociado(termino):
    conn = sqlite3.connect('cooperenka.db')
    query = '''
    SELECT * FROM asociados 
    WHERE cedula LIKE ? OR nombre1 LIKE ? OR apellido1 LIKE ?
    OR (nombre1 || ' ' || nombre2 || ' ' || apellido1 || ' ' || apellido2) LIKE ?
    ORDER BY apellido1, nombre1
    '''
    df = pd.read_sql_query(query, conn, params=[f'%{termino}%']*4)
    conn.close()
    return df

def marcar_entregado(asociado_id, usuario):
    conn = sqlite3.connect('cooperenka.db')
    cursor = conn.cursor()
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute('''
    UPDATE asociados 
    SET estado = 'ENTREGADO', fecha_entrega = ?, usuario_entrega = ?
    WHERE id = ?
    ''', (fecha_actual, usuario, asociado_id))
    
    conn.commit()
    conn.close()

# Inicializar base de datos
init_db()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #3CB371 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .result-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .observation-alert {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎁 Sistema de Entrega de Regalos - Cooperenka</h1>
    <p>Gestión completa de entregas en tiempo real</p>
</div>
""", unsafe_allow_html=True)

# Obtener estadísticas
total, entregados, pendientes, novedades = get_estadisticas()

# Dashboard de estadísticas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Asociados", total)

with col2:
    st.metric("✅ Entregados", entregados, delta=f"{(entregados/total*100):.1f}%" if total > 0 else "0%")

with col3:
    st.metric("⏳ Pendientes", pendientes)

with col4:
    st.metric("⚠️ Con Novedades", novedades)

# Sidebar para navegación
st.sidebar.title("🧭 Navegación")
page = st.sidebar.selectbox(
    "Seleccionar página:",
    ["🔍 Buscar Asociado", "📋 Lista Completa", "📊 Estadísticas", "📁 Cargar Datos"]
)

# Contenido principal según la página
if page == "🔍 Buscar Asociado":
    st.header("🔍 Buscar Asociado")
    
    # Campo de búsqueda
    search_term = st.text_input(
        "Buscar por cédula o nombre:",
        placeholder="Ingresa cédula o nombre del asociado...",
        help="Puedes buscar por número de cédula o por cualquier parte del nombre"
    )
    
    if search_term:
        resultados = buscar_asociado(search_term)
        
        if resultados.empty:
            st.warning(f"❌ No se encontraron resultados para: '{search_term}'")
        else:
            st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)")
            
            for index, row in resultados.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        nombre_completo = f"{row['nombre1']} {row['nombre2']} {row['apellido1']} {row['apellido2']}".strip()
                        st.markdown(f"**👤 {nombre_completo}**")
                        st.write(f"📊 Cédula: {row['cedula']} | 🏢 Agencia: {row['agencia']} | 🏭 Empresa: {row['empresa']}")
                        
                        if row['observaciones']:
                            st.markdown(f"""
                            <div class="observation-alert">
                                <strong>⚠️ OBSERVACIONES:</strong> {row['observaciones']}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        if row['estado'] == 'ENTREGADO':
                            st.success("✅ ENTREGADO")
                            if row['fecha_entrega']:
                                st.caption(f"📅 {row['fecha_entrega']}")
                        else:
                            st.warning("⏳ PENDIENTE")
                    
                    with col3:
                        if row['estado'] == 'PENDIENTE':
                            if st.button(f"✅ Entregar", key=f"entregar_{row['id']}"):
                                usuario = st.session_state.get('usuario_actual', 'Usuario Web')
                                marcar_entregado(row['id'], usuario)
                                st.success("✅ Regalo marcado como entregado!")
                                st.experimental_rerun()
                    
                    st.markdown("---")

elif page == "📋 Lista Completa":
    st.header("📋 Lista Completa de Asociados")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "PENDIENTE", "ENTREGADO"])
    
    with col2:
        df_asociados = get_all_asociados()
        agencias = ["Todas"] + sorted(df_asociados['agencia'].unique().tolist())
        filtro_agencia = st.selectbox("Filtrar por agencia:", agencias)
    
    with col3:
        filtro_novedades = st.selectbox("Filtrar:", ["Todos", "Con observaciones", "Sin observaciones"])
    
    # Aplicar filtros
    df_filtrado = df_asociados.copy()
    
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado]
    
    if filtro_agencia != "Todas":
        df_filtrado = df_filtrado[df_filtrado['agencia'] == filtro_agencia]
    
    if filtro_novedades == "Con observaciones":
        df_filtrado = df_filtrado[df_filtrado['observaciones'].notna() & (df_filtrado['observaciones'] != '')]
    elif filtro_novedades == "Sin observaciones":
        df_filtrado = df_filtrado[(df_filtrado['observaciones'].isna()) | (df_filtrado['observaciones'] == '')]
    
    st.subheader(f"📊 Registros ({len(df_filtrado)} de {len(df_asociados)})")
    
    if not df_filtrado.empty:
        # Preparar datos para mostrar
        df_display = df_filtrado.copy()
        df_display['nombre_completo'] = df_display['nombre1'] + ' ' + df_display['nombre2'] + ' ' + df_display['apellido1'] + ' ' + df_display['apellido2']
        
        # Mostrar tabla
        st.dataframe(
            df_display[['cedula', 'nombre_completo', 'agencia', 'empresa', 'estado', 'observaciones', 'fecha_entrega']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📭 No hay registros que coincidan con los filtros seleccionados.")

elif page == "📊 Estadísticas":
    st.header("📊 Estadísticas Detalladas")
    
    df_asociados = get_all_asociados()
    
    if not df_asociados.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de estado
            estados = df_asociados['estado'].value_counts()
            st.subheader("📈 Estado de Entregas")
            st.bar_chart(estados)
        
        with col2:
            # Gráfico por agencia
            agencias = df_asociados['agencia'].value_counts()
            st.subheader("🏢 Distribución por Agencia")
            st.bar_chart(agencias)
        
        # Tabla resumen por agencia
        st.subheader("📋 Resumen por Agencia")
        resumen_agencias = df_asociados.groupby('agencia')['estado'].value_counts().unstack(fill_value=0)
        if 'ENTREGADO' in resumen_agencias.columns and 'PENDIENTE' in resumen_agencias.columns:
            resumen_agencias['Total'] = resumen_agencias.sum(axis=1)
            resumen_agencias['% Entregados'] = (resumen_agencias['ENTREGADO'] / resumen_agencias['Total'] * 100).round(1)
        
        st.dataframe(resumen_agencias, use_container_width=True)

elif page == "📁 Cargar Datos":
    st.header("📁 Cargar Datos")
    
    st.info("🔄 Funcionalidad de carga disponible. Sistema funcionando con datos de ejemplo.")
    
    # Mostrar formato esperado
    st.subheader("📋 Formato Esperado")
    formato_ejemplo = pd.DataFrame({
        'CEDULA': ['12345678', '87654321'],
        'NOMBRE 1': ['JUAN', 'MARIA'],
        'NOMBRE 2': ['CARLOS', 'ELENA'],
        'APELLIDO 1': ['GARCIA', 'MARTINEZ'],
        'APELLIDO 2': ['PEREZ', 'GONZALEZ'],
        'AGENCIA': ['PRINCIPAL', 'ZONA NORTE'],
        'EMPRESA': ['EMPRESA A', 'EMPRESA B'],
        'OBSERVACIONES': ['', 'Contactar antes']
    })
    
    st.dataframe(formato_ejemplo, use_container_width=True)

# Configurar usuario en sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("👤 Usuario")
    usuario_actual = st.text_input("Tu nombre:", value=st.session_state.get('usuario_actual', ''))
    if usuario_actual:
        st.session_state['usuario_actual'] = usuario_actual
        st.success(f"👋 Hola, {usuario_actual}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Cooperenka</strong> - Sistema de Registro de Entregas</p>
    <p>🔄 Sistema funcionando online | 🌐 Acceso multi-dispositivo</p>
</div>
""", unsafe_allow_html=True)
