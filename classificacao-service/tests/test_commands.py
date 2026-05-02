import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.application.commands import (
    CriarClassificacaoCommand,
    CriarClassificacaoManipulador,
)
from app.application.commands.criar_classificacao import ClassificacaoCriadaEvento
from app.application.commands.reclassificar_manualmente import (
    ReclassificarManualmenteCommand,
    ReclassificarManualmenteManipulador,
)
from app.domain.enums import RiskColor, StatusClassificacao
from app.domain.exceptions import (
    ValidacaoBiologicaException,
    PermissaoNegadaException,
    JustificativaObrigatoriaException,
)
from app.domain.value_objects import SinaisVitais


class TestCriarClassificacaoCommand:

    @pytest.mark.asyncio
    async def test_criar_classificacao_com_sucesso(self, sinais_vitais_normais):
        repositorio = AsyncMock()
        despachador = AsyncMock()

        comando = CriarClassificacaoCommand(
            paciente_id="PAC-001",
            temperatura=36.5,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=72,
            dor_peito=False,
            usuario_id="medico-001",
        )

        manipulador = CriarClassificacaoManipulador(repositorio, despachador)
        resultado = await manipulador.manipular(comando)

        assert resultado["paciente_id"] == "PAC-001"
        assert resultado["cor_risco"] == "AZUL"
        assert resultado["tempo_espera_minutos"] == 120
        assert resultado["status"] == "ATIVO"
        assert resultado["tipo_mudanca"] == "AUTOMATICA"

        repositorio.salvar.assert_called_once()
        despachador.despachar.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_classificacao_com_dor_peito(self):
        repositorio = AsyncMock()
        despachador = AsyncMock()

        comando = CriarClassificacaoCommand(
            paciente_id="PAC-002",
            temperatura=37.0,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=80,
            dor_peito=True,
            usuario_id="medico-001",
        )

        manipulador = CriarClassificacaoManipulador(repositorio, despachador)
        resultado = await manipulador.manipular(comando)

        assert resultado["cor_risco"] == "VERMELHO"
        assert resultado["tempo_espera_minutos"] == 0

    @pytest.mark.asyncio
    async def test_criar_classificacao_com_febre(self):
        repositorio = AsyncMock()
        despachador = AsyncMock()

        comando = CriarClassificacaoCommand(
            paciente_id="PAC-003",
            temperatura=39.5,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=80,
            usuario_id="medico-001",
        )

        manipulador = CriarClassificacaoManipulador(repositorio, despachador)
        resultado = await manipulador.manipular(comando)

        assert resultado["cor_risco"] == "LARANJA"
        assert resultado["tempo_espera_minutos"] == 10

    @pytest.mark.asyncio
    async def test_criar_classificacao_vital_invalido(self):
        repositorio = AsyncMock()
        despachador = AsyncMock()

        comando = CriarClassificacaoCommand(
            paciente_id="PAC-004",
            temperatura=50.0,  # Inválido
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_oxigenio=98.0,
            frequencia_cardiaca=80,
            usuario_id="medico-001",
        )

        manipulador = CriarClassificacaoManipulador(repositorio, despachador)

        with pytest.raises(ValidacaoBiologicaException):
            await manipulador.manipular(comando)

    def test_classificacao_criada_evento_para_dict(self):
        evento = ClassificacaoCriadaEvento(
            classificacao_id="cls-001",
            paciente_id="PAC-001",
            cor_risco="AZUL",
            tempo_espera_minutos=120,
            usuario_id="medico-001",
        )

        resultado = evento.para_dict()

        assert resultado["tipo_evento"] == "classificacao.criada"
        assert resultado["versao"] == "1.0"
        assert "timestamp" in resultado
        assert resultado["dados"]["classificacao_id"] == "cls-001"
        assert resultado["dados"]["cor_risco"] == "AZUL"


class TestReclassificarManualmenteCommand:

    @pytest.mark.asyncio
    async def test_reclassificar_com_sucesso(self, classificacao_padrao):
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao
        event_store = AsyncMock()
        despachador = AsyncMock()

        comando = ReclassificarManualmenteCommand(
            classificacao_id=str(classificacao_padrao.id),
            nova_cor="VERMELHO",
            usuario_id="medico-001",
            usuario_role="MEDICO",
            usuario_email="medico@hospital.com",
            justificativa="Piora clínica observada",
            ip_origem="192.168.1.1",
        )

        manipulador = ReclassificarManualmenteManipulador(
            repositorio, event_store, despachador
        )
        resultado = await manipulador.manipular(comando)

        assert resultado["cor_risco"] == "VERMELHO"
        assert resultado["tipo_mudanca"] == "MANUAL"
        assert resultado["tempo_espera_minutos"] == 0

        repositorio.obter_por_id.assert_called_once_with(str(classificacao_padrao.id))
        event_store.registrar.assert_called_once()
        repositorio.salvar.assert_called_once()
        despachador.despachar.assert_called_once()

    @pytest.mark.asyncio
    async def test_reclassificar_sem_permissao(self, classificacao_padrao):
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao
        event_store = AsyncMock()
        despachador = AsyncMock()

        comando = ReclassificarManualmenteCommand(
            classificacao_id=str(classificacao_padrao.id),
            nova_cor="VERMELHO",
            usuario_id="paciente-001",
            usuario_role="PACIENTE",
            usuario_email="paciente@email.com",
            justificativa="Quero mudar",
            ip_origem="192.168.1.1",
        )

        manipulador = ReclassificarManualmenteManipulador(
            repositorio, event_store, despachador
        )

        with pytest.raises(PermissaoNegadaException):
            await manipulador.manipular(comando)

    @pytest.mark.asyncio
    async def test_reclassificar_sem_justificativa(self, classificacao_padrao):
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao
        event_store = AsyncMock()
        despachador = AsyncMock()

        comando = ReclassificarManualmenteCommand(
            classificacao_id=str(classificacao_padrao.id),
            nova_cor="VERMELHO",
            usuario_id="medico-001",
            usuario_role="MEDICO",
            usuario_email="medico@hospital.com",
            justificativa="",  # Vazio
            ip_origem="192.168.1.1",
        )

        manipulador = ReclassificarManualmenteManipulador(
            repositorio, event_store, despachador
        )

        with pytest.raises(JustificativaObrigatoriaException):
            await manipulador.manipular(comando)

    @pytest.mark.asyncio
    async def test_reclassificar_com_justificativa_muito_curta(self, classificacao_padrao):
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao
        event_store = AsyncMock()
        despachador = AsyncMock()

        comando = ReclassificarManualmenteCommand(
            classificacao_id=str(classificacao_padrao.id),
            nova_cor="VERMELHO",
            usuario_id="medico-001",
            usuario_role="MEDICO",
            usuario_email="medico@hospital.com",
            justificativa="ok",  # Muito curto
            ip_origem="192.168.1.1",
        )

        manipulador = ReclassificarManualmenteManipulador(
            repositorio, event_store, despachador
        )

        with pytest.raises(JustificativaObrigatoriaException):
            await manipulador.manipular(comando)

    @pytest.mark.asyncio
    async def test_reclassificar_classificacao_inexistente(self):
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = None
        event_store = AsyncMock()
        despachador = AsyncMock()

        comando = ReclassificarManualmenteCommand(
            classificacao_id="inexistente",
            nova_cor="VERMELHO",
            usuario_id="medico-001",
            usuario_role="MEDICO",
            usuario_email="medico@hospital.com",
            justificativa="Piora clínica",
            ip_origem="192.168.1.1",
        )

        manipulador = ReclassificarManualmenteManipulador(
            repositorio, event_store, despachador
        )

        with pytest.raises(ValueError):
            await manipulador.manipular(comando)
