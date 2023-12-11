# Projet InPoDa

## Table des Matières

- [Auteurs](#auteurs)
- [Licence](#licence)
- [Mainteneur](#mainteneur)
- [Statut du Projet](#statut-du-projet)
- [Description du Projet](#description-du-projet)
- [Dépendances](#dépendances)
- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Remarques Importantes](#remarques-importantes)
- [Avenir du Projet](#avenir-du-projet)

## Auteurs

- GAUTEUR Mathilde
- ARIAS Joseph

## Licence

GPL (General Public License)

## Mainteneur

Joseph ARIAS (Contact: joseph.arias@ens.uvsq.fr)

## Statut du Projet

Projet rendu le 12 décembre 2023

## Description du Projet

InPoDA est une plateforme fictive pour l’analyse de données de réseaux sociaux. On fournit à la plateforme une liste de tweet sous le format .json. InPoDA vérifie d’abord la structure de l’objet tweet, le nettoie en éliminant les emojis au cas où il y en a, et stocke la liste de tweet nettoyés dont la structure est correcte dans un fichier, appelé « zone d’atterrissage ». En pièces jointes un jeu de publications (tweets) que vous pouvez utiliser.

## Dépendances

    pip install json time geopy textblob folium plotly pandas emoji gradio regex

- json (js) : Pour le traitement des données au format JSON.
- time : Pour la gestion du temps et des délais.
- geopy.exc : Pour la gestion des exceptions dans les fonctionnalités de géolocalisation.
- TextBlob (de la bibliothèque textblob) : Pour l'analyse de texte et le traitement du langage naturel.
- random : Pour la génération de nombres aléatoires.
- folium : Pour la création de cartes interactives.
- Counter (de la bibliothèque collections) : Pour le comptage d'éléments itérables.
- Nominatim (de la bibliothèque geopy.geocoders) : Pour la géocodification et la recherche de coordonnées à partir d'adresses.
- regex (re) : Pour les expressions régulières.
- plotly.express (px) : Pour la création de visualisations interactives.
- pandas (pd) : Pour la manipulation et l'analyse de données.
- os : Pour les fonctionnalités liées au système d'exploitation.
- emoji : Pour la gestion des émojis.
- gradio : Pour la création d'interfaces utilisateur interactives.
- operator : Pour les opérations sur les opérateurs en Python.
- threading : Pour la gestion des threads et le multithreading.

## Fonctionnalités Principales

Extraction des Informations des Tweets:
- Extraction des hashtags, utilisateurs mentionnés, auteur de la publication, le nombre de publication d'un auteur
- Analyse de sentiment (positif, neutre, négatif).
- Analyse de l'objectivité des tweets.

Visualisation des Données:
- Top k hashtags, k utilisateurs mentionnés, et k utilisateurs ayant posté le plus de tweets.
- Nombre de publications pour un hashtag donné.
- Affichage des tweets d'un utilisateur spécifique.

Graphiques Statistiques:
- Graphiques représentant la polarité et l'objectivité des tweets.
- Carte mondiale indiquant les lieux où les tweets ont été postés.
- Visualisation du nombre de tweets par heure.

Interface Utilisateur:
- Interface graphique permettant de charger un fichier JSON contenant des tweets.
- Affichage des résultats dans la console.

## Remarques Importantes:

- La fonction world_map nécessite une connexion internet pour fonctionner.
- La fonction world_map() prend du temps à s'exécuter en raison de la géolocalisation des tweets (3 tweets géolocalisés par seconde environ).

## Avenir du Projet

La version finale du projet a été rendue le 12 décembre 2023. Plus aucune mis à jour ne sera faite. Cependant il est toujours possible de contacter le mainteneur pour toute question relative au projet.
