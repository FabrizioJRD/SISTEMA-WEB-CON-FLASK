from flask import Flask, request, jsonify, session
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'super_clave_secreta_examen'

app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True 
CORS(app, supports_credentials=True)

DB_NAME = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, nombre TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nombre TEXT, descripcion TEXT, precio REAL, stock INTEGER, categoria TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, nombre) VALUES ('admin', '1234', 'Administrador del Sistema')")
        cursor.execute("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES ('0001', 'Laptop HP', 'Laptop 16GB RAM 512GB SSD', 3500.00, 15, 'Electrónicos')")
        conn.commit()
    conn.close()

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        return jsonify({"success": True, "nombre": user[3]})
    else:
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos."}), 401

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    data = request.get_json()
    codigo = data.get('codigo', '')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre, descripcion, precio, stock, categoria FROM productos WHERE codigo = ?", (codigo,))
    producto = cursor.fetchone()
    conn.close()
    
    if producto:
        return jsonify({
            "encontrado": True,
            "producto": {
                "codigo": producto[0], "nombre": producto[1], "descripcion": producto[2],
                "precio": producto[3], "stock": producto[4], "categoria": producto[5]
            }
        })
    else:
        return jsonify({"encontrado": False})

@app.route('/api/logout', methods=['POST'])
def logout_api():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)