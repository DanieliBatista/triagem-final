import pytest
from unittest.mock import MagicMock
from src.domain.entities import Prontuario
from src.application.use_cases import ProntuarioUseCase

# --- TESTES DE DOMÍNIO ---
def test_geracao_sumario_alta_sucesso():
    prontuario = Prontuario(
        paciente_id="123", medico_id="CRM-456",
        anamnese="Paciente apresenta melhora significativa.",
        prescricoes=["Dipirona 500mg"]
    )
    sumario = prontuario.gerar_sumario_alta()
    assert "SUMÁRIO DE ALTA" in sumario

def test_validacao_anamnese_curta():
    with pytest.raises(ValueError, match="anamnese deve ser mais detalhada"):
        p = Prontuario("123", "M1", "Dor", [])
        p.validar()

# --- TESTES DE APLICAÇÃO (Ajustados para a nova arquitetura) ---
class MockRepository:
    def save(self, db, obj): return obj
    def get_by_paciente(self, db, id): return MagicMock(paciente_id=id, medico_id="M1", anamnese="Teste", prescricoes=[])
    def buscar_historico(self, db, id): return []

def test_registrar_atendimento_permissao_negada():
    repo = MockRepository()
    use_case = ProntuarioUseCase(repo)
    db_mock = MagicMock() # Banco falso
    dados = {"paciente_id": "1", "medico_id": "M1", "anamnese": "Texto longo o suficiente", "prescricoes": []}
    
    with pytest.raises(PermissionError, match="Apenas médicos"):
        # Passando o db_mock como primeiro argumento
        use_case.registrar_atendimento(db_mock, dados, user_role="ENFERMEIRO")

def test_registrar_atendimento_sucesso_medico():
    repo = MockRepository()
    use_case = ProntuarioUseCase(repo)
    db_mock = MagicMock()
    dados = {"paciente_id": "1", "medico_id": "M1", "anamnese": "Paciente com quadro estável.", "prescricoes": []}
    
    resultado = use_case.registrar_atendimento(db_mock, dados, user_role="MEDICO")
    assert resultado.paciente_id == "1"