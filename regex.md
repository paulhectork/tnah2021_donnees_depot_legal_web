noms propres 1: ^[A-Z](d'|-|de)?(\s[A-Z])?([àáâäéèêëíìîïòóôöúùûüøœæ]|[a-z])+$ (sans virgule)
noms propres 2: ^[A-Z](\w|\s)*,\s[A-Z]\w+$ (quand il y a une virgule)


der: noms propres avec virgules: ^([A-Z](\w|[àáâäéèêëíìîïòóôöúùûüøœæ]|\s|')*)+,\s([A-Z](\w|[àáâäéèêëíìîïòóôöúùûüøœæ]|\s|')*)(\s\(\d{4}-\d{4}\))?$ (remplacé par $3 $1 $5
der: noms propres sans virgules: ^[A-Z](((d')|-|de|\s|[A-Z])*([àáâäéèêëíìîïòóôöúùûüøœæ]|[a-z])+)+(\s\(\d{4}-\d{4}\))?$
