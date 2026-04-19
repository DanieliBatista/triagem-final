from sqlalchemy.orm import Session
from src.infrastructure.database import ProntuarioTable 

class ProntuarioRepository:

    def save(self, db: Session, entidade_prontuario):
        tabela_prontuario = ProntuarioTable(
            paciente_id=entidade_prontuario.paciente_id,
            medico_id=entidade_prontuario.medico_id,
            anamnese=entidade_prontuario.anamnese,
            prescricoes=entidade_prontuario.prescricoes,
            status="EM_ANDAMENTO"
        )
        
        db.add(tabela_prontuario)
        db.commit()
        db.refresh(tabela_prontuario)
        
        return tabela_prontuario

    def get_by_paciente(self, db: Session, paciente_id: str):
        return db.query(ProntuarioTable)\
                 .filter(ProntuarioTable.paciente_id == paciente_id)\
                 .order_by(ProntuarioTable.id.desc())\
                 .first()

    def buscar_historico(self, db: Session, paciente_id: str):
        return db.query(ProntuarioTable)\
                 .filter(ProntuarioTable.paciente_id == paciente_id)\
                 .all()