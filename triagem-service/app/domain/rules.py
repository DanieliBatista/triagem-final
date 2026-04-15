def calcular_risco(temperatura, pressao_sistolica, dor_peito):
    if temperatura > 45 or temperatura < 30:
        raise ValueError("Dados biométricos fora da realidade humana.")

    if dor_peito or pressao_sistolica > 180:
        return "VERMELHO (Emergencia)" 
    elif temperatura > 38.5:
        return "LARANJA (Muito urgente)"  
    
    return "VERDE (Pouco Urgente)"

def estimar_tempo_espera(cor):
    tempos = {"VERMELHO": 0, "LARANJA": 10, "VERDE": 120}
    return tempos.get(cor, 60)