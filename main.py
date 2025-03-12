import tempfile 
import os
import io
from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re
from pdf2image import convert_from_bytes, convert_from_path
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/processar-pdf/")
async def processar_pdf(file: UploadFile = File(...)):
    # Função para extrair o valor a pagar e o vencimento do PDF
    def extrair_dados_pdf(arquivo_pdf):
        valor_a_pagar = "N/D"
        vencimento_pdf = "N/D"
        try:
            with pdfplumber.open(arquivo_pdf) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    print(f"Texto extraído: {texto}")  # Verifique se está extraindo o texto corretamente
                    if texto:
                        match_valor_a_pagar = re.search(
                            r"(?i)(valor\s*a\s*pagar)[:\s]*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})", texto)
                        if match_valor_a_pagar:
                            valor_a_pagar = f"R$ {match_valor_a_pagar.group(2)}"
                        match_vencimento = re.search(r"(?i)(vencimento)[:\s]*(\d{2}/\d{2}/\d{4})", texto)
                        if match_vencimento:
                            vencimento_pdf = match_vencimento.group(2).strip()
        except Exception as e:
            print(f"Erro ao extrair dados do PDF: {e}")
        return valor_a_pagar, vencimento_pdf


    # Função para converter PDF em imagens
    def converter_pdf_para_imagem(arquivo_pdf):
        try:
            # Convertendo o conteúdo do arquivo PDF para bytes usando getvalue()
            arquivo_pdf_bytes = arquivo_pdf.getvalue()
            imagens = convert_from_bytes(arquivo_pdf_bytes, dpi=300)  # Usando os bytes diretamente
            return imagens
        except Exception as e:
            print(f"Erro ao converter PDF para imagem: {e}")
            return []


    # Função para extrair QR Code das imagens
    def extrair_qrcode(imagens):
        for img in imagens:
            img_cv = np.array(img)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            decoded_objects = decode(img_cv)
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                return qr_data
        return None

    # Lendo o arquivo PDF enviado
    pdf_bytes = await file.read()
    pdf_io = io.BytesIO(pdf_bytes)

    # Extraindo dados do PDF
    valor_a_pagar_pdf, vencimento_pdf = extrair_dados_pdf(pdf_io)

    # Convertendo PDF para imagens
    imagens_pdf = converter_pdf_para_imagem(pdf_io)

    # Extraindo QR Code
    qr_data = extrair_qrcode(imagens_pdf)

    if qr_data:
        print(f"QR Code encontrado: {qr_data}")
    else:
        print("QR Code não encontrado na imagem.")

    return {
        "valor_a_pagar": valor_a_pagar_pdf,
        "vencimento": vencimento_pdf,
        "qr_code": qr_data if qr_data else "QR Code não encontrado"
    }
