
import glob
import os
from funciones import subirtiff


#Datos Conexión
user = "maie" #Usuario
passw = "Test2018!" #Contraseña
ipgeo = "10.77.72.68" #IP del servidor
port = "8080" #Puerto

#Estilos
estilo_mndwi = "mndwi"
estilo_mndwi_water = "mndwi_water"

#Workspace
ws_mndwi = "mndwi"
ws_mndwi_water = "agua_superficial"

#Res img
resx = 0.000269494585235856472
resy = 0.000269494585235856472

paises = ["AR", "BR", "PY", "UY"]

for pais in paises:
	os.chdir('/mnt/datos/Repositorio/sancor/indices/mndwi/'+pais+'/')
	if pais == "AR":
		lista_mndwi = ('2022049_MNDWI_AR-0000000000-0000000000.tif' ,'2022049_MNDWI_AR-0000000000-0000046592.tif','2022049_MNDWI_AR-0000046592-0000000000.tif','2022049_MNDWI_AR-0000046592-0000046592.tif','2022049_MNDWI_AR-0000093184-0000000000.tif','2022049_MNDWI_AR-0000093184-0000046592.tif')
		lista_water = ('2022049_MNDWI_AR_water-0000000000-0000000000.tif' ,'2022049_MNDWI_AR_water-0000000000-0000032768.tif','2022049_MNDWI_AR_water-0000000000-0000065536.tif','2022049_MNDWI_AR_water-0000032768-0000000000.tif','2022049_MNDWI_AR_water-0000032768-0000032768.tif','2022049_MNDWI_AR_water-0000065536-0000000000.tif','2022049_MNDWI_AR_water-0000065536-0000032768.tif','2022049_MNDWI_AR_water-0000098304-0000000000.tif','2022049_MNDWI_AR_water-0000098304-0000032768.tif')
	elif pais == "PY":
		lista_mndwi = ['2022049_MNDWI_PY.tif']
		lista_water = ['2022049_MNDWI_PY_water.tif']
	elif pais == "UY":
		lista_mndwi = ['2022049_MNDWI_UY.tif']
		lista_water = ['2022049_MNDWI_UY_water.tif']
	else:
		lista_mndwi = ['2022049_MNDWI_BR-0000046592-0000139776.tif','2022049_MNDWI_BR-0000093184-0000046592.tif','2022049_MNDWI_BR-0000093184-0000093184.tif','2022049_MNDWI_BR-0000093184-0000139776.tif','2022049_MNDWI_BR-0000139776-0000046592.tif','2022049_MNDWI_BR-0000000000-0000000000.tif','2022049_MNDWI_BR-0000000000-0000046592.tif','2022049_MNDWI_BR-0000000000-0000093184.tif','2022049_MNDWI_BR-0000000000-0000139776.tif','2022049_MNDWI_BR-0000046592-0000000000.tif','2022049_MNDWI_BR-0000046592-0000046592.tif','2022049_MNDWI_BR-0000046592-0000093184.tif','2022049_MNDWI_BR-0000046592-0000139776.tif','2022049_MNDWI_BR-0000093184-0000046592.tif','2022049_MNDWI_BR-0000093184-0000093184.tif','2022049_MNDWI_BR-0000093184-0000139776.tif','2022049_MNDWI_BR-0000139776-0000046592.tif']
		lista_water = ['2022049_MNDWI_BR_water-0000000000-0000000000.tif','2022049_MNDWI_BR_water-0000000000-0000032768.tif','2022049_MNDWI_BR_water-0000000000-0000065536.tif','2022049_MNDWI_BR_water-0000000000-0000098304.tif','2022049_MNDWI_BR_water-0000032768-0000000000.tif','2022049_MNDWI_BR_water-0000032768-0000032768.tif','2022049_MNDWI_BR_water-0000032768-0000065536.tif','2022049_MNDWI_BR_water-0000032768-0000098304.tif','2022049_MNDWI_BR_water-0000032768-0000131072.tif','2022049_MNDWI_BR_water-0000065536-0000032768.tif','2022049_MNDWI_BR_water-0000065536-0000065536.tif','2022049_MNDWI_BR_water-0000065536-0000098304.tif','2022049_MNDWI_BR_water-0000065536-0000131072.tif','2022049_MNDWI_BR_water-0000065536-0000163840.tif','2022049_MNDWI_BR_water-0000098304-0000032768.tif','2022049_MNDWI_BR_water-0000098304-0000065536.tif','2022049_MNDWI_BR_water-0000098304-0000098304.tif','2022049_MNDWI_BR_water-0000131072-0000032768.tif','2022049_MNDWI_BR_water-0000131072-0000065536.tif']

	print(len(lista_mndwi))
	lista_img = glob.glob("*.tif")
	for i, entrada in enumerate(lista_mndwi):
		splited = entrada.split("-")
		if len(splited)>1:
			salida = splited[0]+'_'+str(i)+'.tif'
		else:
			salida = splited[0][:-4]+'_'+str(i)+'.tif'

		if salida in lista_img:
			pass
		else:
			print(salida)
			os.system("gdal_translate -of GTiff -tr %s %s -a_nodata %i -co compress=LZW %s %s"%(resx,resy,0,entrada,salida))
			subirtiff(salida, estilo_mndwi, ws_mndwi, user, passw, ipgeo, port)

	for i, entrada in enumerate(lista_water):
		splited = entrada.split("-")
		if len(splited)>1:
			salida = splited[0]+'_'+str(i)+'.tif'
		else:
			salida = splited[0][:-4]+'_'+str(i)+'.tif'

		if salida in lista_img:
			pass
		else:
			print(salida)
			os.system("gdal_translate -of GTiff -tr %s %s -a_nodata %i -co compress=LZW %s %s"%(resx,resy,0,entrada,salida))
			subirtiff(salida, estilo_mndwi_water, ws_mndwi_water, user, passw, ipgeo, port)

