#!/usr/bin/python2
#-*- coding:utf-8 -*-
#Variables
import socket, os, signal, sys, tarfile, shutil, getpass
host = "127.0.0.1" #casa
port = 8000
def handler(signum, frame):
    os.system("fuser -k -n tcp %s" % port)
    sys.exit()
signal.signal(signal.SIGTSTP, handler)
obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Conexion con el servidor. Parametros: IP (puede ser del tipo 192.168.1.1 o localhost), Puerto
obj.connect((host, port))
name_host_server = socket.gethostname()
carpeta_actual_server = os.getcwd()
print("\033[1;32m"+"[+]"+"\033[1;37m"+" conexion establecida")
 
#Creamos un bucle para retener la conexion
while True:
    #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
    mens = raw_input("\033[1;31m"+host+"\033[1;32m"+"@"+name_host_server+":"+"\033[1;37m"+"$ ")
    if mens == "close":
            os.system("fuser -k -n tcp %s" % port)
            break
    #Con el metodo send, enviamos el mensaje
    obj.send(mens)
    data = obj.recv(1073741824)
    descargar_archivo = data.startswith("download -f ready")
    descargar_carpeta_listo = data.startswith("download -d ready")
    copiar_archivo = mens.startswith("copy -f")
    copiar_carpeta = mens.startswith("copy -d")
    eliminar_copiar_carpeta = data.startswith("Eliminar copy")
    sudo = mens.startswith("root")
    instalar = mens.startswith("install")
    desinstalar = mens.startswith("uninstall")
    #descargar un archivo del servidor al cliente
    if descargar_archivo == 1: 
            ruta = raw_input("ruta absoluta, donde se descargará el archivo >>\n")
            archivo_filtro = data.replace("download -f ready|","")
            lista_archivo = archivo_filtro.split("|")
            nombre_archivo = lista_archivo[0]
            restante = nombre_archivo+"|"
            archivo_filtro2 = archivo_filtro.replace(restante,"")
            crear_ruta = ruta+"/"+nombre_archivo
            archivo_descargar = open(crear_ruta,"a")
            archivo_descargar.write(archivo_filtro2)
            archivo_descargar.close()
            print("\033[1;32m"+"[+]"+"\033[1;37m"+"archivo descargado correctamente")
    #copiar un archivo del cliente al servidor
    elif descargar_carpeta_listo == 1: #descargar carpeta del servidor al cliente
            ruta = raw_input("ruta absoluta donde descargarás el directorio >>\n")
            filtro = data.replace("download -d ready |","")
            lista = filtro.split(" | ")
            archivo = lista[0]
            ruta_tmp = lista[1]
            lista_ruta = ruta_tmp.split("/")
            ultimo = len(lista_ruta) -1
            nombre = lista_ruta[ultimo]
            nombre_dir = nombre.split(".")
            nombre_directorio = nombre_dir[0]
            abrir = open(ruta_tmp,"w")
            abrir.write(archivo)
            abrir.close()
            os.system("mkdir "+ruta+"/"+nombre_directorio)
            desempaquetar = tarfile.open(ruta_tmp)
            desempaquetar.extractall(path=ruta+"/"+nombre_directorio+"/")
            eliminar = open(ruta_tmp,"w")
            eliminar.write("00000000")
            eliminar.close()
            os.system("shred -u "+ruta_tmp)
            obj.send("Eliminar download "+ruta_tmp)
            print("\033[1;32m"+"[+]"+"\033[1;37m"+"carpeta descargada correctamente")
    elif copiar_archivo == 1:
            destino_servidor = raw_input("ruta absoluta, donde se copiará el archivo al servidor >>\n")
            filtro = mens.replace("copy -f ","")
            abrir = open(filtro,"rb")
            leer = abrir.read()
            lista = filtro.split("/")
            lon_lista = len(lista)
            ultim_lista = lon_lista-1
            nombre = lista[ultim_lista]
            nombre1 = "".join(nombre.split())
            obj.send("copy -f ready |"+leer+" | "+destino_servidor+" | "+nombre1)
    elif copiar_carpeta == 1:
            destino_servidor = raw_input("ruta absoluta, donde se copiará la carpeta al servidor >>\n")
            filtro = mens.replace("copy -d ","")
            lista = filtro.split("/")
            lon_lista = len(lista)
            ultim_lista = lon_lista-1
            directorio = lista[ultim_lista]
            directorio1 = "".join(directorio.split())
            tmp = "/tmp/"+directorio1
            tar = "/tmp/"+directorio1+".tar.bz2"
            comprimir = shutil.make_archive(tmp,"bztar",filtro)
            abrir = open(tar,"rb")
            leer = abrir.read()
            obj.send("copy -d ready |"+leer+" | "+destino_servidor+" | "+directorio1)
            print("\033[1;32m"+"[+]"+"\033[1;37m"+" Directorio copiado correctamente")
    elif  eliminar_copiar_carpeta == 1:
            filtro = data.replace("Eliminar copy ","")
            os.system("shred -u "+filtro)
    elif sudo == 1:
        contrasena = getpass.getpass("Contraaseña del usuario root: ")
        mensaje = mens.replace("root ","")
        obj.send("sudo "+mensaje+" | "+contrasena)
    elif instalar == 1:
        contrasena = getpass.getpass("Contraseña del usuario root: ")
        mensaje = mens.replace("install ","")
        obj.send("install ready "+mensaje+" | "+contrasena)
        while data == "error sudo install":
            contrasena = getpass.getpass("Contraseña del usuario root: ")
            pass
    elif desinstalar == 1:
        contrasena = getpass.getpass("Contraseña del usuario root: ")
        mensaje = mens.replace("uninstall ","")
        obj.send("uninstall ready "+mensaje+" | "+contrasena)
    elif mens == "man":
        print("""
            """+"\033[1;31m"+"""-t"""+"\033[1;37m"+""" [texto] : Envía un mensaje por la terminal.\n
            """+"\033[1;31m"+"""-m --error"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de error.\n
            """+"\033[1;31m"+"""-m --info"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de información.\n 
            """+"\033[1;31m"+"""-m --input"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de entrada de texto.\n 
            """+"\033[1;31m"+"""-m --question"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de pregunta.\n
            """+"\033[1;31m"+"""-m --alert"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de alerta.\n
            """+"\033[1;31m"+"""-m --notification"""+"\033[1;37m"+""" "[texto]" : Muestra un diálogo de notificación.\n
            """+"\033[1;31m"+"""download -f"""+"\033[1;37m"+""" [ruta del archivo del servidor a descargar] : Descarga un archivo del servidor al cliente.\n
                Cuando lo ejecutes, te preguntará donde quieres que se guarde el archivo.\n
                    """+"\033[1;31m"+"""$"""+"\033[1;37m"+""" download -f /home/administrador/Imágenes/cleanet.png
                    ruta absoluta, donde se descargará el archivo """+"\033[1;31m"+""">>"""+"\033[1;37m"+"""
                    /home/administrador/Escritorio\n
                    [!]
            """+"\033[1;31m"+"""download -d"""+"\033[1;37m"+""" [ruta del directorio del servidor a descargar] : Descarga un directorio del servidor al cliente.\n
                Cuando lo ejecutes, te preguntará donde quieres que se guarde el directorio.\n
                    """+"\033[1;31m"+"""$"""+"\033[1;37m"+""" download -d /home/administrador/scripts\n
                    ruta absoluta, donde descargarás el directorio """+"\033[1;31m"+""">>"""+"\033[1;37m"+"""
                    /home/administrador/Escritorio\n
            """+"\033[1;31m"+"""copy -f"""+"\033[1;37m"+""" [ruta del archivo del cliente para copiarlo al servidor] : copia un archivo del cliente al servidor.\n
                Cuando lo ejecutes, te preguntará donde quieres que se guarde el archivo.\n
                    """+"\033[1;31m"+"""$"""+"\033[1;37m"+""" copy -f /home/administrador/conexion.py\n
                    ruta absoluta, donde se copiará el archivo al servidor"""+"\033[1;31m"+""">>"""+"\033[1;37m"+"""
                    /home/administrador/Documentos\n
            """+"\033[1;31m"+"""copy -d"""+"\033[1;37m"+""" [ruta del directorio del cliente para copiarlo al servidor] : copia un directorio del cliente al servidor.\n
                Cuando lo ejecutes, te preguntará donde quieres que se guarde el archivo.\n
                    """+"\033[1;31m"+"""$"""+"\033[1;37m"+""" copy -d /home/administrador/actividades \n
                    ruta absoluta, donde se copiará el archivo al servidor"""+"\033[1;31m"+""">>"""+"\033[1;37m"+"""
                    /home/administrador/Documentos \n 

                [!] Cuando se haga una transferencia de archivo el tamaño máximo es de 1GB
                [!] Al introducir las rutas, no deben de tener un '/' al final          
            """)
    else:
        print(data)
#Cerramos la instancia del objeto servidor
obj.close()
#Imprimimos la palabra Adios para cuando se cierre la conexion
print("Conexion cerrada")
