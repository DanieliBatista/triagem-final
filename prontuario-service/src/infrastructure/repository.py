class ProntuarioRepository:
    def __init__(self):
        self._db = []

    def save(self, prontuario):
        self._db.append(prontuario)
        return prontuario

    def get_by_paciente(self, paciente_id: str):
        for prontuario in reversed(self._db):
            if prontuario.paciente_id == paciente_id:
                return prontuario
        return None