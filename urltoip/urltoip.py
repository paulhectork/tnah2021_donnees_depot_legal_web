import csv
import dns.resolver

"""
A PROPOS
--------
ce script python permet prend tous les URLs du jeu de données et leur associe une adresse IP. si 
l'adresse IP n'est pas retrouvée, le script remplace l'adresse IP par 3 types de messages: 
    -'lien mort' (correspondant à un message d'erreur "The DNS query name does not exist")
    -'timed out' (correspondant à un message "The DNS operation timed out.")
    -'autre erreur' (pour les autres messages d'erreur, moins fréquents).
le script est externe à Dataiku parce que nous n'avons pas réussi à le faire fonctionner dans l'implémentation
python de Dataiku (après de **nombreux** essais). nous avons donc téléchargé le fichier source avant d'y appliquer
le script en local, de mettre en ligne le fichier csv produit et de le joindre avec notre jeu de données.

input
-----
un fichier csv composé des différentes années de notre jeu de données nettoyé une première fois.
ce CSV correspond au fichier INPUT* du présent dossier.

output
------
un fichier csv qui associe à chaque URL une ou plusieurs adresses IP. ce fichier correspond au fichier
OUTPUT* du présent dossier.
"""

# ouvrir les fichiers, initier les variables etc
with open("collecteweb_litteratureetart_bnf_2011_2016_prepared_stacked_prepared.csv") as fr:
    csvreader = csv.reader(fr, delimiter=",")
    fr.seek(0)
    next(fr)
    nboucles = 0  # nombre d'itérations.
                  # attention: nboucles compte le nombre d'URLs, nboucles_ok|no comptent le nombre d'IP
    nboucles_ok = 0  # nombre d'adresses IP ok
    nboucles_no = 0  # nombre d'adresses IP non trouvées
    with open("collecteweb_litteratureetart_bnf_2011_2016_python.csv", mode="w") as fw:
        csvwriter = csv.writer(fw, delimiter=",")
        csvwriter.writerow(["URL de départ", "URL to IP"])

        # itérer sur chaque élément pour récupérer les adresses IP si elles existent
        for row in csvreader:
            nboucles += 1
            print("-----")
            print(nboucles)
            url = row[1]  # url : l'url source
            try:
                result = dns.resolver.resolve(url, "A")
                for ipadr in result:
                    nboucles_ok += 1
                    csvwriter.writerow([url, ipadr])
                    print(ipadr)
            except Exception as error:
                if "timed out" in str(error):
                    ipadr = "timeout"
                    csvwriter.writerow([url, ipadr])
                    nboucles_no += 1
                elif "DNS query name does not exist" in str(error):
                    ipadr = "lien mort"
                    csvwriter.writerow([url, ipadr])
                    nboucles_no += 1
                else:
                    ipadr = "autre erreur"
                    csvwriter.writerow([url, ipadr])
                    nboucles_no += 1
                print(ipadr)
                print(str(error))

print(nboucles)
print(nboucles_ok)
print(nboucles_no)
