import os
import csv
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import hl7
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Conexión a atlas documentación
uri = "mongodb+srv://isabelgarcesg:isabel@cluster0.hhlhbws.mongodb.net/"
datos = MongoClient(uri, server_api=ServerApi('1'))                         
# Verificar conexión exitosa
try:
    datos.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = datos["DATA"] # Base de datos creada en mongoDB

# Ruta de la carpeta que contiene los archivos, luego desde UI uno es el que selecciona la carpeta
carpeta = r'pacientes'

# Función que itera sobre todos los archivos en la carpeta y extrae información de paciente
def procesar_archivos(carpeta):
    for archivo in os.listdir(carpeta):
        ruta_completa = os.path.join(carpeta, archivo)
        
        # Verificar si es un archivo
        if os.path.isfile(ruta_completa):
            # Leer y procesar el archivo según su extensión

            if archivo.endswith('.txt'):
                examenes = {}
                P = {}
                with open(ruta_completa, 'r', encoding='utf-8') as file:
                    for line in file:
                        
                            if line.startswith('3O'):                          
                                doc = line.split('|')[2]
                                edad = line.split('|')[4].split('^')[3]
                                nombre = line.split('|')[12]
                                apellido = line.split('|')[13]
                                genero =  line.split('|')[27].replace('\n','')
                                if genero=='M':
                                    genero='Masculino'
                                else:
                                    genero='Femenino'                            
                                
                                P.update({
                                    "doc_identidad" : int(doc),
                                    "edad": int(edad),
                                    "nombre" : nombre,
                                    "apellido" : apellido,
                                    "genero": genero,
                                    "extension": 'txt'
                                })

                            if (line[0].isdigit() and line[1] == 'R'):

                                nombre_prueba = line.split('|')[2].split('^')[3]

                                if int(line[0])%2 == 0:
                                    
                                    resultado = float(line.split('|')[3])
                                
                                if int(line[0])%2 != 0:

                                    tiempo = float(line.split('|')[3])

                                    examenes[nombre_prueba] = {"resultado": resultado,"tiempo": tiempo}

                                if int(line[0]) == 0:

                                    examenes[nombre_prueba] = {"resultado": resultado}

                    if db['Pacientes'].count_documents({"doc_identidad": int(doc)}) > 0:
                                    messagebox.showinfo("Alerta", f"El paciente con documento de identidad {doc} ya está en la base de datos.")
                                    break  # Saltar a la próxima iteración sin insertar el paciente
                    else:      
                        P['examenes'] = examenes 
                        db['Pacientes'].insert_one(P)

            elif archivo.endswith('.csv'):
                with open(ruta_completa, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    i = 1
                    for row in reader:
                        if i==1:
                            header = row
                        elif i==2:
                            break
                        i+=1
                    dic = dict(zip(header , row))
                    doc = int(row[7])
                    if db['Pacientes'].count_documents({"doc_identidad": int(doc)}) > 0:
                        messagebox.showinfo("Alerta", f"El paciente con documento de identidad {doc} ya está en la base de datos.")
                        continue  # Saltar a la próxima iteración sin insertar el paciente
                    equipo = row[1]
                    modelo = row[2]
                    serial = row[3]
                    responsable = row[4]
                    profesion = row[5]
                    ips = row[6]
                    nombre = row[8]
                    apellido = row[9]
                    genero = row[10]
                    edad = int(row[11])
                    proc_tp = row[12]
                    proc_ptt = row[13]
                    proc_fib = row[14]
                    medico = row[15]
                    especialidad = row[16]
                    ingreso = row[17]
                    dx_principal = row[18]

                    P = {

                        "doc_identidad" : doc,
                        "edad":edad,
                        "nombre" : nombre,
                        "apellido" : apellido,
                        "genero": genero,
                        "equipo": equipo,
                        "modelo": modelo,
                        "serial": serial,
                        "responsable": responsable,
                        "profesion": profesion,
                        "ips": ips,
                        "proc_tp": proc_tp,
                        "proc_ptt": proc_ptt,
                        "proc_fib": proc_fib,
                        "medico": medico,
                        "especialidad": especialidad,
                        "ingreso": ingreso,
                        "dx_principal": dx_principal,
                        "extension": 'csv'
                    }
                    
                    db['Pacientes'].insert_one(P)

            elif archivo.endswith('.json'):
                with open(ruta_completa, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    doc = int(data[0]['id'])
                    if db['Pacientes'].count_documents({"doc_identidad": int(doc)}) > 0:
                        messagebox.showinfo("Alerta", f"El paciente con documento de identidad {doc} ya está en la base de datos.")
                        continue  # Saltar a la próxima iteración sin insertar el paciente
                    equipo = data[0]['equipo']
                    modelo = data[0]['modelo']
                    serial = data[0]['serial']
                    responsable = data[0]['responsable']
                    profesion = data[0]['profesión']
                    ips = data[0]['ips']
                    nombre = data[0]['nombre']
                    apellido = data[0]['apellido']
                    genero = data[0]['sexo']
                    edad = data[0]['edad']
                    examen = data[0]['examen']
                    medico = data[0]['médico']
                    especialidad = data[0]['especialidad']
                    ingreso = data[0]['ingreso']
                    dx = data[0]['dx']
                    comorbilidades = data[0]['Comorbilidades']
                    

                    P = {
                        "doc_identidad" : doc,
                        "edad":edad,
                        "nombre" : nombre,
                        "apellido" : apellido,
                        "genero": genero,
                        "equipo": equipo,
                        "modelo": modelo,
                        "serial": serial,
                        "responsable": responsable,
                        "profesion": profesion,
                        "ips": ips,
                        "examen": examen,
                        "medico": medico,
                        "especialidad": especialidad,
                        "ingreso": ingreso,
                        "dx": dx,
                        "comorbilidades": comorbilidades,
                        "extension": 'json'
                    }
                    db['Pacientes'].insert_one(P)
            else:
                print(f"Formato no compatible para el archivo: {archivo}")
        

def cargar_archivos():
    # Cargar carpeta con archivos para leer
    carpeta = filedialog.askdirectory()
    if carpeta:
        procesar_archivos(carpeta)        

def insertar_paciente(paciente):
    # Insertar paciente en la colección
    result = db["Pacientes"].insert_one(paciente)
    print(f"Paciente insertado con el ID: {result.inserted_id}")

def buscar_paciente(id):
    # Buscar paciente por ID
    paciente = db["Pacientes"].find_one({"doc_identidad": id})
    return paciente


def actualizar_paciente(id, nuevo_valor):
    # Actualizar paciente por ID
    resultado = db["Pacientes"].update_one({"doc_identidad": id}, {"$set": nuevo_valor})
    if resultado.modified_count == 0:
        messagebox.showinfo("Alerta", "El paciente no está en la base de datos.")
    else:
        print(f"Paciente actualizado correctamente.")

def eliminar_paciente(id):
    # Eliminar paciente por ID
    resultado = db['Pacientes'].delete_one({"doc_identidad": id})
    if resultado.deleted_count == 0:
        messagebox.showinfo("Alerta", "El paciente no está en la base de datos.")
    else:
        print(f"Paciente eliminado correctamente.")


# Funciones para cada operación CRUD
def crear_paciente():
    doc_identidad = entry_id.get()
    if not doc_identidad:
        messagebox.showinfo("Alerta", "Por favor ingrese el documento de identidad para crear al paciente.")
        return
    
    # Verificar si el documento de identidad es un número válido
    try:
        doc_identidad = int(doc_identidad)
    except ValueError:
        messagebox.showinfo("Alerta", "Por favor ingrese un número válido para el documento de identidad.")
        return
    
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    edad = int(entry_edad.get())
    genero = genero_seleccionado.get()

    # Verificar que todos los campos estén llenos
    if not doc_identidad or not nombre or not apellido or not edad:
        messagebox.showinfo("Alerta", "Por favor complete todos los campos para crear el paciente.")
        return
    
    # Verificar si el paciente ya existe en la base de datos
    if db['Pacientes'].count_documents({"doc_identidad": int(doc_identidad)}) > 0:
        messagebox.showinfo("Alerta", f"El paciente con documento de identidad {doc_identidad} ya está en la base de datos.")
        return  # Salir de la función sin crear el paciente
    
    paciente = {"doc_identidad": doc_identidad, "nombre": nombre, "apellido": apellido, "edad": edad, "genero": genero}
    insertar_paciente(paciente)

# Variable global para almacenar el documento de identidad original
documento_original = None
target_folder = 'data'
# Función para buscar paciente
def buscar_paciente_crud():
    global documento_original
    global target_folder
    id = entry_id.get()
    if not id:
        messagebox.showinfo("Alerta", "Por favor ingrese el documento de identidad para buscar al paciente.")
        return
    
    # Verificar si el documento de identidad es un número válido
    try:
        id = int(id)
    except ValueError:
        messagebox.showinfo("Alerta", "Por favor ingrese un número válido para el documento de identidad.")
        return
    
    paciente = buscar_paciente(id)


    if paciente:
        documento_original = paciente["doc_identidad"]
        # Rellenar los campos de entrada con la información del paciente
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, paciente["nombre"])
        
        entry_apellido.delete(0, tk.END)
        entry_apellido.insert(0, paciente["apellido"])
        
        entry_edad.delete(0, tk.END)
        entry_edad.insert(0, paciente["edad"])
        
        # Actualizar el valor del desplegable de género
        genero_seleccionado.set(paciente["genero"])        
        btn_actualizar.config(state=tk.NORMAL) # Habilitar el botón de actualización
        if not os.path.exists(target_folder):
            # Si no existe, crear la carpeta
            os.makedirs(target_folder)
            print(f"La carpeta '{target_folder}' ha sido creada.")
        else:
            print(f"La carpeta '{target_folder}' ya existe.")
        nombre_archivow = target_folder + '/' + str(paciente["doc_identidad"]) + '.txt'
        if not os.path.exists(nombre_archivow):
            # Si no existe, crear el archivo
            with open(nombre_archivow, 'w') as archivo:

                PID_paciente = f"PID||{paciente['doc_identidad']}|||{paciente['apellido']}^{paciente['nombre']}^|||{paciente['genero']}"
                archivo.write(PID_paciente + '\n')
                
            messagebox.showinfo('Alerta', f"El archivo '{str(paciente['doc_identidad'])}.txt' ha sido creado.")
        else:

            messagebox.showinfo('Alerta', f"El archivo {nombre_archivow[5:]} ya existe. No se ha realizado ninguna escritura.")



    else:
            messagebox.showinfo("Alerta", "El paciente no está en la base de datos.")
            # Deshabilitar el botón de actualización si no se encuentra el paciente
            btn_actualizar.config(state=tk.DISABLED)


def actualizar_paciente_crud():
    global documento_original # Así aunque se modifique el documento va a actualizar el paciente que es
    # id = entry_id.get()
    if not documento_original:
        messagebox.showinfo("Alerta", "Por favor ingrese el documento de identidad para actualizar al paciente.")
        return
    
    # Verificar si el documento de identidad es un número válido
    try:
        documento_original = int(documento_original)
    except ValueError:
        messagebox.showinfo("Alerta", "Por favor ingrese un número válido para el documento de identidad.")
        return
    
    nuevo_valor = {
        "nombre": entry_nombre.get(),
        "apellido": entry_apellido.get(),
        "edad": int(entry_edad.get()),
        "genero": genero_seleccionado.get()
    }
    actualizar_paciente(documento_original, nuevo_valor)

def eliminar_paciente_crud():
    id = entry_id.get()
    if not id:
        messagebox.showinfo("Alerta", "Por favor ingrese el documento de identidad para eliminar al paciente.")
        return
    
    # Verificar si el documento de identidad es un número válido
    try:
        id = int(id)
    except ValueError:
        messagebox.showinfo("Alerta", "Por favor ingrese un número válido para el documento de identidad.")
        return

    eliminar_paciente(id)


# Interfaz gráfica

# Crear ventana principal
root = tk.Tk()
root.title("Gestión de Pacientes")

# Cargar carpeta con archivos
label_carpeta = tk.Label(root, text="Cargar carpeta con archivos")
label_carpeta.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

btn_cargar = tk.Button(root, text="Cargar Carpeta", command=cargar_archivos)
btn_cargar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Etiquetas y campos de entrada
label_id = tk.Label(root, text="Documento Identidad:")
label_id.grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_id = tk.Entry(root)
entry_id.grid(row=2, column=1, padx=10, pady=5, sticky="w")

label_nombre = tk.Label(root, text="Nombre:")
label_nombre.grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_nombre = tk.Entry(root)
entry_nombre.grid(row=3, column=1, padx=10, pady=5, sticky="w")

label_apellido = tk.Label(root, text="Apellido:")
label_apellido.grid(row=4, column=0, padx=10, pady=5, sticky="e")
entry_apellido = tk.Entry(root)
entry_apellido.grid(row=4, column=1, padx=10, pady=5, sticky="w")

label_edad = tk.Label(root, text="Edad:")
label_edad.grid(row=5, column=0, padx=10, pady=5, sticky="e")
entry_edad = tk.Entry(root)
entry_edad.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Opciones disponibles para el género
opciones_genero = ["Masculino", "Femenino"]
# Variable de control para el género seleccionado
genero_seleccionado = tk.StringVar(root)
genero_seleccionado.set(opciones_genero[0])  # Selecciona "Masculino" por defecto
label_genero = tk.Label(root, text="Género:")
label_genero.grid(row=6, column=0, padx=10, pady=5, sticky="e")
desplegable_genero = tk.OptionMenu(root, genero_seleccionado, *opciones_genero)
desplegable_genero.grid(row=6, column=1, padx=10, pady=5, sticky="w")

# Botones CRUD
btn_crear = tk.Button(root, text="Crear paciente", command=crear_paciente)
btn_crear.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

btn_buscar = tk.Button(root, text="Buscar paciente", command=buscar_paciente_crud)
btn_buscar.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

btn_actualizar = tk.Button(root, text="Actualizar paciente", command=actualizar_paciente_crud)
btn_actualizar.config(state=tk.DISABLED)
btn_actualizar.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

btn_eliminar = tk.Button(root, text="Eliminar paciente", command=eliminar_paciente_crud)
btn_eliminar.grid(row=8, column=1, padx=10, pady=5, sticky="ew")


# Ejecutar la ventana principal
root.mainloop()