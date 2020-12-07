import pandas as pd
from normalize import normalize_text

output_ontology = "Location_Ontology.ttl"


uri_template = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Federative_Unit/$var>"
data = pd.read_csv("estados.csv",sep=";",encoding="utf8")

uris = ""
out_string = ""
with open(output_ontology,"a+") as out_file:
	for index, row in data.iterrows():
		estado = normalize_text(str(row[0]).replace("\n",""))
		uri = uri_template.replace("$var",estado)
		uris+=uri+"\n"
		out_string+= """ 
###  http://www.sefaz.ma.gov.br/IBGE/Location/resource/Federative_Unit/$estado
<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Federative_Unit/$estado> rdf:type owl:NamedIndividual ,
                                                                           loc:Federative_Unit ;
                                                                  loc:is_part_of <http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/BRASIL> ;
                                                                  loc:abbreviation_UF "$id"^^xsd:string ;
                                                                  rdfs:label "$label"^^xsd:string , "$id"^^xsd:string ;
                                                                  skos:skos:prefLabel "$label"^^xsd:string ;
                                                                  loc:uf_code_IBGE "$code_uf"^^xsd:string ;
                                                                  owl:sameAs <$dbpedia> .

		""".replace("$id",str(row[1])).replace("$label",str(row[0]).replace("\n","")).replace("$dbpedia",str(row[2])).replace('$estado',estado).replace("$code_uf",str(row[3]))
	out_string+= """
[ rdf:type owl:AllDifferent ;
	owl:distinctMembers ($vars)
] .
	""".replace("$vars",uris)
	out_string+= """
loc:Federative_Unit owl:equivalentClass [ rdf:type owl:Class ;
		owl:oneOf (
		$vars)
	] .
	""".replace("$vars",uris)
	out_file.write(out_string)