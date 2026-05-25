import importlib


def carregar_main(monkeypatch, ambiente):
    monkeypatch.setenv("APP_ENV", ambiente)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    import app.infrastructure.config as config
    import app.main as main

    importlib.reload(config)
    return importlib.reload(main)


def test_swagger_habilitado_em_dev(monkeypatch):
    main = carregar_main(monkeypatch, "DEV")

    assert main.app.docs_url == "/docs"
    assert main.app.redoc_url == "/redoc"
    assert main.app.openapi_url == "/openapi.json"


def test_swagger_desabilitado_em_homol(monkeypatch):
    main = carregar_main(monkeypatch, "HOMOL")

    assert main.app.docs_url is None
    assert main.app.redoc_url is None
    assert main.app.openapi_url is None


def test_inicializacao_cria_tabelas(monkeypatch):
    main = carregar_main(monkeypatch, "DEV")
    executou = {"valor": False}

    def criar_tabelas_fake():
        executou["valor"] = True

    monkeypatch.setattr(main, "criar_tabelas", criar_tabelas_fake)
    main.inicializar_banco()

    assert executou["valor"] is True
