FROM python:3.9

# Instalar dependências do sistema necessárias para o OpenCV e o Poppler
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libglib2.0-dev \
    libgl1 \
    zbar-tools \
    poppler-utils  # Instala o Poppler

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos da aplicação para o contêiner
COPY . /app

# Instalar as dependências do Python
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expor a porta 8000
EXPOSE 8000

# Rodar o servidor FastAPI com uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
