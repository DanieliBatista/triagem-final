"""Exceções do domain"""


class DomainException(Exception):
    """Exceção base do domain"""
    pass


class ValidacaoBiologicaException(DomainException):
    """Exceção para dados vitais fora dos limites humanamente possíveis"""
    pass


class ClassificacaoNaoEncontradaException(DomainException):
    """Exceção quando classificação não existe"""
    pass


class PermissaoNegadaException(DomainException):
    """Exceção quando usuário sem permissão tenta ação"""
    pass


class JustificativaObrigatoriaException(DomainException):
    """Exceção quando justificativa é obrigatória mas não foi fornecida"""
    pass
