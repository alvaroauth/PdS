from web import create_app

app = create_app(env="test")
client = app.test_client()


def test_home():
    response = client.get("/")
    assert b"<h1>Inicio</h1>" in response.data


def test_issues_index():
    response = client.get("/consultas/")
    assert b"<h1>Consultas</h1>" in response.data
