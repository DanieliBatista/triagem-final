import importlib


def carregar_main(monkeypatch, ambiente):
    monkeypatch.setenv("APP_ENV", ambiente)

    import app.infrastructure.config as config
    import app.main as main

    importlib.reload(config)
    return importlib.reload(main)


def test_swagger_habilitado_em_dev(monkeypatch):
    main = carregar_main(monkeypatch, "DEV")

    assert main.app.docs_url == "/docs"
    assert main.app.redoc_url == "/redoc"
    assert main.app.openapi_url == "/openapi.json"
    assert main.root()["endpoints"]["api_docs"] == "/docs"


def test_swagger_desabilitado_em_homol(monkeypatch):
    main = carregar_main(monkeypatch, "HOMOL")

    assert main.app.docs_url is None
    assert main.app.redoc_url is None
    assert main.app.openapi_url is None
    assert "api_docs" not in main.root()["endpoints"]
