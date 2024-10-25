
from pickle import FALSE, TRUE
import pygame, sys, math
from modelo import *
from math import *

#Variables:
WINDOW_H = 900
WINDOW_W =  1400
ROTATE_SPEED = 0.02
MAIN_W = WINDOW_W*0.7
PANEL_W = WINDOW_W*0.3
pygame.init()
window = pygame.display.set_mode( (WINDOW_W, WINDOW_H) ) 
surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
background_surface = pygame.Surface((WINDOW_W, WINDOW_H))
clock = pygame.time.Clock()
base_font = pygame.font.Font(None, 24)
label_font = pygame.font.Font(None, 17)
scale = 70
angle_x = angle_y = angle_z = 0
panel_rect = pygame.Rect(MAIN_W, 0, PANEL_W, WINDOW_H)

# Crear el rectángulo del botón y variables de interfaz.
BUTTON_POS = (MAIN_W + 50, 550)
BUTTON_SIZE = (100, 30)
BORDER_COLOR = (0, 0, 0)  # Negro
BUTTON_COLOR = (0, 255, 0)  # Verde
TEXT_COLOR = (0, 0, 0)  # Negro
BORDER_SIZE = 4
RADIUS = 10
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('gray15')
material_text = ""
info_nodo = []
error = ""

# Definir fuente
base_font = pygame.font.SysFont("Arial", 24)

# Configuración del aura
aura_color = (255, 255, 255)  # Blanco
aura_alpha = 128  # Transparencia
aura_active = FALSE
indice_esfera = 0

# Crear una superficie para el aura
aura_surface = pygame.Surface((261 * 2, 261 * 2), pygame.SRCALPHA)
aura_surface.fill((0, 0, 0, 0))  # Transparente

#valor por defecto
gestor_internet = GestorInternet()
edificio = Edificio(gestor_internet)

def draw_rounded_rect(surface, rect, color, border_color, border_size, radius):
    x, y, w, h = rect

    # Dibujar el borde del botón
    pygame.draw.rect(surface, border_color, (x - border_size, y - border_size, w + 2 * border_size, h + 2 * border_size), border_radius=radius)
    
    # Dibujar el botón
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# Método que crea el espectro de un área
def espectro_area(radio):
    
    # Configuración del aura
    aura_radius = radio
    
    # Dibujar la esfera en la superficie
    for y in range(aura_radius * 2):
        for x in range(aura_radius * 2):
            dx = x - aura_radius
            dy = y - aura_radius
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= aura_radius:
                alpha = int((1 - distance / aura_radius) * 255)
                aura_surface.set_at((x, y), (aura_color[0], aura_color[1], aura_color[2], alpha))
                
# Método usado para validar entradas.
def validar_valor(valor, rango, campo):
  
    inicio, fin = rango
    try:
        numero = int(valor)
    except ValueError:
        return "Por favor, ingresa un número válido en el campo, " + campo + "."
    if numero < inicio or numero > fin:
        return "El número debe estar entre " + str(inicio) + " y " + str(fin) + " en el campo, " + campo +"."
    return None

# Clase que maneja los eventos que se activan con cada campo de entrada...
class Input:
    
    def __init__(self, type, labels, rect, active) -> None:
        self.labels = labels
        self.rect = rect
        self.active = active
        self.text = ""
        self.color = color_passive
        self.type = type

    def press_enter(self):
        # Se activa "global", para actualizar mensajes de error.
        global error
        # Por cada evento se han agregado sus respectivas validaciones.
        if self.type == "pisos":
            if validar_valor(self.text, (1,12), "pisos") != None:
                error = validar_valor(self.text, (1,12), "pisos")
            else:
                error = ""
                pisos_points.clear() 
                bordes_points.clear()
                areas_points.clear()
                conexiones.clear()
                edificio.gestor_internet.aps.clear()
                edificio.obtener_areas().clear()
                edificio.set_altura(self.text)
                for ap in edificio.gestor_internet.aps:
                    ap.obtener_areas_que_cubre().clear()
                for i in range(int(self.text) + 1):
                    pisos_points.append([[[0], [int(self.text)/2-i], [0]], (255, 255, 255)])
                    bordes_points.append([
                        [[3],[int(self.text)/2-i],[3]],
                        [[3],[int(self.text)/2-i],[-3]],
                        [[-3],[int(self.text)/2-i],[3]],
                        [[-3],[int(self.text)/2-i],[-3]]
                    ])
                pisos_points.pop(int(self.text))

        elif self.type == "material":
            global material_text 
            materiales= list(map(str.upper, self.text.split()))
            if any(material not in ["CONCRETO", "MADERA"] for material in materiales):
                error = "Entrada equivocada, un material o más no coinciden con los materiales permitidos."
            else:
                error = ""
                edificio.materiales_edificio = [Material[materiales[0]], Material[materiales[1]]]
                material_text = self.text
            
        elif self.type == "ap":
            try:
                piso, tipo_ap_ind = map(int, self.text.split())
                if validar_valor(str(piso), (0,edificio.obtener_altura()), "piso") != None:
                    error = validar_valor(str(piso), (0,edificio.obtener_altura()), "piso")
                elif validar_valor(str(tipo_ap_ind), (1,2), "tipo_ap") != None:
                    error = validar_valor(str(tipo_ap_ind), (1,2), "tipo_ap")    
                else:
                    error = ""
                    pisos_points[piso-1][1] = (255,1,0)
                    ap = Ap(tipo_ap_ind, piso,len(gestor_internet.aps)+1)
                    gestor_internet.aps.append(ap)
            except ValueError as e:
                error = "Faltan valores en la entrada..."
            
        elif self.type == "area":
            try:
                piso, x, y, actividad, personas = self.text.split()
                if validar_valor(str(piso), (0,edificio.obtener_altura()), "piso") != None:
                    error = validar_valor(str(piso), (0,edificio.obtener_altura()), "piso")
                elif validar_valor(str(x), (-10,10), "coordenada x") != None:
                   error = validar_valor(str(x), (-10,10), "coordenada x")
                elif validar_valor(str(y), (-10,10), "coordenada y") != None:
                   error = validar_valor(str(y), (-10,10), "coordenada y")
                elif validar_valor(str(personas), (1,100), "personas") != None:
                   error = validar_valor(str(personas), (1,100), "personas")
                elif actividad != "EMAIL_WEB" and actividad != "STREAMING":
                    error = "Entrada equivocada: debe ser EMAIL_WEB o STREAMING, en el campo actividad."
                else:
                    #Suponiendo que cada piso tiene 3 metros, y 3 metros esta representado como 1 (la unidad del piso)
                    #Recalculamos x y 
                    x = int(x)
                    y = int(y)
                    x /= 3
                    y /= 3
                    area = Area(actividad, int(piso), x, y, (0, 255, 0),len(edificio.obtener_areas())+1, int(personas))
                    edificio.agregar_area(area)
                    error = ""
                    areas_points.append([[[x], [len(pisos_points)/2-(int(piso)-1)] ,[y]], area.color])
            except ValueError as e:
                error = "Faltan valores en la entrada..."
            
        
        elif self.type == "configurar":
            try:
                area, potencia, personas = self.text.split()
                if validar_valor(str(area), (1,len(edificio.obtener_areas())), "área") != None:
                    error = validar_valor(str(area), (1,len(edificio.obtener_areas())), "área")
                elif validar_valor(str(personas), (1,100), "personas") != None:
                   error = validar_valor(str(personas), (1,100), "personas")
                elif potencia != "EMAIL_WEB" and potencia != "STREAMING":
                    error = "Entrada equivocada: debe ser EMAIL_WEB o STREAMING, en el campo potencia."
                else:
                    area = int(area)
                    personas = int(personas)
                    potencia = potencia
                    cambiar_config(area-1, potencia, personas)

            except ValueError as e:
                error = "Faltan valores en la entrada..."
            
                     
def generar_conexion():
    conexiones.clear()
    for area in edificio.obtener_areas():
        if not area.hab and area.opcion == 1:
            #Se cambia el color a rojo cuando no hay habitabilidad favorable (señal desfavorable)...
            idx = edificio.obtener_areas().index(area)
            area_point = areas_points[idx]    
            area_point[1] = (255,0,0)
        if not area.hab and area.opcion == 2:
            #Se cambia el color a amarillo cuando no hay habitabilidad favorable (falta de ancho de banda)...
            idx = edificio.obtener_areas().index(area)
            area_point = areas_points[idx]    
            area_point[1] = (204,204 ,0)
    for ap in edificio.gestor_internet.aps:
        piso_point = pisos_points[ap.obtener_piso()-1]
        if len(ap.obtener_areas_que_cubre()) != 0:
            for area in ap.obtener_areas_que_cubre():
                #Se cambia el color a rojo cuando no hay habitabilidad favorable...
                idx = edificio.obtener_areas().index(area)
                area_point = areas_points[idx]
                area_point[1] = (0,255,0)
                conexiones.append([piso_point, area_point])
                
            
inputs = {}
#introducir pisos
pisos = Input("pisos",
              ["Número de pisos"
               #, "Si cambia el número de pisos se reinicia el sistema"
               ],
                 pygame.Rect(MAIN_W+50,60, 140, 32),
                 False) 
inputs["pisos"] = pisos

#cambiar material
material = Input("material",
                 ["Asignar Material Edificio",
                  "input: Pared (CONCRETO, LADRILLO)",
                  "Puerta (VIDRIO, MADERA)",
                  "Ej(CONCRETO MADERA)"],
                 pygame.Rect(MAIN_W+50,180, 140, 32),
                 False)
inputs["material"] = material

#agregar ap
ap = Input("ap",
           ["Agregar Ap",
            "Tipos de ap:",
            "1. 2.4ghz_IEEE802.11.b",
            "2. 5ghz_IEEE802.11.a",
            "input: Piso tipo_ap",
            "Ej(1 2)"],
           pygame.Rect(MAIN_W+50,340, 140, 32),
           False)
inputs["ap"] = ap

#agregar area
area = Input("area",
             ["Agregar Area",
              "actividades: STREAMING / EMAIL_WEB",
              "x y son la coordenada en metros dentro de un cierto piso",
              "número de personas, que define ancho de banda",
              "input: Piso x y  actividad",
              "Ej(1 -1 1 EMAIL_WEB 10)"],
             pygame.Rect(MAIN_W+50,510, 140, 32),
             False)
inputs["area"] = area 

#cambiar flujo de area
configurar = Input("configurar",
             ["Cambiar potencia y ancho de banda del área",
              "Selecciona alguna de las áreas por su índice",
              "y cambie su potencia o ancho para verificar",
              "habitabilidad.",
              "input: número área, actividad Y personas",
              "Ej(1 STREAMING 10)"],
             pygame.Rect(MAIN_W+50,720, 140, 32),
             False)
inputs["configurar"] = configurar

#Algebra
projection_matrix = [[1,0,0],
                     [0,1,0],
                     [0,0,0]] 

# Colecciones necesarias.
pisos_points = []
bordes_points = []
areas_points = []
conexiones = []
habitabilidad = []

def multiply_m(a, b):
    a_rows = len(a)
    a_cols = len(a[0])

    b_rows = len(b)
    b_cols = len(b[0])
    # Dot product matrix dimentions = a_rows x b_cols
    product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]

    if a_cols == b_rows: 
        for i in range(a_rows):
            for j in range(b_cols):
                for k in range(b_rows):
                    product[i][j] += a[i][k] * b[k][j]
    else:
        pass
        #print("INCOMPATIBLE MATRIX SIZES")
    return product 

# Función para configurar un área, cambiando su potencia o modificando su ancho a raíz del número de personas.
def cambiar_config(area_indice, potencia, personas): 
    area = edificio.obtener_area(area_indice)
    area.set_actividad(potencia)
    area.set_anchoBanda(personas)
    area.actualizar_info()
    edificio.configurar_area(area_indice,area)
    # Se realiza la actualización de áreas y conexiones después de realizar un cambio.
    if len(edificio.gestor_internet.aps) != 0:
        edificio.verificar_habitabilidad_areas()
        generar_conexion()
    
# Función para realizar conexiones entre AP's y áreas.
def connect_points(i, j, points, color):
    pygame.draw.line(window, color, (points[i][0], points[i][1]) , (points[j][0], points[j][1]))

# Función para verificar colisiones.
def verify_collide(pos, points):
    x = pos[0]
    y = pos[1]
    for i, point in enumerate(points):
        click = math.sqrt((point[0]-x)**2 + (point[1]-y)**2)
        if click <= 5:
            return i
    
    return -1

# Función encargada de dibujar el edificio.
def draw_edificio_lines(rotation_x, rotation_y, rotation_z):
    
    j=0
    surface.fill((0, 0, 0, 0))
    color_index = 0  # Índice del color actual
    colors = [(102, 51, 0,90), (150, 150, 150,90)]  # Café y gris, respectivamente
    colors1 = [(204, 201, 45, 90), (22, 112, 81, 90)] # Colores de las paredes
    puntos = []
    for conexion in conexiones:
        points = [0 for _ in range(len(conexion))]
        i=0
        for point in conexion:
            point_dim = point[0]
            rotate_x = multiply_m(rotation_x, point_dim)
            rotate_y = multiply_m(rotation_y, rotate_x)
            rotate_z = multiply_m(rotation_z, rotate_y)
            point_2d = multiply_m(projection_matrix, rotate_z)
            
            x = (point_2d[0][0] * scale) + MAIN_W/2
            y = (point_2d[1][0] * scale) + WINDOW_H/2
            
            points[i] = (x,y)
            i += 1
        
        connect_points(0,1, points, (150,150,150))
        
    for bordes in bordes_points:

        points = [0 for _ in range(len(bordes))]
        i = 0
        for point in bordes:
            rotate_x = multiply_m(rotation_x, point)
            rotate_y = multiply_m(rotation_y, rotate_x)
            rotate_z = multiply_m(rotation_z, rotate_y)
            point_2d = multiply_m(projection_matrix, rotate_z)
        
            x = (point_2d[0][0] * scale) + MAIN_W/2
            y = (point_2d[1][0] * scale) + WINDOW_H/2

            points[i] = (x,y)
            i += 1
        
        # Ordenar los puntos para formar un rectángulo
        # Asumiendo que son los puntos de un rectángulo    
        ordered_points = [points[0], points[1], points[3], points[2]]
        # Guarda todos los puntos para crear las paredes de un piso
        puntos.append(points[0])
        puntos.append(points[1])
        puntos.append(points[2])
        puntos.append(points[3])
        # Cuando tiene todos los vertices del edificio, (esquinas), calcula cuales son las que deben estar unidas por una pared, simepre que existan
        # más de dos pisos...
        if len(puntos) > 4:
            pygame.draw.polygon(surface, colors1[color_index], (puntos[j], puntos[j+4], puntos[j+5] ,puntos[j+1]))
            pygame.draw.polygon(surface, colors1[color_index], (puntos[j+3], puntos[j+7], puntos[j+6] ,puntos[j+2]))
            j +=4
        pygame.draw.polygon(surface, colors[color_index], ordered_points)
        # Alternar entre los dos colores
        color_index = (color_index + 1) % len(colors)
        


# Main Loop
while True:
    clock.tick(60)
    window.fill((0,0,0))
    window.blit(background_surface, (0, 0))
    window.blit(surface, (0,0))

    #Panel:
    pygame.draw.rect(window, (50, 50, 50), panel_rect)
    #Material text
    text_surface_mat = base_font.render("MATERIALES EDIFICIO: "+material_text, True, (255,255,255))
    window.blit(text_surface_mat, (30, WINDOW_H-20))
    #Agregar explicación
    text_surface_exp_1 = base_font.render("Introduce los datos separados por espacio", True, (255,90,80))
    window.blit(text_surface_exp_1, (MAIN_W+50, 5))
    text_surface_exp_2 = base_font.render("Para confirmar el input dale ENTER", True, (255,90,80))
    window.blit(text_surface_exp_2, (MAIN_W+50, 30))
    
    #Grafo
    rotation_x = [[1, 0, 0], 
                    [0, cos(angle_x), -sin(angle_x)],
                    [0, sin(angle_x), cos(angle_x)]]

    rotation_y = [[cos(angle_y), 0, sin(angle_y)],
                    [0, 1, 0],
                    [-sin(angle_y), 0, cos(angle_y)]]

    rotation_z = [[cos(angle_z), -sin(angle_z), 0],
                    [sin(angle_z), cos(angle_z), 0],
                    [0, 0, 1]]

    points = [0 for _ in range(len(pisos_points)+len(areas_points))]
    i = 0
    for point in pisos_points + areas_points:
        point_dim = point[0]
        point_color = point[1]
        rotate_x = multiply_m(rotation_x, point_dim)
        rotate_y = multiply_m(rotation_y, rotate_x)
        rotate_z = multiply_m(rotation_z, rotate_y)
        point_2d = multiply_m(projection_matrix, rotate_z)
    
        x = (point_2d[0][0] * scale) + MAIN_W/2
        y = (point_2d[1][0] * scale) + WINDOW_H/2

        points[i] = (x,y)
        i += 1
        
        pygame.draw.circle(window, point_color, (x, y), 5)
        
        # Dibujar el aura
        if aura_active == True and indice_esfera == i - len(pisos_points):
            aura_alpha += 1  # Incrementar la transparencia
            if aura_alpha > 255:
                aura_alpha = 128  # Resetear la transparencia
            aura_surface.set_alpha(aura_alpha)
            window.blit(aura_surface, (x-261,y-261))

    draw_edificio_lines(rotation_x, rotation_y, rotation_z)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for input in inputs.values():
                if input.rect.collidepoint(event.pos):
                    input.active = True
                else:
                    input.active = False
                    
            idx = verify_collide(event.pos, points)
            posicion = pygame.mouse.get_pos()
            # Evento que activa la información de un área, al dar click sobre ella...
            if idx != -1 and len(pisos_points) <= idx:
                idx -= (len(pisos_points))
                info_nodo = edificio.obtener_areas()[idx].info
                indice_esfera = edificio.obtener_areas()[idx].indice
                espectro_area(261)
                aura_active = True
            elif idx != -1 and pisos_points[idx][1] == (255,1,0):
                idx -= (len(pisos_points))
                idx = (len(pisos_points)+1) + idx 
                for ap in gestor_internet.aps:
                    if ap.piso == idx:
                        info_nodo = ap.get_info()
                        break
            else:
                info_nodo = []
                aura_active = False
            if recalc_button.collidepoint(event.pos): 
                edificio.verificar_habitabilidad_areas()
                generar_conexion()

        # Eventos de las entradas.
        if event.type == pygame.KEYDOWN:
            for input in inputs.values():                
                if input.active:
                    if event.key == pygame.K_BACKSPACE:
                        input.text = input.text[:-1]
                    elif event.key == pygame.K_RETURN:
                        input.press_enter()
                        input.active = False
                    else:
                        input.text += event.unicode
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            angle_y = angle_x = angle_z = 0
        if keys[pygame.K_a]:
            angle_y += ROTATE_SPEED
        if keys[pygame.K_d]:
            angle_y -= ROTATE_SPEED      
        if keys[pygame.K_w]:
            angle_x += ROTATE_SPEED
        if keys[pygame.K_s]:
            angle_x -= ROTATE_SPEED
        if keys[pygame.K_q]:
            angle_z -= ROTATE_SPEED
        if keys[pygame.K_e]:
            angle_z += ROTATE_SPEED   
            
    # Muestra el error en pantalla
    text_surface_info = label_font.render(error, True, (255,255,255))
    window.blit(text_surface_info, (30, 30+7*20))

    for i, info in enumerate(info_nodo):
        if info != "":
            text_surface_info = label_font.render(info, True, (255,255,255))
            window.blit(text_surface_info, (30, 30+i*20))
    for input in inputs.values():

        if input.active:
            input.color = color_active
        else:
            input.color = color_passive
            
        pygame.draw.rect(window, input.color, input.rect, 2)
        
        text_surface = base_font.render(input.text, True, (255,255,255))
        window.blit(text_surface, (input.rect.x+5, input.rect.y + 5))
        for i, label in enumerate(input.labels):
            text_surface_label = label_font.render(label, True, (255,255,255))
            window.blit(text_surface_label, (input.rect.x+5, input.rect.y - 20*(len(input.labels)-i)))
        
        input.rect.w = max(100, text_surface.get_width() + 10)

    
    # Dibujar el botón con borde y esquinas redondeadas
    recalc_button = pygame.Rect(BUTTON_POS, BUTTON_SIZE)
    draw_rounded_rect(window, recalc_button, BUTTON_COLOR, BORDER_COLOR, BORDER_SIZE, RADIUS)
    
    # Dibujar el texto en el botón
    button_surface = base_font.render("Calcular", True, TEXT_COLOR)
    text_rect = button_surface.get_rect(center=recalc_button.center)
    window.blit(button_surface, (recalc_button.x + 15, recalc_button.y))
    
    pygame.display.flip()
    pygame.display.update()