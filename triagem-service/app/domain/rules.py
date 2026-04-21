"""Regras de validação do Triagem Service"""


class ValidacaoBiologicaException(Exception):
    """Exceção para dados fora dos limites biológicos"""
    pass


def validar_sinais_vitais(temperatura, pressao_sistolica, pressao_diastolica,
                         saturacao_oxigenio, frequencia_cardiaca):
    """
    Validar se os sinais vitais estão dentro dos limites biologicamente possíveis

    Args:
        temperatura: em °C
        pressao_sistolica: em mmHg
        pressao_diastolica: em mmHg
        saturacao_oxigenio: em %
        frequencia_cardiaca: em bpm

    Raises:
        ValidacaoBiologicaException: Se algum valor está fora dos limites
    """

    # Validações de intervalo biologicamente possível
    if not (30.0 <= temperatura <= 45.0):
        raise ValidacaoBiologicaException(
            f"Temperatura {temperatura}°C fora do intervalo (30-45°C)"
        )

    if not (50 <= pressao_sistolica <= 300):
        raise ValidacaoBiologicaException(
            f"Pressão sistólica {pressao_sistolica} mmHg fora do intervalo (50-300)"
        )

    if not (30 <= pressao_diastolica <= 200):
        raise ValidacaoBiologicaException(
            f"Pressão diastólica {pressao_diastolica} mmHg fora do intervalo (30-200)"
        )

    if not (50.0 <= saturacao_oxigenio <= 100.0):
        raise ValidacaoBiologicaException(
            f"Saturação de oxigênio {saturacao_oxigenio}% fora do intervalo (50-100)"
        )

    if not (20 <= frequencia_cardiaca <= 300):
        raise ValidacaoBiologicaException(
            f"Frequência cardíaca {frequencia_cardiaca} bpm fora do intervalo (20-300)"
        )