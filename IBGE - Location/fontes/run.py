import os
from datetime import date
import time

print("triplificando paises...")
os.system("python paises.py")
print("paises triplificados.\ntriplificando unidades federativas...")
os.system("python ufs.py")
print("unidades federativas triplificadas.\ntriplificando municípios...")
os.system("python municipios.py")
print("gerando informações de proveniência...")
with open("provenance.ttl","w") as out_file:
	today = date.today()
	provenance_graph = """
@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sfz: <http://www.sefaz.ma.gov.br/ontology/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


<http://www.sefaz.ma.gov.br/ontology/Graph/IBGE-Location-{0}> a sd:NamedGraph;
																sd:name <http://www.sefaz.ma.gov.br/ontology/Graph/IBGE-Location-{0}>;
																prov:generatedAtTime "{1}"^^xsd:dateTime;
																sfz:source_recorded "{1}"^^xsd:dateTime;
																sfz:type_view sfz:MATERIALIZED;
																rdfs:label "IBGE Location".""".format(today.strftime("%Y_%m_%d"),time.strftime("%Y-%m-%dT%H:%M:%S"))
	out_file.write(provenance_graph)
print("processo concluído com sucesso.")