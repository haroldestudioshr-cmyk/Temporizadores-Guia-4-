import tkinter as tk
import random
import time
from pathlib import Path


# Definicion de parametros globales para la carrera
CANTIDAD_VEHICULOS = 10
SALIDA = 70
META = 675
PASO = 0.02
INTERVALO_MIN = 20
INTERVALO_MAX = 80
COLOR_FONDO = "mediumpurple4"
COLOR_PANEL = "purple4"
COLOR_PISTA = "darkorchid4"
COLOR_BOTON = "mediumpurple"
COLOR_BOTON_ACTIVO = "mediumpurple1"
COLORES_VEHICULOS = [
    "red", "deepskyblue", "gold", "limegreen", "orange",
    "hotpink", "cyan", "white", "black", "gray",
]

posiciones = [0.0] * CANTIDAD_VEHICULOS
direcciones = [1] * CANTIDAD_VEHICULOS
intervalos = [INTERVALO_MAX] * CANTIDAD_VEHICULOS
rondas_hechas = [0] * CANTIDAD_VEHICULOS
timers = [None] * CANTIDAD_VEHICULOS
ids_vehiculos = []
tiempos = {}
carrera_en_curso = False
vehiculo_apostado = 1
rondas_totales = 1
factor_velocidad = 1.0
tiempo_inicio = 0.0

ventana = tk.Tk()
ventana.title("Carrera de 10 vehículos")
ventana.geometry("1100x750")
ventana.configure(bg=COLOR_FONDO)


def crear_vehiculo(color):
    imagen = tk.PhotoImage(width=50, height=25)
    imagen.put(color, to=(5, 8, 45, 18))
    imagen.put(color, to=(15, 3, 35, 10))
    imagen.put("lightblue", to=(18, 4, 24, 9))
    imagen.put("lightblue", to=(26, 4, 32, 9))
    imagen.put("black", to=(10, 17, 18, 24))
    imagen.put("black", to=(34, 17, 42, 24))
    return imagen


imagenes_vehiculos = [crear_vehiculo(color) for color in COLORES_VEHICULOS]

encabezado = tk.Frame(ventana, bg=COLOR_FONDO)
encabezado.pack(fill="x", padx=12, pady=10)
encabezado.grid_columnconfigure(0, weight=1)
encabezado.grid_columnconfigure(2, weight=1)

titulo = tk.Label(
    encabezado,
    text="CARRERA DE 10 VEHÍCULOS",
    font=("Arial", 20, "bold"),
    bg=COLOR_FONDO,
    fg="white",
)
titulo.grid(row=0, column=1)

try:
    icono_umnges = tk.PhotoImage(file=str(Path(__file__).with_name("umnges.png")))
    tk.Label(encabezado, image=icono_umnges, bg=COLOR_FONDO).grid(
        row=0, column=2, sticky="e", padx=5
    )
except tk.TclError:
    pass

opciones = tk.Frame(ventana, bg=COLOR_FONDO)
opciones.pack(pady=5)

for texto, columna in (("Apuesta:", 0), ("Rondas:", 2), ("Velocidad:", 4)):
    tk.Label(
        opciones, text=texto, bg=COLOR_FONDO, fg="white"
    ).grid(row=0, column=columna, padx=5)

selector_apuesta = tk.Spinbox(
    opciones, from_=1, to=10, width=5, bg=COLOR_PANEL, fg="white",
    buttonbackground=COLOR_BOTON, insertbackground="white",
)
selector_apuesta.grid(row=0, column=1, padx=5)

selector_rondas = tk.Spinbox(
    opciones, from_=1, to=10, width=5, bg=COLOR_PANEL, fg="white",
    buttonbackground=COLOR_BOTON, insertbackground="white",
)
selector_rondas.grid(row=0, column=3, padx=5)


def cambiar_velocidad(valor):
    global factor_velocidad
    factor_velocidad = float(valor)


slider_velocidad = tk.Scale(
    opciones,
    from_=1,
    to=5,
    orient="horizontal",
    length=150,
    command=cambiar_velocidad,
    bg=COLOR_FONDO,
    fg="white",
    troughcolor=COLOR_BOTON,
    activebackground=COLOR_BOTON_ACTIVO,
    highlightthickness=0,
)
slider_velocidad.set(1)
slider_velocidad.grid(row=0, column=5, padx=5)

contenido = tk.Frame(ventana, bg=COLOR_FONDO)
contenido.pack(fill="both", expand=True, padx=10, pady=10)

canvas_pista = tk.Canvas(
    contenido,
    width=740,
    height=430,
    bg=COLOR_PISTA,
    highlightthickness=0,
)
canvas_pista.grid(row=0, column=0, padx=(0, 10), sticky="n")

panel_lateral = tk.Frame(contenido, bg=COLOR_FONDO, width=320)
panel_lateral.grid(row=0, column=1, sticky="n")
panel_lateral.grid_propagate(False)

panel_resultados = tk.Frame(panel_lateral, bg=COLOR_FONDO)
panel_resultados.pack(pady=5)


# ----- DIBUJAR PISTA Y VEHICULOS -----
def dibujar_pista():
    global ids_vehiculos
    canvas_pista.delete("all")
    canvas_pista.create_line(SALIDA, 20, SALIDA, 400, fill="white", width=4)
    canvas_pista.create_line(META, 20, META, 400, fill="white", width=4)
    canvas_pista.create_text(SALIDA, 10, text="SALIDA", fill="white")
    canvas_pista.create_text(META, 10, text="META", fill="white")
    ids_vehiculos = []

    for indice in range(CANTIDAD_VEHICULOS):
        posicion_y = 40 + indice * 35
        canvas_pista.create_line(
            SALIDA, posicion_y + 20, META, posicion_y + 20,
            fill="thistle",
        )
        canvas_pista.create_text(
            30, posicion_y + 10, text=str(indice + 1), fill="white"
        )
        posicion_x = SALIDA + posiciones[indice] * (META - SALIDA)
        ids_vehiculos.append(
            canvas_pista.create_image(
                posicion_x, posicion_y + 10, image=imagenes_vehiculos[indice]
            )
        )


def mover_imagen(indice):
    posicion_x = SALIDA + posiciones[indice] * (META - SALIDA)
    posicion_y = 40 + indice * 35 + 10
    canvas_pista.coords(ids_vehiculos[indice], posicion_x, posicion_y)


def intervalo_aleatorio():
    return random.randint(INTERVALO_MIN, INTERVALO_MAX)


# Logica principal de movimiento por cada vehiculo
def mover_vehiculo(numero):
    global carrera_en_curso
    indice = numero - 1
    if not carrera_en_curso:
        return

    posiciones[indice] += direcciones[indice] * PASO
    terminado = False

    if posiciones[indice] >= 1.0:
        posiciones[indice] = 1.0
        direcciones[indice] = -1
        intervalos[indice] = intervalo_aleatorio()
    elif posiciones[indice] <= 0.0:
        posiciones[indice] = 0.0
        rondas_hechas[indice] += 1
        if rondas_hechas[indice] >= rondas_totales:
            terminado = True
        else:
            direcciones[indice] = 1
            intervalos[indice] = intervalo_aleatorio()

    mover_imagen(indice)

    if terminado:
        tiempos[numero] = time.perf_counter() - tiempo_inicio
        timers[indice] = None
        if len(tiempos) == CANTIDAD_VEHICULOS:
            carrera_en_curso = False
            mostrar_resultados()
        return

    espera = max(1, int(intervalos[indice] / factor_velocidad))
    timers[indice] = ventana.after(espera, mover_vehiculo, numero)


def cancelar_timers():
    for indice in range(CANTIDAD_VEHICULOS):
        if timers[indice] is not None:
            ventana.after_cancel(timers[indice])
            timers[indice] = None


def iniciar_carrera():
    global vehiculo_apostado, carrera_en_curso, rondas_totales, tiempo_inicio

    if carrera_en_curso:
        return
    try:
        apuesta_nueva = int(selector_apuesta.get())
        rondas_nuevas = int(selector_rondas.get())
    except ValueError:
        etiqueta_estado.config(text="Ingresa numeros validos para la apuesta y las rondas.")
        return
    
    if not 1 <= apuesta_nueva <= CANTIDAD_VEHICULOS:
        etiqueta_estado.config(text="La apuesta debe estar entre 1 y 10.")
        return
    if rondas_nuevas < 1:
        etiqueta_estado.config(text="Las rondas deben ser 1 o más.")
        return

    reiniciar_valores()
    vehiculo_apostado = apuesta_nueva
    rondas_totales = rondas_nuevas
    carrera_en_curso = True
    tiempo_inicio = time.perf_counter()
    etiqueta_estado.config(text="¡Carrera en curso!")

    for numero in range(1, CANTIDAD_VEHICULOS + 1):
        intervalos[numero - 1] = intervalo_aleatorio()
        espera = max(1, int(intervalos[numero - 1] / factor_velocidad))
        timers[numero - 1] = ventana.after(espera, mover_vehiculo, numero)

    boton_iniciar.config(state="disabled")
    selector_apuesta.config(state="disabled")
    selector_rondas.config(state="disabled")


def reiniciar_valores():
    global posiciones, direcciones, rondas_hechas, tiempos, carrera_en_curso
    carrera_en_curso = False
    cancelar_timers()
    posiciones = [0.0] * CANTIDAD_VEHICULOS
    direcciones = [1] * CANTIDAD_VEHICULOS
    rondas_hechas = [0] * CANTIDAD_VEHICULOS
    tiempos = {}
    for componente in panel_resultados.winfo_children():
        componente.destroy()
    dibujar_pista()


def reiniciar_carrera():
    reiniciar_valores()
    boton_iniciar.config(state="normal")
    selector_apuesta.config(state="normal")
    selector_rondas.config(state="normal")
    etiqueta_estado.config(text="Listos en la salida")


# Gestion de resultados finales y apuestas
def mostrar_resultados():
    tk.Label(
        panel_resultados,
        text="RESULTADOS",
        font=("Arial", 14, "bold"),
        bg=COLOR_FONDO,
        fg="white",
    ).grid(row=0, column=0, columnspan=3, pady=5)

    resultados = sorted(tiempos.items(), key=lambda resultado: resultado[1])
    color_fila = "thistle"
    for columna, texto in enumerate(("Posición", "Vehículo", "Tiempo")):
        tk.Label(
            panel_resultados,
            text=texto,
            font=("Arial", 10, "bold"),
            bg=COLOR_PANEL,
            fg="white",
            width=12,
        ).grid(row=1, column=columna)

    for indice, (numero, tiempo_final) in enumerate(resultados):
        valores = (str(indice + 1), f"Vehículo {numero}", f"{tiempo_final:.2f} s")
        for columna, valor in enumerate(valores):
            tk.Label(
                panel_resultados,
                text=valor,
                bg=COLOR_FONDO,
                fg=color_fila,
            ).grid(row=indice + 2, column=columna, pady=1)

    ganador = resultados[0][0]
    if ganador == vehiculo_apostado:
        mensaje = f"¡Ganaste! El vehículo {ganador} fue el ganador."
        color_mensaje = "palegreen"
    else:
        mensaje = f"No acertaste. Ganó el vehículo {ganador}."
        color_mensaje = "salmon"

    tk.Label(
        panel_resultados,
        text=mensaje,
        font=("Arial", 12, "bold"),
        fg=color_mensaje,
        bg=COLOR_FONDO,
    ).grid(row=len(resultados) + 2, column=0, columnspan=3, pady=10)

    etiqueta_estado.config(text=mensaje)
    boton_iniciar.config(state="normal")
    selector_apuesta.config(state="normal")
    selector_rondas.config(state="normal")


boton_iniciar = tk.Button(
    panel_lateral,
    text="INICIAR CARRERA",
    font=("Arial", 12, "bold"),
    command=iniciar_carrera,
    bg=COLOR_BOTON,
    fg="white",
    activebackground=COLOR_BOTON_ACTIVO,
    activeforeground="white",
    width=20,
    relief="flat",
)
boton_iniciar.pack(pady=5)

boton_reiniciar = tk.Button(
    panel_lateral,
    text="REINICIAR CARRERA",
    font=("Arial", 12, "bold"),
    command=reiniciar_carrera,
    bg=COLOR_BOTON,
    fg="white",
    activebackground=COLOR_BOTON_ACTIVO,
    activeforeground="white",
    width=20,
    relief="flat",
)
boton_reiniciar.pack(pady=5)

etiqueta_estado = tk.Label(
    panel_lateral,
    text="Listos en la salida",
    bg=COLOR_FONDO,
    fg="white",
    font=("Arial", 10),
)
etiqueta_estado.pack(pady=3)

dibujar_pista()

ventana.mainloop()