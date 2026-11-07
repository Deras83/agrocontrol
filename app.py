from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Configuración estricta de CORS para permitir peticiones desde Vite
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_db_connection():
    conn = sqlite3.connect('database/agrocontrol.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/lotes', methods=['GET'])
def get_lotes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lotes')
    filas = cursor.fetchall()
    conn.close()
    
    lotes = [dict(fila) for fila in filas]
    return jsonify(lotes)

@app.route('/api/lotes', methods=['POST'])
def create_lote():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lotes (nombre, area_ha, tipo_suelo, ph)
        VALUES (?, ?, ?, ?)
    ''', (data.get('nombre'), data.get('area_ha'), data.get('tipo_suelo'), data.get('ph')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '¡Lote registrado con éxito!'}), 201

@app.route('/api/lotes/<int:id>', methods=['DELETE'])
def delete_lote(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lotes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Lote eliminado correctamente'}), 200

@app.route('/api/cultivos', methods=['GET'])
def get_cultivos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, l.nombre as nombre_lote 
        FROM cultivos c
        JOIN lotes l ON c.lote_id = l.id
    ''')
    filas = cursor.fetchall()
    conn.close()
    return jsonify([dict(fila) for fila in filas])

@app.route('/api/cultivos', methods=['POST'])
def create_cultivo():
    data = request.json
    # Convertimos la etapa a minúsculas automáticamente para evitar conflictos con el CHECK de SQLite
    etapa_normalizada = str(data.get('etapa', '')).strip().lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cultivos (lote_id, tipo_cultivo, variedad, fecha_siembra, etapa)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data.get('lote_id'), 
        data.get('tipo_cultivo'), 
        data.get('variedad'), 
        data.get('fecha_siembra'), 
        etapa_normalizada
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Cultivo registrado exitosamente'}), 201
if __name__ == '__main__':
    app.run(debug=True, port=5000)