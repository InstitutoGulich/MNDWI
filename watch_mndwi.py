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

#path = "/mnt/datos/Repositorio/sancor/indices/mndwi/" #Ruta de los archivos MNDWI
path = "/home/jrubio/Documentos/VENVS/SANCOR4/temp/"#indices/mndwi/" #Ruta de los archivos MNDWI
script = "python3 /mnt/datos/Repositorio/sancor/scripts/main_mndwi.py "
paises ["UY"]#,"PY","BR","AR"]

def ultimaDescarga(path):
	listDates = []
	for date in glob.glob(path+"*.tif"):
		listDates.append(date.split("/")[-1][0:7])
	return sorted(listDates,reverse=True)[0]

for pais in paises:
	ult=ultimaDescarga(path)

	anyo = int(ult[0:4])
	dia = int(ult[-3:])
	if dia == 361:
		anyo = anyo+1
		dia = -7

	dia = dia + 8
	dwnldDate = str(anyo)+"%03d"%dia
	print(dwnldDate)

#	driveDownload(path,pais,dwnldDate)
	os.system('python3 '+'main_mndwi.py "'+ff+'" "'+pais+'"')
	
	
