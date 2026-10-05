# CadastralDataAnalyser

Ce projet est un outil pédagogique pour me remettre a jour sur certaines technologies (notamment lié au monde de la géomatique). Il permet actuellement de récupérer automatiquement des données cadastrales et d'adresse depuis l'open data du gouvernement et les stocker dans une base de données géospatiale pour une visualisation ultérieure via GeoServer.

## Fonctionnalités

Ce projet comprend les principales fonctionnalités suivantes :

1. **Téléchargement de données cadastrales** :
   - La fonction `download_cadastre_data` permet de télécharger des données cadastrales pour un territoire spécifique (commune ou département) et une couche spécifique (communes, sections, feuilles, parcelles, batiments).
   - Les données sont ensuite stockées dans une base de données PostGIS.

2. **Téléchargement de données d'adresse** :
   - La fonction `download_ban_data` permet de télécharger les données de l'adresse nationale (BAN) pour un territoire spécifique (commune ou département).
   - Les données sont ensuite stockées dans la même base de données PostGIS.

3. **Utilisation de Docker** :
   - Le projet est mis en place dans un environnement Docker pour simplifier la gestion des dépendances et la configuration.

## Architecture

L'architecture du projet est basée sur les composants suivants :

- **PostGIS** : Base de données géospatiale pour stocker les données cadastrales et d'adresse.
- **GeoServer** : Serveur pour la visualisation des données géospatiales stockées dans PostGIS.

## Installation et utilisation

Pour installer et utiliser ce projet, suivez les étapes suivantes :

1. **Installation des dépendances** :
   - Assurez-vous d'avoir Docker et Docker Compose installés sur votre système.
   - Clonez ce dépôt sur votre machine.
   - Naviguez jusqu'au répertoire du projet et exécutez :
     ```bash
     docker-compose up -d
     ```

2. **Configuration des variables d'environnement** :
   - Le fichier `.env` doit être créé dans le répertoire racine du projet.
   - Ajoutez les variables suivantes :
     ```plaintext
     DB_USER=postgres
     DB_PASSWORD=postgres
     DB_HOST=postgis
     DB_PORT=5432
     DB_NAME=cadastral_data
     ```

3. **Exécution du script** :
   - Exécutez le script principal `download_data.py` :
     ```bash
     docker-compose run --rm app python src/Base_data_creation/download_data.py
     ```

## Contribuer

Les contributions sont les bienvenues! Veuillez vous assurer de suivre les lignes directrices de contribution avant de soumettre une demande de fusion.

## License

Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus de détails.

## Auteur

Ce projet a été réalisé par [Benjamin Daniere](mailto:benjamin.daniere@gmail.com).

---

Ce projet a pour objectif de vous aider à mieux comprendre les outils de géomatique et de gestion de données, en vous permettant de travailler avec des données ouvertes et de les stocker et visualiser efficacement. N'hésitez pas à me poser des questions si vous avez besoin d'aide supplémentaire.