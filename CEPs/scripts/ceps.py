import pandas as pd
from normalize import normalize_text
from normalize import normalize_ascii
from normalize import normalize_number
from datetime import date
import time



output_ontology = "CEP_Location_Ontology.ttl"


data = pd.read_csv("CEP via TCU.csv",sep=";",encoding="utf8")

uris = ""
uris_set = set()
out_string = ""
estados = { "AC": "Acre",
			"AL": "Alagoas",
			"AP": "Amapá",
			"AM": "Amazonas",
			"BA": "Bahia",
			"CE": "Ceará",
			"ES": "Espírito Santo",
			"GO": "Goiás",
			"MA": "Maranhão",
			"MT": "Mato Grosso",
			"MS": "Mato Grosso do Sul",
			"MG": "Minas Gerais",
			"PA": "Pará",
			"PB": "Paraíba",
			"PR": "Paraná",
			"PE": "Pernambuco",
			"PI": "Piauí",
			"RJ": "Rio de Janeiro",
			"RN": "Rio Grande do Norte",
			"RS": "Rio Grande do Sul",
			"RO": "Rondônia",
			"RR": "Roraima",
			"SC": "Santa Catarina",
			"SP": "São Paulo",
			"SE": "Sergipe",
			"TO": "Tocantins",
			"DF": "Distrito Federal"
}


with open(output_ontology,"a+") as out_file:
# with open(output_ontology,"w") as out_file:
	for index, row in data.iterrows():
		#Estado
		estado = normalize_text(estados[row[4]])
		uri_estado = "<http://www.sefaz.ma.gov.br/Correios/Location/resource/Federative_Unit/$var>".replace("$var",estado)
		if uri_estado not in uris_set:
			uris_set.add(uri_estado)
			uris+= uri_estado+"\n"
			out_string+= """ 
###  http://www.sefaz.ma.gov.br/Correios/Location/resource/Federative_Unit/$estado
<http://www.sefaz.ma.gov.br/Correios/Location/resource/Federative_Unit/$estado> rdf:type owl:NamedIndividual , cor:Federative_Unit ;
	cor:is_part_of <http://www.sefaz.ma.gov.br/IBGE/Location/resource/Country/BRASIL> ;
	cor:abbreviation_UF "$id"^^xsd:string ;
	rdfs:label "$label"^^xsd:string , "$id"^^xsd:string .

			""".replace("$id",str(row[4])).replace("$label",estados[row[4]]).replace('$estado',estado)

		
		#Município
		municipio = normalize_text(str(row[3]).replace("\n",""))
		uri_municipio = "<http://www.sefaz.ma.gov.br/Correios/Location/resource/City/$var-$estado>".replace("$var",municipio).replace("$estado",estado)
		if uri_municipio not in uris_set:
			uris_set.add(uri_municipio)
			uris+= uri_municipio+"\n"
			out_string+= """ 
###  $uri_municipio
$uri_municipio rdf:type owl:NamedIndividual , cor:City ;
	cor:is_part_of $uri_estado ;
	rdfs:label "$label"^^xsd:string .

					""".replace("$uri_municipio",uri_municipio).replace("$uri_estado",uri_estado).replace("$label",str(row[3]).replace("\n",""))


		#Bairro
		bairro = normalize_text(str(row[2]).replace("\n",""))
		uri_bairro = "<http://www.sefaz.ma.gov.br/Correios/Location/resource/District/$var-$municipio>".replace("$var",bairro).replace("$municipio",municipio)
		if uri_bairro not in uris_set:
			uris_set.add(uri_bairro)
			uris+= uri_bairro+"\n"
			out_string+= """ 
###  $uri_bairro
$uri_bairro rdf:type owl:NamedIndividual , cor:District ;
	cor:is_part_of $uri_municipio ;
	rdfs:label "$label"^^xsd:string .

					""".replace("$uri_bairro",uri_bairro).replace("$uri_municipio",uri_municipio).replace("$label",str(row[2]).replace("\n",""))


		#Logradouro
		logradouro = normalize_text(str(row[1]).replace("\n",""))
		uri_logradouro = "<http://www.sefaz.ma.gov.br/Correios/Location/resource/District/$var-$bairro>".replace("$var",logradouro).replace("$bairro",bairro)
		if uri_logradouro not in uris_set:
			uris_set.add(uri_logradouro)
			uris+= uri_logradouro+"\n"
			out_string+= """ 
###  $uri_logradouro
$uri_logradouro rdf:type owl:NamedIndividual , cor:Locality ;
	cor:is_part_of $uri_bairro ;
	rdfs:label "$label"^^xsd:string .

					""".replace("$uri_logradouro",uri_logradouro).replace("$uri_bairro",uri_bairro).replace("$label",str(row[1]).replace("\n","").replace('"',""))


		#CEP
		cep = row[0]
		raw_cep = normalize_number(cep)
		out_string+= """ 
###  $uri_logradouro
$uri_logradouro		cor:valid_cep "$cep"^^xsd:string , "$raw_cep"^^xsd:string ;
	cor:raw_valid_cep "$raw_cep"^^xsd:string .

				""".replace("$uri_logradouro",uri_logradouro).replace("$cep",cep).replace("$raw_cep",raw_cep)


	out_string+= """
[ rdf:type owl:AllDifferent ;
	owl:distinctMembers ($vars)
] .
	""".replace("$vars",uris)
	
	out_file.write(out_string)

with open("provenance.ttl","w") as out_file:
	today = date.today()
	provenance_graph = """
@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sfz: <http://www.sefaz.ma.gov.br/ontology/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


<http://www.sefaz.ma.gov.br/ontology/Graph/Correios-Location-{0}> a sd:NamedGraph;
																sd:name <http://www.sefaz.ma.gov.br/ontology/Graph/Correios-Location-{0}>;
																prov:generatedAtTime "{1}"^^xsd:dateTime;
																sfz:type_view sfz:MATERIALIZED;
																rdfs:label "Correios CEP Location".""".format(today.strftime("%Y_%m_%d"),time.strftime("%Y-%m-%dT%H:%M:%S"))
	out_file.write(provenance_graph)
print("processo concluído com sucesso.")