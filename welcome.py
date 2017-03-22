import MySQLdb
import os
from rtcclient.client import RTCClient
from flask import Flask, jsonify, request
import requests
import os
import urllib2
import socket
import socks
import json
import signal
from RTCClientNew import RTCClientNew
from timeit import default_timer
import xml.etree.ElementTree as ET
from datetime import datetime
#import codecs

app = Flask(__name__)
db = 0

def signal_handler(signum, frame):
    raise Exception("Timed out!")

@app.route('/')
def home(): 
    return "Cannot GET"

@app.errorhandler(500)
def server_error(error):
    if (db != 0) :
        db.close()
    print "returning5"
    return '{ "result" : 0 }'

@app.route('/migrate_tareas')
def migrate_tareas(): 
    query = "0"
    
    try:
        start = default_timer()
        url = "https://jazz.diamante.com.pe:9443/jts"
        username = "jreporting"
        password = "Diamante321"
        resource_url = "https://jazz.diamante.com.pe:9443/ccm/oslc/queries/_VQnJUF54EeaeoIoGmmsDXg/rtc_cm:results.json?oslc_cm.properties=dc:identifier,dc:title,dc:type{dc:title},rtc_cm:state{dc:title},rtc_cm:ownedBy,rtc_cm:due,rtc_cm:filedAgainst{rtc_cm:hierarchicalName},rtc_cm:plannedFor{dc:title},rtc_cm:closeActivity{dc:title}"
        query = RTCClientNew(url, username, password, resource_url, True)
        duration = default_timer() - start
        print duration
        if (duration > 120) :
            print "returning1" 
            return "{ 'result': 0 }"
        jParse = json.loads(query.getQuery())
        host="us-cdbr-iron-east-04.cleardb.net"
        user="b207514370152f"
        password="4cbd8a50"
        dbname="ad_a261e53a087dc9c"
        
        list = []
        sprint = jParse["oslc_cm:results"][0]["rtc_cm:plannedFor"]["dc:title"][0:6]

        continueNext = True
        while(continueNext):   
            if "oslc_cm:next" in jParse:
                nextU = jParse["oslc_cm:next"]
            else:
                nextU = ""
            for i in range(len(jParse["oslc_cm:results"])):
                obj = jParse["oslc_cm:results"][i]
                identifier = obj["dc:identifier"]
                tipo = obj["dc:type"]["dc:title"]
                resumen = obj["dc:title"]
                propiedad = obj["rtc_cm:ownedBy"]["rdf:resource"][44:]
                state = obj["rtc_cm:state"]["dc:title"]
                fecha_vencimiento = obj["rtc_cm:due"]
                archivado = obj["rtc_cm:filedAgainst"]["rtc_cm:hierarchicalName"]
                sprint = obj["rtc_cm:plannedFor"]["dc:title"][0:6]
                list.append((identifier, tipo, resumen, propiedad, state, fecha_vencimiento, archivado, sprint))
            if (nextU != ""):
                continueNext = True
                duration = default_timer() - start
                if (duration > 120) :
                    print "returning2"
                    return "{ 'result': 0 }"
                resource_url = nextU
                resource_url = resource_url.replace("results?oslc_cm", "results.json?oslc_cm")
                queryNew = query.get(resource_url, verify=False)
                jParse = json.loads(queryNew.content)
            else:
                continueNext = False
        db=MySQLdb.connect(host,user,password,dbname)
        c=db.cursor()
        c.execute("""DELETE from tareas WHERE sprint=%s """, (sprint,))
        c.executemany("""INSERT INTO tareas (id, tipo, resumen, propiedad, estado, fecha_vencimiento, archivado, sprint) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", list)
        db.commit()
        db.close()
        return "{ 'result': 1 }"
    except Exception, e:
        if (db != 0) :
            db.close()
        print "returning3"
        return "{ 'result': 0 }"
    print "returning4"
    return "{ 'result': 0 }"

@app.route('/migrate_proyectos')
def migrateProyectos():
    query = "0"
    
    try:
        start = default_timer()
        url = "https://jazz.diamante.com.pe:9443/jts"
        username = "jreporting"
        password = "Diamante321"
        resource_url = "https://jazz.diamante.com.pe:9443/ccm/oslc/queries/_BQiIwO7cEeafN7bgGFf5Gg/rtc_cm:results.json?oslc_cm.properties=dc:identifier,dc:title,dc:description,dc:type{dc:title},rtc_cm:state{dc:title},rtc_cm:due,rtc_cm:filedAgainst{rtc_cm:hierarchicalName},rtc_cm:ownedBy,rtc_cm:plannedFor{dc:title},dc:created,rtc_cm:due,rtc_cm:com.ibm.team.workitem.attribute.featureType{dc:title},oslc_cm:severity{dc:title},oslc_cm:priority{dc:title}"
        query = RTCClientNew(url, username, password, resource_url, True)
        duration = default_timer() - start
        if (duration > 120) :
            print "returning1" 
            return "{ 'result': 0 }"
        jParse = json.loads(query.getQuery())
        host="us-cdbr-iron-east-04.cleardb.net"
        user="b207514370152f"
        password="4cbd8a50"
        dbname="ad_a261e53a087dc9c"

        # PROYECTOS
        list_proyectos = []
        start = default_timer()
        continueNext = True
        while(continueNext):   
            if "oslc_cm:next" in jParse:
                nextU = jParse["oslc_cm:next"]
            else:
                nextU = ""
            for i in range(len(jParse["oslc_cm:results"])):
                obj = jParse["oslc_cm:results"][i]
                identifier = obj["dc:identifier"]
                resumen = obj["dc:title"]
                descripcion = obj["dc:description"]
                tipo = obj["dc:type"]["dc:title"]
                archivado = obj["rtc_cm:filedAgainst"]["rtc_cm:hierarchicalName"]
                propiedad = obj["rtc_cm:ownedBy"]["rdf:resource"][44:]
                planificado = obj["rtc_cm:plannedFor"]["dc:title"]
                fecha_creacion = obj["dc:created"]
                fecha_vencimiento = obj["rtc_cm:due"]
                tipo_necesidad = obj["rtc_cm:com.ibm.team.workitem.attribute.featureType"]["dc:title"]
                gravedad = obj["oslc_cm:severity"]["dc:title"] 
                prioridad = obj["oslc_cm:priority"]["dc:title"]               
                estado = obj["rtc_cm:state"]["dc:title"]
                list_proyectos.append((identifier, resumen, descripcion, tipo, archivado, propiedad, planificado, fecha_creacion, fecha_vencimiento, tipo_necesidad, gravedad, prioridad, estado))
            if (nextU != ""):
                continueNext = True
                duration = default_timer() - start
                if (duration > 120) :
                    print "returning2"
                    return "{ 'result': 0 }"
                resource_url = nextU
                resource_url = resource_url.replace("results?oslc_cm", "results.json?oslc_cm")
                queryNew = query.get(resource_url, verify=False)
                jParse = json.loads(queryNew.content)
            else:
                continueNext = False

        #PROYECTOS CERRADOS
        list_proyectos_cerrados = []
        start = default_timer()
        resource_url = "https://jazz.diamante.com.pe:9443/ccm/oslc/queries/_P_jwwAQLEeekPvM2pzq6kQ/rtc_cm:results.json?oslc_cm.properties=dc:identifier"
        query2 = query.get(resource_url, verify=False)
        jParse = json.loads(query2.content)
        duration = default_timer() - start
        continueNext = True
        proyectos_ids = ""
        while(continueNext):   
            if "oslc_cm:next" in jParse:
                nextU = jParse["oslc_cm:next"]
            else:
                nextU = ""
            for i in range(len(jParse["oslc_cm:results"])):
                obj = jParse["oslc_cm:results"][i]
                identifier = obj["dc:identifier"]
                proyectos_ids = proyectos_ids + str(identifier) + ","
            if (nextU != ""):
                continueNext = True
                duration = default_timer() - start
                if (duration > 120) :
                    print "returning2"
                    return "{ 'result': 0 }"
                resource_url = nextU
                resource_url = resource_url.replace("results?oslc_cm", "results.json?oslc_cm")
                queryNew = query2.get(resource_url, verify=False)
                jParse = json.loads(queryNew.content)
            else:
                print "ENDINGGGGG"
                continueNext = False

        print "PROYECTOS IDS"
        proyectos_ids = proyectos_ids[:-1]
        print proyectos_ids

        # REQUERIMIENTOS
        print "REQUERIMIENTOS"
        list_requerimientos = []
        start = default_timer()
        resource_url = "https://jazz.diamante.com.pe:9443/ccm/oslc/queries/_z8-LgO7cEeafN7bgGFf5Gg/rtc_cm:results.json?oslc_cm.properties=dc:identifier,dc:title,dc:description,dc:type{dc:title},rtc_cm:state{dc:title},rtc_cm:due,rtc_cm:filedAgainst{rtc_cm:hierarchicalName},rtc_cm:ownedBy,rtc_cm:plannedFor{dc:title},oslc_cm:severity{dc:title},oslc_cm:priority{dc:title},rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.parent{dc:identifier},rtc_cm:com.ibm.team.apt.attribute.complexity{dc:title}"
        query = query.get(resource_url, verify=False)
        jParse = json.loads(query.content)
        duration = default_timer() - start
        continueNext = True
        print "CONNECTED"
        while(continueNext):   
            if "oslc_cm:next" in jParse:
                nextU = jParse["oslc_cm:next"]
            else:
                nextU = ""
            for i in range(len(jParse["oslc_cm:results"])):
                print "ENTEEERRDEDD"
                obj = jParse["oslc_cm:results"][i]
                identifier = obj["dc:identifier"]
                resumen = obj["dc:title"]
                descripcion = obj["dc:description"]
                tipo = obj["dc:type"]["dc:title"]
                archivado = obj["rtc_cm:filedAgainst"]["rtc_cm:hierarchicalName"]
                propiedad = obj["rtc_cm:ownedBy"]["rdf:resource"][44:]
                planificado = obj["rtc_cm:plannedFor"]["dc:title"]
                fecha_vencimiento = obj["rtc_cm:due"]
                gravedad = obj["oslc_cm:severity"]["dc:title"] 
                prioridad = obj["oslc_cm:priority"]["dc:title"]               
                estado = obj["rtc_cm:state"]["dc:title"]
                print "HALF DONE"
                idProyecto = obj["rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.parent"][0]["dc:identifier"]
                print "NEARLYDONE"
                complejidad = obj["rtc_cm:com.ibm.team.apt.attribute.complexity"]["dc:title"]
                print "DONWW"
                list_requerimientos.append((identifier, resumen, descripcion, tipo, archivado, propiedad, planificado, fecha_vencimiento, gravedad, prioridad, estado, complejidad, idProyecto))
            if (nextU != ""):
                continueNext = True
                duration = default_timer() - start
                if (duration > 120) :
                    print "returning2"
                    return "{ 'result': 0 }"
                resource_url = nextU
                resource_url = resource_url.replace("results?oslc_cm", "results.json?oslc_cm")
                queryNew = query.get(resource_url, verify=False)
                jParse = json.loads(queryNew.content)
            else:
                print "ENDINGGGGG"
                continueNext = False

        # TAREAS
        print "start tareas"
        list_tareas = []
        start = default_timer()
        resource_url = "https://jreporting:Diamante321@jazz.diamante.com.pe:9443/rs/query/156/dataservice?limit=-1&basicAuthenticationEnabled=true&report=148"
        headers = {"Accept": "application/xml", "Content-Type": "application/xml"}
        req = requests.get(resource_url, headers=headers, params={})
        xmltext = req.text
        print "start tareas2"
        print "startttttt11122"
        #xmltext = unicode(xmltext.strip(codecs.BOM_UTF8), 'utf-8')
        print "startttttt"
        tree = ET.fromstring(xmltext.encode('utf-8'))
        print "start tareas3"

        test1 = list(tree)
        for element in test1:
            print element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REFERENCE_ID2").text
            identifier = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REFERENCE_ID2").text
            nombre = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}NAME2").text
            idProyecto  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REFERENCE_ID").text
            idRequerimiento  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REFERENCE_ID1").text
            tipo  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REQUEST_TYPE").text
            propietario  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}FULL_NAME").text
            fecha_vencimiento  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}DUE_DATE").text
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%m/%d/%y %I:%M %p')
            planificado  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}ITERATION_NAME").text
            archivado  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REQUEST_CATEGORY_NAME").text
            prioridad  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REQUEST_PRIORITY").text
            estado  = element.find("{https://jazz.diamante.com.pe:9443/rs/query/156/dataservice/ns}REQUEST_STATE").text
            list_tareas.append((identifier, nombre, idProyecto, idRequerimiento, tipo, propietario, fecha_vencimiento, planificado, archivado, prioridad, estado))
        db=MySQLdb.connect(host,user,password,dbname)
        c=db.cursor()
        db.set_character_set('utf8')
        c.execute("UPDATE proyectos SET seguimiento = 0 WHERE id IN (" + proyectos_ids + ")")
        c.execute("""DELETE from tareas_proyectos WHERE idProyecto in (select id from proyectos where seguimiento = 1) """)
        c.execute("""DELETE from requerimientos WHERE idProyecto in ( select id from proyectos where seguimiento = 1) """)
        c.execute("""DELETE from proyectos WHERE seguimiento = 1  """)
        c.executemany("""INSERT INTO proyectos (id, resumen, descripcion, tipo, archivado, propiedad, planificado, fecha_creacion, fecha_vencimiento, tipo_necesidad, gravedad, prioridad, estado, seguimiento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)""", list_proyectos)
        c.executemany("""INSERT INTO requerimientos (id, resumen, descripcion, tipo, archivado, propiedad, planificado, fecha_vencimiento, gravedad, prioridad, estado, complejidad, idProyecto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", list_requerimientos)
        c.executemany("""INSERT INTO tareas_proyectos (id, nombre, idProyecto, idRequerimiento, tipo, propietario, fecha_vencimiento, planificado, archivado, prioridad, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", list_tareas)
        db.commit()
        db.close()
        return "{ 'result': 1 }"
    except Exception, e:
        print e
        if (db != 0) :
            db.close()
        print "returning3"
        return "{ 'result': 0 }"
    print "returning4"
    return "{ 'result': 0 }"

port = os.getenv('PORT', '1080')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
