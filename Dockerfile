# ============================================
# Dockerfile para TikTok Live Overlay
# ============================================
# 
# COMO USAR:
# 1. Build: docker build -t tiktok-overlay .
# 2. Run:   docker run -p 5000:5000 tiktok-overlay
#
# Para alterar o usuário do TikTok, edite main.py
# ou passe como variável de ambiente (requer modificação no código)
# ============================================

# Usa Python 3.11 slim como base (leve e eficiente)
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro
# Isso aproveita o cache do Docker se as dependências não mudarem
COPY requirements.txt .

# Instala as dependências
# --no-cache-dir reduz o tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

# Expõe a porta 5000 (Flask)
EXPOSE 5000

# Comando para iniciar a aplicação
# Usa eventlet como servidor WSGI para melhor performance com Socket.IO
CMD ["python", "main.py"]
