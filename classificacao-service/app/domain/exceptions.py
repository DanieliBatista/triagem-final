class DomainException(Exception):
    pass


class ValidacaoBiologicaException(DomainException):
    pass


class ClassificacaoNaoEncontradaException(DomainException):
    pass


class PermissaoNegadaException(DomainException):
    pass


class JustificativaObrigatoriaException(DomainException):
    pass
