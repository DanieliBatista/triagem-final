from src.domain.entities import Prontuario

class ProntuarioUseCase:
    def __init__(self, repository):
        """
        O 'repository' é o que conversa com o Banco de Dados.
        Na Clean Architecture, o Use Case não sabe se o banco é SQL ou NoSQL.
        """
        self.repository = repository

    def registrar_atendimento(self, dados: dict, user_role: str):
        """
        RN02: Controle de acesso (Somente médicos podem criar anamnese/prescrição)
        """
        if user_role != "MEDICO":
            raise PermissionError("Apenas médicos podem registrar novos prontuários.")
        
        novo_prontuario = Prontuario(
            paciente_id=dados.get("paciente_id"),
            medico_id=dados.get("medico_id"),
            anamnese=dados.get("anamnese"),
            prescricoes=dados.get("prescricoes", [])
        )
        
        return self.repository.save(novo_prontuario)

    def fechar_consulta_e_gerar_alta(self, paciente_id: str, user_role: str):
        """
        RN03: Geração de sumário de alta automático pós-consulta.
        """
        if user_role not in ["MEDICO", "ENFERMEIRO"]:
            raise PermissionError("Usuário sem permissão para gerar sumário de alta.")

        prontuario = self.repository.get_by_paciente(paciente_id)
        
        if not prontuario:
            raise ValueError("Prontuário não encontrado para este paciente.")

        sumario = prontuario.gerar_sumario_alta()

        return {
            "paciente_id": paciente_id,
            "documento_alta": sumario,
            "mensagem": "Alta processada com sucesso."
        }