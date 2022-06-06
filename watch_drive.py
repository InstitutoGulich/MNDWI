#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################################
################# Este script verifica a diario si se encuentra disponible #################
####################### un nuevo dato para procesar el índice MNDWI ########################
############################################################################################

import os
from datetime import date, datetime, timedelta
import glob
import numpy as np
from clases import DriveAPI

obj = DriveAPI()

path = "/mnt/datos/Repositorio/.../indices/mndwi/" #Ruta de descarga para los archivos MNDWI
paises = ["UY","PY","BR","AR"]
controlDate = "2022041" # Ùltima fecha a revisar para descarga. El control puede ser para descarga ascendente o descendente.

def descargar(pcPath,drivePath,dwnldDate,controlDate):
	# Ver si hay descarga pendiente para la fecha
	# Si la hay, se descarga
	drive_items = obj.FileList(drivePath,dwnldDate)
	if len(drive_items) > 0:
		os.system('python3 main_drive_NB.py %s %s %s'%(pcPath,drivePath,dwnldDate))

	# Pasamos auna nueva fecha.
	# Recordar que estamos yendo de adelante hacia atrás
	anyo = int(dwnldDate[0:4])
	dia = int(dwnldDate[-3:])
#	if dia == 1: #361:
#		anyo = anyo-1 #+1
#		dia = 361
#	dia = dia - 8

	if dia == 361:
		anyo = anyo+1
		dia = -7
	dia = dia + 8

	dwnldDate = str(anyo)+"%03d"%dia
	print(dwnldDate)

	# Ponemos una fecha de corte para parar las descargas
#	if int(dwnldDate)>=int(controlDate):
	if int(dwnldDate)<=int(controlDate):
		descargar(pcPath,drivePath,dwnldDate,controlDate)


def ultimaDescarga(path):
	listDates = []
	for date in glob.glob(path+"*.tif"):
		listDates.append(date.split("/")[-1][0:7])
#	print(listDates)

#	## Vamos a descargar de adelante hacia atrás
	ascendente = sorted(listDates, reverse=True)
#	descendente = sorted(listDates)
	return ascendente[0]

for pais in paises:
	print(pais)
	pcPath = path+pais+"/"
	drivePath = "_"+pais+"."

	dwnldDate=str(int(ultimaDescarga(pcPath)))
	print(dwnldDate)
	descargar(pcPath,drivePath,dwnldDate,controlDate)
#	descargar(pcPath,drivePath,controlDate,controlDate)
