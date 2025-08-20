import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

class SistemaEntregaRegalos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Registro de Entregas - Cooperenka")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Datos del sistema
        self.datos_asociados = pd.DataFrame()
        self.datos_filtrados = pd.DataFrame()
        self.archivo_actual = None
        
        # Variables de estadísticas
        self.var_total = tk.StringVar(value="0")
        self.var_entregados = tk.StringVar(value="0")
        self.var_pendientes = tk.StringVar(value="0")
        self.var_novedades = tk.StringVar(value="0")
        
        self.crear_interfaz()
        self.actualizar_estadisticas()
    
    def crear_interfaz(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2E8B57', height=120)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        # Logo y título
        title_label = tk.Label(header_frame, text="cooperenka", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2E8B57')
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(header_frame, text="Cooperativa Especializada de Ahorro y Crédito", 
                                 font=('Arial', 10), fg='white', bg='#2E8B57')
        subtitle_label.pack()
        
        system_title = tk.Label(header_frame, text="📦 Sistema de Registro de Entregas", 
                               font=('Arial', 14, 'bold'), fg='white', bg='#2E8B57')
        system_title.pack(pady=5)
        
        system_subtitle = tk.Label(header_frame, text="Gestión avanzada de entregas de regalos con control de novedades", 
                                  font=('Arial', 9), fg='white', bg='#2E8B57')
        system_subtitle.pack()
        
        # Panel de estadísticas
        stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Tarjetas de estadísticas
        self.crear_tarjeta_estadistica(stats_frame, "Total Asociados", self.var_total, "#e3f2fd", 0)
        self.crear_tarjeta_estadistica(stats_frame, "Entregados", self.var_entregados, "#e8f5e8", 1)
        self.crear_tarjeta_estadistica(stats_frame, "Pendientes", self.var_pendientes, "#fff3e0", 2)
        self.crear_tarjeta_estadistica(stats_frame, "Con Novedad", self.var_novedades, "#ffebee", 3)
        
        # Notebook para las pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear pestañas
        self.crear_pestaña_carga()
        self.crear_pestaña_busqueda()
        self.crear_pestaña_registro()
        self.crear_pestaña_herramientas()
    
    def crear_tarjeta_estadistica(self, parent, titulo, variable, color, column):
        frame = tk.Frame(parent, bg=color, relief='raised', bd=1)
        frame.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.columnconfigure(column, weight=1)
        
        tk.Label(frame, text=variable.get(), font=('Arial', 24, 'bold'), 
                bg=color, fg='#333').pack(pady=5)
        tk.Label(frame, text=titulo, font=('Arial', 10), 
                bg=color, fg='#666').pack(pady=(0,5))
    
    def crear_pestaña_carga(self):
        # Frame para carga de archivos
        carga_frame = ttk.Frame(self.notebook)
        self.notebook.add(carga_frame, text="📁 Cargar Archivo de Asociados")
        
        # Sección de carga
        load_section = tk.LabelFrame(carga_frame, text="📁 Cargar Archivo de Asociados", 
                                    font=('Arial', 12, 'bold'), fg='#2E8B57')
        load_section.pack(fill='x', padx=20, pady=20)
        
        # Área de arrastrar archivo
        drag_frame = tk.Frame(load_section, bg='#f8f9fa', relief='solid', bd=2, height=100)
        drag_frame.pack(fill='x', padx=20, pady=20)
        drag_frame.pack_propagate(False)
        
        tk.Label(drag_frame, text="📎 Arrastra tu archivo aquí o haz clic para seleccionar", 
                font=('Arial', 12), bg='#f8f9fa', fg='#666').pack(expand=True)
        tk.Label(drag_frame, text="Formatos soportados: CSV, Excel (.xlsx, .xls)", 
                font=('Arial', 9), bg='#f8f9fa', fg='#999').pack()
        
        # Botón de carga
        btn_frame = tk.Frame(load_section)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📂 Seleccionar Archivo", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', command=self.cargar_archivo,
                 relief='flat', padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📊 Cargar Datos de Ejemplo", font=('Arial', 10),
                 bg='#17a2b8', fg='white', command=self.cargar_datos_ejemplo,
                 relief='flat', padx=20, pady=10).pack(side='left', padx=5)
        
        # Información del formato
        info_frame = tk.LabelFrame(carga_frame, text="ℹ️ Formato Esperado", 
                                  font=('Arial', 11, 'bold'), fg='#2E8B57')
        info_frame.pack(fill='x', padx=20, pady=10)
        
        formato_text = """El archivo debe contener las siguientes columnas:
• CEDULA: Número de cédula del asociado
• APELLIDO 1: Primer apellido
• APELLIDO 2: Segundo apellido  
• NOMBRE 1: Primer nombre
• NOMBRE 2: Segundo nombre
• AGENCIA: Agencia a la que pertenece
• EMPRESA: Empresa donde trabaja
• OBSERVACIONES: Notas especiales o restricciones (opcional)"""
        
        tk.Label(info_frame, text=formato_text, justify='left', 
                font=('Arial', 9), bg='#e7f3ff').pack(padx=15, pady=10, anchor='w')
    
    def crear_pestaña_busqueda(self):
        # Frame para búsqueda
        busqueda_frame = ttk.Frame(self.notebook)
        self.notebook.add(busqueda_frame, text="🔍 Buscar Asociado")
        
        # Sección de búsqueda
        search_section = tk.LabelFrame(busqueda_frame, text="🔍 Buscar Asociado", 
                                      font=('Arial', 12, 'bold'), fg='#2E8B57')
        search_section.pack(fill='x', padx=20, pady=20)
        
        # Campo de búsqueda
        search_frame = tk.Frame(search_section)
        search_frame.pack(pady=15)
        
        tk.Label(search_frame, text="Buscar por nombre o cédula:", 
                font=('Arial', 10)).pack(anchor='w')
        
        entry_frame = tk.Frame(search_frame)
        entry_frame.pack(fill='x', pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(entry_frame, textvariable=self.search_var, 
                               font=('Arial', 12), width=40)
        search_entry.pack(side='left', padx=(0,10))
        search_entry.bind('<KeyRelease>', self.buscar_tiempo_real)
        
        tk.Button(entry_frame, text="🔍 Buscar", bg='#007bff', fg='white',
                 command=self.buscar_asociado, relief='flat', padx=15).pack(side='left', padx=2)
        tk.Button(entry_frame, text="🗑️ Limpiar", bg='#6c757d', fg='white',
                 command=self.limpiar_busqueda, relief='flat', padx=15).pack(side='left', padx=2)
        
        # Resultados de búsqueda
        self.resultado_frame = tk.Frame(busqueda_frame, bg='white')
        self.resultado_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    def crear_pestaña_registro(self):
        # Frame para registro de entregas
        registro_frame = ttk.Frame(self.notebook)
        self.notebook.add(registro_frame, text="📋 Registro de Entregas")
        
        # Botones de control
        control_frame = tk.Frame(registro_frame, bg='#f8f9fa')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(control_frame, text="📄 Generar Reporte PDF", bg='#28a745', fg='white',
                 font=('Arial', 10, 'bold'), command=self.generar_reporte_pdf,
                 relief='flat', padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="📊 Exportar CSV", bg='#ffc107', fg='black',
                 font=('Arial', 10, 'bold'), command=self.exportar_csv,
                 relief='flat', padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="📈 Ver Historial", bg='#17a2b8', fg='white',
                 font=('Arial', 10, 'bold'), command=self.ver_historial,
                 relief='flat', padx=15, pady=8).pack(side='left', padx=5)
        
        # Tabla de datos
        tabla_frame = tk.Frame(registro_frame)
        tabla_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear Treeview
        columns = ('Cédula', 'Nombre Completo', 'Agencia', 'Empresa', 'Estado', 'Observaciones')
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'Cédula': 100, 'Nombre Completo': 200, 'Agencia': 120, 
                        'Empresa': 150, 'Estado': 80, 'Observaciones': 200}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tabla_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tabla_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar tabla y scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Eventos
        self.tree.bind('<Double-1>', self.editar_registro)
    
    def crear_pestaña_herramientas(self):
        # Frame para herramientas avanzadas
        herramientas_frame = ttk.Frame(self.notebook)
        self.notebook.add(herramientas_frame, text="🔧 Herramientas Avanzadas")
        
        # Sección de herramientas
        tools_section = tk.LabelFrame(herramientas_frame, text="🔧 Herramientas Avanzadas", 
                                     font=('Arial', 12, 'bold'), fg='#2E8B57')
        tools_section.pack(fill='x', padx=20, pady=20)
        
        # Botones de herramientas
        buttons_frame = tk.Frame(tools_section)
        buttons_frame.pack(pady=20)
        
        # Primera fila de botones
        fila1 = tk.Frame(buttons_frame)
        fila1.pack(fill='x', pady=5)
        
        tk.Button(fila1, text="📊 Mostrar Todos", bg='#007bff', fg='white',
                 font=('Arial', 10, 'bold'), command=self.mostrar_todos,
                 relief='flat', padx=20, pady=10, width=18).pack(side='left', padx=5)
        
        tk.Button(fila1, text="✅ Solo Entregados", bg='#28a745', fg='white',
                 font=('Arial', 10, 'bold'), command=self.filtrar_entregados,
                 relief='flat', padx=20, pady=10, width=18).pack(side='left', padx=5)
        
        tk.Button(fila1, text="⏳ Solo Pendientes", bg='#ffc107', fg='black',
                 font=('Arial', 10, 'bold'), command=self.filtrar_pendientes,
                 relief='flat', padx=20, pady=10, width=18).pack(side='left', padx=5)
        
        # Segunda fila de botones
        fila2 = tk.Frame(buttons_frame)
        fila2.pack(fill='x', pady=5)
        
        tk.Button(fila2, text="⚠️ Con Novedades", bg='#dc3545', fg='white',
                 font=('Arial', 10, 'bold'), command=self.filtrar_novedades,
                 relief='flat', padx=20, pady=10, width=18).pack(side='left', padx=5)
        
        tk.Button(fila2, text="🗑️ Limpiar Todos los Datos", bg='#6c757d', fg='white',
                 font=('Arial', 10, 'bold'), command=self.limpiar_datos,
                 relief='flat', padx=20, pady=10, width=18).pack(side='left', padx=5)
    
    def cargar_archivo(self):
        """Cargar archivo Excel o CSV"""
        filetypes = (
            ('Archivos Excel', '*.xlsx *.xls'),
            ('Archivos CSV', '*.csv'),
            ('Todos los archivos', '*.*')
        )
        
        archivo = filedialog.askopenfilename(
            title='Seleccionar archivo de asociados',
            filetypes=filetypes
        )
        
        if archivo:
            try:
                # Cargar según el tipo de archivo
                if archivo.endswith('.csv'):
                    df = pd.read_csv(archivo)
                else:
                    df = pd.read_excel(archivo)
                
                # Validar columnas requeridas
                columnas_requeridas = ['CEDULA', 'APELLIDO 1', 'APELLIDO 2', 
                                     'NOMBRE 1', 'NOMBRE 2', 'AGENCIA', 'EMPRESA']
                
                columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                
                if columnas_faltantes:
                    messagebox.showerror("Error de formato", 
                                       f"El archivo no contiene las columnas requeridas:\n{', '.join(columnas_faltantes)}")
                    return
                
                # Agregar columnas adicionales si no existen
                if 'OBSERVACIONES' not in df.columns:
                    df['OBSERVACIONES'] = ''
                if 'ESTADO' not in df.columns:
                    df['ESTADO'] = 'PENDIENTE'
                if 'FECHA_ENTREGA' not in df.columns:
                    df['FECHA_ENTREGA'] = ''
                
                self.datos_asociados = df
                self.archivo_actual = archivo
                self.actualizar_tabla()
                self.actualizar_estadisticas()
                
                messagebox.showinfo("Éxito", f"Archivo cargado correctamente.\n{len(df)} registros importados.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
    
    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo para demostración"""
        datos_ejemplo = {
            'CEDULA': ['12345678', '87654321', '11223344', '99887766'],
            'APELLIDO 1': ['GARCIA', 'MARTINEZ', 'RODRIGUEZ', 'LOPEZ'],
            'APELLIDO 2': ['PEREZ', 'GONZALEZ', 'HERNANDEZ', 'DIAZ'],
            'NOMBRE 1': ['JUAN', 'MARIA', 'CARLOS', 'ANA'],
            'NOMBRE 2': ['CARLOS', 'ELENA', 'ALBERTO', 'SOFIA'],
            'AGENCIA': ['PRINCIPAL', 'ZONA NORTE', 'CENTRO', 'SUR'],
            'EMPRESA': ['EMPRESA A', 'EMPRESA B', 'EMPRESA C', 'EMPRESA D'],
            'OBSERVACIONES': ['', 'No entregar - Suspendido', '', 'Contactar antes de entregar'],
            'ESTADO': ['PENDIENTE', 'PENDIENTE', 'ENTREGADO', 'PENDIENTE'],
            'FECHA_ENTREGA': ['', '', '2024-12-15', '']
        }
        
        self.datos_asociados = pd.DataFrame(datos_ejemplo)
        self.actualizar_tabla()
        self.actualizar_estadisticas()
        
        messagebox.showinfo("Datos de ejemplo", "Se han cargado 4 registros de ejemplo.")
    
    def buscar_asociado(self):
        """Buscar asociado por cédula o nombre"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "Primero debe cargar un archivo de asociados.")
            return
        
        termino = self.search_var.get().strip().upper()
        if not termino:
            messagebox.showwarning("Campo vacío", "Ingrese un término de búsqueda.")
            return
        
        # Buscar en cédula o nombre completo
        mask = (
            self.datos_asociados['CEDULA'].astype(str).str.contains(termino, na=False) |
            (self.datos_asociados['NOMBRE 1'] + ' ' + 
             self.datos_asociados['NOMBRE 2'] + ' ' +
             self.datos_asociados['APELLIDO 1'] + ' ' + 
             self.datos_asociados['APELLIDO 2']).str.upper().str.contains(termino, na=False)
        )
        
        resultados = self.datos_asociados[mask]
        
        # Limpiar frame de resultados
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
        
        if resultados.empty:
            tk.Label(self.resultado_frame, text="❌ No se encontraron resultados", 
                    font=('Arial', 12), fg='red').pack(pady=20)
        else:
            self.mostrar_resultados_busqueda(resultados)
    
    def buscar_tiempo_real(self, event):
        """Búsqueda en tiempo real mientras se escribe"""
        if len(self.search_var.get()) >= 3:  # Buscar cuando hay al menos 3 caracteres
            self.buscar_asociado()
    
    def mostrar_resultados_busqueda(self, resultados):
        """Mostrar resultados de búsqueda en tarjetas"""
        # Título de resultados
        titulo_frame = tk.Frame(self.resultado_frame)
        titulo_frame.pack(fill='x', pady=10)
        
        tk.Label(titulo_frame, text=f"✅ {len(resultados)} resultado(s) encontrado(s)", 
                font=('Arial', 12, 'bold'), fg='green').pack(anchor='w')
        
        # Crear scrollable frame
        canvas = tk.Canvas(self.resultado_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.resultado_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar cada resultado
        for index, row in resultados.iterrows():
            self.crear_tarjeta_resultado(scrollable_frame, index, row)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def crear_tarjeta_resultado(self, parent, index, row):
        """Crear una tarjeta para mostrar un resultado de búsqueda"""
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief='raised', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Header de la tarjeta
        header_frame = tk.Frame(card_frame, bg='#2E8B57')
        header_frame.pack(fill='x')
        
        nombre_completo = f"{row['NOMBRE 1']} {row['NOMBRE 2']} {row['APELLIDO 1']} {row['APELLIDO 2']}"
        tk.Label(header_frame, text=f"👤 {nombre_completo}", font=('Arial', 12, 'bold'),
                fg='white', bg='#2E8B57').pack(side='left', padx=10, pady=5)
        
        # Estado
        estado = row.get('ESTADO', 'PENDIENTE')
        color_estado = '#28a745' if estado == 'ENTREGADO' else '#ffc107'
        tk.Label(header_frame, text=estado, font=('Arial', 10, 'bold'),
                fg='white', bg=color_estado).pack(side='right', padx=10, pady=5)
        
        # Contenido de la tarjeta
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='x', padx=10, pady=10)
        
        # Información básica
        info_text = f"""📊 Cédula: {row['CEDULA']}
🏢 Agencia: {row['AGENCIA']}
🏭 Empresa: {row['EMPRESA']}"""
        
        tk.Label(content_frame, text=info_text, justify='left', font=('Arial', 10),
                bg='white').pack(anchor='w')
        
        # Observaciones (destacadas si existen)
        if row['OBSERVACIONES'] and str(row['OBSERVACIONES']).strip():
            obs_frame = tk.Frame(content_frame, bg='#fff3cd', relief='solid', bd=1)
            obs_frame.pack(fill='x', pady=(10,0))
            
            tk.Label(obs_frame, text="⚠️ OBSERVACIONES:", font=('Arial', 10, 'bold'),
                    fg='#856404', bg='#fff3cd').pack(anchor='w', padx=5, pady=2)
            tk.Label(obs_frame, text=str(row['OBSERVACIONES']), font=('Arial', 10),
                    fg='#856404', bg='#fff3cd', wraplength=400).pack(anchor='w', padx=5, pady=2)
        
        # Botones de acción
        btn_frame = tk.Frame(content_frame, bg='white')
        btn_frame.pack(fill='x', pady=(10,0))
        
        if estado == 'PENDIENTE':
            tk.Button(btn_frame, text="✅ Marcar como Entregado", bg='#28a745', fg='white',
                     command=lambda idx=index: self.marcar_entregado(idx),
                     relief='flat', padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✏️ Editar", bg='#007bff', fg='white',
                 command=lambda idx=index: self.editar_registro_busqueda(idx),
                 relief='flat', padx=10, pady=5).pack(side='left', padx=5)
    
    def marcar_entregado(self, index):
        """Marcar un registro como entregado"""
        if messagebox.askyesno("Confirmar", "¿Marcar este regalo como entregado?"):
            self.datos_asociados.loc[index, 'ESTADO'] = 'ENTREGADO'
            self.datos_asociados.loc[index, 'FECHA_ENTREGA'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Actualizar todo inmediatamente
            self.actualizar_tabla()
            self.actualizar_estadisticas()
            
            # Forzar actualización de la ventana
            self.root.update_idletasks()
            
            # Actualizar resultados de búsqueda si están visibles
            if hasattr(self, 'search_var') and self.search_var.get().strip():
                self.buscar_asociado()
            
            messagebox.showinfo("Éxito", "Regalo marcado como entregado.")
            
            # Segunda actualización para asegurar que todo se vea
            self.root.after(100, self.actualizar_estadisticas)
    
    def editar_registro_busqueda(self, index):
        """Editar un registro desde los resultados de búsqueda"""
        self.abrir_editor_registro(index)
    
    def editar_registro(self, event):
        """Editar registro desde la tabla principal"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            cedula = item['values'][0]
            
            # Encontrar el índice en el DataFrame
            index = self.datos_asociados[self.datos_asociados['CEDULA'].astype(str) == str(cedula)].index[0]
            self.abrir_editor_registro(index)
    
    def abrir_editor_registro(self, index):
        """Abrir ventana de edición de registro"""
        row = self.datos_asociados.loc[index]
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Registro")
        edit_window.geometry("500x650")
        edit_window.configure(bg='#f0f0f0')
        edit_window.grab_set()  # Hacer ventana modal
        
        # Variables para los campos
        vars_campos = {}
        widgets_campos = {}  # Para guardar referencias a los widgets
        campos = ['CEDULA', 'NOMBRE 1', 'NOMBRE 2', 'APELLIDO 1', 'APELLIDO 2', 
                 'AGENCIA', 'EMPRESA', 'OBSERVACIONES', 'ESTADO']
        
        # Título de la ventana
        title_frame = tk.Frame(edit_window, bg='#2E8B57')
        title_frame.pack(fill='x', pady=(0,20))
        
        tk.Label(title_frame, text="✏️ Editar Registro de Asociado", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2E8B57').pack(pady=10)
        
        # Frame para los campos
        campos_frame = tk.Frame(edit_window, bg='#f0f0f0')
        campos_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Crear campos de entrada
        for i, campo in enumerate(campos):
            # Label del campo
            label_frame = tk.Frame(campos_frame, bg='#f0f0f0')
            label_frame.pack(fill='x', pady=(10,2))
            
            tk.Label(label_frame, text=f"{campo}:", font=('Arial', 10, 'bold'),
                    bg='#f0f0f0', fg='#333').pack(anchor='w')
            
            # Widget de entrada según el tipo de campo
            if campo == 'ESTADO':
                # Combobox para estado
                vars_campos[campo] = tk.StringVar(value=str(row[campo]) if pd.notna(row[campo]) else 'PENDIENTE')
                combo = ttk.Combobox(campos_frame, textvariable=vars_campos[campo],
                                   values=['PENDIENTE', 'ENTREGADO'], state='readonly',
                                   font=('Arial', 10))
                combo.pack(fill='x', pady=(0,5))
                widgets_campos[campo] = combo
                
            elif campo == 'OBSERVACIONES':
                # Text area para observaciones
                text_frame = tk.Frame(campos_frame, bg='#f0f0f0')
                text_frame.pack(fill='x', pady=(0,5))
                
                text_widget = tk.Text(text_frame, height=4, font=('Arial', 10), wrap='word')
                scrollbar_text = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar_text.set)
                
                # Insertar valor actual
                valor_actual = str(row[campo]) if pd.notna(row[campo]) else ''
                text_widget.insert('1.0', valor_actual)
                
                text_widget.pack(side='left', fill='both', expand=True)
                scrollbar_text.pack(side='right', fill='y')
                
                widgets_campos[campo] = text_widget
                vars_campos[campo] = None  # No usamos StringVar para Text
                
            else:
                # Entry normal para otros campos
                vars_campos[campo] = tk.StringVar(value=str(row[campo]) if pd.notna(row[campo]) else '')
                entry = tk.Entry(campos_frame, textvariable=vars_campos[campo], 
                               font=('Arial', 10), bg='white')
                entry.pack(fill='x', pady=(0,5))
                widgets_campos[campo] = entry
        
        # Frame para botones
        btn_frame = tk.Frame(edit_window, bg='#f0f0f0')
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        def guardar_cambios():
            try:
                # Validar campos obligatorios
                campos_obligatorios = ['CEDULA', 'NOMBRE 1', 'APELLIDO 1', 'AGENCIA', 'EMPRESA']
                for campo in campos_obligatorios:
                    if campo == 'OBSERVACIONES':
                        continue
                    valor = vars_campos[campo].get().strip() if vars_campos[campo] else ''
                    if not valor:
                        messagebox.showerror("Error", f"El campo '{campo}' es obligatorio.")
                        return
                
                # Guardar todos los cambios
                cambios_realizados = False
                for campo in campos:
                    if campo == 'OBSERVACIONES':
                        # Para el Text widget
                        nuevo_valor = widgets_campos[campo].get('1.0', 'end-1c').strip()
                    else:
                        # Para StringVar
                        nuevo_valor = vars_campos[campo].get().strip()
                    
                    valor_anterior = str(self.datos_asociados.loc[index, campo]) if pd.notna(self.datos_asociados.loc[index, campo]) else ''
                    
                    if nuevo_valor != valor_anterior:
                        self.datos_asociados.loc[index, campo] = nuevo_valor
                        cambios_realizados = True
                
                # Si se marca como entregado y antes no estaba, agregar fecha
                estado_nuevo = vars_campos['ESTADO'].get()
                estado_anterior = str(row['ESTADO']) if pd.notna(row['ESTADO']) else 'PENDIENTE'
                
                if estado_nuevo == 'ENTREGADO' and estado_anterior != 'ENTREGADO':
                    self.datos_asociados.loc[index, 'FECHA_ENTREGA'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                    cambios_realizados = True
                
                if cambios_realizados:
                    # Actualizar todo inmediatamente
                    self.actualizar_tabla()
                    self.actualizar_estadisticas()
                    
                    # Forzar actualización visual
                    self.root.update_idletasks()
                    
                    edit_window.destroy()
                    messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
                    
                    # Actualizar búsqueda si está activa
                    if hasattr(self, 'search_var') and self.search_var.get().strip():
                        self.root.after(100, self.buscar_asociado)
                    
                    # Segunda actualización para asegurar que todo se vea
                    self.root.after(100, self.actualizar_estadisticas)
                else:
                    edit_window.destroy()
                    messagebox.showinfo("Sin cambios", "No se realizaron cambios en el registro.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar cambios:\n{str(e)}")
        
        def cancelar():
            if messagebox.askyesno("Cancelar", "¿Está seguro de que desea cancelar? Se perderán los cambios no guardados."):
                edit_window.destroy()
        
        # Botones de acción
        tk.Button(btn_frame, text="💾 Guardar Cambios", bg='#28a745', fg='white',
                 font=('Arial', 11, 'bold'), command=guardar_cambios,
                 relief='flat', padx=25, pady=10, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancelar", bg='#6c757d', fg='white',
                 font=('Arial', 11, 'bold'), command=cancelar,
                 relief='flat', padx=25, pady=10, cursor='hand2').pack(side='left', padx=5)
        
        # Información adicional
        info_frame = tk.Frame(edit_window, bg='#e9ecef', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=20, pady=(0,10))
        
        info_text = f"📊 Editando registro de: {row['NOMBRE 1']} {row['APELLIDO 1']}\n📍 Cédula: {row['CEDULA']}"
        tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                bg='#e9ecef', fg='#495057', justify='left').pack(padx=10, pady=8)
        
        # Centrar ventana
        edit_window.transient(self.root)
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (edit_window.winfo_width() // 2)
        y = (edit_window.winfo_screenheight() // 2) - (edit_window.winfo_height() // 2)
        edit_window.geometry(f"+{x}+{y}")
        
        # Enfocar el primer campo
        if 'CEDULA' in widgets_campos:
            widgets_campos['CEDULA'].focus_set()
    
    def actualizar_tabla(self):
        """Actualizar la tabla principal con los datos actuales"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.datos_asociados.empty:
            return
        
        # Agregar datos
        for index, row in self.datos_asociados.iterrows():
            nombre_completo = f"{row['NOMBRE 1']} {row['NOMBRE 2']} {row['APELLIDO 1']} {row['APELLIDO 2']}"
            estado = row.get('ESTADO', 'PENDIENTE')
            observaciones = str(row.get('OBSERVACIONES', ''))[:50] + '...' if len(str(row.get('OBSERVACIONES', ''))) > 50 else str(row.get('OBSERVACIONES', ''))
            
            # Insertar fila
            item_id = self.tree.insert('', 'end', values=(
                row['CEDULA'],
                nombre_completo,
                row['AGENCIA'],
                row['EMPRESA'],
                estado,
                observaciones
            ))
            
            # Colorear según estado
            if estado == 'ENTREGADO':
                self.tree.set(item_id, 'Estado', '✅ ENTREGADO')
            elif observaciones and observaciones.strip():
                self.tree.set(item_id, 'Estado', '⚠️ PENDIENTE')
            else:
                self.tree.set(item_id, 'Estado', '⏳ PENDIENTE')
    
    def actualizar_estadisticas(self):
        """Actualizar las estadísticas mostradas"""
        if self.datos_asociados.empty:
            self.var_total.set("0")
            self.var_entregados.set("0")
            self.var_pendientes.set("0")
            self.var_novedades.set("0")
            # Actualizar tarjetas visuales
            self.actualizar_tarjetas_estadisticas()
            return
        
        total = len(self.datos_asociados)
        entregados = len(self.datos_asociados[self.datos_asociados['ESTADO'] == 'ENTREGADO'])
        pendientes = total - entregados
        
        # Contar novedades (registros con observaciones no vacías)
        novedades = len(self.datos_asociados[
            (self.datos_asociados['OBSERVACIONES'].notna()) & 
            (self.datos_asociados['OBSERVACIONES'].str.strip() != '')
        ])
        
        self.var_total.set(str(total))
        self.var_entregados.set(str(entregados))
        self.var_pendientes.set(str(pendientes))
        self.var_novedades.set(str(novedades))
        
        # Actualizar tarjetas visuales
        self.actualizar_tarjetas_estadisticas()
    
    def actualizar_tarjetas_estadisticas(self):
        """Actualizar visualmente las tarjetas de estadísticas"""
        try:
            # Buscar y actualizar cada tarjeta
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            # Buscar frames de estadísticas
                            labels = [w for w in child.winfo_children() if isinstance(w, tk.Label)]
                            if len(labels) >= 2:
                                # El primer label tiene el número, el segundo el título
                                numero_label = labels[0]
                                titulo_label = labels[1]
                                titulo = titulo_label.cget('text')
                                
                                # Actualizar según el título
                                if 'Total' in titulo:
                                    numero_label.config(text=self.var_total.get())
                                elif 'Entregados' in titulo:
                                    numero_label.config(text=self.var_entregados.get())
                                elif 'Pendientes' in titulo:
                                    numero_label.config(text=self.var_pendientes.get())
                                elif 'Novedad' in titulo:
                                    numero_label.config(text=self.var_novedades.get())
        except Exception as e:
            # Si hay algún error en la actualización visual, continuar silenciosamente
            pass
    
    def limpiar_busqueda(self):
        """Limpiar campo de búsqueda y resultados"""
        self.search_var.set("")
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
    
    def generar_reporte_pdf(self):
        """Generar reporte en PDF"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para generar el reporte.")
            return
        
        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte PDF"
        )
        
        if archivo_pdf:
            try:
                # Crear documento PDF
                doc = SimpleDocTemplate(archivo_pdf, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                # Título
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30,
                    alignment=1  # Centrado
                )
                
                story.append(Paragraph("COOPERENKA", title_style))
                story.append(Paragraph("Reporte de Entrega de Regalos", title_style))
                story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Estadísticas
                stats_data = [
                    ['Estadística', 'Cantidad'],
                    ['Total Asociados', self.var_total.get()],
                    ['Entregados', self.var_entregados.get()],
                    ['Pendientes', self.var_pendientes.get()],
                    ['Con Novedades', self.var_novedades.get()]
                ]
                
                stats_table = Table(stats_data)
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(stats_table)
                story.append(Spacer(1, 30))
                
                # Tabla de datos
                data = [['Cédula', 'Nombre Completo', 'Agencia', 'Empresa', 'Estado', 'Observaciones']]
                
                for index, row in self.datos_asociados.iterrows():
                    nombre_completo = f"{row['NOMBRE 1']} {row['NOMBRE 2']} {row['APELLIDO 1']} {row['APELLIDO 2']}"
                    observaciones = str(row.get('OBSERVACIONES', ''))[:30] + '...' if len(str(row.get('OBSERVACIONES', ''))) > 30 else str(row.get('OBSERVACIONES', ''))
                    
                    data.append([
                        str(row['CEDULA']),
                        nombre_completo,
                        str(row['AGENCIA']),
                        str(row['EMPRESA']),
                        str(row.get('ESTADO', 'PENDIENTE')),
                        observaciones
                    ])
                
                # Crear tabla
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                story.append(table)
                
                # Construir PDF
                doc.build(story)
                
                messagebox.showinfo("Éxito", f"Reporte PDF generado correctamente:\n{archivo_pdf}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar el PDF:\n{str(e)}")
    
    def exportar_csv(self):
        """Exportar datos a CSV"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return
        
        archivo_csv = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Exportar a CSV"
        )
        
        if archivo_csv:
            try:
                self.datos_asociados.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Éxito", f"Datos exportados correctamente:\n{archivo_csv}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar CSV:\n{str(e)}")
    
    def ver_historial(self):
        """Ver historial de entregas"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para mostrar.")
            return
        
        # Crear ventana de historial
        historial_window = tk.Toplevel(self.root)
        historial_window.title("Historial de Entregas")
        historial_window.geometry("800x600")
        
        # Frame para el historial
        frame = tk.Frame(historial_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear Treeview para historial
        columns = ('Fecha', 'Cédula', 'Nombre', 'Estado')
        hist_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            hist_tree.heading(col, text=col)
            hist_tree.column(col, width=150)
        
        # Agregar datos entregados
        entregados = self.datos_asociados[self.datos_asociados['ESTADO'] == 'ENTREGADO']
        for index, row in entregados.iterrows():
            nombre = f"{row['NOMBRE 1']} {row['APELLIDO 1']}"
            fecha = row.get('FECHA_ENTREGA', 'N/A')
            
            hist_tree.insert('', 'end', values=(
                fecha,
                row['CEDULA'],
                nombre,
                'ENTREGADO'
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=hist_tree.yview)
        hist_tree.configure(yscrollcommand=scrollbar.set)
        
        hist_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def mostrar_todos(self):
        """Mostrar todos los registros"""
        self.datos_filtrados = self.datos_asociados.copy()
        self.actualizar_tabla()
    
    def filtrar_entregados(self):
        """Filtrar solo entregados"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para filtrar.")
            return
        
        entregados = self.datos_asociados[self.datos_asociados['ESTADO'] == 'ENTREGADO']
        
        # Temporalmente reemplazar datos para mostrar solo entregados
        datos_originales = self.datos_asociados.copy()
        self.datos_asociados = entregados
        self.actualizar_tabla()
        self.datos_asociados = datos_originales
        
        messagebox.showinfo("Filtro aplicado", f"Mostrando {len(entregados)} registros entregados.")
    
    def filtrar_pendientes(self):
        """Filtrar solo pendientes"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para filtrar.")
            return
        
        pendientes = self.datos_asociados[self.datos_asociados['ESTADO'] != 'ENTREGADO']
        
        # Temporalmente reemplazar datos para mostrar solo pendientes
        datos_originales = self.datos_asociados.copy()
        self.datos_asociados = pendientes
        self.actualizar_tabla()
        self.datos_asociados = datos_originales
        
        messagebox.showinfo("Filtro aplicado", f"Mostrando {len(pendientes)} registros pendientes.")
    
    def filtrar_novedades(self):
        """Filtrar solo registros con novedades"""
        if self.datos_asociados.empty:
            messagebox.showwarning("Sin datos", "No hay datos para filtrar.")
            return
        
        novedades = self.datos_asociados[
            (self.datos_asociados['OBSERVACIONES'].notna()) & 
            (self.datos_asociados['OBSERVACIONES'].str.strip() != '')
        ]
        
        # Temporalmente reemplazar datos para mostrar solo con novedades
        datos_originales = self.datos_asociados.copy()
        self.datos_asociados = novedades
        self.actualizar_tabla()
        self.datos_asociados = datos_originales
        
        messagebox.showinfo("Filtro aplicado", f"Mostrando {len(novedades)} registros con novedades.")
    
    def limpiar_datos(self):
        """Limpiar todos los datos"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea limpiar todos los datos?\nEsta acción no se puede deshacer."):
            self.datos_asociados = pd.DataFrame()
            self.datos_filtrados = pd.DataFrame()
            self.archivo_actual = None
            
            self.actualizar_tabla()
            self.actualizar_estadisticas()
            
            # Limpiar búsqueda
            self.limpiar_busqueda()
            
            messagebox.showinfo("Datos limpiados", "Todos los datos han sido eliminados.")


def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = SistemaEntregaRegalos(root)
    root.mainloop()


if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pandas as pd
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        print("✅ Todas las dependencias están disponibles")
    except ImportError as e:
        print(f"❌ Error: Falta instalar una dependencia: {e}")
        print("\nPara instalar las dependencias necesarias, ejecute:")
        print("pip install pandas openpyxl reportlab")
        exit(1)
    
    main()