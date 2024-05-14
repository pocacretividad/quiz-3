import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import nibabel as nib


class Paciente:
    def __init__(self, nombre, edad, identificacion, imagen_nifti):
        self.nombre = nombre
        self.edad = edad
        self.identificacion = identificacion
        self.imagen_nifti = imagen_nifti


class GestionImagenes:
    def __init__(self):
        self.archivos_dicom = {}
        self.archivos_jpg_png = {}

    def cargar_dicom(self, ruta_carpeta):
        for raiz, ruta ,archivos in os.walk(ruta_carpeta):
            for archivo in archivos:
                if archivo.endswith(".dcm"):
                    ruta_dcm = os.path.join(raiz, archivo)
                    ds = pydicom.dcmread(ruta_dcm)
                    info_paciente = {
                        "nombre": ds.PatientName,
                        "edad": ds.PatientAge,
                        "identificacion": ds.PatientID,
                        "imagen_nifti": None
                    }
                    paciente = Paciente(**info_paciente)
                    self.archivos_dicom[ds.PatientID] = ruta_dcm
                    yield paciente

    def convertir_dicom_a_nifti(self, id_paciente, ruta_salida):
        if id_paciente in self.archivos_dicom:
            ruta_dcm = self.archivos_dicom[id_paciente]
            ds = pydicom.dcmread(ruta_dcm)
            img = ds.pixel_array

            orientacion = ds.ImageOrientationPatient
            vect_fila = np.array(orientacion[:3])
            vect_col = np.array(orientacion[3:])
            vect_corte = np.cross(vect_fila, vect_col)

            origen = ds.ImagePositionPatient

            espaciado_pixel = ds.PixelSpacing
            if isinstance(espaciado_pixel, (list, tuple)):
                espaciado_pixel = espaciado_pixel[::-1]  
            matriz_afin = np.zeros((4, 4))
            matriz_afin[:3, 0] = vect_fila * espaciado_pixel[0]
            matriz_afin[:3, 1] = vect_col * espaciado_pixel[1]
            matriz_afin[:3, 2] = vect_corte * ds.SliceThickness
            matriz_afin[:3, 3] = origen
            matriz_afin[3, 3] = 1

            img_nifti = nib.Nifti1Image(img, matriz_afin)
            nib.save(img_nifti, ruta_salida)
            return ruta_salida
        else:
            print(f"No se encontró el paciente con ID {id_paciente}")
            return None

    def cargar_jpg_png(self, ruta_carpeta):
        for raiz, archivos in os.walk(ruta_carpeta):
            for archivo in archivos:
                if archivo.endswith((".jpg", ".jpeg", ".png")):
                    ruta_img = os.path.join(raiz, archivo)
                    img = cv2.imread(ruta_img)
                    self.archivos_jpg_png[archivo] = ruta_img
                    yield ruta_img

    def rotar_imagen_dicom(self, id_paciente, grados):
        if id_paciente in self.archivos_dicom:
            ruta_dcm = self.archivos_dicom[id_paciente]
            ds = pydicom.dcmread(ruta_dcm)
            img = ds.pixel_array
            img_rotada = np.rot90(img, k=grados // 90)
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.imshow(img, cmap='gray')
            plt.title("Imagen Original")
            plt.subplot(1, 2, 2)
            plt.imshow(img_rotada, cmap='gray')
            plt.title("Imagen Rotada")
            plt.show()
            ds.PixelData = img_rotada.tobytes()
            ds.save_as(f"rotated_{os.path.basename(ruta_dcm)}")

    def binarizar_y_texto(self, ruta_img, umbral, tam_kernel):
        img = cv2.imread(ruta_img, cv2.IMREAD_GRAYSCALE)
        binarizada = cv2.threshold(img, umbral, 255, cv2.THRESH_BINARY)
        kernel = np.ones((tam_kernel, tam_kernel), np.uint8)
        morfologia = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel)
        cv2.putText(morfologia, f'Imagen binarizada, umbral: {umbral}, tamaño kernel: {tam_kernel}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(f"binarized_{os.path.basename(ruta_img)}", morfologia)