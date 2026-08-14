# ---------- Base image ----------
# najlepiej wspierany przez biblioteki data engineering,
FROM python:3.10-slim

# ---------- Working directory ----------
# ustawia katalog roboczy
WORKDIR /app

# ---------- Copy dependencies ----------
# Instaluje wszystkie zależności Pythona w kontenerze.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy project files ----------
# --no-cache-dir sprawia, że instalacja jest lżejsza i szybsza.
COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/
COPY data_output/ ./data_output/
COPY images/ ./images/

# ---------- Environment variables ----------
# logi w czasie rzeczywistym
ENV PYTHONUNBUFFERED=1

# ---------- Run tests automatically (optional) ----------
# Uncomment if you want tests to run when building
# RUN pytest --maxfail=1 --disable-warnings -q

# ---------- Default command ----------
CMD ["python", "src/procurement_dataset1.py"]
