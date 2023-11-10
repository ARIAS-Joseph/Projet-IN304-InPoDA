### README - Projet InPoDa

# Auteurs

GAUTEUR Mathilde
ARIAS Joseph

# Licence

GPL (General Public License)

# Mainteneur

Joseph ARIAS (Contact: joseph.arias@ens.uvsq.fr)

# Statut du Projet

En cours de développement

# Description du Projet

InPoDA est une plateforme fictive pour l’analyse de données de réseaux sociaux. On fournit à la plateforme une liste de tweet sous le format .json. InPoDA vérifie d’abord la structure de l’objet tweet, le nettoie en éliminant les emojis au cas où il y en a, et stocke la liste de tweet nettoyés dont la structure est correcte dans un fichier, appelé « zone d’atterrissage ». En pièces jointes un jeu de publications (tweets) que vous pouvez utiliser.

# Dépendances

textblob: Pour l'analyse de sentiment.
matplotlib: Pour la création de graphiques.
folium: Pour la création de cartes géographiques.
geopy: Pour la géolocalisation des tweets.
regex: Pour les opérations sur les expressions régulières.
plotly: Pour la visualisation de données.
tkinter: Pour l'interface graphique.
Pillow (PIL): Pour le traitement des images.
emoji: Pour la gestion des emojis dans les tweets.

# Fonctionnalités Principales

Extraction des Informations des Tweets
    Extraction des hashtags, utilisateurs mentionnés, auteur de la publication, le nombre de publication d'un auteur
    Analyse de sentiment (positif, neutre, négatif).
    Analyse de l'objectivité des tweets.

Visualisation des Données
    Top k hashtags, k utilisateurs mentionnés, et k utilisateurs ayant posté le plus de tweets.
    Nombre de publications pour un hashtag donné.
    Affichage des tweets d'un utilisateur spécifique.

Graphiques Statistiques
    Graphiques représentant la polarité et l'objectivité des tweets.
    Carte mondiale indiquant les lieux où les tweets ont été postés.
    Visualisation du nombre de tweets par heure.

Interface Utilisateur
    Interface graphique permettant de charger un fichier JSON contenant des tweets.
    Affichage des résultats dans la console.

# Remarques Importantes

La fonction world_map nécessite une connexion internet pour fonctionner.
La fonction world_map() prend du temps à s'exécuter en raison de la géolocalisation des tweets.

# Avenir du Projet

Le projet est en cours de développement jusqu'en décembre 2023, et des fonctionnalités supplémentaires ainsi que des améliorations sont à prévoir. Votre contribution est la bienvenue!
