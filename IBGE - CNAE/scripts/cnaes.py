import pandas as pd
import numpy as np
import re
import json
import datetime
from normalize import normalize_text
from datetime import date
import time
import os
from tabula import read_pdf
import pandas as pd

output_ontology = "CNAE_Ontology.ttl"

def raw_cnae(cnae):
	cnae = re.sub('[^A-Za-z0-9]+', '', str(cnae).lower())
	if cnae.isnumeric():
		return str(int(cnae))
	return cnae




# sources = [("cnaes/cnae0.csv","0.0"),("cnaes/cnae1.csv","1.0"),("cnaes/cnae1-1.csv","1.1"),("cnaes/cnae2.csv","2.0"),("cnaes/cnae2-1.csv","2.1"),("cnaes/cnae2-2.csv","2.2"),("cnaes/cnae2-3.csv","2.3")]
#sources = [("cnaes/cnae0.csv","0.0")]

sources = []
with open("config_cnaes.json","r") as config:
	data = json.load(config)
	for cnae in data:
		if len(sources) != 0 and cnae["validity_start"] != "":
			previous = sources.pop()
			p_validity_end = datetime.datetime.strptime(cnae["validity_start"],"%Y-%m-%d") - datetime.timedelta(days=1)
			previous.append(p_validity_end)
			sources.append(previous)
		sources.append([cnae["path"],cnae["version"],cnae["validity_start"],cnae["seeAlso"],cnae["previous_version"]])

#Pega lista de Atividades permitidas para o MEI
triples_MEIs = ""
allowed_MEI = {}
MEI_files = os.listdir("MEI")
for MEI_file in MEI_files:
	year = MEI_file.split(".")[0]
	triples_MEIs += """
###  http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/Activities_Allowed_For_MEI/PERMITIDO_MEI_EM_{0}
<http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/Activities_Allowed_For_MEI/PERMITIDO_MEI_EM_{0}> rdf:type owl:NamedIndividual , cnae:Activities_Allowed_For_MEI , cnae:Activities_Collection , skos:Collection ;
	cnae:validate_year "{0}"^^xsd:int ;
	rdfs:label "Atividades econômicas permitidas para MEI no ano de {0}"@pt .
	""".format(year)
	with open("MEI/"+MEI_file,"r") as activies_allowed:
		for line in activies_allowed:
			line = line.strip()
			cnaes = re.findall("[0-9].*",line)
			for cnae in cnaes:
				raw_cnae_value = raw_cnae(cnae)
				raw_cnae_value = re.sub("[^0-9]","",raw_cnae_value)
				if raw_cnae_value not in allowed_MEI:
					allowed_MEI[raw_cnae_value] = set()
				allowed_MEI[raw_cnae_value].add(year)




#Pega lista de Atividades impeditivas para SIMPLES
triples_prevented = ""
dir_prevented = "impeditivos/"
activies_prevented = {}
prevented_files = os.listdir(dir_prevented)
for prevented_file in prevented_files:
	year = prevented_file.split(".")[0]
	triples_prevented += """
###  http://www.sefaz.ma.gov.br/ontology/Activities_Prevented_For_SIMPLES/IMPEDIDOS_EM_{0}
<http://www.sefaz.ma.gov.br/ontology/Activities_Prevented_For_SIMPLES/IMPEDIDOS_EM_{0}> rdf:type owl:NamedIndividual , cnae:Activities_Prevented_For_SIMPLES , cnae:Activities_Collection , skos:Collection ;
	cnae:validate_year "{0}"^^xsd:int ;
	rdfs:label "Atividades impeditivas para SIMPLES em {0}"@pt .
	""".format(year)
	tables = read_pdf(dir_prevented+prevented_file, pages = "all", multiple_tables = True)

for df in tables:
	for idx,row in df.iterrows():
		value = row[0]
		if not pd.isnull(value):
			cnaes = re.findall("[0-9].*",value)
			for cnae in cnaes:
				raw_cnae_value = raw_cnae(cnae)
				raw_cnae_value = re.sub("[^0-9]","",raw_cnae_value)
				if raw_cnae_value not in activies_prevented:
					activies_prevented[raw_cnae_value] = set()
				activies_prevented[raw_cnae_value].add(year)




#Pega lista de atividades isentas de ICMS
triples_ICMS = ""
ICMS_Free = {}
ICMS_files = os.listdir("ICMS")
for ICMS_file in ICMS_files:
	version_ICMS = str(ICMS_file.split(".")[0]).replace("_",".")
	triples_ICMS += """
###  http://www.sefaz.ma.gov.br/ontology/Activities_ICMS-Free/ISENTOS_DE_ICMS_CNAE_{0}
<http://www.sefaz.ma.gov.br/ontology/Activities_ICMS-Free/ISENTOS_DE_ICMS_CNAE_{0}> rdf:type owl:NamedIndividual , cnae:Activities_ICMS-Free ;
	cnae:cnae_version "{0}"^^xsd:double ;
	rdfs:label "Atividades {0} isentas de ICMS"@pt .
	""".format(version_ICMS)
	data = pd.read_csv("ICMS/"+ICMS_file,sep=";",encoding="utf8")
	for index, row in data.iterrows():
		cnae = str(row[0])
		raw_cnae_value = raw_cnae(cnae)
		if raw_cnae_value not in ICMS_Free:
			ICMS_Free[raw_cnae_value] = set()
		ICMS_Free[raw_cnae_value].add(version_ICMS)






# print(sources)
output_tiples = ""
uris=""
uris_cnaes=""

current_section = ""
current_division = ""
current_group = ""
current_classe = ""
current_subclasse = ""
#included_CNAES = set()
included_CNAES = {}

with open(output_ontology,"a+") as out_file:
	for source in sources:
		print("triplification of source: ",source[0])
		current_version_cnae = str(source[1]).replace(".","_")
		included_CNAES[current_version_cnae] = {}

		cnae_version = "http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/CNAE_Version/CNAE_{}".format(source[1])
		uris+="<{}>\n".format(cnae_version)

		previous_version = ""
		if source[4] != "":
			previous_version = "\n\tcnae:previous_version <http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/CNAE_Version/CNAE_{}> ;".format(source[4])

		validity_start = ""
		if source[2] != "":
			v_date = datetime.datetime.strptime(source[2],"%Y-%m-%d")
			validity_start = """\n\tcnae:validity_start "{}"^^xsd:dateTime ;""".format(v_date.strftime("%Y-%m-%dT%H:%M:%S"))
			if source[4] != "":
				p_validity_end = v_date - datetime.timedelta(days=1)
				output_tiples+= """<http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/CNAE_Version/CNAE_{}> cnae:validity_end "{}"^^xsd:dateTime .\n""".format(source[4],p_validity_end.strftime("%Y-%m-%dT%H:%M:%S"))

		seeAlso = ""
		if source[3] != "":
			seeAlso = "\n\trdfs:seeAlso <{}> ;".format(source[3])


		output_tiples += """
###  $ver_uri
<$ver_uri> rdf:type owl:NamedIndividual ,
					cnae:CNAE_Version ;$previous$validity_start$seeAlso
			rdfs:label "$ver"^^xsd:string .
		""".replace("$ver_uri",cnae_version).replace("$previous",previous_version).replace("$validity_start",validity_start).replace("$seeAlso",seeAlso).replace("$ver",source[1])

		cnae_version = "<"+cnae_version+">"

		template_uri = "http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/Economic_Activity/CNAE_{}_".format(source[1])
		data = pd.read_csv(source[0],sep=",",encoding="utf8",dtype=str)
		
		for index, row in data.iterrows():
			if not pd.isnull(row['DENOMINAÇÃO']):
				current_cnae = ""
				current_uri = ""
				current_activity = ""
				if not pd.isnull(row['SEÇÃO']):
					#Seção
					current_section = "<" + template_uri + "SECAO-" + normalize_text(str(row['DENOMINAÇÃO'])) + ">"
					current_activity = "SECAO-" + normalize_text(str(row['DENOMINAÇÃO']))
					current_cnae =  raw_cnae(row['SEÇÃO'])
					uris+= current_section + "\n"
					uris_cnaes+= current_section + "\n"
					current_uri = current_section
					output_tiples += """
### {0}
{0} rdf:type owl:NamedIndividual , cnae:CNAE_Section , cnae:Economic_Activity ;
	cnae:has_version {1} ;
	cnae:formated_cnae "{2}"^^xsd:string ;
	cnae:raw_cnae "{3}"^^xsd:string ;
	cnae:cnae "{3}"^^xsd:string , "{2}"^^xsd:string ;
	cnae:activity_description "{4}"^^xsd:string ;
		rdfs:label "{4}"^^xsd:string .
					""".format(current_section, cnae_version, str(row['SEÇÃO']),str(raw_cnae(row['SEÇÃO'])),str(row['DENOMINAÇÃO']).replace("\"","\'").replace("\n",""))
					
				elif not pd.isnull(row['DIVISÃO']):
					#Divisão
					cnae = row['DIVISÃO']
					current_division = "<" + template_uri  + "DIVISAO-" + normalize_text(str(row['DENOMINAÇÃO'])) + ">"
					current_activity = "DIVISAO-" + normalize_text(str(row['DENOMINAÇÃO']))
					current_cnae =  raw_cnae(cnae)
					uris+= current_division + "\n"
					uris_cnaes+= current_division + "\n"
					current_uri = current_division
					output_tiples += """
### {0}
{0} rdf:type owl:NamedIndividual , cnae:CNAE_Division , cnae:Economic_Activity ;
	cnae:has_version {1} ;
	skos:broader {2} ;
	skos:broaderTransitive {2} ;
	cnae:has_cnae_section {2} ;
	cnae:formated_cnae "{3}"^^xsd:string ;
	cnae:raw_cnae "{4}"^^xsd:string ;
	cnae:cnae "{3}"^^xsd:string , "{4}"^^xsd:string ;
	cnae:activity_description "{5}"^^xsd:string ;
	rdfs:label "{5}"^^xsd:string .
					""".format(current_division, cnae_version, current_section ,str(cnae),str(raw_cnae(cnae)),str(row['DENOMINAÇÃO']).replace("\"","\'").replace("\n",""))

				elif not pd.isnull(row['GRUPO']):
					#GRUPO
					cnae = row['GRUPO']
					current_group = "<" + template_uri  + "GRUPO-" + normalize_text(str(row['DENOMINAÇÃO'])) +  ">"
					current_activity = "GRUPO-" + normalize_text(str(row['DENOMINAÇÃO']))
					current_cnae =  raw_cnae(cnae)
					uris+= current_group + "\n"
					uris_cnaes+= current_group + "\n"
					current_uri = current_group
					output_tiples += """
### {0}
{0} rdf:type owl:NamedIndividual , cnae:CNAE_Group , cnae:Economic_Activity ;
	cnae:has_version {1} ;
	skos:broader {2} ;
	skos:broaderTransitive {2} , {6} ;
	cnae:has_cnae_division {2} ;
	cnae:has_cnae_section {6} ;
	cnae:formated_cnae "{3}"^^xsd:string ;
	cnae:raw_cnae "{4}"^^xsd:string ;
	cnae:cnae "{3}"^^xsd:string , "{4}"^^xsd:string ;
	cnae:activity_description "{5}"^^xsd:string ;
	rdfs:label "{5}"^^xsd:string .
					""".format(current_group, cnae_version, current_division ,str(cnae),str(raw_cnae(cnae)),str(row['DENOMINAÇÃO']).replace("\"","\'").replace("\n",""),current_section)

				elif not pd.isnull(row['CLASSE']):
					#CLASSE
					cnae = row['CLASSE']
					current_classe = "<" + template_uri  + "CLASSE-" + normalize_text(str(row['DENOMINAÇÃO'])) +">"
					current_activity = "CLASSE-" + normalize_text(str(row['DENOMINAÇÃO']))
					current_cnae =  raw_cnae(cnae)
					uris+= current_classe + "\n"
					uris_cnaes+= current_classe + "\n"
					current_uri = current_classe
					output_tiples += """
### {0}
{0} rdf:type owl:NamedIndividual , cnae:CNAE_Class , cnae:Economic_Activity ;
	cnae:has_version {1} ;
	skos:broader {2} ;
	skos:broaderTransitive {2} , {6} , {7} ;
	cnae:has_cnae_group {2};
	cnae:has_cnae_division {6};
	cnae:has_cnae_section {7};
	cnae:formated_cnae "{3}"^^xsd:string ;
	cnae:raw_cnae "{4}"^^xsd:string ;
	cnae:cnae "{3}"^^xsd:string , "{4}"^^xsd:string ;
	cnae:activity_description "{5}"^^xsd:string ;
	rdfs:label "{5}"^^xsd:string .
					""".format(current_classe, cnae_version, current_group ,str(cnae),str(raw_cnae(cnae)),str(row['DENOMINAÇÃO']).replace("\"","\'").replace("\n",""),current_division,current_section)

				elif not pd.isnull(row['SUBCLASSE']):
					#SUBCLASSE
					cnae = row['SUBCLASSE']
					current_subclasse = "<" + template_uri  + "SUBCLASSE-" + normalize_text(str(row['DENOMINAÇÃO'])) + ">"
					current_activity = "SUBCLASSE-" + normalize_text(str(row['DENOMINAÇÃO']))
					current_cnae =  raw_cnae(cnae)
					uris+= current_subclasse + "\n"
					uris_cnaes+= current_subclasse + "\n"
					current_uri = current_subclasse
					output_tiples += """
### {0}
{0} rdf:type owl:NamedIndividual , cnae:CNAE_Subclass , cnae:Economic_Activity ;
	cnae:has_version {1} ;
	skos:broader {2} ;
	skos:broaderTransitive {2} , {6} , {7} , {8};
	cnae:has_cnae_class {2};
	cnae:has_cnae_group {6};
	cnae:has_cnae_division {7};
	cnae:has_cnae_section {8};
	cnae:formated_cnae "{3}"^^xsd:string ;
	cnae:raw_cnae "{4}"^^xsd:string ;
	cnae:cnae "{3}"^^xsd:string , "{4}"^^xsd:string ;
	cnae:activity_description "{5}"^^xsd:string ;
	rdfs:label "{5}"^^xsd:string .
					""".format(current_subclasse, cnae_version, current_classe ,str(cnae),str(raw_cnae(cnae)),str(row['DENOMINAÇÃO']).replace("\"","\'").replace("\n",""),current_group,current_division,current_section)
				

				

				#checa versões antigas do cnae
				# included_CNAES.add("{}_{}".format(source[1],current_activity))
				# previous_cnae = "{}_{}".format(source[4],current_activity) 
				# if source[4] != "" and previous_cnae in included_CNAES:
				# 	previous_uri = "<http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/Economic_Activity/CNAE_{}> ;".format(previous_cnae)
				# 	output_tiples += "{} cnae:previous_version {} .".format(current_uri,previous_uri)
				included_CNAES[current_version_cnae][current_cnae] = current_uri
				if source[4] != "":
					previous_version_cnae = str(source[4]).replace(".","_")
					if previous_version_cnae in included_CNAES and current_cnae in included_CNAES[previous_version_cnae]:
						previous_uri = included_CNAES[previous_version_cnae][current_cnae]
						output_tiples += "\n{} cnae:previous_version {} . \n".format(current_uri,previous_uri)

				#checa se atividade é permitida para MEI
				if current_cnae in allowed_MEI:
					years_allowed = allowed_MEI[current_cnae]
					for year in years_allowed:
						if int(year) >= v_date.year:
							if len(source) < 6 or (source[5].year >= int(year)):
								triples_MEIs+= "<http://www.sefaz.ma.gov.br/IBGE/CNAE/resource/Activities_Allowed_For_MEI/PERMITIDO_MEI_EM_{0}> skos:member {1} .\n".format(year,current_uri)

				#checa se atividade é impeditiva para SIMPLES
				if current_cnae in activies_prevented:
					years_allowed = activies_prevented[current_cnae]
					for year in years_allowed:
						# if int(year) >= v_date.year: #Está incluíndo todos as versões do CNAES que existem depois desse ano, inclusive as versões que ainda nem existiam na data de publicação.
						if len(source) < 6 or (source[5].year >= int(year)):
							triples_prevented+= "<http://www.sefaz.ma.gov.br/ontology/Activities_Prevented_For_SIMPLES/IMPEDIDOS_EM_{0}> skos:member {1} .\n".format(year,current_uri)

				#checa se atividade é isenta de ICMS
				if current_cnae in ICMS_Free:
					versions_free = ICMS_Free[current_cnae]
					for version in versions_free:
						if version == source[1]:
							triples_ICMS+= "<http://www.sefaz.ma.gov.br/ontology/Activities_ICMS-Free/ISENTOS_DE_ICMS_CNAE_{0}> skos:member {1} .\n".format(version,current_uri)
			

##END
	output_tiples+= """
[ rdf:type owl:AllDifferent ;
	owl:distinctMembers ($vars)
] .
	""".replace("$vars",uris)
	output_tiples+= """
cnae:Economic_Activity owl:equivalentClass [ rdf:type owl:Class ;
		owl:oneOf (
		$vars)
	] .
	""".replace("$vars",uris_cnaes)
	output_tiples+= triples_MEIs
	output_tiples+= triples_prevented
	output_tiples+= triples_ICMS
	out_file.write(output_tiples)

with open("provenance.ttl","w") as out_file:
	today = date.today()
	provenance_graph = """
@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sfz: <http://www.sefaz.ma.gov.br/ontology/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


<http://www.sefaz.ma.gov.br/ontology/Graph/IBGE-CNAE-{0}> a sd:NamedGraph;
																sd:name <http://www.sefaz.ma.gov.br/ontology/Graph/IBGE-CNAE-{0}>;
																prov:generatedAtTime "{1}"^^xsd:dateTime;
																sfz:source_recorded "{1}"^^xsd:dateTime;
																sfz:type_view sfz:MATERIALIZED;
																rdfs:label "IBGE CNAE".""".format(today.strftime("%Y_%m_%d"),time.strftime("%Y-%m-%dT%H:%M:%S"))
	out_file.write(provenance_graph)
