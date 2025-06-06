from fastapi import FastAPI

app = FastAPI()

@app.get("/testando/{texto}")
def teste(texto):
    return f'teste foi: {texto}'
