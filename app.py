from flask import Flask, request, render_template_string, send_file
import pandas as pd
import webbrowser
import threading
import io

app = Flask(__name__)

HTML_COMPLETO = '''
<!DOCTYPE html>
<html>
<head>
    <title>Analizador de Inventario | Sistema de Alertas</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f5f5f5;
            padding: 30px 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
            padding: 30px;
        }
        h1 { 
            color: #1a1a1a; 
            margin-bottom: 8px;
            font-size: 24px;
            font-weight: 600;
        }
        .subtitle { 
            color: #666; 
            margin-bottom: 30px;
            font-size: 14px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 20px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 6px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 20px;
            background: #fafafa;
        }
        .upload-area:hover { 
            border-color: #2c7da0; 
            background: #f0f4f8; 
        }
        .upload-area.dragover { 
            border-color: #2c7da0; 
            background: #e8f0f5; 
        }
        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
            color: #666;
        }
        input[type="file"] { display: none; }
        button {
            background: #2c7da0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.2s;
        }
        button:hover { background: #1f5e7a; }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
            color: #666;
        }
        .resultado {
            margin-top: 30px;
        }
        .error {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            border-left: 3px solid #dc2626;
            font-size: 14px;
        }
        .success {
            background: #f0fdf4;
            color: #16a34a;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            border-left: 3px solid #16a34a;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .kpi-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
        }
        .kpi-card h3 { 
            font-size: 13px; 
            color: #6c757d; 
            margin-bottom: 8px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-card .number { 
            font-size: 28px; 
            font-weight: 600;
            color: #1a1a1a;
        }
        .urgente {
            background: #fef7e0;
            border-left: 3px solid #f59e0b;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }
        .urgente h3 { 
            color: #92400e; 
            margin-bottom: 12px;
            font-size: 14px;
            font-weight: 600;
        }
        .urgente p { 
            margin: 6px 0;
            font-size: 14px;
            color: #78350f;
        }
        .urgente strong {
            color: #1a1a1a;
        }
        .tabla-wrapper {
            overflow-x: auto;
            margin: 20px 0;
            border: 1px solid #e9ecef;
            border-radius: 6px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th {
            background: #f8f9fa;
            color: #495057;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border-bottom: 1px solid #dee2e6;
        }
        td {
            padding: 10px 16px;
            border-bottom: 1px solid #f0f0f0;
            color: #333;
        }
        tr:hover td {
            background: #f8f9fa;
        }
        .botones {
            margin-top: 30px;
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        .btn {
            padding: 8px 20px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            display: inline-block;
            cursor: pointer;
            border: none;
            font-size: 13px;
            transition: all 0.2s;
        }
        .btn-volver {
            background: #6c757d;
            color: white;
        }
        .btn-volver:hover { background: #5a6268; }
        .btn-pdf {
            background: #dc2626;
            color: white;
        }
        .btn-pdf:hover { background: #b91c1c; }
        .file-name {
            margin: 10px 0;
            padding: 10px;
            background: #f0fdf4;
            border-radius: 4px;
            color: #16a34a;
            font-size: 13px;
        }
        .seccion-titulo {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 25px 0 15px 0;
            padding-left: 0;
            border-left: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Sistema de Alertas de Inventario</h1>
        <p class="subtitle">Análisis de stock bajo y cálculo de reposición</p>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📂</div>
            Seleccione o arrastre el archivo Excel
            <input type="file" id="fileInput" accept=".xlsx,.xls">
        </div>
        <div id="fileName" style="display:none;"></div>
        <button id="analyzeBtn">Analizar inventario</button>
        
        <div class="loading" id="loading">
            Procesando archivo...
        </div>
        
        <div id="resultado"></div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileNameDiv = document.getElementById('fileName');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const resultado = document.getElementById('resultado');
        
        let selectedFile = null;
        
        uploadArea.onclick = () => fileInput.click();
        
        uploadArea.ondragover = (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        };
        
        uploadArea.ondragleave = () => {
            uploadArea.classList.remove('dragover');
        };
        
        uploadArea.ondrop = (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            selectedFile = e.dataTransfer.files[0];
            if (selectedFile && (selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls'))) {
                fileNameDiv.innerHTML = '✓ Archivo seleccionado: ' + selectedFile.name;
                fileNameDiv.style.display = 'block';
                fileNameDiv.style.background = '#f0fdf4';
                fileNameDiv.style.color = '#16a34a';
            } else {
                fileNameDiv.innerHTML = '✗ Seleccione un archivo Excel válido';
                fileNameDiv.style.display = 'block';
                fileNameDiv.style.background = '#fef2f2';
                fileNameDiv.style.color = '#dc2626';
                selectedFile = null;
            }
        };
        
        fileInput.onchange = (e) => {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                fileNameDiv.innerHTML = '✓ Archivo seleccionado: ' + selectedFile.name;
                fileNameDiv.style.display = 'block';
                fileNameDiv.style.background = '#f0fdf4';
                fileNameDiv.style.color = '#16a34a';
            }
        };
        
        analyzeBtn.onclick = async () => {
            if (!selectedFile) {
                alert('Seleccione un archivo Excel');
                return;
            }
            
            loading.style.display = 'block';
            resultado.innerHTML = '';
            
            const formData = new FormData();
            formData.append('excel_file', selectedFile);
            
            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    body: formData
                });
                const html = await response.text();
                resultado.innerHTML = html;
            } catch (error) {
                resultado.innerHTML = '<div class="error">Error al procesar el archivo</div>';
            } finally {
                loading.style.display = 'none';
            }
        };
        
        function exportarPDF() {
            const contenido = document.getElementById('reporteParaPDF').innerHTML;
            const titulo = document.getElementById('reporteTitulo').innerText;
            const fecha = new Date().toLocaleDateString('es-ES');
            
            const ventana = window.open('', '_blank');
            ventana.document.write(`
                <html>
                <head>
                    <title>Reporte_Inventario_${fecha}</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Arial, sans-serif;
                            margin: 40px;
                            color: #1a1a1a;
                        }
                        h1 {
                            font-size: 20px;
                            color: #1a1a1a;
                            margin-bottom: 5px;
                        }
                        .fecha {
                            color: #666;
                            font-size: 12px;
                            margin-bottom: 30px;
                            border-bottom: 1px solid #ddd;
                            padding-bottom: 15px;
                        }
                        .kpi-grid {
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 20px;
                            margin: 20px 0;
                        }
                        .kpi-card {
                            border: 1px solid #ddd;
                            padding: 15px;
                            text-align: center;
                            background: #f9f9f9;
                        }
                        .kpi-card .number {
                            font-size: 24px;
                            font-weight: bold;
                            margin-top: 5px;
                        }
                        .urgente {
                            background: #fef7e0;
                            border-left: 3px solid #f59e0b;
                            padding: 15px;
                            margin: 20px 0;
                        }
                        table {
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                            font-size: 11px;
                        }
                        th {
                            background: #f0f0f0;
                            padding: 10px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                        }
                        td {
                            padding: 8px 10px;
                            border-bottom: 1px solid #eee;
                        }
                        .total {
                            margin-top: 30px;
                            padding-top: 15px;
                            border-top: 2px solid #1a1a1a;
                            text-align: right;
                            font-size: 14px;
                            font-weight: bold;
                        }
                        .footer {
                            margin-top: 40px;
                            text-align: center;
                            font-size: 10px;
                            color: #999;
                        }
                        @media print {
                            body { margin: 0; }
                        }
                    </style>
                </head>
                <body>
                    <h1>${titulo}</h1>
                    <div class="fecha">Generado: ${fecha}</div>
                    ${contenido}
                    <div class="footer">Sistema de Alertas de Inventario</div>
                </body>
                </html>
            `);
            ventana.document.close();
            ventana.print();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_COMPLETO)

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        file = request.files.get('excel_file')
        if not file or file.filename == '':
            return '<div class="error">No se seleccionó ningún archivo</div>'
        
        df = pd.read_excel(file)
        
        columnas_necesarias = ['Stock_Actual', 'Stock_Minimo', 'Precio_Unitario_USD', 'Nombre', 'ID_Producto']
        faltantes = [col for col in columnas_necesarias if col not in df.columns]
        
        if faltantes:
            return f'<div class="error">El archivo no tiene las columnas: {", ".join(faltantes)}</div>'
        
        alerta = df[df['Stock_Actual'] < df['Stock_Minimo']].copy()
        
        if len(alerta) == 0:
            return '''
            <div class="resultado">
                <div class="success">
                    ✓ No hay productos con stock bajo. El inventario está saludable.
                </div>
                <div class="botones">
                    <a href="/" class="btn btn-volver">Analizar otro archivo</a>
                </div>
            </div>
            '''
        
        alerta['Faltante'] = alerta['Stock_Minimo'] - alerta['Stock_Actual']
        alerta['Costo_Reposicion'] = alerta['Faltante'] * alerta['Precio_Unitario_USD']
        
        total_productos = len(alerta)
        total_dinero = alerta['Costo_Reposicion'].sum()
        
        idx_max = alerta['Costo_Reposicion'].idxmax()
        mas_urgente = alerta.loc[idx_max]
        
        tabla_mostrar = alerta[['ID_Producto', 'Nombre', 'Stock_Actual', 'Stock_Minimo', 'Faltante', 'Precio_Unitario_USD', 'Costo_Reposicion']].copy()
        tabla_mostrar['Stock_Actual'] = tabla_mostrar['Stock_Actual'].astype(int)
        tabla_mostrar['Stock_Minimo'] = tabla_mostrar['Stock_Minimo'].astype(int)
        tabla_mostrar['Faltante'] = tabla_mostrar['Faltante'].astype(int)
        
        tabla_html = tabla_mostrar.to_html(index=False, float_format='%.2f', border=0)
        tabla_html = tabla_html.replace('<table', '<table')
        tabla_html = tabla_html.replace('<th', '<th')
        tabla_html = tabla_html.replace('<td', '<td')
        
        return f'''
        <div class="resultado">
            <div id="reporteTitulo" style="display:none;">Reporte de Alertas de Inventario</div>
            <div id="reporteParaPDF">
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <h3>Productos en alerta</h3>
                        <div class="number">{total_productos}</div>
                    </div>
                    <div class="kpi-card">
                        <h3>Total a reponer</h3>
                        <div class="number">${total_dinero:,.2f}</div>
                    </div>
                </div>
                
                <div class="urgente">
                    <h3>Producto con mayor urgencia</h3>
                    <p><strong>{mas_urgente['Nombre']}</strong> (Código: {mas_urgente['ID_Producto']})</p>
                    <p>Stock actual: {int(mas_urgente['Stock_Actual'])} | Mínimo requerido: {int(mas_urgente['Stock_Minimo'])}</p>
                    <p>Unidades a reponer: {int(mas_urgente['Faltante'])} | Costo: <strong>${mas_urgente['Costo_Reposicion']:.2f}</strong></p>
                </div>
                
                <div class="tabla-wrapper">
                    {tabla_html}
                </div>
            </div>
            
            <div class="botones">
                <a href="/" class="btn btn-volver">Nuevo análisis</a>
                <button onclick="exportarPDF()" class="btn btn-pdf">Exportar PDF</button>
            </div>
        </div>
        '''
        
    except Exception as e:
        return f'<div class="error">Error: {str(e)}</div>'

if __name__ == '__main__':
    threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)