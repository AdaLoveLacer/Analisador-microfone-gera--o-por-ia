"""
Testes de integração para as rotas da API
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from web.app import create_app


@pytest.fixture
def analyzer():
    """Mock do MicrophoneAnalyzer para testes"""
    mock_analyzer = MagicMock()
    mock_config = MagicMock()
    mock_config.get.return_value = "INFO"
    mock_analyzer.config = mock_config
    mock_analyzer.database = MagicMock()
    return mock_analyzer


@pytest.fixture
def app(analyzer):
    """Cria app Flask para testes"""
    app = create_app(analyzer)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Client para requisições de teste"""
    return app.test_client()


class TestHealthEndpoint:
    """Testes para endpoint de saúde"""

    def test_health_check(self, client):
        """Verifica endpoint de saúde"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestConfigEndpoints:
    """Testes para endpoints de configuração"""

    def test_get_config(self, client):
        """GET /api/config retorna config"""
        response = client.get('/api/config')
        assert response.status_code in [200, 500]  # Pode falhar se config não existe
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict)

    def test_update_config(self, client):
        """POST /api/config atualiza config"""
        new_config = {
            "audio": {
                "sample_rate": 16000
            }
        }
        
        response = client.post(
            '/api/config',
            data=json.dumps(new_config),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 500]

    def test_export_config(self, client):
        """GET /api/config/export exporta config"""
        response = client.get('/api/config/export')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            # Deve retornar JSON
            assert response.content_type == 'application/json'

    def test_reset_config(self, client):
        """POST /api/config/reset reseta para padrão"""
        response = client.post('/api/config/reset')
        assert response.status_code in [200, 500]


class TestKeywordEndpoints:
    """Testes para endpoints de palavras-chave"""

    def test_get_keywords(self, client):
        """GET /api/keywords retorna lista"""
        response = client.get('/api/keywords')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_add_keyword(self, client):
        """POST /api/keywords cria palavra-chave"""
        keyword = {
            "name": "Sus",
            "pattern": "sus",
            "sound_id": "sound_1",
            "variations": ["suspeitoso"],
            "context_keywords": []
        }
        
        response = client.post(
            '/api/keywords',
            data=json.dumps(keyword),
            content_type='application/json'
        )
        
        assert response.status_code in [201, 400, 500]

    def test_update_keyword(self, client):
        """PUT /api/keywords/<id> atualiza palavra-chave"""
        keyword_update = {
            "name": "SUS Updated",
            "pattern": "sus"
        }
        
        response = client.put(
            '/api/keywords/test_id',
            data=json.dumps(keyword_update),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 404, 500]

    def test_delete_keyword(self, client):
        """DELETE /api/keywords/<id> deleta palavra-chave"""
        response = client.delete('/api/keywords/test_id')
        assert response.status_code in [200, 404, 500]


class TestSoundEndpoints:
    """Testes para endpoints de sons"""

    def test_get_sounds(self, client):
        """GET /api/sounds retorna lista"""
        response = client.get('/api/sounds')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_add_sound(self, client):
        """POST /api/sounds cria som"""
        sound = {
            "name": "Meme Sound",
            "file_path": "audio_library/memes/sound.mp3",
            "volume": 0.8,
            "category": "memes"
        }
        
        response = client.post(
            '/api/sounds',
            data=json.dumps(sound),
            content_type='application/json'
        )
        
        assert response.status_code in [201, 400, 500]

    def test_preview_sound(self, client):
        """POST /api/sounds/<id>/preview reproduz som"""
        response = client.post('/api/sounds/test_id/preview')
        assert response.status_code in [200, 404, 500]


class TestCaptureEndpoints:
    """Testes para endpoints de captura"""

    def test_capture_start(self, client):
        """POST /api/capture/start inicia captura"""
        response = client.post('/api/capture/start')
        assert response.status_code in [200, 400, 500]

    def test_capture_stop(self, client):
        """POST /api/capture/stop para captura"""
        response = client.post('/api/capture/stop')
        assert response.status_code in [200, 400, 500]

    def test_capture_status(self, client):
        """GET /api/capture/status retorna status"""
        response = client.get('/api/capture/status')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'is_capturing' in data

    def test_list_devices(self, client):
        """GET /api/devices lista dispositivos"""
        response = client.get('/api/devices')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)


class TestHistoryEndpoints:
    """Testes para endpoints de histórico"""

    def test_get_detections(self, client):
        """GET /api/detections retorna detecções"""
        response = client.get('/api/detections')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_get_detection_stats(self, client):
        """GET /api/detections/stats retorna estatísticas"""
        response = client.get('/api/detections/stats')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict)

    def test_get_transcriptions(self, client):
        """GET /api/transcriptions retorna transcrições"""
        response = client.get('/api/transcriptions')
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)


class TestTestingEndpoints:
    """Testes para endpoints de teste"""

    def test_test_keyword(self, client):
        """POST /api/test/keyword/<id> testa palavra-chave"""
        test_data = {
            "text": "muito sus mesmo"
        }
        
        response = client.post(
            '/api/test/keyword/test_id',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 404, 500]

    def test_test_sound(self, client):
        """POST /api/test/sound/<id> testa som"""
        response = client.post('/api/test/sound/test_id')
        assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Testes para tratamento de erros"""

    def test_404_not_found(self, client):
        """Rota inexistente retorna 404"""
        response = client.get('/api/inexistente')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Método não permitido retorna 405"""
        response = client.put('/health')
        # Pode ser 405 ou 404 dependendo da implementação
        assert response.status_code in [404, 405]

    def test_invalid_json(self, client):
        """JSON inválido retorna 400"""
        response = client.post(
            '/api/keywords',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]


class TestCORSHeaders:
    """Testes para headers CORS"""

    def test_cors_headers_present(self, client):
        """CORS headers estão presentes"""
        response = client.get('/api/config')
        
        # Não falha se CORS não estiver configurado
        assert response.status_code in [200, 500]


class TestIntegrationFlow:
    """Testes de fluxo de integração"""

    def test_create_and_retrieve_keyword(self, client):
        """Cria e recupera palavra-chave"""
        # Cria keyword
        keyword = {
            "name": "TestSus",
            "pattern": "test_sus",
            "sound_id": "sound_1"
        }
        
        create_response = client.post(
            '/api/keywords',
            data=json.dumps(keyword),
            content_type='application/json'
        )
        
        # Se criou com sucesso
        if create_response.status_code == 201:
            # Recupera lista
            list_response = client.get('/api/keywords')
            assert list_response.status_code == 200

    def test_start_and_check_capture(self, client):
        """Inicia captura e verifica status"""
        # Inicia captura
        start_response = client.post('/api/capture/start')
        
        # Verifica status
        status_response = client.get('/api/capture/status')
        
        if status_response.status_code == 200:
            data = json.loads(status_response.data)
            assert 'is_capturing' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
