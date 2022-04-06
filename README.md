# PROJET DONNÉES - DÉPÔT LÉGAL DU WEB

Ce projet a été réalisé par Anahi Haedo, Paul Kervegan et Kristina Konstantinova dans le cadre du cours de Données du master 
TNAH de l'École des Chartes (promotion 2021-2022).

---

## STRUCTURE DU DÉPÔT

à compléter!

---

## PRÉSENTATION GÉNÉRALE DU PROJET

Notre projet porte sur le Dépôt légal du web, organisé par la BNF. Ce dépôt étant organisé thématiquement, nous avons choisi
de travailler sur la collecte Littérature et Art effectuée entre 2011 et 2020. Les données de cette collecte sont disponibles sur
[Data.gouv.fr](https://www.data.gouv.fr/fr/datasets/collectes-thematiques-du-web-par-la-bnf/) et diffusées sous licence libre.

La collecte Littérature et art regroupe des sites sélectionnés par le département Littérature et art de la Bibliothèque 
nationale de France.

---

## DESCRIPTION DES JEUX DE DONNÉES

Notre dataset initial est constitué de 5 fichiers CSV correspondant à 5 phases de collecte (2011-2016, 2017, 2018, 
2019, 2020), soit un total de 19529 entrées. Chaque entrée correspond à un site collecté, et plusieurs sites sont requêtés
plusieurs années de suite. Chaque entrée est classifiée à l'aide d'un thème issu d'un vocabulaire contrôlé 30 thèmes : 
art, littérature française, francophone, étrangère et jeunesse, bibliothéconomie, linguistique, bandes dessinés, éditeurs... 
Plusieurs mots clés servent également à décrire les sites. Ces termes ne font pas partie d'un vocabulaire contrôlé; 
il y a donc 8196 mots clés en tout. En plus des mots clés, la fréquence à laquelle les sites sont collectés est également
renseignée. Deux champs complémentaires servent à indiquer des informations descriptives et à donner un historique des URLs. 

---

## OBJECTIFS

Le jeu de données est très riche, autant du point de vue thématique que du point de vue chronologique, puisqu'il représente
10 ans de sites internet, ce qui n'est pas négligeable au vu des évolutions qu'a connu le web. Nous avons donc choisi d'étudier
le dataset en suivant plusieurs axes :
- **Un axe chronologique**. Ccomment le web a-t-il évolué sur 10 ans ? Les thématiques des sites collectées ont-elles évolué 
sur cette période ? Qu'en est-il des sites requêtés : comment la proportion de blogs, de réseaux sociaux et de sites académiques 
a t-elle évolué ?
- **Un axe thématique**. Comment les thématiques requêtées s'organisent-elles entre elles ? Est-ce que la répartition des sites
web par thématique est représentative de la production ou de la consommation culturelle ? Nous avons enfin voulu relier nos données
à des sources externes d'information, en récupérant notamment des liens vers les pages Wikipedia des mots clés les plus utilisés.
Cette partie s'appuie fortement sur des données externes récupérées avec Sparql sur [Data BnF](https://data.bnf.fr/) et 
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) ainsi que sur un dump du Ministère de la Culture récupéré sur 
[Data.gouv.fr](https://www.data.gouv.fr)
- **Un axe géographique**. Nous sommes parti.e.s de l'idée que le dépôt légal du web de la BnF représentait "l'internet français".
À partir de cette idée, nous sommes arrivé.e.s à un questionnement simple: d'un point de vue géographique, l'internet français
est-il réellement français ? Pour répondre à cette question, nous avons écrit un script Python qui récupère les adresses IP liées
à des URLs grâce au *Domain Name System*. La localisation des adresses IP extraites a été traduite en données géographiques avec
Dataiku. 

---

## ENRICHISSEMENTS EXTÉRIEURS À DATAIKU

Dans cette partie, nous expliquons le travail d'enrichissement réalisé à l'extérieur de Dataiku (tous les scripts utilisés sont
fournis dans ce dépôt et documentés), afin de ne pas alourdir le descriptif de la chaîne de traitement ci-dessous.

### Création d'un script Python pour récupérer les adresses IP

Notre objectif de compléter les URLs présentes dans notre dataset en extrayant les adresses IP auxquelles elles renvoient.
Malgré de nombreux essais, nous n'avons pas réussi à utiliser Python à l'intérieur de Dataiku, en partie à cause d'une difficulté
à prendre en main la librairie `pandas`. Nous avons donc exporté une version nettoyée du dataset principal afin d'y appliquer
un script Python localement. Le script `urltoip.py` (disponible [ici](urltoip/urltoip.py)) est relativement simple : en utilisant
la librairie [`dnspython`](https://www.dnspython.org/), il boucle sur chaque URL du jeu de données et extrait les adresses IP si 
elles existent. Si une erreur a lieu, alors le script produit un message d'erreur qui permet de savoir quel type d'erreur a eu 
lieu :
- `timeout` si l'adresse IP a été retrouvée, mais n'a pas répondu à temps
- `lien mort`, si le DNS ne retourne pas de résultat : cela veut dire que l'URL n'est plus attribuée
- `àutre erreur`, si une autre erreur a été rencontrée.

Ces données sont ensuite écrites dans un fichier CSV qui associe à chaque URL, une adresse IP ou un message d'erreur. Le fichier
a ensuite été ajouté à Dataiku et une jointure a été faite sur le dataset principal.

### Requêtes sur Data BnF et Wikidata avec Python

Pour enrichir les datasets, des requêtes SPARQL ont été lancées sur DataBNF et Wikidata pour récupérer des informations
supplémentaires sur tous les thèmes et sur les mots clés utilisés sur plus de 0,5% du dataset (respectivement). Les mêmes
requêtes étant lancées en boucle sur des termes différents, l'utilisation de python a servi a automatiser le processus. Les
termes requêtés sont stockés dans un dictionnaire ; on boucle sur chaque terme pour construire une requête adaptée, avant de
lancer la requête grâce à la librairie [`SPARQLWrapper`](https://sparqlwrapper.readthedocs.io/en/latest/main.html) et
d'enregistrer les résultats. Suivant ce principe, deux scripts ont été écrits: un pour [lancer des requêtes sur les mots clés 
dans Wikidata](sparql/sparqlmaker_wikidata.py) et un pour [faire des requêtes sur les thèmes dans Data BnF](sparql/sparqlmaker_databnf.py).
Dans les deux cas, un document Markdown permet de faire le lien entre les requêtes et les données du tableur :
- [un premier fichier](sparql/sparql_wikidata.md) relie à chaque mot clé retenu son équivalent dans Wikidata et son identifiant
- [un second fichier](sparl/sparql_databnf.md) associe chaque thème de notre dataset son équivalent dans DataBnF et son URI pour
lancer les requêtes.

Ainsi, il est possible de savoir à quelle donnée de notre dataset correspondent les termes requêtés.

Une seule requête est lancée sur chaque mot clé dans **Wikidata**. Celle ci est exportée en JSON; ce format est converti
en CSV dans Dataiku et les différents fichiers sont "empilés" (*stacked*) afin de n'avoir qu'un seul fichier. Cette
requête permet de récupérer : 
- `?id`: l'identifiant du mot clé dans wikidata
- `?labelFR`: le nom du mot clé dans wikidata en français
- `?labelEN`: le nom du mot clé dans wikidata en anglais
- `?instanceOFlabel`: les noms des entités dont le mot clé est l'instance, en anglais
- `?partOFlabel`: le nom des entités dont le mot clé fait partie, en anglais
- `?countFOW`: le nombre de personnes morales/physiques qui ont le mot clé comme domaine de travail/étude
- `?countINS`: nombre d'instances du mot clé
- `?wikidataURL`: l'URL wikidata
- `?wikipediaFR`: un lien vers la page wikipedia en français, si elle existe
- `?wikipediaEN`: un lien vers la page wikipedia en anglais, si elle existe 

Sur **Data BnF**, trois requêtes sont lancées pour chaque mot clé (pour éviter que la durée n'excède la durée maximale autorisée
pour une requête - 1 minute - il a fallu diviser les requêtes en 3). Pour chaque thème, le script lance les trois requêtes et
produit 3 CSV (disponibles [ici](sparql/sparql_out_databnf)) : `sparql_main|broader|narrower_out_X_databnf.csv` (avec `broader`
pour les requêtes cherchant à récupérer les termes génériques d'un thème, `narrower` pour récupérer les termes spécifiques
et `main` pour le reste. Ces requêtes permettent de récupérer :
- `?label` : le nom du thème requêté dans databnf
- `?uri` : l'uri de ce thème
- `?cntAUT` : le nombre d'auteur.ice.s lié.e.s au thème
- `?ctnDOC` : le nombre de documents liés au thème
- `?labelRTD` : les noms des termes liés au thème requêté qui figurent aussi dans le dataset
- `?uriRTD` : les uris des termes liés au thème requêté qui figurent aussi dans le dataset
- `?uriNRW` : l'URI des termes spécifiques du thème requêté qui figurent également dans la liste des thèmes
- `?labelNRW` : le nom des termes spécifiques
- `?uriBRD` : l'URI des termes génériques du thème requêté qui figurent également dans la liste des thèmes
- `?labelBRD` : le nom des termes génériques

L'ensemble des fichiers produits et utilisés pour les deux requêtes sont **conservés dans [ce dossier](sparql)**.
- Les requêtes Wikidata se trouvent [ici](sparql/sparql_requests_wikidata)
- Les requêtes Data BnF se trouvent [ici](sparql/sparql_requests_databnf)
- Les résultats des requêtes DataBnF se trouvent [ici](sparql/sparql_out_databnf)
- Les résultats des requêtes Wikidata se trouvent [ici](sparql/sparql_out_wikidata). 

---

## CHÂINE DE TRAITEMENT DATAIKU


---
## FAIT
- url to IP + count IPs
- join table + IPs
- geoIP
- split URL into columns
- split date range into columns
- split mots_clés into columns
- nettoyage des mots clés: lowercase sauf pour noms propres, mettre tout au singulier
 - clusterizer et nettoyer tout à grands coups de regex
 - conserver les sigles entre () pour les mots clés
 - écrire "nomlangue (langue)"
 - normalisation des noms : Nom, Prénom (dates)
- extraction de noms propres via regex
- distinct
- sparql

## APRES
- jointure avec les enrichissements :
 - tableaux d'anahi
 - requêtes sparql
- préparation de petits datasets pour faire des visualisations
- visualisations

