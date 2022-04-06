import os
import re
import csv
from SPARQLWrapper import SPARQLWrapper, CSV

"""
A PROPOS
--------
ce script permet de générer en série une version différente de la même requête
SPARQL dataBnF pour tous les thèmes du dataset (soit 23 termes, les 30 thèmes
de du dataset n'ayant pas forcément d'équivalent dans DataBNF, et plusieurs
thèmes du dataset renvoyant aux mêmes termes DataBNF). chaque requête 
est lancée automatiquement. le texte des requêtes sont stockées dans le dossier 
sparql_request. le résultat des requêtes sont stockées en JSON dans le dossier 
sparql_out. la requête de base a été divisée en 3 requêtes pour éviter les timeout

variables
---------
keywords: un dictionnaire des noms des entités de wikidata qui correspondent aux thèmes requêtés et de leurs URIs
sparql_main: le template de requête sparql de principale
sparql_narrower: le template de requête sparql pour récupérer les termes spécifiques d'un thème qui font partie des 
                 thèmes de notre dataset
sparql_broader: le template de requête sparql pour récupérer les termes génériques d'un thème qui font partie des 
                thèmes de notre dataset
urilist: une chaîne de définissant en sparql une variable "?urilist" contenant tous les URIs requêtés
actual_path: chemin du fichier actuel
out_path: chemin de sortie des requêtes sparql (dossier sparql_requests_databnf)
sparql_out: chemin de sortie des résultats des requêtes sparql (dossier sparql_out_databnf)
nboucles: nombre d'itérations, pour nommer les requêtes
keys: une liste des clés du dictionnaire, pour modifier les requêtes dans la boucle
endpoint: l'URL du sparql endpoint de wikidata

outputs
-------
dans le dossier sparql_requests_databnf : une série de requêtes sparql numérotées et enregistrées
dans le dossier sparql_out_databnf : les résultats de chaque requête sparql
"""


# ---- DÉFINITION DES MOTS CLÉS ET DES TEMPLATES DES REQUÊTES ---- #

# tous les thèmes du dataset n'ont pas leur équivalent parfait dans databnf; plusieurs
# thèmes renvoient au même terme dans databnf ; la requête n'est donc pas lancée
# sur la totalité des termes du dataset
keywords = {
    "Littérature française": "http://data.bnf.fr/ark:/12148/cb119322773",
    "Littérature -- 1945-....": "http://data.bnf.fr/ark:/12148/cb12082408f",
    "Art": "http://data.bnf.fr/ark:/12148/cb11934758p",
    "Littérature francophone": "http://data.bnf.fr/ark:/12148/cb12083177p",
    "Littérature": "http://data.bnf.fr/ark:/12148/cb11939456c",
    "Édition": "http://data.bnf.fr/ark:/12148/cb13318593f",
    "Littérature pour la jeunesse": "http://data.bnf.fr/ark:/12148/cb11932269g",
    "Bibliothéconomie": "http://data.bnf.fr/ark:/12148/cb119316669",
    "Bandes dessinées": "http://data.bnf.fr/ark:/12148/cb119310194",
    "Rentrée littéraire": "http://data.bnf.fr/ark:/12148/cb17072240v",
    "Linguistique": "http://data.bnf.fr/ark:/12148/cb11932194d",
    "Science-fiction": "http://data.bnf.fr/ark:/12148/cb119332311",
    "Sports": "http://data.bnf.fr/ark:/12148/cb133188907",
    "Langues étrangères appliquées": "http://data.bnf.fr/ark:/12148/cb12567294z",
    "Librairie": "http://data.bnf.fr/ark:/12148/cb11932248h",
    "Français (langue)": "http://data.bnf.fr/ark:/12148/cb11935375d",
    "Roman policier": "http://data.bnf.fr/ark:/12148/cb11932793q",
    "Livres -- histoire": "http://data.bnf.fr/ark:/12148/cb11937824c",
    "Littérature antique": "http://data.bnf.fr/ark:/12148/cb11937824c",
    "Littérature comparée": "http://data.bnf.fr/ark:/12148/cb119322684",
    "Langues classiques": "http://data.bnf.fr/ark:/12148/cb119495514",
    "Femmes et littérature": "http://data.bnf.fr/ark:/12148/cb12200402k",
    "Littérature asiatique": "http://data.bnf.fr/ark:/12148/cb11968623b"
}

sparql_main = """
PREFIX bnfroles: <http://data.bnf.fr/vocabulary/roles/>
PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# requête sur le thème : {KEYWORD}

SELECT DISTINCT ?label ?uri ?cntAUT ?cntDOC ?uriRTD ?labelRTD
# ?label : le nom du thème requêté
# ?uri : l'URI du thème requêté dans databnf
# ?cntAUT : le nombre d'auteur.ice.s lié.e.s au thème
# ?ctnDOC : le nombre de documents liés au thème
# ?labelRTD : les noms des termes liés au thème requêté qui figurent aussi dans le dataset
# ?uriRTD : les uris des termes liés au thème requêté qui figurent aussi dans le dataset
WHERE {
  # stocker l'uri sur lequel la requête est faite et l'ensemble des URI requêtés dans des variables
  VALUES ?uri {"{URI}"}
  
  # récupérer le nom du thème requêté
  <{URI}> skos:prefLabel ?label .
  
  # récupérer le nombre d'auteur.ices.s lié.e.s au thème requêté
  OPTIONAL {
    SELECT (COUNT(DISTINCT ?aut) AS ?cntAUT)
    WHERE {
      ?expr dcterms:subject <{URI}> ;
            rdf:type frbr-rda:Expression ;
            bnfroles:r70 ?aut .
    }
  }
  
  # récupérer le nombre de documents liés au thème requêté
  OPTIONAL {
    SELECT (COUNT(DISTINCT ?doc) AS ?cntDOC)
    WHERE {
      ?doc dcterms:subject <{URI}> ;
            rdf:type frbr-rda:Expression .
    }
  }
  
  # récupérer les termes liés au thème requêté
  OPTIONAL {
    <{URI}> skos:related ?uriRTD .
    ?uriRTD skos:prefLabel ?labelRTD .
  }
}
"""

sparql_narrower = """
PREFIX bnfroles: <http://data.bnf.fr/vocabulary/roles/>
PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# requête sur le mot clé {KEYWORD}
# cette requête permet de récupérer les termes spécifiques d'un terme de notre dataset

SELECT DISTINCT ?label ?uri ?uriNRW ?labelNRW
# ?label : le nom du thème requêté dans databnf
# ?uri : l'uri de ce thème
# ?uriNRW : l'URI des termes spécifiques du thème requêté qui figurent également dans la liste des thèmes
# ?labelNRW : le nom des termes spécifiques
WHERE {
  # stocker l'uri sur lequel la requête est faite
  VALUES ?uri {"{URI}"}
  
  # récupérer le nom du thème requêté
  <{URI}> skos:prefLabel ?label .
  
  # filtrer les données, récupérer les URI et les noms associés
  <{URI}> skos:narrower* ?uriNRW .
  ?uriNRW skos:prefLabel ?labelNRW .
}
"""

sparql_broader = """
PREFIX bnfroles: <http://data.bnf.fr/vocabulary/roles/>
PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# requête sur le mot clé {KEYWORD}
# cette requête permet de récupérer les termes génériques (à 3 niveaux) d'un thème de notre dataset
# qui font également partie de notre dataset

SELECT DISTINCT ?uri ?label ?uriBRD ?labelBRD
# ?label : le nom du thème requêté dans databnf
# ?uri : l'uri de ce thème
# ?uriBRD : l'URI des termes génériques du thème requêté qui figurent également dans la liste des thèmes
# ?labelBRD : le nom des termes génériques
WHERE {
  # stocker l'uri sur lequel la requête est faite
  VALUES ?uri {"{URI}"}
  
  # récupérer le nom du thème requêté
  <{URI}> skos:prefLabel ?label .
  
  # filtrer les données, récupérer les URI et les noms associés
  <{URI}> skos:broader* ?uriBRD .
  ?uriBRD skos:prefLabel ?labelBRD .
}
"""


# ---- DÉFINITION DES AUTRES VARIABLES ---- #

# définir une liste de tous les URIs pour nettoyer les URIs récupérer avec dataiku
# afin de ne garder que les TS, TG et termes reliés faisant également partie de la liste de thèmes
urilist = "("
nboucles = 0
for v in keywords.values():
    nboucles +=1
    if nboucles < 23:
        urilist += f"({v})|"
    else:
        urilist += f"({v}))"

urilist = re.sub(r"\.", r"\\.", urilist)
print(urilist)

# définition des autres variables pour tout faire marcher
actual_path = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(actual_path, "sparql_requests_databnf")
sparql_out = os.path.join(actual_path, "sparql_out_databnf")
nboucles = 0
keys = list(keywords.keys())

endpoint = SPARQLWrapper("https://data.bnf.fr/sparql")
#sparql_main = sparql_main.replace("{URILIST}", urilist)
#sparql_narrower = sparql_narrower.replace("{URILIST}", urilist)
#sparql_broader = sparql_broader.replace("{URILIST}", urilist)

# variables pour replacer les caractères héxadécimaux par des caractères utf-8
e_aigu = "é"
e_aigu_maj = "É"
e_grave = "è"
c_cedille = "ç"


# ---- LANCEMENT DES REQUÊTES ---- #

# lancer la requête principale
for k in keywords.items():
    nboucles += 1
    # ouvrir le fichier en écriture
    with open(os.path.join(sparql_out, f"sparql_main_out_{nboucles}_databnf.csv"), mode="w") as f:
        writer = csv.writer(f, delimiter=",", quotechar="\"")  # j'ai un problème là sur le dialect

        # convertir les données pour mener la requête et enregistrer le fichier
        key = k[0]  # récupérer la clé de l'élément du dico sur lequel on itère
        value = k[1]  # récupérer la valeur de l'élément du dico sur lequel on itère

        # si on en est à la première boucle, remplacer {KEYWORD} et {URI} et lancer les requêtes
        if nboucles == 1:
            sparql_main = sparql_main.replace("{KEYWORD}", key)
            sparql_main = sparql_main.replace("{URI}", value)
            try:
                # lancer la requête
                endpoint.setQuery(sparql_main)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_main_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_main)

            except Exception as error:
                print(str(error))

        # sinon, remplacer les valeurs de l'itération précédente et lancer la requête
        else:
            idx = keys.index(key) - 1  # l'index de l'itération précédente
            sparql_main = sparql_main.replace(keys[idx], key)  # remplacer la clé précédente par la clé actuelle
            sparql_main = sparql_main.replace(keywords[keys[idx]], value)  # remplacer la valeur précédente par la valeur actuelle
            try:
                # lancer la requête
                endpoint.setQuery(sparql_main)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_main_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_main)

            except Exception as error:
                print(str(error))


# lancer la requête sparql_narrower pour récupérer les TS
nboucles = 0
for k in keywords.items():
    nboucles += 1
    # ouvrir le fichier en écriture
    with open(os.path.join(sparql_out, f"sparql_narrower_out_{nboucles}_databnf.csv"), mode="w") as f:
        writer = csv.writer(f, delimiter=",", quotechar="\"")  # j'ai un problème là sur le dialect

        # convertir les données pour mener la requête et enregistrer le fichier
        key = k[0]  # récupérer la clé de l'élément du dico sur lequel on itère
        value = k[1]  # récupérer la valeur de l'élément du dico sur lequel on itère

        # si on en est à la première boucle, remplacer {KEYWORD} et {URI} et lancer les requêtes
        if nboucles == 1:
            sparql_narrower = sparql_narrower.replace("{KEYWORD}", key)
            sparql_narrower = sparql_narrower.replace("{URI}", value)
            try:
                # lancer la requête
                endpoint.setQuery(sparql_narrower)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_narrower_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_narrower)

            except Exception as error:
                print(str(error))

        # sinon, remplacer les valeurs de l'itération précédente et lancer la requête
        else:
            idx = keys.index(key) - 1  # l'index de l'itération précédente
            sparql_narrower = sparql_narrower.replace(keys[idx], key)  # remplacer la clé précédente par la clé actuelle
            sparql_narrower = sparql_narrower.replace(keywords[keys[idx]], value)  # remplacer la valeur précédente par la valeur actuelle
            try:
                # lancer la requête
                endpoint.setQuery(sparql_narrower)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_narrower_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_narrower)

            except Exception as error:
                print(str(error))


# lancer la requête sparql_broader pour récupérer les TG
nboucles = 0
for k in keywords.items():
    nboucles += 1
    # ouvrir le fichier en écriture
    with open(os.path.join(sparql_out, f"sparql_broader_out_{nboucles}_databnf.csv"), mode="w") as f:
        writer = csv.writer(f, delimiter=",", quotechar="\"")  # j'ai un problème là sur le dialect

        # convertir les données pour mener la requête et enregistrer le fichier
        key = k[0]  # récupérer la clé de l'élément du dico sur lequel on itère
        value = k[1]  # récupérer la valeur de l'élément du dico sur lequel on itère

        # si on en est à la première boucle, remplacer {KEYWORD} et {URI} et lancer les requêtes
        if nboucles == 1:
            sparql_broader = sparql_broader.replace("{KEYWORD}", key)
            sparql_broader = sparql_broader.replace("{URI}", value)
            try:
                # lancer la requête
                endpoint.setQuery(sparql_broader)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_broader_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_broader)

            except Exception as error:
                print(str(error))

        # sinon, remplacer les valeurs de l'itération précédente et lancer la requête
        else:
            idx = keys.index(key) - 1  # l'index de l'itération précédente
            sparql_broader = sparql_broader.replace(keys[idx], key)  # remplacer la clé précédente par la clé actuelle
            sparql_broader = sparql_broader.replace(keywords[keys[idx]], value)  # remplacer la valeur précédente par la valeur actuelle
            try:
                # lancer la requête
                endpoint.setQuery(sparql_broader)
                endpoint.setReturnFormat(CSV)
                results = endpoint.query().convert()
                results = str(results).replace("\\xc3\\xa9", e_aigu)
                results = results.replace("\\xc3\\x89", e_aigu_maj)
                results = results.replace("\\xc3\\xa8", e_grave)
                results = results.replace("n\\xc3\\xa7", c_cedille)
                results = results.split("\\n")
                for r in results:
                    r = r.split(",")
                    writer.writerow(r)

                # enregistrer la requête si tout s'est bien passé
                with open(os.path.join(out_path, f"sparql_broader_request_{nboucles}_databnf.sparql"), mode="w") as f:
                    f.write(sparql_broader)

            except Exception as error:
                print(str(error))

# ------- ENREGISTRER LA LISTE D'URIs ------- #
with open(os.path.join(actual_path, "urilist.txt"), mode="w") as f:
    f.write(urilist)

