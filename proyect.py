import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk 

class EditorImagen:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imágenes")
        self.original_image = None
        self.edited_image = None
        self.history = []

        self.canvas = tk.Canvas(root, width=800, height=600, bg="gray")
        self.canvas.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        botones = [
            ("Abrir", self.abrir_imagen),
            ("Guardar", self.guardar_imagen),
            ("Deshacer", self.deshacer),
            ("Recortar", self.recortar),
            ("Redimensionar", self.redimensionar),
            ("Trasladar", self.trasladar),
            ("Rotar", self.rotar),
            ("Reflejar", self.reflejar),
            ("Ecualizar", self.ecualizar),
            ("Suavizar", self.suavizar)
        ]

        for (texto, comando) in botones:
            tk.Button(btn_frame, text=texto, command=comando, width=12).pack(side=tk.LEFT, padx=2, pady=5)

    def mostrar_imagen(self):
        if self.edited_image is not None:
            rgb_image = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_image)
            img.thumbnail((800, 600))
            self.tk_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def abrir_imagen(self):
        path = filedialog.askopenfilename()
        if path:
            self.original_image = cv2.imread(path)
            self.edited_image = self.original_image.copy()
            self.history.clear()
            self.mostrar_imagen()

    def guardar_imagen(self):
        if self.edited_image is not None:
            path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if path:
                cv2.imwrite(path, self.edited_image)
                messagebox.showinfo("Guardado", "Imagen guardada con éxito.")

    def deshacer(self):
        if self.history:
            self.edited_image = self.history.pop()
            self.mostrar_imagen()

    def guardar_estado(self):
        if self.edited_image is not None:
            self.history.append(self.edited_image.copy())

    def recortar(self):
        if self.edited_image is not None:
            x1 = simpledialog.askinteger("Recorte", "x1:")
            y1 = simpledialog.askinteger("Recorte", "y1:")
            x2 = simpledialog.askinteger("Recorte", "x2:")
            y2 = simpledialog.askinteger("Recorte", "y2:")
            if None not in (x1, y1, x2, y2):
                self.guardar_estado()
                self.edited_image = self.edited_image[y1:y2, x1:x2]
                self.mostrar_imagen()

    def redimensionar(self):
        if self.edited_image is not None:
            ancho = simpledialog.askinteger("Redimensionar", "Nuevo ancho:")
            alto = simpledialog.askinteger("Redimensionar", "Nuevo alto:")
            if ancho and alto:
                self.guardar_estado()
                self.edited_image = cv2.resize(self.edited_image, (ancho, alto))
                self.mostrar_imagen()

    def trasladar(self):
        if self.edited_image is not None:
            dx = simpledialog.askinteger("Trasladar", "Desplazamiento X:")
            dy = simpledialog.askinteger("Trasladar", "Desplazamiento Y:")
            if dx is not None and dy is not None:
                self.guardar_estado()
                M = np.float32([[1, 0, dx], [0, 1, dy]])
                filas, cols = self.edited_image.shape[:2]
                self.edited_image = cv2.warpAffine(self.edited_image, M, (cols, filas))
                self.mostrar_imagen()

    def rotar(self):
        if self.edited_image is not None:
            angulo = simpledialog.askfloat("Rotar", "Ángulo de rotación:")
            if angulo is not None:
                self.guardar_estado()
                (h, w) = self.edited_image.shape[:2]
                centro = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(centro, angulo, 1.0)
                self.edited_image = cv2.warpAffine(self.edited_image, M, (w, h))
                self.mostrar_imagen()

    def reflejar(self):
        if self.edited_image is not None:
            
            top = tk.Toplevel(self.root)
            top.title("Reflejar Imagen")
            
            tk.Label(top, text="Selecciona modo de reflejo:").pack(pady=10)
            
            opciones = ["horizontal", "vertical", "ambos"]
            seleccion = tk.StringVar(top)
            seleccion.set(opciones[0])

            menu = tk.OptionMenu(top, seleccion, *opciones)
            menu.pack(pady=5)

            def aplicar_reflejo():
                modo = seleccion.get()
                self.guardar_estado()
                if modo == "horizontal":
                    self.edited_image = cv2.flip(self.edited_image, 1)
                elif modo == "vertical":
                    self.edited_image = cv2.flip(self.edited_image, 0)
                elif modo == "ambos":
                    self.edited_image = cv2.flip(self.edited_image, -1)
                self.mostrar_imagen()
                top.destroy()

            tk.Button(top, text="Aplicar", command=aplicar_reflejo).pack(pady=10)


    def ecualizar(self):
        if self.edited_image is not None:
            self.guardar_estado()
            canales = cv2.split(self.edited_image)
            ecualizados = [cv2.equalizeHist(cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2GRAY))]
            if len(canales) == 3:
                canales_eq = [cv2.equalizeHist(c) for c in canales]
                self.edited_image = cv2.merge(canales_eq)
            self.mostrar_imagen()

    def suavizar(self):
        if self.edited_image is not None:
            top = tk.Toplevel(self.root)
            top.title("Suavizar Imagen")

            tk.Label(top, text="Selecciona tipo de suavizado:").pack(pady=10)

            opciones = ["promedio", "gaussiano", "mediana", "bilateral"]
            seleccion = tk.StringVar(top)
            seleccion.set(opciones[0])

            menu = tk.OptionMenu(top, seleccion, *opciones)
            menu.pack(pady=5)

            def aplicar_suavizado():
                tipo = seleccion.get()
                funciones = {
                    "promedio": lambda img: cv2.blur(img, (5, 5)),
                    "gaussiano": lambda img: cv2.GaussianBlur(img, (5, 5), 0),
                    "mediana": lambda img: cv2.medianBlur(img, 5),
                    "bilateral": lambda img: cv2.bilateralFilter(img, 9, 75, 75)
                }
                self.guardar_estado()
                self.edited_image = funciones[tipo](self.edited_image)
                self.mostrar_imagen()
                top.destroy()

            tk.Button(top, text="Aplicar", command=aplicar_suavizado).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorImagen(root)
    root.mainloop()
