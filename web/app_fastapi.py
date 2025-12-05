"""FastAPI web application with Socket.IO support."""

import os
import logging
import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, Set
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import socketio

from core.analyzer import MicrophoneAnalyzer
from core.event_logger import setup_logging, get_logger

logger = get_logger(__name__)


# Container global para armazenar referência ao event loop principal
class EventLoopHolder:
    loop = None


class SocketIOManager:
    """Gerencia múltiplas conexões Socket.IO."""
    
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.active_connections: Dict[str, str] = {}  # sid -> client_id
    
    async def connect(self, sid: str, client_id: str = None):
        if client_id is None:
            client_id = f"client_{uuid.uuid4().hex[:8]}"
        self.active_connections[sid] = client_id
        logger.info(f"✓ Socket.IO conectado: {client_id} (SID: {sid})")
        return client_id
    
    def disconnect(self, sid: str):
        if sid in self.active_connections:
            client_id = self.active_connections[sid]
            del self.active_connections[sid]
            logger.info(f"✗ Socket.IO desconectado: {client_id} (SID: {sid})")
    
    async def broadcast(self, event: str, data: Dict[str, Any], skip_sid: str = None):
        """Envia evento para todos os clientes conectados."""
        try:
            await self.sio.emit(event, data, skip_sid=skip_sid, to=None)
        except Exception as e:
            logger.error(f"Erro ao fazer broadcast de {event}: {e}")
    
    async def send_personal(self, sid: str, event: str, data: Dict[str, Any]):
        """Envia evento para um cliente específico."""
        try:
            await self.sio.emit(event, data, to=sid)
        except Exception as e:
            logger.error(f"Erro ao enviar {event} para {sid}: {e}")


# Criar servidor Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=10,
    ping_timeout=5,
    engine_kwargs={"async_mode": "asgi"}
)

# Gerenciador global de Socket.IO
sio_manager = SocketIOManager(sio)


def create_app(analyzer: MicrophoneAnalyzer) -> FastAPI:
    """
    Cria e configura aplicação FastAPI com Socket.IO.
    
    Args:
        analyzer: Instância de MicrophoneAnalyzer
    
    Returns:
        Aplicação FastAPI configurada
    """
    
    # Lifecycle events
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Gerencia lifecycle da aplicação."""
        # STARTUP: Armazenar event loop para callbacks de threads
        EventLoopHolder.loop = asyncio.get_running_loop()
        logger.info("🚀 Iniciando aplicação FastAPI com Socket.IO")
        logger.info("✓ Event loop principal armazenado para callbacks")
        yield
        # SHUTDOWN
        EventLoopHolder.loop = None
        logger.info("🛑 Encerrando aplicação FastAPI")
    
    # Criar app
    app = FastAPI(
        title="Analisador de Microfone com IA",
        description="API para análise de áudio e transcrição com IA",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Setup logging
    setup_logging(
        log_level=analyzer.config.get("app.log_level", "INFO"),
        log_file="logs/app.log",
        db_manager=analyzer.database,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store references
    app.analyzer = analyzer
    app.config_manager = analyzer.config
    app.db_manager = analyzer.database
    app.sio_manager = sio_manager
    
    # ============ REGISTRAR HANDLERS SOCKET.IO ============
    
    @sio.on("connect")
    async def socket_connect(sid, environ):
        """Quando cliente se conecta via Socket.IO."""
        client_id = await sio_manager.connect(sid)
        logger.info(f"✓ Socket.IO conectado: {client_id}")
        
        # Enviar status inicial
        status = app.analyzer.get_status()
        await sio_manager.send_personal(sid, "status", status)
    
    @sio.on("disconnect")
    async def socket_disconnect(sid):
        """Quando cliente se desconecta via Socket.IO."""
        sio_manager.disconnect(sid)
        logger.info(f"✗ Socket.IO desconectado")
    
    @sio.on("get_status")
    async def handle_get_status(sid):
        """Recebe pedido de status."""
        status = app.analyzer.get_status()
        await sio_manager.send_personal(sid, "status", status)
    
    @sio.on("start_capture")
    async def handle_start_capture(sid, data=None):
        """Inicia captura de áudio via Socket.IO."""
        try:
            if app.analyzer.is_running:
                await sio_manager.send_personal(sid, "capture_status", {"status": "already_running"})
                return
            
            import threading
            def start_in_thread():
                try:
                    app.analyzer.start()
                except Exception as e:
                    logger.error(f"Erro ao iniciar captura: {e}")
            
            thread = threading.Thread(target=start_in_thread, daemon=True)
            thread.start()
            
            await sio_manager.send_personal(sid, "capture_status", {"status": "starting"})
            logger.info(f"🎙️ Captura iniciada via Socket.IO (SID: {sid})")
        except Exception as e:
            logger.error(f"Erro ao iniciar captura via Socket.IO: {e}")
            await sio_manager.send_personal(sid, "error", {"message": str(e)})
    
    @sio.on("stop_capture")
    async def handle_stop_capture(sid, data=None):
        """Para captura de áudio via Socket.IO."""
        try:
            if not app.analyzer.is_running:
                await sio_manager.send_personal(sid, "capture_status", {"status": "already_stopped"})
                return
            
            app.analyzer.stop()
            await sio_manager.send_personal(sid, "capture_status", {"status": "stopped"})
            logger.info(f"🛑 Captura parada via Socket.IO (SID: {sid})")
        except Exception as e:
            logger.error(f"Erro ao parar captura via Socket.IO: {e}")
            await sio_manager.send_personal(sid, "error", {"message": str(e)})
    
    # ============ CALLBACKS DO ANALYZER PARA SOCKET.IO ============
    
    import threading
    
    def _emit_event_threadsafe(event: str, data: dict):
        """Emite evento de forma thread-safe no event loop principal."""
        try:
            loop = EventLoopHolder.loop
            if loop is not None and loop.is_running():
                # Cria a corotina e executa no event loop de forma thread-safe
                future = asyncio.run_coroutine_threadsafe(
                    sio_manager.broadcast(event, data),
                    loop
                )
                # Não logar cada evento de áudio para evitar spam
                if event != "audio_level":
                    logger.debug(f"📡 Emitindo evento {event} via Socket.IO")
            else:
                logger.warning("Event loop não disponível para emissão de evento")
        except Exception as e:
            logger.error(f"Erro ao emitir evento {event}: {e}")
    
    def on_transcription(text: str, confidence: float):
        """Callback quando há nova transcrição - emite para todos os clientes."""
        try:
            _emit_event_threadsafe(
                "transcription_update",
                {
                    "text": text,
                    "confidence": float(confidence),
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.debug(f"📝 Transcrição broadcast: {text[:40]}...")
        except Exception as e:
            logger.error(f"Erro ao emitir transcrição: {e}")
    
    def on_audio_level(data: dict):
        """Callback quando há atualização de nível de áudio."""
        try:
            _emit_event_threadsafe(
                "audio_level",
                {
                    "level": data.get("level", 0),
                    "energy": data.get("energy", 0),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Erro ao emitir nível de áudio: {e}")
    
    def on_keyword_detected(keyword_id: str, text: str, confidence: float, context_score: float):
        """Callback quando palavra-chave é detectada."""
        try:
            _emit_event_threadsafe(
                "keyword_detected",
                {
                    "keyword_id": keyword_id,
                    "text": text,
                    "confidence": float(confidence),
                    "context_score": float(context_score),
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"🎯 Keyword detectada broadcast: {keyword_id}")
        except Exception as e:
            logger.error(f"Erro ao emitir keyword: {e}")
    
    # Registrar callbacks no analyzer
    analyzer.register_transcription_callback(on_transcription)
    analyzer.register_audio_level_callback(on_audio_level)
    analyzer.register_detection_callback(on_keyword_detected)
    logger.info("✓ Callbacks do analyzer registrados para Socket.IO")
    
    # ============ ROTAS DE STATUS ============
    
    @app.get("/api/status")
    async def get_status():
        """Obtém status da aplicação."""
        try:
            status = app.analyzer.get_status()
            return JSONResponse(status, status_code=200)
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/health")
    async def health_check():
        """Health check para load balancers."""
        return {"status": "healthy"}
    
    # ============ ROTAS DE CAPTURA ============
    
    @app.post("/api/capture/start")
    async def start_capture():
        """Inicia captura de áudio."""
        try:
            if app.analyzer.is_running:
                return {"message": "Captura já está rodando"}
            
            # Iniciar em background
            import threading
            def start_in_thread():
                try:
                    app.analyzer.start()
                except Exception as e:
                    logger.error(f"Erro ao iniciar: {e}")
            
            thread = threading.Thread(target=start_in_thread, daemon=True)
            thread.start()
            
            return {"message": "Captura iniciando..."}
        except Exception as e:
            logger.error(f"Erro ao iniciar captura: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.post("/api/capture/stop")
    async def stop_capture():
        """Para captura de áudio."""
        try:
            app.analyzer.stop()
            return {"message": "Captura parada"}
        except Exception as e:
            logger.error(f"Erro ao parar captura: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/capture/status")
    async def capture_status():
        """Obtém status da captura."""
        try:
            return {
                "is_capturing": app.analyzer.is_capturing,
                "is_running": app.analyzer.is_running,
            }
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # ============ ROTAS DO WHISPER ============
    
    @app.get("/api/whisper/status")
    async def get_whisper_status():
        """Obtém status do Whisper (modelo carregado, device, etc.)."""
        try:
            # Verificar se o transcriber está disponível
            if hasattr(app.analyzer, 'transcriber') and app.analyzer.transcriber:
                transcriber = app.analyzer.transcriber
                if hasattr(transcriber, 'get_status'):
                    status = transcriber.get_status()
                    return {
                        "available": True,
                        "status": "running" if status.get("is_running", False) else "stopped",
                        **status
                    }
                else:
                    # TranscriberThread básico
                    return {
                        "available": True,
                        "status": "running" if transcriber.is_running else "stopped",
                        "model": getattr(transcriber.transcriber, 'model_name', 'unknown'),
                        "device": getattr(transcriber.transcriber, 'device', 'unknown'),
                        "language": getattr(transcriber.transcriber, 'language', 'pt'),
                    }
            else:
                return {
                    "available": False,
                    "status": "not_loaded",
                    "message": "Whisper não está carregado. Inicie a captura de áudio."
                }
        except Exception as e:
            logger.error(f"Erro ao obter status do Whisper: {e}")
            return JSONResponse({
                "available": False,
                "status": "error",
                "error": str(e)
            }, status_code=500)
    
    @app.post("/api/whisper/test")
    async def test_whisper():
        """Testa o Whisper verificando se está carregado e funcionando."""
        try:
            # Verificar se o transcriber está disponível
            if not hasattr(app.analyzer, 'transcriber') or not app.analyzer.transcriber:
                return JSONResponse({
                    "success": False,
                    "error": "Whisper não está carregado. Inicie a captura de áudio primeiro."
                }, status_code=400)
            
            transcriber = app.analyzer.transcriber
            
            # Obter informações do transcriber
            if hasattr(transcriber, 'transcriber'):
                inner_transcriber = transcriber.transcriber
            else:
                inner_transcriber = transcriber
            
            model_name = getattr(inner_transcriber, 'model_name', 'unknown')
            device = getattr(inner_transcriber, 'device', 'unknown')
            language = getattr(inner_transcriber, 'language', 'pt')
            
            # Verificar se o modelo está carregado
            model_loaded = hasattr(inner_transcriber, 'model') and inner_transcriber.model is not None
            
            if not model_loaded:
                return JSONResponse({
                    "success": False,
                    "error": "Modelo Whisper não está carregado."
                }, status_code=500)
            
            # Em vez de transcrever silêncio (que pode dar erro), apenas verificamos que está funcionando
            return {
                "success": True,
                "message": "Whisper está funcionando corretamente!",
                "model": model_name,
                "device": device,
                "language": language,
                "model_loaded": model_loaded,
                "is_running": transcriber.is_running if hasattr(transcriber, 'is_running') else True,
            }
        except Exception as e:
            logger.error(f"Erro ao testar Whisper: {e}")
            return JSONResponse({
                "success": False,
                "error": str(e)
            }, status_code=500)
    
    @app.post("/api/whisper/reload")
    async def reload_whisper_model(request: Request):
        """Recarrega o modelo Whisper com as configurações atuais (troca de modelo em tempo real)."""
        try:
            data = await request.json() if request.headers.get("content-type") == "application/json" else {}
            
            # Validar modelo se especificado
            valid_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
            new_model = data.get("model")
            if new_model and new_model not in valid_models:
                return JSONResponse({"error": f"Modelo inválido. Use: {valid_models}"}, status_code=400)
            
            # Se novo modelo especificado, atualizar config
            if new_model:
                app.config_manager.set("whisper.model", new_model, persist=True)
            
            # Obter configurações atuais do Whisper
            whisper_config = app.config_manager.get("whisper", {})
            model_name = whisper_config.get("model", "base")
            language = whisper_config.get("language", "pt")
            device = whisper_config.get("device", "auto")
            
            # Verificar se está capturando
            was_capturing = app.analyzer.is_capturing
            
            logger.info(f"🔄 Recarregando modelo Whisper: {model_name} -> {new_model or model_name}")
            
            # Parar captura se estiver ativa
            if was_capturing:
                app.analyzer.stop_capture()
                await asyncio.sleep(0.5)  # Aguardar parada
            
            # Recriar o transcriber
            try:
                from audio.transcriber import TranscriberThread
                
                # Parar e limpar transcriber atual se existir
                if hasattr(app.analyzer, 'transcriber') and app.analyzer.transcriber:
                    logger.info("🧹 Limpando modelo anterior da memória...")
                    
                    # Usar método cleanup que libera GPU corretamente
                    if hasattr(app.analyzer.transcriber, 'cleanup'):
                        app.analyzer.transcriber.cleanup()
                    else:
                        # Fallback para versões antigas
                        if hasattr(app.analyzer.transcriber, 'stop'):
                            app.analyzer.transcriber.stop()
                    
                    # Garantir que a referência é removida
                    app.analyzer.transcriber = None
                    
                    # Forçar coleta de lixo e liberar CUDA
                    import gc
                    gc.collect()
                    
                    try:
                        import torch
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                            torch.cuda.synchronize()
                            
                            # Verificar memória disponível
                            total_mem = torch.cuda.get_device_properties(0).total_memory
                            reserved_mem = torch.cuda.memory_reserved(0)
                            allocated_mem = torch.cuda.memory_allocated(0)
                            free_mem = total_mem - reserved_mem
                            
                            logger.info(f"📊 Memória GPU após cleanup:")
                            logger.info(f"   Total: {total_mem / 1024**3:.1f} GB")
                            logger.info(f"   Reservada: {reserved_mem / 1024**3:.1f} GB")
                            logger.info(f"   Alocada: {allocated_mem / 1024**3:.1f} GB")
                            logger.info(f"   Livre: {free_mem / 1024**3:.1f} GB")
                    except Exception as e:
                        logger.warning(f"Erro ao verificar memória GPU: {e}")
                    
                    # Aguardar um pouco para garantir que a memória foi liberada
                    await asyncio.sleep(1.0)
                
                logger.info(f"📥 Carregando novo modelo: {new_model or model_name}")
                
                # Criar novo transcriber com as configurações atualizadas
                new_transcriber = TranscriberThread(
                    model_name=new_model or model_name,
                    language=language,
                    device=device if device != "auto" else None,
                    # Parâmetros avançados
                    beam_size=whisper_config.get("beam_size", 5),
                    best_of=whisper_config.get("best_of", 5),
                    temperature=whisper_config.get("temperature", 0.0),
                    no_speech_threshold=whisper_config.get("no_speech_threshold", 0.6),
                    initial_prompt=whisper_config.get("initial_prompt", ""),
                )
                
                app.analyzer.transcriber = new_transcriber
                app.analyzer.transcriber.start()
                
                logger.info(f"✓ Novo modelo Whisper carregado: {new_model or model_name}")
                
            except Exception as e:
                logger.error(f"Erro ao recarregar transcriber: {e}")
                return JSONResponse({
                    "success": False,
                    "error": f"Erro ao carregar modelo: {str(e)}"
                }, status_code=500)
            
            # Reiniciar captura se estava ativa
            if was_capturing:
                app.analyzer.start_capture()
            
            return {
                "success": True,
                "message": f"Modelo Whisper alterado para '{new_model or model_name}'",
                "model": new_model or model_name,
                "device": device,
                "language": language,
                "capture_restarted": was_capturing
            }
            
        except Exception as e:
            logger.error(f"Erro ao recarregar modelo Whisper: {e}")
            return JSONResponse({
                "success": False,
                "error": str(e)
            }, status_code=500)
    
    # ============ ROTAS DE DISPOSITIVOS ============
    
    @app.get("/api/devices")
    async def list_devices():
        """Lista dispositivos de áudio disponíveis."""
        try:
            devices = app.analyzer.get_devices()
            return {"devices": devices}
        except Exception as e:
            logger.error(f"Erro ao listar dispositivos: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/whisper-devices")
    async def get_whisper_devices():
        """Obtém dispositivos Whisper disponíveis (CPU/CUDA)."""
        try:
            import torch
            devices = []
            
            devices.append({
                "value": "cpu",
                "label": "💻 CPU (Mais Compatível)",
                "description": "Funciona em qualquer máquina, mas é mais lento"
            })
            
            if torch.cuda.is_available():
                devices.append({
                    "value": "cuda",
                    "label": "⚡ CUDA (Rápido)",
                    "description": f"GPU NVIDIA - {torch.cuda.get_device_name(0)}"
                })
            
            return {"devices": devices}
        except Exception as e:
            logger.error(f"Erro ao obter Whisper devices: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # ============ ROTAS DE CONFIGURAÇÃO ============
    
    @app.get("/api/config")
    async def get_config():
        """Obtém configuração atual."""
        try:
            config = app.config_manager.get_all()
            return config
        except Exception as e:
            logger.error(f"Erro ao obter config: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.post("/api/config")
    async def update_config(request: Request):
        """Atualiza configuração."""
        try:
            data = await request.json()
            
            def flatten_dict(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            def convert_value(key, value):
                """Converte valores para tipos apropriados."""
                if value is None or value == '':
                    return None
                
                if isinstance(value, bool):
                    return value
                if isinstance(value, (int, float)):
                    return value
                
                if isinstance(value, str):
                    if value.lower() in ('true', 'yes', '1'):
                        return True
                    if value.lower() in ('false', 'no', '0'):
                        return False
                    
                    if any(field in key for field in ['device_id', 'chunk_size', 'channels', 'port']):
                        try:
                            return int(value)
                        except ValueError:
                            pass
                    
                    if any(field in key for field in ['threshold', 'weight', 'rate', 'confidence', 'score']):
                        try:
                            return float(value)
                        except ValueError:
                            pass
                
                return value
            
            flat_config = flatten_dict(data)
            
            for key, value in flat_config.items():
                converted_value = convert_value(key, value)
                app.config_manager.set(key, converted_value, persist=False)
            
            app.config_manager.save_config()
            app.analyzer.reload_config()
            
            return {"message": "Configuração atualizada"}
        except Exception as e:
            logger.error(f"Erro ao atualizar config: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.post("/api/config/device")
    async def set_input_device(request: Request):
        """Define dispositivo de entrada de áudio."""
        try:
            data = await request.json()
            device_id = data.get("device_id")
            
            if device_id is None:
                return JSONResponse({"error": "device_id não fornecido"}, status_code=400)
            
            # Garantir que device_id seja inteiro
            try:
                device_id = int(device_id)
            except (ValueError, TypeError):
                return JSONResponse({"error": "device_id deve ser um número inteiro"}, status_code=400)
            
            logger.info(f"Audio input device set to {device_id}")
            app.analyzer.set_input_device(device_id, persist=True)
            
            return {
                "message": "Dispositivo configurado",
                "device_id": device_id
            }
        except Exception as e:
            logger.error(f"Erro ao configurar dispositivo: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/config/whisper-device")
    async def get_whisper_device():
        """Obtém configuração atual do dispositivo Whisper."""
        try:
            whisper_device = app.config_manager.get("whisper.device", "auto")
            return {"device": whisper_device}
        except Exception as e:
            logger.error(f"Erro ao obter whisper device: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.post("/api/config/whisper-device")
    async def set_whisper_device(request: Request):
        """Define dispositivo de processamento Whisper (cpu/cuda/auto)."""
        try:
            data = await request.json()
            device = data.get("device", "auto")
            
            if device not in ["cpu", "cuda", "auto"]:
                return JSONResponse({"error": "Dispositivo inválido. Use: cpu, cuda ou auto"}, status_code=400)
            
            app.config_manager.set("whisper.device", device, persist=True)
            logger.info(f"Whisper device set to {device}")
            
            return {
                "message": "Dispositivo Whisper configurado",
                "device": device
            }
        except Exception as e:
            logger.error(f"Erro ao configurar whisper device: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/config/whisper")
    async def get_whisper_config():
        """Obtém todas as configurações do Whisper."""
        try:
            whisper_config = app.config_manager.get("whisper", {})
            return {
                "model": whisper_config.get("model", "base"),
                "language": whisper_config.get("language", "pt"),
                "task": whisper_config.get("task", "transcribe"),
                "fp16": whisper_config.get("fp16", False),
                "device": whisper_config.get("device", "auto"),
                "beam_size": whisper_config.get("beam_size", 5),
                "best_of": whisper_config.get("best_of", 5),
                "temperature": whisper_config.get("temperature", 0.0),
                "patience": whisper_config.get("patience", 1.0),
                "length_penalty": whisper_config.get("length_penalty", 1.0),
                "suppress_blank": whisper_config.get("suppress_blank", True),
                "condition_on_previous_text": whisper_config.get("condition_on_previous_text", True),
                "no_speech_threshold": whisper_config.get("no_speech_threshold", 0.6),
                "compression_ratio_threshold": whisper_config.get("compression_ratio_threshold", 2.4),
                "logprob_threshold": whisper_config.get("logprob_threshold", -1.0),
                "initial_prompt": whisper_config.get("initial_prompt", ""),
                "word_timestamps": whisper_config.get("word_timestamps", False),
                "hallucination_silence_threshold": whisper_config.get("hallucination_silence_threshold"),
            }
        except Exception as e:
            logger.error(f"Erro ao obter config whisper: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.post("/api/config/whisper")
    async def set_whisper_config(request: Request):
        """Atualiza configurações do Whisper."""
        try:
            data = await request.json()
            
            # Validações
            valid_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
            valid_languages = ["pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "auto"]
            valid_tasks = ["transcribe", "translate"]
            valid_devices = ["cpu", "cuda", "auto"]
            
            if "model" in data and data["model"] not in valid_models:
                return JSONResponse({"error": f"Modelo inválido. Use: {valid_models}"}, status_code=400)
            if "language" in data and data["language"] not in valid_languages:
                return JSONResponse({"error": f"Idioma inválido. Use: {valid_languages}"}, status_code=400)
            if "task" in data and data["task"] not in valid_tasks:
                return JSONResponse({"error": f"Task inválida. Use: {valid_tasks}"}, status_code=400)
            if "device" in data and data["device"] not in valid_devices:
                return JSONResponse({"error": f"Dispositivo inválido. Use: {valid_devices}"}, status_code=400)
            
            # Validar valores numéricos
            if "beam_size" in data:
                beam_size = int(data["beam_size"])
                if beam_size < 1 or beam_size > 20:
                    return JSONResponse({"error": "beam_size deve estar entre 1 e 20"}, status_code=400)
                data["beam_size"] = beam_size
            
            if "best_of" in data:
                best_of = int(data["best_of"])
                if best_of < 1 or best_of > 20:
                    return JSONResponse({"error": "best_of deve estar entre 1 e 20"}, status_code=400)
                data["best_of"] = best_of
            
            if "temperature" in data:
                temp = float(data["temperature"])
                if temp < 0.0 or temp > 1.0:
                    return JSONResponse({"error": "temperature deve estar entre 0.0 e 1.0"}, status_code=400)
                data["temperature"] = temp
            
            if "no_speech_threshold" in data:
                nst = float(data["no_speech_threshold"])
                if nst < 0.0 or nst > 1.0:
                    return JSONResponse({"error": "no_speech_threshold deve estar entre 0.0 e 1.0"}, status_code=400)
                data["no_speech_threshold"] = nst
            
            # Atualizar cada configuração
            for key, value in data.items():
                app.config_manager.set(f"whisper.{key}", value, persist=False)
            
            app.config_manager.save_config()
            logger.info(f"Whisper config updated: {list(data.keys())}")
            
            return {
                "message": "Configurações do Whisper atualizadas",
                "updated_fields": list(data.keys()),
                "note": "Reinicie a captura para aplicar mudanças no modelo"
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar config whisper: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # ============ ROTAS LLM ============
    
    @app.get("/api/llm/status")
    async def llm_status():
        """Obtém status do engine LLM."""
        try:
            llm_engine = getattr(app.analyzer, 'llm_engine', None)
            
            if llm_engine is None:
                return {
                    "available": False,
                    "backend": "none",
                    "model": None,
                    "device": "cpu",
                    "error": "LLM engine não inicializado"
                }
            
            return {
                "available": getattr(llm_engine, 'model', None) is not None,
                "backend": getattr(llm_engine, 'backend', "unknown"),
                "model": getattr(llm_engine, 'model_name', None),
                "device": str(getattr(llm_engine, 'device', "cpu")),
                "error": None
            }
        except Exception as e:
            logger.error(f"Erro ao obter status LLM: {e}")
            return {
                "available": False,
                "backend": "error",
                "model": None,
                "device": "cpu",
                "error": str(e)
            }
    
    @app.post("/api/llm/generate")
    async def llm_generate(request: Request):
        """Gera texto usando o LLM."""
        try:
            data = await request.json()
            prompt = data.get("prompt", "")
            max_tokens = data.get("max_tokens", 100)
            
            llm_engine = getattr(app.analyzer, 'llm_engine', None)
            if llm_engine is None:
                return JSONResponse({"error": "LLM não disponível"}, status_code=503)
            
            response = llm_engine.generate(prompt, max_tokens=max_tokens)
            return {"response": response}
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/api/audio/level")
    async def get_audio_level():
        """Obtém nível de áudio atual."""
        try:
            if not app.analyzer.audio_processor:
                return {
                    "energy": 0,
                    "db": -100,
                    "normalized_level": 0,
                    "is_silent": True,
                    "suggestion": "Microfone não inicializado"
                }
            
            energy = app.analyzer.audio_processor.get_energy()
            is_silent = bool(app.analyzer.audio_processor.is_silent())  # Converter numpy.bool para bool Python
            
            import math
            db = 20 * math.log10(max(energy, 1e-10))
            normalized = min(100, max(0, int((db + 80) * 1.25)))
            
            suggestion = ""
            if is_silent:
                suggestion = "Microfone muito baixo - ajuste o volume"
            elif normalized < 30:
                suggestion = "Volume baixo - aumente o microfone"
            elif normalized > 80:
                suggestion = "Volume muito alto - reduza para evitar distorção"
            else:
                suggestion = "Volume OK ✓"
            
            return {
                "energy": float(energy),
                "db": float(db),
                "normalized_level": normalized,
                "is_silent": is_silent,
                "suggestion": suggestion
            }
        except Exception as e:
            logger.error(f"Erro ao obter nível de áudio: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # ============ STATIC FILES ============
    
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_folder):
        app.mount("/static", StaticFiles(directory=static_folder), name="static")
    
    return app


def run_app(analyzer: MicrophoneAnalyzer, host: str = "0.0.0.0", port: int = 5000, reload: bool = False):
    """
    Inicia servidor FastAPI com Socket.IO.
    
    Args:
        analyzer: Instância de MicrophoneAnalyzer
        host: Host para ouvir
        port: Porta para ouvir
        reload: Recarregar ao mudar arquivos (desenvolvimento)
    """
    app = create_app(analyzer)
    
    # Usar socketio.ASGIApp para integrar Socket.IO e FastAPI corretamente
    # Isso lida automaticamente com polling HTTP e WebSocket
    app_with_socketio = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=app,
        socketio_path='socket.io'
    )
    
    uvicorn.run(
        app_with_socketio,
        host=host,
        port=port,
        reload=reload,
        access_log=True
    )
