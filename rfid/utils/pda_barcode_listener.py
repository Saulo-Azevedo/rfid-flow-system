import subprocess
import time
import xml.etree.ElementTree as ET
import requests
from pathlib import Path


# ================================
# CONFIGURAÇÕES
# ================================
URL_API = "http://127.0.0.1:8000/api/barcode/registrar/"
DUMP_PATH = "/sdcard/rfid_panel.xml"

# Agora capturamos APENAS o campo confiável:
TARGET_RESOURCE_ID = "com.saulo.rfidpanel:id/textLastCode"
TARGET_CLASS = "android.widget.TextView"

DUMP_DEBUG = Path("ultimo_dump.xml")
ultimo_valor_enviado = None


# ================================
# ADB WRAPPER
# ================================
def adb(args, capture=False):
    cmd = ["adb"] + args
    if capture:
        return subprocess.check_output(cmd, encoding="utf-8", errors="ignore")
    subprocess.run(cmd)


# ================================
# DUMP XML
# ================================
def dump_xml():
    adb(["shell", "uiautomator", "dump", "--compressed", DUMP_PATH])
    xml = adb(["shell", "cat", DUMP_PATH], capture=True)

    # salva para debug
    try:
        DUMP_DEBUG.write_text(xml, encoding="utf-8")
    except:
        pass

    return xml


# ================================
# EXTRATOR → TEXTO DO textLastCode
# ================================
def extrair_texto(xml):
    try:
        root = ET.fromstring(xml)
    except Exception:
        return None

    for node in root.iter():
        rid = node.attrib.get("resource-id", "")
        cls = node.attrib.get("class", "")

        if rid == TARGET_RESOURCE_ID and cls == TARGET_CLASS:
            valor = node.attrib.get("text", "").strip()
            return valor if valor else None

    return None


# ================================
# LEITURA ESTÁVEL (2 a 4 dumps)
# ================================
def ler_valor_estavel():
    ultimo = None

    for _ in range(4):
        xml = dump_xml()
        valor = extrair_texto(xml)

        print(f"→ Capturado: {valor!r}")  # debug forte no console

        if valor:
            if valor == ultimo:
                return valor  # estabilizado
            ultimo = valor

        time.sleep(0.10)

    return None


# ================================
# ENVIO PARA DJANGO
# ================================
def enviar(valor):
    try:
        resp = requests.post(URL_API, json={"barcode": valor})
        print(f"[API] {resp.status_code} -> {resp.text}")
    except Exception as e:
        print("[ERRO API]:", e)


# ================================
# LOOP PRINCIPAL
# ================================
def main():
    global ultimo_valor_enviado

    print("🔍 Listener iniciado... (Modo textLastCode — Estável)\n")

    while True:
        try:
            valor = ler_valor_estavel()

            if valor and valor != ultimo_valor_enviado:
                print(f"📸 Código detectado: {valor}")
                ultimo_valor_enviado = valor
                enviar(valor)

        except KeyboardInterrupt:
            print("\n🛑 Encerrado manualmente.")
            break
        except Exception as e:
            print("⚠ ERRO:", e)

        time.sleep(0.10)  # segura para evitar spam de dump


if __name__ == "__main__":
    main()
