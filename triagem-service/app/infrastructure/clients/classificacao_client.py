"""Cliente HTTP para Classificação Service"""
import httpx
from typing import Dict, Any, Optional
from app.infrastructure.config import settings


class ClassificacaoClientException(Exception):
    """Exceção para erros na comunicação com Classificação Service"""
    pass


class ClassificacaoClient:
    """Cliente para comunicar com o serviço de Classificação"""

    def __init__(self, base_url: str = None):
        """
        Inicializar cliente

        Args:
            base_url: URL base do Classificação Service
                     Default: valor de CLASSIFICACAO_SERVICE_URL das settings
        """
        self.base_url = (base_url or settings.CLASSIFICACAO_SERVICE_URL).rstrip("/")
        self.timeout = 30.0

    async def criar_classificacao(
        self,
        paciente_id: str,
        temperatura: float,
        pressao_sistolica: int,
        pressao_diastolica: int,
        saturacao_oxigenio: float,
        frequencia_cardiaca: int,
        dor_peito: bool,
        token: str,
    ) -> Dict[str, Any]:
        """
        Criar classificação no serviço de Classificação

        Args:
            paciente_id: ID do paciente
            temperatura: Temperatura em °C
            pressao_sistolica: Pressão sistólica em mmHg
            pressao_diastolica: Pressão diastólica em mmHg
            saturacao_oxigenio: Saturação O2 em %
            frequencia_cardiaca: Frequência cardíaca em bpm
            dor_peito: Se tem dor no peito
            token: JWT token para autenticação

        Returns:
            Dict com dados da classificação criada:
            {
                "id": "classificacao_id",
                "paciente_id": "PAC-001",
                "cor_risco": "VERMELHO",
                "tempo_espera_minutos": 0,
                "status": "ATIVO",
                "tipo_mudanca": "AUTOMATICA",
                "usuario_id": "usuario_id",
                "data_criacao": "ISO8601",
                "data_atualizacao": "ISO8601",
                "requer_retriage": false,
                "sinais_vitais": {...}
            }

        Raises:
            ClassificacaoClientException: Se falhar a comunicação
        """
        url = f"{self.base_url}/v1/classificacoes"

        payload = {
            "paciente_id": paciente_id,
            "vital_signs": {
                "temperatura": temperatura,
                "pressao_sistolica": pressao_sistolica,
                "pressao_diastolica": pressao_diastolica,
                "saturacao_oxigenio": saturacao_oxigenio,
                "frequencia_cardiaca": frequencia_cardiaca,
                "dor_peito": dor_peito,
            },
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)

                # Tratar erro HTTP
                if response.status_code >= 400:
                    raise ClassificacaoClientException(
                        f"Classificação Service retornou erro {response.status_code}: "
                        f"{response.text}"
                    )

                return response.json()

        except httpx.TimeoutException:
            raise ClassificacaoClientException(
                f"Timeout ao conectar com Classificação Service ({url})"
            )
        except httpx.ConnectError:
            raise ClassificacaoClientException(
                f"Não conseguiu conectar com Classificação Service ({url}). "
                f"Serviço está rodando?"
            )
        except httpx.RequestError as e:
            raise ClassificacaoClientException(
                f"Erro na requisição para Classificação Service: {str(e)}"
            )
        except Exception as e:
            raise ClassificacaoClientException(
                f"Erro inesperado ao chamar Classificação Service: {str(e)}"
            )
