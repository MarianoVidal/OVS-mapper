from ..wrappers.wrappers import default_to_incremental, default_to_NoneNode
from ..incrementals.incrementals import Incremental
from rdflib.namespace import DC, FOAF, RDF, RDFS, SDO
from ..null_objects.safe_objects import  SafeNamespace
from .. import Node
from rdflib import BNode, Graph, URIRef


# Namespaces
IO = SafeNamespace("http://www.semanticweb.org/luciana/ontologies/2024/8/inmontology#")
PR = SafeNamespace("https://raw.githubusercontent.com/fdioguardi/pronto/main/ontology/pronto.owl#")
SIOC = SafeNamespace("http://rdfs.org/sioc/ns#")
GR = SafeNamespace("http://purl.org/goodrelations/v1#")
REC = SafeNamespace("https://w3id.org/rec#")
TIME = SafeNamespace("http://www.w3.org/2006/time#")
BRICK = SafeNamespace("https://brickschema.org/schema/Brick#")

class Create() :

    def __init__(self):
        pass
    
    @classmethod
    @default_to_incremental(PR, Incremental.LISTING)
    def create_listing(row : dict):
        return IO[f"listing_{row['site']}_{row['listing_id']}"]

    @classmethod
    @default_to_NoneNode
    def create_agent(row : dict):
        return IO[f"agent_{row['advertiser_name']}"]
    @classmethod
    @default_to_NoneNode
    def create_account(row : dict):
        return IO[f"account_{row['site']}_{row['advertiser_id']}"]

    @classmethod
    @default_to_incremental(PR, Incremental.REAL_ESTATE)
    def create_real_estate(row: dict) -> Node:
        return IO[f"real_estate_{row['site']}_{row['listing_id']}"]
    @classmethod
    @default_to_incremental(PR, Incremental.SPACE)
    def create_space(s_type: str, row: dict) -> Node:
        return IO[f"space_{s_type}_{row['site']}_{row['listing_id']}"]

    @classmethod
    @default_to_NoneNode
    def create_district(province:str, district:str):
        return IO[f'district_{province.replace(" ", "_")}_{district.replace(" ", "_")}']
    @classmethod
    @default_to_NoneNode
    def create_province(province:str):
        return IO[f'province_{province.replace(" ", "_")}']
    
    @classmethod
    @default_to_NoneNode
    def create_neighborhood(province:URIRef, district:URIRef, neighborhood:str):
        return IO[
            f"neiborhood_{province.fragment}_{district.fragment}_{neighborhood}"
        ]

    @classmethod
    @default_to_incremental(IO, Incremental.FEATURE)
    def create_feature(subject: Node, feature: str) -> Node:
        return IO[f"feature_{feature}_{subject.fragment}"]

    @classmethod
    def create_room(space: Node, room : str, i : int) -> Node:
        fragment = getattr(space, "fragment", None)
        if not fragment:
            return BNode()
        return IO[f"{fragment}_{room}_{i}"]