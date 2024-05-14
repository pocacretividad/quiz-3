from clases import GestionImagenes

gestor_imagenes = GestionImagenes()

def main():
    while True:
        print('''
                            Menú:
            1. Ingresar paciente desde archivos DICOM")
            2. Ingresar imágenes JPG o PNG")
            3. Rotar imagen DICOM")
            4. Binarizar y aplicar transformación morfológica a imagen JPG/PNG")
            5. Salir
        ''')

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ruta_carpeta = input("Ingrese la ruta de la carpeta DICOM: ")
            for paciente in gestor_imagenes.cargar_dicom(ruta_carpeta):
                print(f"Paciente: {paciente.nombre}, ID: {paciente.identificacion}")
                ruta_salida = f"nifti_{paciente.identificacion}.nii"
                nifti_ruta = gestor_imagenes.convertir_dicom_a_nifti(paciente.identificacion, ruta_salida)
                if nifti_ruta:
                    print(f"Imagen DICOM convertida a NIfTI: {nifti_ruta}")

        elif opcion == "2":
            ruta_carpeta = input("Ingrese la ruta de la carpeta de imágenes JPG/PNG: ")
            for ruta_img in gestor_imagenes.cargar_jpg_png(ruta_carpeta):
                print(f"Imagen: {ruta_img} guardada ")

        elif opcion == "3":
            id_paciente = input("Ingrese el ID del paciente: ")
            grados = int(input("Ingrese el ángulo de rotación (90, 180, 270): "))
            gestor_imagenes.rotar_imagen_dicom(id_paciente, grados)

        elif opcion == "4":
            ruta_img = input("Ingrese la ruta de la imagen JPG/PNG: ")
            umbral = int(input("Ingrese el umbral de binarización: "))
            tam_kernel = int(input("Ingrese el tamaño del kernel para la morfología: "))
            gestor_imagenes.binarizar_y_texto(ruta_img, umbral, tam_kernel)

        elif opcion == "5":
            print("Saliendo")
            break

        else:
            print("Opción inválida. Intente de nuevo.")


if __name__ == "__main__":
    main()