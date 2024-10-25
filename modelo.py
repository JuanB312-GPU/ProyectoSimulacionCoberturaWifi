import math
from enum import Enum

minReqActividad = {"STREAMING": -67.0, "EMAIL_WEB": -70.0}
minCapActividad = {"STREAMING": 6, "EMAIL_WEB": 3}

# Factor de atenuación para cada material
RESISTENCIA_MATERIAL = {
    "2.4ghz_IEEE802.11.b": [27, 17, 5, 5],
    "5ghz_IEEE802.11.a": [29, 20, 7, 5]
}

class Material(Enum):
  # Enumeración que define los materiales
  CONCRETO = 0
  LADRILLO = 1
  VIDRIO = 2
  MADERA = 3

class Nodo:
  def __init__(self, valor, color):
      self.valor = valor
      self.hijos = []
      self.color = color

  def agregar_hijo(self, hijo):
      self.hijos.append(hijo)

  def eliminar_hijo(self, hijo):
    self.hijos.remove(hijo)

class Arbol:
  def __init__(self, raiz):
    self.raiz = raiz

class Area:
  # Clase que representa un área de trabajo

  def __init__(self, tipo_actividad, piso, x, y, color, indice, personas):
    self.tipo_actividad = tipo_actividad  # Tipo de actividad
    self.minReqAct = minReqActividad[tipo_actividad]
    self.ancho_necesario = personas * minCapActividad[tipo_actividad]
    self.indice = indice
    self.personas = personas
    self.piso = piso
    self.opcion = 0 #Sirve para informar sobre la razón por la que un área es inhabitable.
    self.x = x
    self.y = y
    self.color = color
    self.info = [f"ID Área: {indice}",
                 f"Actividad: {tipo_actividad}",
                 f"Mínima Señal Requerida: {minReqActividad[tipo_actividad]} dBm", 
                 f"Mínima ancho de banda Requerido: {personas * minCapActividad[tipo_actividad]} Mb/s", 
                 f"Personas: {personas} ", "",""]

  def obtener_tipo_actividad(self):
    return self.tipo_actividad  # Devuelve el nombre del tipo de actividad

  def obtener_piso(self):
    return self.piso  # Devuelve el piso

  def obtener_minReqAct(self):
    return self.minReqAct  # Devuelve el minReqAct

  def obtener_ancho(self):
    return self.ancho_necesario # Devuelve ancho de banda

  def set_actividad(self, actividad): # Para configurar la potencia del área
    self.tipo_actividad = actividad 
    
  def set_anchoBanda(self, personas): # Para configurar el ancho de banda requerido, aumentado las personas en el área
    self.ancho_necesario = personas * minCapActividad[self.tipo_actividad]
    
  def actualizar_info(self):
    self.info = [f"ID Área: {self.indice}",
                 f"Actividad: {self.tipo_actividad}",
                 f"Mínima Señal Requerida: {minReqActividad[self.tipo_actividad]} dBm", 
                 f"Mínima ancho de banda Requerido: {self.personas * minCapActividad[self.tipo_actividad]} Mb/s", 
                 f"Personas: {self.personas} ", "",""]

  def set_hab(self, hab): # Para insertar habitabilidad
    self.hab = hab

class Ap:
  # Clase que el access point
  def __init__(self, tipo_ap_ind, piso, indice):
    self.indice = indice
    self.tipo_ap_ind = tipo_ap_ind
    self.piso = piso
    self.areas_que_cubre = []
    self.info = []
    if (tipo_ap_ind == 1):
      self.tipo_ap = "2.4ghz_IEEE802.11.b"
      self.f = 2.4
      self.ganancia_antena = 4.5
      self.fuerza_transmision = 26
      self.ancho_de_banda = 60
    else:
      self.tipo_ap = "5ghz_IEEE802.11.a"
      self.f = 5
      self.ganancia_antena = 6
      self.fuerza_transmision = 29
      self.ancho_de_banda = 90
      
  def get_info(self):
    self.info = ["",f"AP número: {self.indice}",
                 f"AP Tipo: {self.tipo_ap}",
                 f"Ancho de banda disponible: {self.ancho_de_banda}"]
    return self.info
      
  def reiniciar_ancho(self):
    if (self.tipo_ap_ind == 1):
      self.ancho_de_banda = 60
    else:
      self.ancho_de_banda = 90

  def obtener_piso(self):
    return self.piso  # Devuelve el piso

  def obtener_ancho(self):
    return self.ancho_de_banda #Devuelve el ancho de banda

  def modificar_ancho(self, valor):
    self.ancho_de_banda = self.ancho_de_banda - valor #Resta el valor del ancho de banda del area a la disponible

  def calcular_ganancia_total(self):
    return self.fuerza_transmision + 2 * self.ganancia_antena - 3  #Calcula la ganancia total

  def calcular_path_loss(self, piso_area, x, y, atten_material):
    d = math.sqrt(
        (self.piso-piso_area)**2 + x**2 + y**2
        ) * 3  #Calcular la distancia de AP y el Area y multiplicar por la altura de cada piso
    if (d == 0):
      d = 2
    return 20 * (math.log10(d) + math.log10(
        self.f * 1000)) - 27.55 + atten_material  #Calcula el path loss

  def calcular_atten(self, materiales):
    sm = 0
    for mat in materiales:
      sm += RESISTENCIA_MATERIAL[self.tipo_ap][mat.value]
    return sm+5

  def add_areas_que_cubre(self, area):
    self.areas_que_cubre.append(area)

  def obtener_areas_que_cubre(self):
    return self.areas_que_cubre

  def borrar_area(self,area):
    self.ancho_de_banda = self.ancho_de_banda + area.obtener_ancho()
    self.areas_que_cubre.remove(area)
    
    

class GestorInternet:
  # Clase que representa al gestor de Internet

  def __init__(self):
    self.aps = [] # Material del edificio

  def obtener_aps(self):
    return self.aps

  def verificar_habitabilidad(self, area, materiales):
    # Verifica si cada área es habitable
    temporal = self.aps.copy()
    while len(temporal) > 0:
        mejor_señal = -float("inf")
        mejor_ap = None
        for ap in temporal:
          #Calculamos la fuerza de señal para cada ap
          fuerza_de_señal = ap.calcular_ganancia_total() - ap.calcular_path_loss(
          area.obtener_piso(), area.x, area.y, ap.calcular_atten(materiales))
          #Elegimos el mejor ap
          if mejor_señal < fuerza_de_señal:
            mejor_ap = ap
            mejor_señal = fuerza_de_señal
        #verificamos si la señal satisface a la actividad del area
        print(area.obtener_minReqAct()) 
        print("señal") 
        print(mejor_señal) 
        if mejor_señal > area.obtener_minReqAct():
          if area.obtener_ancho() <= mejor_ap.obtener_ancho():
            mejor_ap.modificar_ancho(area.obtener_ancho())
            return mejor_ap, mejor_señal, True
          # Si la opción es 2, signfica que el área ha sido rechazada por falta de ancho de banda disponible.  
          if area.opcion != 1:  
            area.opcion = 2  
        temporal.remove(mejor_ap)
        if mejor_señal < area.obtener_minReqAct() and area.opcion != 2:
            # Si la opción es 1, significa que el área ha sido rechazada por que no se encontro una señal sustentable.
            area.opcion = 1   
    return mejor_ap, mejor_señal, False


class Edificio:

  def __init__(self, gestor_internet):
    self.nodos = []
    self.areas = []  # Lista para almacenar las áreas del edificio
    self.gestor_internet = gestor_internet
    self.materiales_edificio = ["CONCRETO", "MADERA"]  # Material del edificio
    self.altura = 0

  def agregar_area(self, area):
    self.areas.append(area)  # Agrega un área a la lista de áreas del edificio

  def obtener_areas(self):
    return self.areas  # Devuelve la lista de áreas del edificio

  def obtener_area(self, indice):
    return self.areas[indice] # Obtiene un área.

  def configurar_area(self, indice, area):
    self.areas[indice] = area # Actualiza el área en cuestión.

  def obtener_materiales(self):
    return self.materiales_edificio  # Devuelve la lista de áreas del edificio.

  def set_altura(self, altura):
    self.altura = altura  # Agrega la altura del edificio.

  def obtener_altura(self):
    return int(self.altura) # Devuelve la altura del edificio.

  def verificar_habitabilidad_areas(self):
    for ap in self.gestor_internet.aps:
      ap.areas_que_cubre.clear()
      ap.reiniciar_ancho()
    for area in self.areas:
      # Verifica la habitabilidad de cada área y muestra un mensaje según el resultado
      mejor_ap, fuerza_señal, habitable = self.gestor_internet.verificar_habitabilidad(
          area, self.materiales_edificio)
      if habitable == True:
        if area not in mejor_ap.obtener_areas_que_cubre():
            mejor_ap.add_areas_que_cubre(area)
        area.info[2] = f"Piso mejor AP: {mejor_ap.obtener_piso()}"
      else:
        area.info[2] = f"Piso mejor AP: Ninguno"
      area.set_hab(habitable)
      area.info[3] = f"Señal: {fuerza_señal} dBm"
      area.info[4] = f"Habitable: {habitable}"
      area.info[5] = f"Ancho de banda: {area.obtener_ancho()} Mb/s"

