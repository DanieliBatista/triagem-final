from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Prontuario:
    """
    Entidade que representa o Histórico Médico do Paciente.
    Regra 1: Armazenamento de anamnese e prescrições.
    """
    paciente_id: str
    medico_id: str
    anamnese: str
    prescricoes: List[str] = field(default_factory=list)
    data_criacao: datetime = field(default_factory=datetime.now)

    def validar(self):
        """
        Garante que o prontuário não seja criado sem informações essenciais.
        """
        if not self.paciente_id or not self.anamnese:
            raise ValueError("Paciente ID e Anamnese são obrigatórios.")
        if len(self.anamnese) < 10:
            raise ValueError("A anamnese deve ser mais detalhada.")

    def gerar_sumario_alta(self) -> str:
        """
        Regra 3: Geração de sumário de alta automático pós-consulta.
        Esta lógica transforma os dados técnicos em um documento textual.
        """
        data_str = self.data_criacao.strftime("%d/%m/%Y às %H:%M")
        
        # Formata a lista de prescrições para o texto
        lista_prescricoes = "\n- ".join(self.prescricoes) if self.prescricoes else "Nenhuma prescrição registrada."

        sumario = (
            f"--- SUMÁRIO DE ALTA HOSPITALAR ---\n"
            f"DATA DO ATENDIMENTO: {data_str}\n"
            f"IDENTIFICAÇÃO DO PACIENTE: {self.paciente_id}\n"
            f"MÉDICO RESPONSÁVEL: {self.medico_id}\n"
            f"-----------------------------------\n"
            f"RESUMO CLÍNICO (ANAMNESE):\n"
            f"{self.anamnese}\n\n"
            f"PRESCRIÇÕES MÉDICAS:\n- {lista_prescricoes}\n"
            f"-----------------------------------\n"
            f"STATUS: ALTA AUTORIZADA PELO SISTEMA."
        )
        return sumario