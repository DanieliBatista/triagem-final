# 1. Escolhe uma imagem base oficial do Python (versão slim para ser mais leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Instala dependências de sistema básicas (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copia primeiro apenas o arquivo de requisitos para aproveitar o cache do Docker
COPY requirements.txt .

# 6. Instala as bibliotecas do projeto
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copia todo o conteúdo da sua pasta local para dentro do container
COPY . .

# 8. Informa qual porta o container vai expor (8000 é o padrão do FastAPI)
EXPOSE 8000

# 9. Comando para iniciar a aplicação quando o container subir
# Usamos o host 0.0.0.0 para que o container aceite conexões externas
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]