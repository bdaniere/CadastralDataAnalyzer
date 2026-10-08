CREATE TABLE IF NOT EXISTS staging.nature_travaux
(
    code VARCHAR(3) PRIMARY KEY,
    description TEXT
);

INSERT INTO staging.nature_travaux (code, description)
VALUES  
    ('CN', 'Construction de bâtiment'),
    ('CSP', 'Construction spéciale (ERP [Établissement Recevant du Public], IGH [Immeuble de Grande Hauteur], ICPE [Installation Classée pour la Protection de l''Environnement])'),
    ('CUR', 'Curage de fossés, de berges'),
    ('DEC', 'Décapage, profilage de chaussées / Démolition superficielle'),
    ('DEM', 'Démolition de bâtiment'),
    ('DRA', 'Drainage, sous-solage d''un terrain (avec ou sans trancheuse)'),
    ('EBL', 'Élagage avec branches au-delà des distances de sécurité'),
    ('ELG', 'Élagage avec branches en-deçà des distances de sécurité'),
    ('ERE', 'Entretien des réseaux électriques'),
    ('ESC', 'Escarpement / talutage'),
    ('FAC', 'Ravalement ou travaux de façade'),
    ('FOH', 'Forage horizontal dirigé'),
    ('FOV', 'Fonçage ou poussage de tuyaux / micro-tunnelier'),
    ('OTR', 'Autres travaux'),
    ('OUV', 'Ouvrages d''art (ponts, murs de soutènement, etc.)'),
    ('RBL', 'Remblaiement'),
    ('SFP', 'Sondage, forage, fondations spéciales, pieux'),
    ('SOU', 'Pose ou réfection de souches / poteaux'),
    ('TER', 'Terrassement général, tranchées ouvertes'),
    ('CHA', 'Chaussée, voirie, pose d''enrobé')
;

CREATE TABLE IF NOT EXISTS staging.technique_travaux
(
    code VARCHAR(3) PRIMARY KEY,
    description TEXT
);

INSERT INTO staging.technique_travaux (code, description)
VALUES
    ('BTO', 'Battage de tube ouvert'),
    ('BRO', 'Brise-roche'),
    ('DBR', 'Découpe de branchement'),
    ('TRA', 'Extraction de tubes par traction'),
    ('ELE', 'Utilisation d''un engin élévateur'),
    ('TUB', 'Fonçage de tubes'),
    ('VIB', 'Utilisation d''un engin vibrant'),
    ('STA', 'Fonçage statique de barres pilotes'),
    ('EXP', 'Emploi d''explosifs')
    ;

CREATE TABLE IF NOT EXISTS staging.nature_declaration
(
    code VARCHAR(10) PRIMARY KEY,
    description TEXT
);

INSERT INTO staging.nature_declaration (code, description)
VALUES
    ('INITIAL', 'Déclaration initiale'),
    ('INVEST', 'Déclaration d''investigation'),
    ('MR_3', 'Déclaration de modification à 3 mois'),
    ('INTERUP', 'Déclaration d''interruption'),
    ('MR_6', 'Déclaration de modification à 6 mois')
;
