
import os

files = os.listdir('/home/lucas/Desktop/DLM50_RLP')

nr = 0

for file in files:
    
    nr = file[22:31]
    
    $ ogr2ogr -where "OGR_GEOMETRY='Point'" -f "ESRI Shapefile" transit_points.shp transit.kml
$ ogr2ogr -where "OGR_GEOMETRY='LineString'" -f "ESRI Shapefile" transit_linestrings.shp transit.kml
    
    
    toRUN = "ogr2ogr -skipfailures -nlt geometry -f \"esri shapefile\" '/home/lucas/Desktop/DLM50_RLP/output_"+str(nr)+"' '/home/lucas/Desktop/DLM50_RLP/"+str(file)+"'"

    os.system(toRUN)
    
files = os.listdir('/home/lucas/Desktop/DLM50_RLP')

files = list(i for i in files if 'output' in i)

toMERGE = ['AX_WegPfadSteig.shp','AX_UnlandVegetationsloseFlaeche.shp','AX_StehendesGewaesser.shp','AX_Siedlungsflaeche.shp','AX_Leitung.shp','AX_Landwirtschaft.shp','AX_IndustrieUndGewerbeflaeche.shp','AX_Gewaesserachse.shp','AX_Fahrwegachse.shp','AX_BauwerkImGewaesserbereich.shp','AX_Bahnstrecke.shp','AX_Vegetationsmerkmal.shp','AX_Strassenachse.shp','AX_SportFreizeitUndErholungsflaeche.shp','AX_Gehoelz.shp','AX_Gebietsgrenze.shp','AX_FlaecheBesondererFunktionalerPraegung.shp','AX_BauwerkOderAnlageFuerSportFreizeitUndErholung.shp','AX_BauwerkImVerkehrsbereich.shp','AX_Wohnplatz.shp','AX_Strassenverkehrsanlage.shp','AX_Ortslage.shp','AX_Gewaessermerkmal.shp','AX_Gebaeude.shp','AX_Platz.shp','AX_NaturUmweltOderBodenschutzrecht.shp','AX_KommunalesGebiet.shp','AX_Friedhof.shp','AX_FelsenFelsblockFelsnadel.shp','AX_DammWallDeich.shp','AX_Bahnverkehr.shp','AX_Strassenverkehr.shp','AX_SonstigesBauwerkOderSonstigeEinrichtung.shp','AX_Fliessgewaesser.shp','AX_TagebauGrubeSteinbruch.shp','AX_Halde.shp','AX_Sumpf.shp','AX_Bahnverkehrsanlage.shp','AX_HistorischesBauwerkOderHistorischeEinrichtung.shp','AX_BauwerkOderAnlageFuerIndustrieUndGewerbe.shp','AX_Schiffsverkehr.shp','AX_Hafen.shp','AX_SchifffahrtslinieFaehrverkehr.shp','AX_Insel.shp','AX_Bergbaubetrieb.shp','AX_Transportanlage.shp','AX_Kondominium.shp','AX_Wasserspiegelhoehe.shp','AX_Schutzzone.shp','AX_Heide.shp','AX_SeilbahnSchwebebahn.shp','AX_Flugverkehr.shp','AX_Flugverkehrsanlage.shp','AX_FlaecheZurZeitUnbestimmbar.shp','AX_Hafenbecken.shp']

for file in files:
    
    SHPs = os.listdir('/home/lucas/Desktop/DLM50_RLP/'+str(file))
    SHPs = list(i for i in SHPs if '.shp' in i)

    if toMERGE != []: 
        
        for SHP in SHPs:
        
            if SHP in toMERGE:
                
                toMERGE.remove(SHP)
                                
                toRUN = "ogr2ogr -skipfailures -f \"ESRI Shapefile\" '/home/lucas/Desktop/DLM50_RLP/"+str(SHP)+"' '/home/lucas/Desktop/DLM50_RLP/"+str(file)+'/'+str(SHP)+"'"
    
                os.system(toRUN)
    
    for SHP in SHPs:            

        toRUN = "ogr2ogr -skipfailures -f \"ESRI Shapefile\" -append -update '/home/lucas/Desktop/DLM50_RLP/"+str(SHP)+"' '/home/lucas/Desktop/DLM50_RLP/"+str(file)+'/'+str(SHP)+"'"   

        os.system(toRUN)
