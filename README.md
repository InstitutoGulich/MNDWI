# MNDWI
Indice satelital combinadopara detectar agua en superficie

Script para calcular en Earth Engin el índice MNWI y almacenarlo en una cuenta de Drive.

Satélites: Sentinel 2, Landsat 8, MODIS Terra
Resolución mínima: 500 mts
Resolución máxima: 30 mts

Resolución temporal: 8 días

Scripts:
  
  ScriptServidorMNDWI - Genera MNDWI y lo almacena en Drive en la carpeta _App0_Dwnld. Por el momento tanto la fecha como el país están hardcoded.
  
  drive_AR_temporal.py - Descarga de drive los MNDWI para Argentina. Por el momento la fecha se encuentra hardcoded
  
  drive_BR_temporal.py - Descarga de drive los MNDWI para Brasil. Por el momento la fecha se encuentra hardcoded
