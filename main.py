from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re
from pdf2image import convert_from_path
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import io
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
    # Function to extract data from the uploaded PDF
    def extrair_dados_pdf(arquivo_pdf):
        valor_a_pagar = "N/D"
        vencimento_pdf = "N/D"
        try:
            with pdfplumber.open(arquivo_pdf) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
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

    # Convert PDF to images
    def converter_pdf_para_imagem(arquivo_pdf):
        try:
            imagens = convert_from_path(arquivo_pdf, 500)
            return imagens
        except Exception as e:
            print(f"Erro ao converter PDF para imagem: {e}")
            return []

    # Extract QR code from images
    def extrair_qrcode(imagens):
        for img in imagens:
            img_cv = np.array(img)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            decoded_objects = decode(img_cv)
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                return qr_data
        return None

    # Read the PDF file from the uploaded file
    pdf_bytes = await file.read()

    # Convert the PDF to a BytesIO object to be processed by pdfplumber and pdf2image
    pdf_io = io.BytesIO(pdf_bytes)

    # Extract data from the PDF
    valor_a_pagar_pdf, vencimento_pdf = extrair_dados_pdf(pdf_io)

    # Convert PDF to images
    imagens = converter_pdf_para_imagem(pdf_io)

    # Extract QR code data from images
    qr_data = extrair_qrcode(imagens)

    # Return the extracted data as a JSON response
    return {
        "valor_a_pagar": valor_a_pagar_pdf,
        "vencimento": vencimento_pdf,
        "qr_code": qr_data if qr_data else "QR Code não encontrado"
    }
