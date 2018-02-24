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

### Hierarchie des classes des ontologies (OK)
**GOOD** : Prendre en compte la hiérarchie des classes de l'ontologie, le rajouter dans le schema rdf avec des subClassOf  

### Améliorer le format pour add methode
**NOT GOOD** : Changer le format du fichier d'entrée pour ajouter une methode pour pouvoir avoir
une hierarchie de cluster  

### Interface de visualisation

**NOT GOOD** : Faire l'interface graphique du site web en prototype

### Noeuds blanc pour les cluster
**NOT GOOD** : Mettre des noeuds blanc pour les cluster

### Erreur / Bug en vrac à corriger
**NOT GOOD** : Erreur code extract_ontologies_concepts.py, on a un retour avec une uri avec espace (voir ligne 409 rdf_onto_extraction.rdf)
