#!/usr/bin/env bash

# Instala libzbar0 no ambiente de execução
sudo apt-get update && sudo apt-get install -y libzbar0

# Inicia a aplicação
uvicorn main:app --host 0.0.0.0 --port 8000
