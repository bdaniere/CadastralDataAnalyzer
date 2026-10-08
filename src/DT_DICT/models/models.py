from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class NatureProjet(Enum):
    CNS = "CNS"
    CSP = "CSP"
    CUR = "CUR"
    DEC = "DEC"
    DEM = "DEM"
    DRA = "DRA"
    EBL = "EBL"
    ELG = "ELG"
    ERE = "ERE"
    ESC = "ESC"
    FAC = "FAC"
    FOH = "FOH"
    FOV = "FOV"
    OTR = "OTR"
    OUV = "OUV"
    RBL = "RBL"
    SFP = "SFP"
    SOU = "SOU"
    TER = "TER"
    CHA = "CHA"


class TechniqueTravaux(Enum):
    BTO = "BTO"
    BRO = "BRO"
    DBR = "DBR"
    TRA = "TRA"
    ELE = "ELE"
    TUB = "TUB"
    VIB = "VIB"
    STA = "STA"
    EXP = "EXP"


class NatureDeclaration(Enum):
    INITIAL = "INITIAL"
    INVEST = "INVEST"
    MR_3 = "3MR"
    INTERUP = "INTERUP"
    MR_6 = "6MR"


class DeclarationType(Enum):
    DT = "DT"
    DICT = "DICT"
    CONJOINTE = "CONJOINTE"


@dataclass
class Coordonnees:
    nom_prenom: str
    telephone: str
    fax: str | None
    courriel: str


@dataclass
class Adresse:
    numero_voie: str | None
    libelle_voie: str | None
    lieu_dit: str | None
    code_postal: str | None
    commune: str | None
    pays: str | None = None


@dataclass
class Acteur:
    denomination: str
    complement: str | None
    adresse: Adresse
    coordonnees: Coordonnees
    numero_siret: str


@dataclass
class ResponsableProjet(Acteur):
    is_moral: bool


@dataclass
class SouhaitReceptionRecepisse:
    want: bool
    mode: str | None
    taille: str | None
    color: bool | None
    vector: bool | None
    format: str | None


@dataclass
class InvestigationComplementaire:
    realisation: bool | None
    motif: str | None
    date_realisation: date | None
    need_dict: bool | None
    envoi_resultat: bool | None


@dataclass
class Declaration:
    """
    Classe racine commune à tous les documents DT-DICT.
    """

    numero_consultation: str
    declaration_type: DeclarationType
    numero_affaire: str | None = None
    date_declaration: date | None = None
    emplacement_projet: Adresse | None = None
    nb_communes: int | None = None
    souhait_reception_recepisse: SouhaitReceptionRecepisse | None = None
    nature_travaux: list[NatureProjet] = field(default_factory=list)
    description_travaux: str | None = None
    distance_elec_aerien: float | None = None
    need_plan_aerien: bool | None = None
    date_travaux: date | None = None
    duree_travaux: float | None = None
    nom_signataire: str | None = None
    geom: str | None = None  # TODO : a voir


@dataclass
class DT(Declaration):
    """
    Déclaration de Travaux.
    """

    responsable_projet: ResponsableProjet | None = None
    representant: Acteur | None = None
    emploi_technique_sans_tranche: bool | None = None
    investigation_complementaire: InvestigationComplementaire | None = None


@dataclass
class DICT(Declaration):
    """
    Déclaration d'Intention de Commencement de Travaux.
    """

    nature_declaration: NatureDeclaration | None = None
    executant: Acteur | None = None
    techniques_utilisees: list[TechniqueTravaux] = field(default_factory=list)
    technique_autre: str | None = None
    profondeur_travaux: float | None = None
    modification_profil: bool | None = None
    resultat_investigation_complementaire: bool | None = None
    duree_travaux: float | None = None
    dt_reference: str | None = None
