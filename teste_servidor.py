#!/usr/bin/env python3
"""
Teste simples da interface web
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trader Bot - Teste</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>🤖 Trader Bot - Interface Web</h1>
        <p>✅ Servidor funcionando corretamente!</p>
        <p>🌐 Acesse: <a href="http://localhost:5000">http://localhost:5000</a></p>
        <p>👤 Login: usuario@exemplo.com</p>
        <p>🔑 Senha: 123456</p>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("[INICIO] Iniciando servidor de teste...")
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
