# Documentation des Requêtes SQL de Validation (`raw_data`)

Ce dossier regroupe l'ensemble des scripts SQL permettant de valider, contrôler et auditer la qualité des données brutes intégrées dans le schéma **`raw_data`**. Ce schéma contient les données initiales téléchargées depuis nos différentes sources (ex: Cadastre, Base Adresse Nationale, etc.).

## Inventaire des scripts de contrôle

Le tableau ci-dessous liste l'intégralité des requêtes disponibles, triées par objectif de contrôle :

| Sous-dossier | Fichier SQL | Description du contrôle | Indicateur mesuré |
| :--- | :--- | :--- | :--- |
| **`attribute_checks`** | `A1_count_records.sql` | Compte le nombre total de lignes par table. | Volume de données importées |
| **`geometry_checks`**  | `G1_count_empty_geoms.sql` | Identifie et compte les enregistrements avec une géométrie vide (`ST_IsEmpty`). | Taux de complétude spatiale |
| | `G2_count_invalid_geoms.sql` | Identifie et compte les géométries corrompues ou invalides (`NOT ST_IsValid`). | Taux de validité topologique |
| | `G3_geometry_duplicate.sql` | Détecte les doublons géométries stricts ou les superpositions exactes (`ST_Equals`). | Taux de duplication spatiale |

---

## Détail des Dossiers & Objectifs

### 1. Contrôles attributaires (`attribute_checks`)
Ces scripts se concentrent sur la validation des données textuelles, numériques et de la cohérence globale des tables.
* **`A1_count_records.sql`** : Permet de s'assurer que le processus d'import (via Pandas ou autre) n'a pas perdu de lignes en comparant le résultat au volume du fichier source d'origine.

### 2. Contrôles géométriques (`geometry_checks`)
Ces scripts exploitent les fonctions spatiales (PostGIS / SpatiaLite) pour auditer la qualité géographique avant traitement.
* **`G1_count_empty_geoms.sql`** : Alerte si des objets censés être localisés n'ont pas de coordonnées (ex: adresses BAN sans `lon/lat`).
* **`G2_count_invalid_geoms.sql`** : Crucial pour les polygones ou lignes complexes qui pourraient bloquer de futures jointures spatiales.
* **`G3_geometry_duplicate.sql`** : Permet d'isoler les entités empilées au même endroit de manière anormale.

