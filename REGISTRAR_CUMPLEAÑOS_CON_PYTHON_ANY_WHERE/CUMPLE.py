from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Archivo donde se almacenarán los datos
DATA_FILE = 'personas.json'

# Función para cargar los datos existentes
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Función para guardar los datos
def guardar_datos(personas):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(personas, file, ensure_ascii=False, indent=2)

# Ruta principal - mostrar el formulario
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar una nueva persona
@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        # Obtener datos del formulario
        nombre_completo = request.form.get('nombre_completo')
        especialidad = request.form.get('especialidad')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        
        # Validar que todos los campos estén llenos
        if not all([nombre_completo, especialidad, fecha_nacimiento]):
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400
        
        # Cargar datos existentes
        personas = cargar_datos()
        
        # Crear nuevo registro
        nueva_persona = {
            'id': len(personas) + 1,
            'nombre_completo': nombre_completo,
            'especialidad': especialidad,
            'fecha_nacimiento': fecha_nacimiento,
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Agregar y guardar
        personas.append(nueva_persona)
        guardar_datos(personas)
        
        return jsonify({
            'mensaje': 'Persona registrada exitosamente',
            'persona': nueva_persona
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para ver todas las personas registradas
@app.route('/personas', methods=['GET'])
def ver_personas():
    personas = cargar_datos()
    return jsonify(personas)

# Ruta para obtener personas que cumplen años hoy
@app.route('/cumpleanos/hoy', methods=['GET'])
def cumpleanos_hoy():
    hoy = datetime.now().strftime('%m-%d')
    personas = cargar_datos()
    
    cumpleaneros = []
    for persona in personas:
        fecha_nac = persona['fecha_nacimiento']
        # Extraer mes y día (formato YYYY-MM-DD)
        mes_dia = fecha_nac[5:]  # Obtiene MM-DD
        if mes_dia == hoy:
            cumpleaneros.append(persona)
    
    return jsonify({
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'cumpleaneros': cumpleaneros
    })

# Ruta para eliminar una persona (opcional)
@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    try:
        personas = cargar_datos()
        persona_eliminada = None
        
        for i, persona in enumerate(personas):
            if persona['id'] == id:
                persona_eliminada = personas.pop(i)
                break
        
        if persona_eliminada:
            guardar_datos(personas)
            return jsonify({
                'mensaje': 'Persona eliminada exitosamente',
                'persona': persona_eliminada
            })
        else:
            return jsonify({'error': 'Persona no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)