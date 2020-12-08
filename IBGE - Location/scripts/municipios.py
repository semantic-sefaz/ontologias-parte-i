import pandas as pd
from normalize import normalize_text
from normalize import normalize_ascii


output_ontology = "Location_Ontology.ttl"


data = pd.read_csv("municipios.csv",sep=";",encoding="utf8")

uris = ""
uris_set = set()
out_string = ""
with open(output_ontology,"a+") as out_file:
	for index, row in data.iterrows():
		
		estado = normalize_text(str(row[1]).replace("\n",""))
		uri_estado = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Federative_Unit/$var>".replace("$var",estado)
		

		mesoregiao = normalize_text(str(row[3]).replace("\n",""))
		uri_mesoregiao = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Mesoregion/$var>".replace("$var",mesoregiao)


		microregiao = normalize_text(str(row[5]).replace("\n",""))
		uri_microregiao = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Microregion/$var>".replace("$var",microregiao)


		municipio = normalize_text(str(row[8]).replace("\n",""))
		uri_municipio = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/City/$var-$estado>".replace("$var",municipio).replace("$estado",estado)

		if uri_mesoregiao not in uris_set:
			uris_set.add(uri_mesoregiao)
			uris+=uri_mesoregiao+"\n"
			out_string+= """ 
###  $uri_mesoregiao
$uri_mesoregiao rdf:type owl:NamedIndividual ,
                        loc:Mesoregion ;
               loc:is_part_of $uri_estado ;
               loc:mesoregion_code "$meso_code"^^xsd:string ;
               rdfs:label "$label"^^xsd:string .

			""".replace("$uri_mesoregiao",uri_mesoregiao).replace("$uri_estado",uri_estado).replace("$label",str(row[3]).replace("\n","")).replace("$meso_code",str(row[2]))


		if uri_microregiao not in uris_set:
					uris_set.add(uri_microregiao)
					uris+=uri_microregiao+"\n"
					out_string+= """ 
###  $uri_microregiao
$uri_microregiao rdf:type owl:NamedIndividual ,
                           loc:Microregion ;
                  loc:is_part_of $uri_mesoregiao ;
                  loc:mircroregion_code "$micro_code"^^xsd:string ;
                  rdfs:label "$label"^^xsd:string .

					""".replace("$uri_microregiao",uri_microregiao).replace("$uri_mesoregiao",uri_mesoregiao).replace("$label",str(row[5]).replace("\n","")).replace("$micro_code",str(row[4]))


		out_string+= """ 
###  $uri_municipio
$uri_municipio rdf:type owl:NamedIndividual ,
                       loc:City ;
              loc:is_part_of $uri_microregiao ;
              loc:city_code_IBGE "$code_ibge"^^xsd:string ;
              loc:city_code_IBGE_full "$full_code_ibge"^^xsd:string ;
              skos:prefLabel "$label"^^xsd:string ;
              skos:hiddenLabel "$comp"^^xsd:string ;
              rdfs:label "$label"^^xsd:string .

					""".replace("$uri_municipio",uri_municipio).replace("$comp",normalize_ascii(row[8])).replace("$uri_microregiao",uri_microregiao).replace("$label",str(row[8]).replace("\n","")).replace("$code_ibge",str(row[6])).replace("$full_code_ibge",str(row[7]))
		uris+=uri_municipio+"\n"

	out_string+= """
[ rdf:type owl:AllDifferent ;
	owl:distinctMembers ($vars)
] .
	""".replace("$vars",uris)
	
	out_file.write(out_string)