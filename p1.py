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
                                
                                P = {
                                    "doc_identidad" : int(doc),
                                    "edad": int(edad),
                                    "nombre" : nombre,
                                    "apellido" : apellido,
                                    "genero": genero
                                }
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
                    nombre = row[8]
                    apellido = row[9]
                    edad = int(row[11])
                    genero = row[10]
                    P = {
                        "doc_identidad" : doc,
                        "edad":edad,
                        "nombre" : nombre,
                        "apellido" : apellido,
                        "genero": genero
                    }
                    db['Pacientes'].insert_one(P)

            elif archivo.endswith('.json'):
                with open(ruta_completa, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    doc = int(data[0]['id'])
                    nombre = data[0]['nombre']
                    apellido = data[0]['apellido']
                    edad= data[0]['edad']
                    genero = data[0]['sexo']
                    P = {
                        "doc_identidad" : doc,
                        "edad":edad,
                        "nombre" : nombre,
                        "apellido" : apellido,
                        "genero": genero
                    }
                    db['Pacientes'].insert_one(P)
            else:
                print(f"Formato no compatible para el archivo: {archivo}")
        print(P)
        

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
    if paciente:
        return paciente
    else:
        messagebox.showinfo("Alerta", "El paciente no está en la base de datos.")

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



# Crear ventana principal
root = tk.Tk()
root.title("Pacientes")


# Funciones para cada operación CRUD
def crear_paciente():
    doc_identidad = int(entry_id.get())
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    edad = int(entry_edad.get())
    genero = entry_genero.get()
    
    paciente = {"doc_identidad": doc_identidad, "nombre": nombre, "apellido": apellido, "edad": edad, "genero": genero}
    insertar_paciente(paciente)

def buscar_paciente_crud():
    id = int(entry_id.get())
    paciente = buscar_paciente(id)
    if paciente:
        
        # Rellenar los campos de entrada con la información del paciente
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, paciente["nombre"])
        
        entry_apellido.delete(0, tk.END)
        entry_apellido.insert(0, paciente["apellido"])
        
        entry_edad.delete(0, tk.END)
        entry_edad.insert(0, paciente["edad"])
        
        entry_genero.delete(0, tk.END)
        entry_genero.insert(0, paciente["genero"])
        boton_actualizar.config(state=tk.NORMAL)
    else:
            messagebox.showinfo("Alerta", "El paciente no está en la base de datos.")
            # Deshabilitar el botón de actualización si no se encuentra el paciente
            boton_actualizar.config(state=tk.DISABLED)


def actualizar_paciente_crud():
    id = int(entry_id.get())
    nuevo_valor = {
        "nombre": entry_nombre.get(),
        "apellido": entry_apellido.get(),
        "edad": int(entry_edad.get()),
        "genero": entry_genero.get()
    }
    actualizar_paciente(id, nuevo_valor)

def eliminar_paciente_crud():
    id = int(entry_id.get())
    eliminar_paciente(id)


# Interfaz gráfica
    
label_id = tk.Label(root, text="Documento identidad:")
label_id.grid(row=0, column=0)
entry_id = tk.Entry(root)
entry_id.grid(row=0, column=1)

label_nombre = tk.Label(root, text="Nombre:")
label_nombre.grid(row=1, column=0)
entry_nombre = tk.Entry(root)
entry_nombre.grid(row=1, column=1)

label_apellido = tk.Label(root, text="Apellido:")
label_apellido.grid(row=2, column=0)
entry_apellido = tk.Entry(root)
entry_apellido.grid(row=2, column=1)

label_edad = tk.Label(root, text="Edad:")
label_edad.grid(row=3, column=0)
entry_edad = tk.Entry(root)
entry_edad.grid(row=3, column=1)

label_genero = tk.Label(root, text="Género:")
label_genero.grid(row=4, column=0)
entry_genero = tk.Entry(root)
entry_genero.grid(row=4, column=1)

boton_crear = tk.Button(root, text="Crear", command=crear_paciente)
boton_crear.grid(row=5, column=0, columnspan=2, pady=10)

boton_buscar = tk.Button(root, text="Buscar", command=buscar_paciente_crud)
boton_buscar.grid(row=6, column=0, columnspan=2, pady=10)

boton_actualizar = tk.Button(root, text="Actualizar", command=actualizar_paciente_crud)
boton_actualizar.config(state=tk.DISABLED)
boton_actualizar.grid(row=7, column=0, columnspan=2, pady=10)

boton_eliminar = tk.Button(root, text="Eliminar", command=eliminar_paciente_crud)
boton_eliminar.grid(row=8, column=0, columnspan=2, pady=10)

# Botón para cargar carpeta con archivos
btn_cargar = tk.Button(root, text="Cargar carpeta", command=cargar_archivos)
btn_cargar.grid(row=9, column=0, columnspan=2, pady=10)


# Ejecutar la ventana principal
root.mainloop()