"""Module to convert dictionaries to RDF graphs."""

import ast
from contextlib import suppress
from datetime import datetime
import pandas as pd
import dateutil.parser as dateparser
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import DC, FOAF, RDF, RDFS, SDO

from . import Node
from .faker.faker import Faker
from .incrementals.incrementals import Incremental
from .null_objects.factory import Boolean, DateTime, Double, Float, Integer, String
from .null_objects.null_objects import NoneLiteral, NoneNode
from .null_objects.safe_objects import SafeGraph, SafeNamespace
from .wrappers.wrappers import default_to_incremental, default_to_NoneNode

IO = SafeNamespace("http://www.semanticweb.org/luciana/ontologies/2024/8/inmontology#")
PR = SafeNamespace("https://raw.githubusercontent.com/fdioguardi/pronto/main/ontology/pronto.owl#")
SIOC = SafeNamespace("http://rdfs.org/sioc/ns#")
GR = SafeNamespace("http://purl.org/goodrelations/v1#")
REC = SafeNamespace("https://w3id.org/rec#")
TIME = SafeNamespace("http://www.w3.org/2006/time#")
BRICK = SafeNamespace("https://brickschema.org/schema/Brick#")

# COMENTARIO - Este método se puede modularizar, tiene cosas específicas de AVE
def add_real_estate(g: Graph, row: dict) -> Node:
    """
    Add real estate to the graph `g` and return the real estate's
    `Node`.
    """   
    real_estate: Node = _create_real_estate()
    land: Node = _create_space("land")  
    building: Node = _create_space("building")  
    
    g.add((real_estate, RDF.type, IO[str(row.get("property_type")).capitalize()])) #subclase de RealEstate
    if not (IO[str(row.get("property_type")).capitalize()], RDFS.subClassOf, REC.RealEstate) in g:
        g.add((IO[str(row.get("property_type")).capitalize()], RDFS.subClassOf, REC.RealEstate))

    g.add((land, RDF.type, REC.Site))
    g.add((building, RDF.type, REC.Building))

    #-----
    point: Node = BNode()
    g.add((point, RDF.type, REC.Point))
    g.add((land, REC.geometry, point)) ##tiene uno que se llama point también, no sé
    g.add((point, REC.coordinates, String(f"[{row.get('latitude')},{row.get('longitude')}]")))
    #-----

    district: Node = _create_district(try_if_row_exists(row, "district"), try_if_row_exists(row, "province"))
    province: Node = _create_province(try_if_row_exists(row, "province"))
    
    # COMENTARIO - El barrio es del AVE y el neighborhood es del Scraper
    barrio = row.get("neighborhood") or row.get("barrio")
    neighborhood : Node = _create_neighborhood(province, district, barrio)

    g.add((district, RDF.type, IO.City))
    g.add((district, RDFS.label, String(row.get("district"))))
    
    g.add((province, RDF.type, IO.Province))
    g.add((province, RDFS.label, String(row.get("province"))))

    if row.get("address"):
        add_address(g, real_estate, IO.Scraper, str(row.get("address")), neighborhood, district, province, try_obtain_date(row, "date_published"))
    if row.get("direccion"):
        add_address(g, real_estate, IO.AVE, str(row.get("direccion")), neighborhood, district, province, try_obtain_date(row, "date_ave"))

    # if row.get("neighborhood"):
    #     add_neighborhood(g, real_estate, IO.hasScraperValue, IO.hasScraperTime, str(row["neighborhood"]), district, province, dateparser.parse(row.get("date_extracted")))
    # if row.get("barrio"):
    #     add_neighborhood(g, real_estate, IO.hasAVEValue, IO.hasAVETime, str(row["barrio"]), district, province, dateparser.parse(row.get("date_ave")))

    
    g.add((real_estate, REC.includes, land))
    g.add((real_estate, REC.includes, building))
    g.add((land, BRICK.hasPart, building))


    # g.add((real_estate, REC.locatedIn, district))
    # g.add((real_estate, REC.locatedIn, province))
    g.add((neighborhood, REC.locatedIn, district))

    g.add((district, REC.locatedIn, province))
    #---

    # if row.get("year_built"):
    #     g.add((space, SDO.yearBuilt, Integer(int(float(row.get("year_built", 0))))))

    # property_mapping = {
    #     "is_new_property": PR.is_brand_new,
    #     "is_finished": PR.is_finished,
    #     "is_studio_apartment": PR.is_studio_apartment,
    # }

    # for name, p in property_mapping.items():
    #     g.add((space, p, Boolean(None if row.get(name) == "" else row.get(name))))

    # g.add((space, PR.luminosity, String(row.get("luminosity"))))
    # g.add((space, PR.orientation, String(row.get("orientation"))))
    # g.add((space, PR.disposition, String(row.get("disposition"))))

    # add features to LAND
    for s in ["esquina", "pileta", "loteo_ph",  "indiviso", "irregular"]:
        with suppress(KeyError):
            if row[s] == "True":
                value = row[s] == "True"
            else:
                value = row[s]

            if value:
                add_feature(g, land, s, value, try_obtain_date(row, "date_ave"))
    if (row.get("medidas")):
        # Mariano: "date_ave" no existe en el documento
        #           Habría que ver si se tiene que utilizar
        #           una fecha por defecto en el caso de que
        #           esta no se encuentre, o si tenemos que
        #           utilizar una de las otras fechas que
        #           están en el csv, como la del scrapper
        add_dimensiones(g, land, str(row.get("medidas")), try_obtain_date(row, "date_ave"))

    #add features to BUILDING
    for s in ["es_monetizable", "a_demoler"]:
        with suppress(KeyError):
            if row[s] == "True":
                value = row[s] == "True"
            else:
                value = row[s]

            if value:
                add_feature(g, building, s, value, try_obtain_date(row, "date_ave"))

    #add features to REAL ESTATE
    for s in ["es_multioferta", "preventa", "posesion"]:
        with suppress(KeyError):
            if row[s] == "True":
                value = row[s] == "True"
            else:
                value = row[s]

            if value:
                add_feature(g, real_estate, s, value, try_obtain_date(row, "data_ave"))

        

    # features: dict = ast.literal_eval(row.get("features") or "{}")
    # for feature, value in features.items():
    #     add_feature(g, real_estate, feature, value, dateparser.parse(row.get("date_extracted")))
    
    # add surfaces
    for s in ["total", "covered", "uncovered", "land"]:
        with suppress(KeyError):
            value = row[f"{s}_surface"] or row[f"reconstructed_{s}_surface"]
            unit = row[f"{s}_surface_unit"] or row[f"reconstructed_{s}_surface_unit"]

            if value and unit:
                add_surface(g, land, value, unit, s, dateparser.parse(row.get("date_extracted")))

    # add amount of rooms
    g.add((building, PR.has_number_of_rooms, Integer(row.get("room_amnt"))))
    rooms: dict[str, Node] = {
        "bath": REC.Bathroom,
        "garage": REC.Garage,
        "bed": REC.Bedroom,
        "toilette": REC.Toilet,
    }
    for room, room_class in rooms.items():
        add_room(g, building, row, room, room_class)
   
    return real_estate

def add_dimensiones(g: Graph, land: Node, value: str, date: datetime|None) -> Node:
    """Add dimensions to the graph g and return the surface's Node."""
    dimensionsValue: Node = BNode()
    featureDimensions: Node = create_feature(land, "dimensions")
    dateNode: Node = BNode() 
    
    g.add((dimensionsValue, RDF.type, PR.SizeSpecification))
    g.add((dimensionsValue, GR.hasValue, String(value)))
    g.add((dimensionsValue, GR.hasUnitOfMeasurement, String("metros")))
    g.add((dimensionsValue, PR.size_type, String("lot dimensions")))
    
    g.add((featureDimensions, RDF.type, IO.Dimensiones))
    g.add((featureDimensions, IO.hasOrigin, IO.AVE))
    g.add((featureDimensions, IO.hasValue, dimensionsValue))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featureDimensions, TIME.hasTime, dateNode))

    g.add((land, IO.hasFeature, featureDimensions))

    return dimensionsValue

# COMENTARIO - No se puede modularizar mas
def add_address(g: Graph, real_estate: Node, origin: URIRef, address: str, neighborhood: Node, district: Node, province: Node, date: datetime|None) -> Node:
    """Add address to the graph g and return the address's Node."""
    addressValue: Node = BNode()
    featureAddress: Node = create_feature(real_estate, "address")
    dateNode: Node = BNode()
    
    g.add((addressValue, RDF.type, IO.PostalAddress))
    g.add((addressValue, IO.address, String(address)))
    g.add((addressValue, IO.neighborhood, neighborhood))
    g.add((addressValue, IO.city, district))
    g.add((addressValue, IO.province, province))
    g.add((featureAddress, IO.hasValue, addressValue))

    g.add((featureAddress, RDF.type, IO.Direccion))
    g.add((featureAddress, IO.hasOrigin, origin))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featureAddress, TIME.hasTime, dateNode))

    g.add((real_estate, IO.hasFeature, featureAddress))

    return addressValue

# ESTE MÉTODO LO USAN AMBOS
def add_feature(g: Graph, space: Node, featureName :str, value, date: datetime|None) -> Node: 
    featureValue: Node = BNode()
    feature: Node = create_feature(space, featureName)
    dateNode: Node = BNode() 
    
    g.add((featureValue, RDF.type, RDFS.Literal))
    if (type(value)==int):
        g.add((featureValue, RDFS.label, Integer(value)))
    if (type(value)==float):
        g.add((featureValue, RDFS.label, Double(value)))
    if (type(value)==str):
        g.add((featureValue, RDFS.label, String(value)))
    if (type(value)==bool):
        g.add((featureValue, RDFS.label, Boolean(value)))
    
    g.add((feature, RDF.type, IO[featureName.capitalize()]))
    g.add((feature, IO.hasValue, featureValue))
    g.add((feature, IO.hasOrigin, IO.AVE))
    
    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((feature, TIME.hasTime, dateNode))
    

    if not (IO[featureName.capitalize()], RDFS.subClassOf, IO.Feature) in g:
        g.add((IO[featureName.capitalize()], RDFS.subClassOf, IO.Feature))


    g.add((space, IO.hasFeature, feature))

    return featureValue