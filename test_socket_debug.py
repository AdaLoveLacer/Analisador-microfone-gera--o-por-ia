#!/usr/bin/env python3
"""
Debug script para verificar Socket.IO connection
Acesse: http://localhost:5000/static/test-socket.html
"""

import socketio
import logging

logging.basicConfig(level=logging.DEBUG)

# Tentar conexão
sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print('✅ Conectado ao servidor Socket.IO')

@sio.event
def disconnect():
    print('❌ Desconectado do servidor Socket.IO')

@sio.event
def connection_response(data):
    print(f'📝 Resposta: {data}')

try:
    print('Tentando conectar a http://localhost:5000...')
    sio.connect('http://localhost:5000', 
                headers={'User-Agent': 'Test'},
                transports=['websocket', 'polling'])
    print('Conectado! Aguardando por 5 segundos...')
    sio.wait(timeout=5)
except Exception as e:
    print(f'❌ Erro: {e}')
