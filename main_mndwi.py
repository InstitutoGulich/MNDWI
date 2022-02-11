## Packages
import ee
from datetime import datetime, timedelta
import sys

##*************************************
## Functions
##*************************************

def feat2mask(feat):
  return feat.set('prop',1);

# Mask inside geometry
def maskInside(image, geometry):
  mask = ee.Image.constant(1).clip(geometry)
  return image.updateMask(mask)

# Convert image to int16
def convertBit(image):
    return image.multiply(1000).int16()

# Transform date to GEE format
def getDates(startYear, startJDay, endJDay):
    startDate = datetime.datetime(startYear, 1, 1) + datetime.timedelta(startJDay - 1)
    startMonth= int(startDate.strftime('%m'))
    startDay = int(startDate.strftime('%d'))

    endDate = datetime.datetime(startYear, 1, 1) + datetime.timedelta(endJDay - 1)
    endYear = 2000+int(endDate.strftime('%y'))
    endMonth= int(endDate.strftime('%m'))
    endDay = int(endDate.strftime('%d'))

    startDate = ee.Date.fromYMD(startYear,startMonth,startDay) #(inclusive)
    endDate = ee.Date.fromYMD(endYear,endMonth,endDay) #(exclusive)

    return startDate, endDate

# Get date from year and julian day
def getDate(startYear,startJDay):
    startDate = datetime(startYear, 1, 1) + timedelta(startJDay - 1)
    startMonth= int(startDate.strftime('%m'))
    startDay = int(startDate.strftime('%d'))

    startDate = ee.Date.fromYMD(startYear,startMonth,startDay) #(inclusive)

    return startDate

# Get index and bands to be processed
def getIndexData(product):
    if product=='COPERNICUS/S2':
        idxData = {'GREEN':'B3', 'SWIR1':'B11', 'name':'MNDWI'}
        
    elif product=='COPERNICUS/S2_SR':
        idxData = {'GREEN':'B3', 'SWIR1':'B11', 'name':'MNDWI'}
        
    elif product=='LANDSAT/LC08/C01/T1_SR':
        idxData = {'GREEN':'B3', 'SWIR1':'B6', 'name':'MNDWI'}

    elif product=='MODIS/006/MOD09A1':
        idxData = {'GREEN':'sur_refl_b04', 'SWIR1':'sur_refl_b06', 'name':'MNDWI'}

    return idxData

def save2drive(img1,scale,prefix,aoi,folder):
    task = ee.batch.Export.image.toDrive(image = img1.clip(aoi),
                                     description = prefix,
                                     folder = folder,
#                                     region= cordoba.bounds().getInfo()['coordinates'],
                                     region = aoi.geometry(),
                                     scale = scale,
                                     fileFormat = 'GeoTIFF',
                                     maxPixels = 10000000000000,
                                     skipEmptyTiles = True)
    task.start()

    
##*************************************
# Clouds masks
##*************************************

# Utility to extract bitmask values.
# Look up the bit-ranges in the catalog.
#
# value - ee.Number or ee.Image to extract from.
# fromBit - int or ee.Number with the first bit.
# toBit - int or ee.Number with the last bit (inclusive).
#         Defaults to fromBit.
def bitwiseExtract(value, fromBit, toBit):
    if toBit == 0: toBit = fromBit
    maskSize = ee.Number(1).add(toBit).subtract(fromBit)
    mask = ee.Number(1).leftShift(maskSize).subtract(1)
    return value.rightShift(fromBit).bitwiseAnd(mask)


def getQABits(image, start, end, mascara):
    # Compute the bits we need to extract.
    pattern = 0
    for i in range(start,end-1):
        pattern += 2**i
    # Return a single band image of the extracted QA bits, giving the     band a new name.
    return image.select([0], [mascara]).bitwiseAnd(pattern).rightShift(start)

#A function to mask out cloudy pixels L8sr
#   image: image to mask
def maskL8srclouds(image):
    # Select the QA band.
    QA = image.select('pixel_qa')
    # Get the internal_cloud_algorithm_flag bit.
    sombra = getQABits(QA,3,3,'cloud_shadow')
    nubes = getQABits(QA,5,5,'cloud')
    cirrus_detected = getQABits(QA,9,9,'cirrus_detected')
    #var cirrus_detected2 = getQABits(QA,8,8,  'cirrus_detected2')
    #Return an image masking out cloudy areas.
    return image.updateMask(sombra.eq(0)).updateMask(nubes.eq(0).updateMask(cirrus_detected.eq(0)))

#A function to mask out cloudy pixels S2
#   image: image to mask
def maskS2clouds(image):
    qa = image.select('QA60');
    cloudBitMask = 1 << 10;
    cirrusBitMask = 1 << 11;
    mask1 = qa.bitwiseAnd(cloudBitMask).eq(0)
    mask2 = qa.bitwiseAnd(cirrusBitMask).eq(0)
    return image.updateMask(mask1).updateMask(mask2)

#A function to mask out cloudy pixels MODIS09A1
#   image: image to mask
def maskM09clouds(image):
    # Select the QA band.
    qa = image.select('StateQA')
    cloudState = bitwiseExtract(qa, 0, 1)
    cloudShadowState = bitwiseExtract(qa, 2, 0)
    cirrusState = bitwiseExtract(qa, 8, 9)
    mask1 = cloudState.eq(0) # Clear
    mask2 = cloudShadowState.eq(0) # No cloud shadow
    mask3 = cirrusState.eq(0) # No cirrus
    return image.updateMask(mask1).updateMask(mask2).updateMask(mask3)

#Functions to out cloudy pixels S2_SR
CLOUD_FILTER = 60
CLD_PRB_THRESH = 50
NIR_DRK_THRESH = 0.15
CLD_PRJ_DIST = 1
BUFFER = 50

def apply_cld_shdw_mask(img):
    # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
    not_cld_shdw = img.select('cloudmask').Not()

    # Subset reflectance bands and update their masks, return the result.
    #return img.select('B.*').updateMask(not_cld_shdw)
    return img.select(['B2', 'B3', 'B4', 'B8', 'B11', "MNDWI"]).updateMask(not_cld_shdw)
    
    
def add_cld_shdw_mask(img):
    img_cloud = add_cloud_bands(img)
    img_cloud_shadow = add_shadow_bands(img_cloud)
    is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)
    is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(BUFFER*2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))

    return img_cloud_shadow.addBands(is_cld_shdw)


def add_shadow_bands(img):
    not_water = img.select('SCL').neq(6)
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')
    shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')))
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))


def add_cloud_bands(img):
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')
    return img.addBands(ee.Image([cld_prb, is_cloud]))



# Función para el cálculo del MNDWI
#   m: mapa folium donde se debe agregar el índice
#   startDate: fecha de inicio (inclusive)
#   endDate: fecha de finalización (exclusive)
#   region: region de interés donde calcular el índice
def Indice_gee(product,startDate,endDate,region,idxData):

    # Determinación de máscara de recurrencia de agua
    waterOcc = ee.Image("JRC/GSW1_0/GlobalSurfaceWater").select('occurrence')
    jrc_data0 = ee.Image("JRC/GSW1_0/Metadata").select('total_obs').lte(0)
    waterOccFilled = waterOcc.unmask(0).max(jrc_data0)
    waterMask = waterOccFilled.lt(60)

    # Función para calcular el MNDWI y agregarlo como banda a la imagen
    # Bandas y nombre de índice hardcoded. Modificar para que sean parámetros.
    #   image: imagen sobre la que se calcula el índice y a la que le agrega el mismo como banda con el nombre MNDWI
    def addIndex(image):
        idx = image.normalizedDifference([idxData['GREEN'],idxData['SWIR1']]).rename(idxData['name'])
        mask = idx.lte(1.00)
        return image.addBands(idx).updateMask(mask);


    ## Main
    if product=='COPERNICUS/S2':

        # prodCollection: colección de iḿagenes filtradas por fecha y nubosidad
        prodCollection = ee.ImageCollection(product).filterBounds(region).filterDate(startDate,endDate).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))

        # Se agrega el índice como banda a la colección de imágenes
        prodCollection = prodCollection.map(addIndex);

        # Se aplica máscara de nubes a la colección de imágenes
        prodCollection = prodCollection.map(maskS2clouds)

    elif product=='COPERNICUS/S2_SR':
        s2_sr_col = ee.ImageCollection(product).filterBounds(region).filterDate(startDate,endDate)  \
                    .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER))
    
    
        s2_cloudless_col = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY') \
                        .filterBounds(region).filterDate(startDate, endDate)
    
        prodCollection= ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
            'primary': s2_sr_col,
            'secondary': s2_cloudless_col,
            'condition': ee.Filter.equals(**{
                'leftField': 'system:index',
                'rightField': 'system:index'
            })
        }))

        prodCollection = prodCollection.select(['B2', 'B3', 'B4', 'B8', 'B11', 'SCL'])
        prodCollection = prodCollection.map(addIndex)
        prodCollection = prodCollection.map(add_cld_shdw_mask)
        prodCollection = prodCollection.map(apply_cld_shdw_mask)
        
    elif product=='LANDSAT/LC08/C01/T1_SR':

        # prodCollection: colección de iḿagenes filtradas por fecha y nubosidad
        prodCollection = ee.ImageCollection(product).filterBounds(region).filterDate(startDate,endDate).filter(ee.Filter.lt('CLOUD_COVER', 10))

        # Se agrega el índice como banda a la colección de imágenes
        prodCollection = prodCollection.map(addIndex);

        # Se aplica máscara de nubes a la colección de imágenes
        prodCollection = prodCollection.map(maskL8srclouds)

    else:

        # prodCollection: colección de iḿagenes filtradas por fecha y nubosidad
        prodCollection = ee.ImageCollection(product).filterBounds(region).filterDate(startDate,endDate)

        # Se agrega el índice como banda a la colección de imágenes
        prodCollection = prodCollection.map(addIndex);

        # Se aplica máscara de nubes a la colección de imágenes
        prodCollection = prodCollection.map(maskM09clouds)

    count = prodCollection.size().getInfo()

#    print(count)
    if count == 0:
        return 'nodata'
    else:
        prodCollectionIndex = prodCollection.select(idxData['name']).mean()#.updateMask(waterMask)

#    return prodCollectionIndex.clip(region), color_real.clip(region)
        return prodCollectionIndex.clip(region)




#### MAIN
### Definición de parámetros generales

# Esta línea se corre sólo la primera vez que se quiere acceder a GEE para autorizar la compu a acceder al servicio.
# Luego no hace falta volver a utilizar
#ee.Authenticate()

# Se inicializa el GEE
ee.Initialize()

# Se define la región de interés
#region = ee.FeatureCollection("users/sectec/Zonas_INTA")
#zonas = ee.FeatureCollection("users/sectec/zonas_agro")
global mndwi
global real

DELTA = 0.10
THRESHOLD = 0.02
imageList = ee.List([])

fecha = sys.argv[1] #Fecha de procesamiento
pais = sys.argv[2] #País de procesamiento

startYear = int(fecha[0:4])
startJDay = int(fecha[-3:])
endJDay = startJDay + 8
if endJDay > 365:
	endJDay = endJDay - 365
	endYear = startYear + 1
else:
	endYear = startYear
startDate = getDate(startYear, startJDay)
endDate = getDate(endYear, endJDay)

#print(startDate)
#print(endDate)

country = ee.FeatureCollection("users/sectec/"+pais)
country = country.map(feat2mask)
countryMask = country.reduceToImage(['prop'],ee.Reducer.first())

#countryList = country.toList(country.size().getInfo())

#feat = ee.Feature(countryList.get(0))
feat = country
prop = pais#feat.get("HASC_1").getInfo()

# Producto a consultar
prod = 'COPERNICUS/S2_SR'
indexData = getIndexData(prod) #dicc con bandas e indice
mndwiS2 = Indice_gee(prod,startDate,endDate,feat.geometry(),indexData)

prod = 'LANDSAT/LC08/C01/T1_SR'
indexData = getIndexData(prod) #dicc con bandas e indice
mndwiL8 = Indice_gee(prod,startDate,endDate,feat.geometry(),indexData) 
    
prod = 'MODIS/006/MOD09A1'
indexData = getIndexData(prod) #dicc con bandas e indice
mndwiM9 = Indice_gee(prod,startDate,endDate,feat.geometry(),indexData) 

description = str(startYear)+"%03i"%startJDay+"_MNDWI_"+prop
        
# S2=No
if mndwiS2 == 'nodata':
    # S2=No - L8=No
    if mndwiL8 == 'nodata':
        # S2=No - L8=No - M9=No
        if mndwiM9 == 'nodata':
            mndwiS2L8M9 = 'nodata'
        # S2=No - L8=No - M9=Si
        else:
            mndwiS2L8M9 = mndwiM9
    # S2=No - L8=Si 
    else:
        # S2=No - L8=Si - M9=No
        if mndwiM9 == 'nodata':
            mndwiS2L8M9 = mndwiL8
        # S2=No - L8=Si - M9=Si
        else:
            mndwiS2L8M9 = ee.ImageCollection([mndwiM9,mndwiL8]).mosaic()
# S2=Si
else:
    # S2=Si - L8=No
    if mndwiL8 == 'nodata':
        # S2=Si - L8=No - M9=No
        if mndwiM9 == 'nodata':
            mndwiS2L8M9 = mndwiS2
        # S2=Si - L8=No - M9=Si
        else:
            mndwiS2L8M9 = ee.ImageCollection([mndwiM9,mndwiS2]).mosaic()
    # S2=Si - L8=Si
    else:
        # S2=Si - L8=Si - M9=No
        if mndwiM9 == 'nodata':
            mndwiS2L8M9 = ee.ImageCollection([mndwiL8,mndwiS2]).mosaic()
        # S2=Si - L8=Si - M9=Si
        else:
            mndwiS2L8M9 = ee.ImageCollection([mndwiM9,mndwiL8,mndwiS2]).mosaic()
          
if mndwiS2L8M9 == 'nodata':
    pass
else:
    img = mndwiS2L8M9
    water0 = img.gte(ee.Number(THRESHOLD).subtract(DELTA)).int16()
    water1 = img.gte(ee.Number(THRESHOLD).subtract(DELTA)).And(img.lt(ee.Number(THRESHOLD))).int16()
    water2 = (img.gte(ee.Number(THRESHOLD)).And(img.lt(ee.Number(THRESHOLD).add(DELTA)))).multiply(2).int16()
    water3 = (img.gte(ee.Number(THRESHOLD).add(DELTA))).multiply(3).int16()
    imgRes = water1.add(water2).add(water3)
    masked = imgRes.updateMask(imgRes)
    save2drive(masked,30,description+"_water",feat,"_"+pais+".")
    
    image = convertBit(mndwiS2L8M9)
    masked = image.updateMask(countryMask)
    save2drive(masked,30,description,feat,"_"+pais+".")
            
