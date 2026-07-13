#!/bin/bash
set -e

# === Bot Telegram Enlaces - Setup para Linux ===
# Ejecutar como root: sudo bash setup-linux.sh

DEST=/opt/bot-enlaces

echo "[1/5] Creando directorio $DEST..."
mkdir -p "$DEST"

echo "[2/5] Copiando archivos..."
cp main.py config.py state.py monitor.py capture.py bot.py scheduler.py requirements.txt "$DEST/"
cp .env "$DEST/"

echo "[3/5] Creando entorno virtual..."
python3 -m venv "$DEST/venv"
source "$DEST/venv/bin/activate"
pip install -r "$DEST/requirements.txt"
deactivate

echo "[4/5] Instalando servicio systemd..."
cp bot-enlaces.service /etc/systemd/system/bot-enlaces.service
systemctl daemon-reload
systemctl enable bot-enlaces
systemctl start bot-enlaces

echo "[5/5] Estado del servicio:"
systemctl status bot-enlaces --no-pager

echo ""
echo "=== Instalacion completada ==="
echo "Ver logs: journalctl -u bot-enlaces -f"
echo "Reinicar: systemctl restart bot-enlaces"
echo "Detener:  systemctl stop bot-enlaces"
