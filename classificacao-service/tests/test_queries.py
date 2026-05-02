"""Testes para consultas (CQRS)"""
import pytest
from unittest.mock import AsyncMock

from app.application.queries.obter_classificacao_atual import (
    ObterClassificacaoQuery,
    ObterClassificacaoManipulador,
)


class TestObterClassificacaoQuery:
    """Testes para obter classificação"""

    @pytest.mark.asyncio
    async def test_obter_classificacao_com_sucesso(self, classificacao_padrao):
        """Deve obter classificação existente"""
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao

        consulta = ObterClassificacaoQuery(classificacao_id=str(classificacao_padrao.id))
        manipulador = ObterClassificacaoManipulador(repositorio)

        resultado = await manipulador.manipular(consulta)

        assert resultado["paciente_id"] == "PAC-001"
        assert resultado["cor_risco"] == "AZUL"
        assert resultado["status"] == "ATIVO"

        repositorio.obter_por_id.assert_called_once_with(str(classificacao_padrao.id))

    @pytest.mark.asyncio
    async def test_obter_classificacao_inexistente(self):
        """Deve rejeitar classificação inexistente"""
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = None

        consulta = ObterClassificacaoQuery(classificacao_id="inexistente")
        manipulador = ObterClassificacaoManipulador(repositorio)

        with pytest.raises(ValueError) as exc_info:
            await manipulador.manipular(consulta)

        assert "não encontrada" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_obter_classificacao_verifica_expiracao(self, classificacao_padrao):
        """Deve verificar expiração ao obter classificação"""
        repositorio = AsyncMock()
        repositorio.obter_por_id.return_value = classificacao_padrao

        from unittest.mock import patch
        with patch.object(
            classificacao_padrao, "verificar_expiracao"
        ) as mock_expiracao:
            consulta = ObterClassificacaoQuery(classificacao_id=str(classificacao_padrao.id))
            manipulador = ObterClassificacaoManipulador(repositorio)

            await manipulador.manipular(consulta)

            mock_expiracao.assert_called_once()
