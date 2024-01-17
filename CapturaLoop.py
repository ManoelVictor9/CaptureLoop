# captura contínua alterando a primeira após chegar no limite do contador.


from pypylon import pylon
import cv2
import numpy as np

# Conectando à primeira câmera disponível
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Tentar obter a largura e a altura máximas de maneira alternativa
try:
    camera.Open()
    camera.WidthMax.SetValue(camera.WidthMax.GetMax())
    camera.HeightMax.SetValue(camera.HeightMax.GetMax())
except Exception as e:
    print(f"Erro ao definir a largura e a altura da câmera: {e}")
finally:
    camera.Close()

# Capturando continuamente (vídeo) com o mínimo de atraso
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# Convertendo para o formato OpenCV BGR
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Número de imagens a serem exibidas
num_images = 4

# Lista para armazenar as imagens redimensionadas
resized_images = []

# Flag para indicar se a captura deve ser feita
capture_flag = False

# Índice da imagem atual no loop contínuo
current_image_index = 0

# Obter as dimensões desejadas
screen_width, screen_height = 1300, 760

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Acessando os dados da imagem
        image = converter.Convert(grabResult)
        img = image.GetArray()

        if capture_flag:
            if len(resized_images) < num_images:
                resized_images.append(img.copy())
            else:
                resized_images[current_image_index] = img.copy()
                current_image_index = (current_image_index + 1) % num_images
            capture_flag = False

        # Exibe a imagem atual nos quadrantes correspondentes
        combined_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        for i in range(len(resized_images)):
            h, w, _ = resized_images[i].shape
            h_ratio = screen_height // 2
            w_ratio = screen_width // 2
            row = i // 2
            col = i % 2

            # Redimensionar a imagem para se ajustar ao quadrante sem cortar
            resized_images[i] = cv2.resize(resized_images[i], (w_ratio, h_ratio))

            combined_image[row * h_ratio : (row + 1) * h_ratio, col * w_ratio : (col + 1) * w_ratio, :] = resized_images[i]

        # Exibindo o frame combinado
        cv2.imshow('Combined Images', combined_image)

    grabResult.Release()

    key = cv2.waitKey(1)
    if key == 27:  # Tecla 'esc' para sair
        break
    elif key == ord(' '):  # Tecla de espaço para capturar a próxima imagem
        capture_flag = True

# Liberando os recursos
camera.StopGrabbing()

# Aguardando a tecla 'esc' para fechar a janela
cv2.waitKey(0)
cv2.destroyAllWindows()
