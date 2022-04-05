import os
import json
from SPARQLWrapper import SPARQLWrapper, JSON

"""
A PROPOS
--------
ce script permet de générer en série une version différente de la même requête
SPARQL wikidata pour tous les mots clés choisis (soit les 21 mots clés occurant dans 
plus de 0.5% des entrées du tableur). chaque requête est lancée automatiquement. le 
texte des requêtes sont stockées dans le dossier sparql_request. le résultat des requêtes
sont stockées en JSON dans le dossier sparql_out (le format CSV posait un problème
avec wikidata).

variables
---------
keywords: un dictionnaire des noms des entités de wikidata qui correspondent aux mots clés retenus
sparql: la requête sparql de base
actual_path: chemin du fichier actuel
out_path: chemin de sortie des requêtes sparql (dossier sparql_requests_wikidata)
sparql_out: chemin de sortie des résultats des requêtes sparql (dossier sparql_out_wikidata)
nboucles: nombre d'itérations, pour nommer les requêtes
keys: une liste des clés du dictionnaire, pour modifier les requêtes dans la boucle
endpoint: l'URL du sparql endpoint de wikidata

outputs
-------
dans le dossier sparql_requests_wikidata : une série de requêtes sparql numérotées et enregistrées
dans le dossier sparql_out_wikidata : les résultats de chaque requête sparql
"""

keywords = {
    "blog": "Q30849",
    "France": "Q142",
    "writer": "Q36180",
    "21st century": "Q6939",
    "website": "Q35127",
    "literature": "Q8242",
    "editor": "Q1607826",
    "20th century": "Q6927",
    "periodical": "Q1002697",
    "artist": "Q483501",
    "children's and youth literature": "Q11163999",
    "francophonie": "Q1003588",
    "creative writing": "Q586060",
    "comics": "Q1004",
    "International Standard Serial Number": "Q131276",
    "cultural event": "Q58687420",
    "association": "Q15911314",
    "bookshop": "Q200764",
    "science fiction": "Q24925",
    "faculty web page": "Q109647055",
    "library science": "Q199655"
}

sparql = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdv: <http://www.wikidata.org/value/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX schema: <http://schema.org/>

# requête pour le mot clé: {KEYWORD}

SELECT ?id ?labelFR ?labelEN ?instanceOFlabel ?partOFlabel ?countFOW ?countINS ?wikidataURL ?wikipediaFR ?wikipediaEN
# toutes les requêtes sont optional pour pouvoir automatiser un maxxx en évitant les erreurs
# ?id: l'identifiant du mot clé dans wikidata
# ?labelFR: le nom du mot clé dans wikidata en français
# ?labelEN: le nom du mot clé dans wikidata en anglais
# ?instanceOFlabel: les noms des entités dont le mot clé est l'instance, en anglais
# ?partOFlabel: le nom des entités dont le mot clé fait partie, en anglais
# ?countFOW: le nombre de personnes morales/physiques qui ont le mot clé comme domaine de travail/étude
# ?countINS: nombre d'instances du mot clé
# ?wikidataURL: l'URL wikidata
# ?wikipediaFR: un lien vers la page wikipedia en français, si elle existe
# ?wikipediaEN: un lien vers la page wikipedia en anglais, si elle existe
WHERE {
  # définir une variable pour stocker l'ID wikidata
  VALUES ?id {"{WIKIDATA}"}

  # afficher le nom en français
  OPTIONAL {
    wd:{WIKIDATA} rdfs:label ?labelFR .
    FILTER (langMatches(lang(?labelFR), "FR"))
  }

  # afficher le nom en anglais
  OPTIONAL {
    {SELECT ?labelEN
      WHERE {
        wd:{WIKIDATA} rdfs:label ?labelEN .
        FILTER (langMatches(lang(?labelEN), "EN"))
      } LIMIT 1
    }
  }

  # lister les éléments dont le mot clé est l'instance
  OPTIONAL {
    {SELECT  ?instanceOFlabel
      WHERE {
        wd:{WIKIDATA} wdt:P31 ?instanceOF . # l'instance
        ?instanceOF rdfs:label ?instanceOFlabel . # le label de l'instance en anglais
        FILTER (langMatches(lang(?instanceOFlabel), "EN"))
      }
    }
  } # cette query ramène potentiellement des résultats multiples qu'il faudra distinct dans dataiku

  # lister les éléments dont le mot clé fait partie
  OPTIONAL {
    {SELECT  ?partOFlabel
      WHERE {
        wd:{WIKIDATA} wdt:P371 ?partOF . # l'instance
        ?instanceOF rdfs:label ?partOFlabel . # le label de l'instance d'au dessus
        FILTER (langMatches(lang(?partOFlabel), "EN"))
      }
    }
  } # cette query ramène potentiellement des résultats multiples qu'il faudra distinct dans dataiku

  # compter le nb de personnes (morales/physiques) qui ont pour "field of work" (domaine de spécialisation) le mot clé
  OPTIONAL {
    {SELECT  (COUNT($fow) AS ?countFOW)
      WHERE {
        $fow wdt:P101 wd:{WIKIDATA} .
      }
    }
  } # cette query ramène potentiellement des résultats multiples qu'il faudra distinct dans dataiku

  # compter le nombre d'instances (éléments spécifiques) du mot clé: livres de la catégorie littérature...
  OPTIONAL {
    {SELECT (COUNT($ins) AS ?countINS)
      WHERE {
        $ins wdt:P31 wd:{WIKIDATA} .
      }
    }
  }

  # construire l'URL wikidata
  BIND (CONCAT("https://www.wikidata.org/wiki/", $id) AS ?wikidataURL)

  # récupérer la page wikipedia en anglais
  OPTIONAL {
    ?wikipediaEN schema:about wd:{WIKIDATA} .
    ?wikipediaEN schema:inLanguage "en" .
    FILTER (SUBSTR(str(?wikipediaEN), 1, 25) = "https://en.wikipedia.org/")
  }

  # récupérer la page wikipedia en français
  OPTIONAL {
    ?wikipediaFR schema:about wd:{WIKIDATA} .
    ?wikipediaFR schema:inLanguage "fr" .
    FILTER (SUBSTR(str(?wikipediaFR), 1, 25) = "https://fr.wikipedia.org/")
  }
}
"""

# définition des variables pour tout faire marcher
actual_path = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(actual_path, "sparql_requests_wikidata")
sparql_out = os.path.join(actual_path, "sparql_out_wikidata")
nboucles = 0
keys = list(keywords.keys())

endpoint = SPARQLWrapper("https://query.wikidata.org/sparql")

for k in keywords.items():
    # convertir les données pour mener la requête et enregistrer le fichier
    nboucles += 1  # compter le nombre d'itérations
    key = k[0]  # récupérer la clé de l'élément du dico sur lequel on itère
    value = k[1]  # récupérer la valeur de l'élément du dico sur lequel on itère

    # si on en est à la première boucle, remplacer {KEYWORD} et {WIKIDATA} et lancer les requêtes
    if nboucles == 1:
        sparql = sparql.replace("{KEYWORD}", key)
        sparql = sparql.replace("{WIKIDATA}", value)
        try:
            # lancer la requête
            endpoint.setQuery(sparql)
            endpoint.setReturnFormat(JSON)
            results = endpoint.query().convert()
            with open(os.path.join(sparql_out, f"sparql_out_{nboucles}.json"), mode="w") as f:
                json.dump(results["results"], f)

            # enregistrer la requête si tout s'est bien passé
            with open(os.path.join(out_path, f"sparql_request_{nboucles}.sparql"), mode="w") as f:
                f.write(sparql)

        except Exception as error:
            print(str(error))

    # sinon, remplacer les valeurs de l'itération précédente et lancer la requête
    else:
        idx = keys.index(key) - 1  # l'index de l'itération précédente
        sparql = sparql.replace(keys[idx], key)  # remplacer la clé précédente par la clé actuelle
        sparql = sparql.replace(keywords[keys[idx]], value)  # remplacer la valeur précédente par la valeur actuelle
        try:
            # lancer la requête
            endpoint.setQuery(sparql)
            endpoint.setReturnFormat(JSON)
            results = endpoint.query().convert()
            with open(os.path.join(sparql_out, f"sparql_out_{nboucles}.json"), mode="w") as f:
                json.dump(results["results"], f)

            # enregistrer la requête si tout s'est bien passé
            with open(os.path.join(out_path, f"sparql_request_{nboucles}.sparql"), mode="w") as f:
                f.write(sparql)

        except Exception as error:
            print(str(error))
