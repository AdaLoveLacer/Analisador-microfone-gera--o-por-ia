#!/usr/bin/env python3
"""
Script para diagnosticar o sistema e identificar problemas.
"""

import sys
import os

print("=" * 60)
print("DIAGNÓSTICO DO SISTEMA")
print("=" * 60)

# 1. Verificar Python
print(f"\n1. PYTHON")
print(f"   Versão: {sys.version}")
print(f"   Executável: {sys.executable}")

# 2. Verificar PyTorch
print(f"\n2. PYTORCH")
try:
    import torch
    print(f"   Versão: {torch.__version__}")
    print(f"   CUDA disponível: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Version: {torch.version.cuda}")
    else:
        print(f"   ⚠️  PyTorch em CPU - deveria estar em CUDA 11.8")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 3. Verificar Socket.IO
print(f"\n3. SOCKET.IO")
try:
    import socketio
    print(f"   Versão: {socketio.__version__}")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 4. Verificar Gevent
print(f"\n4. GEVENT")
try:
    import gevent
    print(f"   Versão: {gevent.__version__}")
    import gevent.monkey
    print(f"   Monkey patching disponível: OK")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 5. Verificar Whisper
print(f"\n5. WHISPER")
try:
    import whisper
    print(f"   Instalado: OK")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 6. Verificar SentenceTransformers
print(f"\n6. SENTENCE TRANSFORMERS")
try:
    from sentence_transformers import SentenceTransformer
    print(f"   Instalado: OK")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 7. Verificar Flask
print(f"\n7. FLASK")
try:
    import flask
    print(f"   Versão: {flask.__version__}")
except Exception as e:
    print(f"   ❌ Erro ao carregar: {e}")

# 8. Verificar importações do projeto
print(f"\n8. IMPORTAÇÕES DO PROJETO")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from ai.context_analyzer import ContextAnalyzer
    print(f"   ContextAnalyzer: OK")
except Exception as e:
    print(f"   ❌ ContextAnalyzer: {e}")

try:
    from audio.transcriber import Transcriber
    print(f"   Transcriber: OK")
except Exception as e:
    print(f"   ❌ Transcriber: {e}")

try:
    from web.app import create_app
    print(f"   Flask App: OK")
except Exception as e:
    print(f"   ❌ Flask App: {e}")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
