import pandas as pd
from normalize import normalize_text

output_ontology = "Location_Ontology.ttl"


uri_template = "<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/$var>"
data = pd.read_csv("pais.csv",sep="|",encoding="utf8")

uris = ""
out_string = ""
with open(output_ontology,"a+") as out_file:
	for index, row in data.iterrows():
		country = normalize_text(str(row[1]).replace("\n",""))
		uri = uri_template.replace("$var",country)
		uris+=uri+"\n"
		out_string+= """ 
###  http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/$country
<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/$country> rdf:type owl:NamedIndividual ,
                                                                         loc:Country ;
                                                                loc:country_code "$id"^^xsd:string ;
                                                                loc:country_code_IBGE "$id"^^xsd:string ;
                                                                rdfs:label "$label"^^xsd:string ;
                                                                vcard:country-name "$label"^^xsd:string .
		""".replace("$id",str(row[0])).replace("$label",str(row[1]).replace("\n","")).replace("$country",country)
		#if row[2].is_integer():
		#	out_string+= '<http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/$country> loc:country_code_IBGE "$ibge"^^xsd:string .'.replace("$ibge",str(int(row[2]))).replace("$country",country)

	out_string+= """
[ rdf:type owl:AllDifferent ;
	owl:distinctMembers ($vars)
] .
	""".replace("$vars",uris)
	out_string+= """
loc:Country owl:equivalentClass [ rdf:type owl:Class ;
		owl:oneOf (
		$vars)
	] .
	""".replace("$vars",uris)
	out_file.write(out_string)