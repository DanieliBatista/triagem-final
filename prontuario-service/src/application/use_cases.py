from sqlalchemy.orm import Session
from src.domain.entities import Prontuario

class ProntuarioUseCase:
    def __init__(self, repository):
        self.repository = repository

    def registrar_atendimento(self, db: Session, dados: dict, user_role: str):
        if user_role != "MEDICO":
            raise PermissionError("Apenas médicos podem registrar novos prontuários.")
        
        novo_prontuario = Prontuario(
            paciente_id=dados.get("paciente_id"),
            medico_id=dados.get("medico_id"),
            anamnese=dados.get("anamnese"),
            prescricoes=dados.get("prescricoes", [])
        )

        return self.repository.save(db, novo_prontuario)

    def fechar_consulta_e_gerar_alta(self, db: Session, paciente_id: str, user_role: str):
        if user_role not in ["MEDICO", "ENFERMEIRO"]:
            raise PermissionError("Usuário sem permissão para gerar sumário de alta.")

        prontuario_db = self.repository.get_by_paciente(db, paciente_id)
        
        if not prontuario_db:
            raise ValueError("Prontuário não encontrado para este paciente.")
        
        prontuario_entidade = Prontuario(
            paciente_id=prontuario_db.paciente_id,
            medico_id=prontuario_db.medico_id,
            anamnese=prontuario_db.anamnese,
            prescricoes=prontuario_db.prescricoes
        )

        sumario = prontuario_entidade.gerar_sumario_alta()

        prontuario_db.status = "ALTA"
        db.commit()

        return {
            "paciente_id": paciente_id,
            "documento_alta": sumario,
            "mensagem": "Alta processada com sucesso."
        }

    def obter_historico(self, db: Session, paciente_id: str, role: str):
        registros = self.repository.buscar_historico(db, paciente_id)
        
        historico_formatado = []
        for reg in registros:
            historico_formatado.append({
                "id": reg.id,
                "anamnese": reg.anamnese,
                "medico_id": reg.medico_id,
                "prescricoes": reg.prescricoes
            })
            
        return {
            "paciente_id": paciente_id,
            "total_atendimentos": len(historico_formatado),
            "solicitado_por": role,
            "historico": historico_formatado
        }