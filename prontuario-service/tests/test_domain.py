import pytest
from src.domain.entities import Prontuario
from src.application.use_cases import ProntuarioUseCase

# --- TESTES DE DOMÍNIO (Regra 3 e Validações) ---

def test_geracao_sumario_alta_sucesso():
    """Testa se o sumário de alta é formatado corretamente (Regra 3)"""
    prontuario = Prontuario(
        paciente_id="123",
        medico_id="CRM-456",
        anamnese="Paciente apresenta melhora significativa no quadro infeccioso.",
        prescricoes=["Dipirona 500mg", "Repouso"]
    )
    
    sumario = prontuario.gerar_sumario_alta()
    
    assert "SUMÁRIO DE ALTA" in sumario
    assert "123" in sumario
    assert "Dipirona 500mg" in sumario
    assert "ALTA AUTORIZADA" in sumario

def test_validacao_anamnese_curta():
    """Testa se o sistema rejeita anamneses muito curtas"""
    with pytest.raises(ValueError, match="anamnese deve ser mais detalhada"):
        p = Prontuario("123", "M1", "Dor", [])
        p.validar()

# --- TESTES DE APLICAÇÃO (Regra 2) ---

class MockRepository:
    """Um repositório falso para testar o Use Case sem precisar de banco"""
    def save(self, obj): return obj
    def get_by_paciente(self, id): return None

def test_registrar_atendimento_permissao_negada():
    """Testa se um ENFERMEIRO é impedido de criar prontuário (Regra 2)"""
    repo = MockRepository()
    use_case = ProntuarioUseCase(repo)
    
    dados = {
        "paciente_id": "1",
        "medico_id": "M1",
        "anamnese": "Texto longo o suficiente",
        "prescricoes": []
    }
    
    with pytest.raises(PermissionError, match="Apenas médicos"):
        use_case.registrar_atendimento(dados, user_role="ENFERMEIRO")

def test_registrar_atendimento_sucesso_medico():
    """Testa se um MÉDICO consegue registrar atendimento"""
    repo = MockRepository()
    use_case = ProntuarioUseCase(repo)
    
    dados = {
        "paciente_id": "1",
        "medico_id": "M1",
        "anamnese": "Paciente com quadro estável e sem febre.",
        "prescricoes": []
    }
    
    resultado = use_case.registrar_atendimento(dados, user_role="MEDICO")
    assert resultado.paciente_id == "1"