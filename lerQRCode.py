from pdf2image import convert_from_path  # Converter PDF em imagem
import cv2  # OpenCV para processar imagens
from pyzbar.pyzbar import decode  # Biblioteca para ler QR Code
import numpy as np
from PIL import Image
import pdfplumber  # Biblioteca para extrair texto do PDF
import pyperclip  # Para copiar texto para a área de transferência
import re
import customtkinter as ctk  # Biblioteca para interface moderna
from customtkinter import CTkImage  # Importando CTkImage para imagens de alta resolução

# Caminho do arquivo PDF
arquivo_pdf = 'carne_265.pdf'

# Função para extrair o valor a pagar e vencimento do PDF
def extrair_dados_pdf(arquivo_pdf):
    valor_a_pagar = "N/D"
    vencimento_pdf = "N/D"
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    match_valor_a_pagar = re.search(r"(?i)(valor\s*a\s*pagar)[:\s]*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})", texto)
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
        imagens = convert_from_path(arquivo_pdf, 500)
        return imagens
    except Exception as e:
        print(f"Erro ao converter PDF para imagem: {e}")
        return []

# Função para extrair o QR Code e exibir interface
def extrair_qrcode_e_exibir(imagens, valor_a_pagar_pdf, vencimento_pdf):
    for idx, img in enumerate(imagens):
        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        decoded_objects = decode(img_cv)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            x, y, w, h = obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height
            qr_img = img_cv[y:y+h, x:x+w]
            qr_pil = Image.fromarray(cv2.cvtColor(qr_img, cv2.COLOR_BGR2RGB))
            exibir_interface(qr_pil, qr_data, vencimento_pdf, valor_a_pagar_pdf)
            return
    print("Nenhum QR Code detectado.")

# Função para exibir a interface gráfica
def exibir_interface(qr_pil, qr_data, vencimento_pdf, valor_a_pagar_pdf):
    root = ctk.CTk()
    root.title("IPTU na Mão - São Miguel do Guaporé-RO")

    # Remover bordas e botões de controle da janela
    root.overrideredirect(True)

    # Definir tamanho da janela
    largura_janela = 400
    altura_janela = 500

    # Obter tamanho da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Calcular posição para centralizar a janela
    x_pos = (largura_tela - largura_janela) // 2
    y_pos = (altura_tela - altura_janela) // 2

    # Posicionar e definir tamanho da janela
    root.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

    # Criar os widgets
    lbl_vencimento_pdf = ctk.CTkLabel(root, text=f"VENCIMENTO: {vencimento_pdf}", font=("Arial", 14, "bold"))
    lbl_vencimento_pdf.pack(pady=5)

    lbl_valor_pdf = ctk.CTkLabel(root, text=f"VALOR A PAGAR: {valor_a_pagar_pdf}", font=("Arial", 14, "bold"))
    lbl_valor_pdf.pack(pady=5)

    # Redimensionar QR Code e converter para CTkImage
    qr_ctk_image = CTkImage(light_image=qr_pil, size=(150, 150))
    lbl_img = ctk.CTkLabel(root, image=qr_ctk_image, text="")
    lbl_img.pack(pady=20)

    def copiar_qrcode():
        pyperclip.copy(qr_data)
        print("QR Code copiado para a área de transferência!")

    btn_copiar = ctk.CTkButton(root, text="COPIAR PIX", command=copiar_qrcode,
                               font=("Arial", 16, "bold"), fg_color="#28a745",
                               text_color="white", corner_radius=30, width=200, height=50)
    btn_copiar.pack(pady=10)

    def fechar_janela():
        root.destroy()

    btn_fechar = ctk.CTkButton(root, text="FECHAR JANELA", command=fechar_janela,
                               font=("Arial", 14, "bold"), fg_color="#dc3545",
                               text_color="white", corner_radius=30, width=200, height=50)
    btn_fechar.pack(pady=10)

    root.mainloop()

# Executando as funções
valor_a_pagar_pdf, vencimento_pdf = extrair_dados_pdf(arquivo_pdf)
imagens = converter_pdf_para_imagem(arquivo_pdf)
if imagens:
    extrair_qrcode_e_exibir(imagens, valor_a_pagar_pdf, vencimento_pdf)
else:
    print("Não foi possível converter o PDF para imagens.")
