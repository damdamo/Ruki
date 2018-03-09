### Problème sur le Prefix CUI
**GOOD** : Le prefix pour les articles a déjà été remplacé: On est passé de cui:article à schema:Article  
De même dans le cas des ontologies nous avons la bonne URI, celle de base du fichier ce qui n'était pas le cas avant. Le lien entre les articles et les concepts a été remplacé par un noeud blanc.  
**NOT GOOD** : Changer les prefix cui ou mettre l'équivalence sameAs (cf cui:article etc...)
DANS LE CAS DU NOM DES CLASSES ON ENLEVE CUI OU PAS ? QUEL URI ?
Voir le fichier extract_ontologies_concept.py
cui.knowledge_extractor_result (Vraiment utile en sachant qu'on est déjà subClassOf concept scheme)
cui.art_concept_link (Qu'est ce qu'on en fait avec toutes les propriétés)
cui.has_concept
cui.has_article etc...

### Erreur / Bug en vrac à corriger
**NOT GOOD** : Erreur code extract_ontologies_concepts.py, on a un retour avec une uri avec espace (voir ligne 409 rdf_onto_extraction.rdf)

### Export data base
**NOT GOOD** : Pouvoir exporter les données de rdf4j sous forme d'un json/yaml avec deux options !
* Option 1: On récupère juste les articles avec leurs infos
* (À VOIR) Option 2: On récupère tout !

### Import sa méthode dans le graphe de connaissance
**NOT GOOD**: Pouvoir mettre un fichier json/yaml qui sera intégré à la base de connaissance

### Créer le bon format json pour l'interface graphique "world"
**NOT GOOD**: Le format du code d3js pour réaliser l'interface graphique prend un json d'un certain format qu'il faut réaliser. Il faut créer un fichier json par méthode qui sera utilisé pour afficher l'ensemble du "world".

### Modifier le script d3js pour ajouter les options voulues
**NOT GOOD**: Ajout des feuilles cliquables qui donnent accès aux données qui nous intéressent !
De plus il faut donner la possibilité à l'utilisateur de changer de vue à ce moment !

### Aggrémenter le site
**NOT GOOD**: Ajouter des pages pour séparer les différentes tâches (import/export, world, ...)
