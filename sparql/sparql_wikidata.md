# faire des requêtes de la colonne `mots_clés` sur wikidata

---

l'objectif: récupérer tous les mots clés qui sont utilisés dans +0.5% des entrées et les utiliser pour faire des requêtes SPARQL sur wikidata
- pour automatiser la récupération d'URLs wikipedia via wikidata, voir: https://opendata.stackexchange.com/questions/6050/get-wikipedia-urls-sitelinks-in-wikidata-sparql-query
- ce que je veux récupérer:
	- l'entité recherchée: `wd:QXXXXX` 
	- instance of : `P31`
	- part of: `P371`
	- part of: `P371`
	- nombre de personnes qui ont pour "field of work": `P101`
	- nombre d'instances spécifiques du mot clé (nombre de livres dans la catégorie littérature): `P31`
	- Wikipedia en anglais et français (avec dans l'exemple ci-dessous CID la ressource recherchée)
 	```
	OPTIONAL {
  	    ?article schema:about ?cid .
      	    ?article schema:inLanguage "en" .
       	    ?article schema:isPartOf <https://en.wikipedia.org/> .
     	}
	 ```

---

## les identifiants (à préfixer de wd: ou wdt: je crois)
- blog | blog: Q30849
- France | France: Q142
- écrivain | writer: Q36180
- 21e siècle | 21st century: Q6939
- site | website: Q35127
- littérature, livre et lecture | literature: Q8242
- éditeur | éditeur: Q1607826
- 20e siècle | 20th century: Q6927
- revue (en ligne ou non) | periodical: Q1002697
- artiste | artist: Q483501
- littérature jeunesse | children's and youth literature: Q11163999
- francophonie | francophonie: Q1003588
- création littéraire | creative writing: Q586060
- bande dessinée | comics: Q1004
- ISSN |  International Standard Serial Number: Q131276
- évènement (festival, biennale, foire) | cultural event: Q58687420
- association | association: Q15911314
- librairie | bookshop: Q200764
- science-fiction  | science fiction: Q24925
- site universitaire | faculty web page: Q109647055
- histoire du livre et bibliothéconomie | library science: Q199655
