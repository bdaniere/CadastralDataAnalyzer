import json
import re
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from functools import cached_property
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints
from xml.etree import ElementTree as ET

import pdfplumber
from models.models import DICT, DT, DeclarationType
from pdfplumber.page import Page as pdfplumber_page
from pypdf import PdfReader
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import transform as shapely_transform

# ██████╗  ██████╗  ██████╗██╗   ██╗███╗   ███╗███████╗███╗   ██╗████████╗    ██╗███╗   ██╗███████╗ ██████╗██████╗ ███████╗ ██████╗████████╗ ██████╗ ██████╗
# ██╔══██╗██╔═══██╗██╔════╝██║   ██║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝    ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
# ██║  ██║██║   ██║██║     ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║       ██║██╔██╗ ██║███████╗██║     ██████╔╝█████╗  ██║        ██║   ██║   ██║██████╔╝
# ██║  ██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║       ██║██║╚██╗██║╚════██║██║     ██╔═══╝ ██╔══╝  ██║        ██║   ██║   ██║██╔══██╗
# ██████╔╝╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║   ██║       ██║██║ ╚████║███████║╚██████╗██║     ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║
# ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝


class FileType(Enum):
    PDF = "pdf"
    IMAGE = "image"
    XML = "xml"
    ZIP = "zip"
    UNKNOWN = "unknown"


class ContentType(Enum):
    ACROFORM_PDF = "acroform_pdf"
    FLATTENED_PDF = "flattened_pdf"
    SCANNED_PDF = "scanned_pdf"
    IMAGE = "image"
    XML = "xml"
    UNKNOWN = "unknown"


# TODO : avoir une approche page par page : es-ce nécéssaire ?
class DocumentInspector:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    @cached_property
    def is_pdf(self) -> bool:
        try:
            with open(self.file_path, "rb") as f:
                return f.read(5) == b"%PDF-"
        except OSError:
            return False

    @cached_property
    def is_xml(self) -> bool:
        try:
            next(ET.iterparse(self.file_path, events=("start",)))
            return True
        except (OSError, ET.ParseError, StopIteration):
            return False

    @cached_property
    def form_fields(self) -> dict[str, str]:
        """
        Extract AcroForm fields if present.
        """

        try:
            fields = self.pdf_reader.get_form_text_fields()
            return fields or {}

        except Exception:
            return {}

    @cached_property
    def pdf_reader(self) -> PdfReader:
        if not self.is_pdf:
            raise ValueError(f"{self.file_path} is not a PDF file.")

        return PdfReader(self.file_path)

    @cached_property
    def has_extractable_text(self) -> bool:

        for page in self.pdf_reader.pages:
            text = (page.extract_text() or "").strip()

            if len(text) >= 20:
                return True

        return False

    @property
    def has_form_fields(self) -> bool:
        return len(self.form_fields) > 0

    @property
    def file_type(self) -> FileType:
        if self.is_pdf:
            return FileType.PDF

        if self.is_xml:
            return FileType.XML

        return FileType.UNKNOWN

    @property
    def content_type(self) -> ContentType:

        if self.file_type == FileType.XML:
            return ContentType.XML

        if self.file_type != FileType.PDF:
            return ContentType.UNKNOWN

        if self.has_form_fields:
            return ContentType.ACROFORM_PDF

        if self.has_extractable_text:
            return ContentType.FLATTENED_PDF

        return ContentType.SCANNED_PDF

    @property
    def document_info(self) -> dict:
        info = {
            "file_type": self.file_type.value,
            "content_type": self.content_type.value,
            "has_form_fields": self.has_form_fields,
        }
        if self.file_type == FileType.PDF:
            info["page_count"] = len(self.pdf_reader.pages)
        return info

    def __repr__(self) -> str:
        return (
            f"DocumentInspector({self.file_path}, document_info={self.document_info})"
        )


# ██████╗  █████╗ ██████╗ ███████╗███████╗██████╗         ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
# ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗        ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
# ██████╔╝███████║██████╔╝███████╗█████╗  ██████╔╝        █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝
# ██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝  ██╔══██╗        ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝
# ██║     ██║  ██║██║  ██║███████║███████╗██║  ██║███████╗██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║
# ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝


class ParserFactory:
    def __init__(self, file_path: Path):
        """
        Initialize the ParserFactory with the given file path.

        Args:
            file_path (Path): The path to the file to be parsed.
        """

        self.file_path = file_path


class FlattenedPDFParser(ParserFactory):
    TARGET_EPSG = "EPSG:2154"

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.reader = PdfReader(file_path)

        with open("template_14434_03.json", encoding="utf-8") as f:
            self.template_cerfa = json.load(f)

        with open("template_cerfa_detection.json", encoding="utf-8") as f:
            self.template_cerfa_detection = json.load(f)

    def read_content(self):
        """
        Read the content of the first page of the PDF.

        TODO :
         - présence de plusieurs cerfa dans un document en entré
         - Aucun cerfa détecté

        Returns:
            list[DT | DICT]: the declarations found in the cerfa (both when
            the cerfa is filled as a joint DT-DICT).
        """

        results = {"DT": {}, "DICT": {}, "global": {}}

        with pdfplumber.open(self.file_path) as pdf_file:
            for page in pdf_file.pages:
                if not (abs(page.width - 595) < 2 and abs(page.height - 842) < 2):
                    raise NotImplementedError(
                        "Page dimensions are not A4 / rezise need ?"
                    )

                if self._is_dt_dict_cerfa(page):
                    results = self.extract_cerfa_data(page, results)
                elif self._is_page_contain_geometry(page):
                    results = self.extract_geometry(page, results)

        return self._build_declarations(results)

    def _build_declarations(self, results: dict) -> list[DT | DICT]:
        """
        Build a list of declarations from the extracted results.

        Args:
            results (dict): The extracted results from the PDF.

        Returns:
            list[DT | DICT]: The list of declarations.
        """

        declarations = []
        for section, cls in (("DT", DT), ("DICT", DICT)):
            values = dict(results[section])
            if not any(v not in (None, False) for v in values.values()):
                continue

            if section == "DICT":
                values["declaration_type"] = DeclarationType.DICT
            elif values.pop("is_conjointe", False):
                values["declaration_type"] = DeclarationType.CONJOINTE
            else:
                values["declaration_type"] = DeclarationType.DT
            values["emprise.geometrie"] = results["global"].get("geom")

            print(values)

            declarations.append(self._build(cls, values))

        return declarations

    @classmethod
    def _build(cls, model: type, values: dict[str, Any], prefix: str = ""):
        """Instantiate a dataclass from flat 'a.b.c' keyed values."""
        hints = get_type_hints(model)
        kwargs = {}
        for f in fields(model):
            tp = cls._unwrap_optional(hints[f.name])
            key = prefix + f.name
            if is_dataclass(tp):
                sub_prefix = key + "."
                has_values = any(
                    k.startswith(sub_prefix) and v not in (None, False)
                    for k, v in values.items()
                )
                kwargs[f.name] = (
                    cls._build(tp, values, sub_prefix) if has_values else None
                )
            else:
                kwargs[f.name] = cls._convert(values.get(key), tp)
        return model(**kwargs)

    @staticmethod
    def _unwrap_optional(tp):
        args = [a for a in get_args(tp) if a is not type(None)]
        if get_origin(tp) in (Union, UnionType) and len(args) == 1:
            return args[0]
        return tp

    @classmethod
    def _convert(cls, value, tp):
        """Coerce an extracted value to the dataclass field type."""
        if get_origin(tp) is list:
            (item_tp,) = get_args(tp)
            if isinstance(value, list):
                return value
            tokens = re.split(r"[\s,;/+]+", value or "")
            items = [cls._convert(t, item_tp) for t in tokens if t]
            return [i for i in items if i is not None]

        if value is None:
            return None
        if isinstance(tp, type) and isinstance(value, tp):
            return value

        try:
            if tp is bool:
                return bool(value)
            if tp is int:
                return int(re.sub(r"\D", "", value))
            if tp is float:
                return float(value.replace(",", ".").replace(" ", ""))
            if isinstance(tp, type) and issubclass(tp, Enum):
                return tp(str(value).strip().upper())
        except (ValueError, TypeError):
            return None
        return value

    def _is_dt_dict_cerfa(self, page: pdfplumber_page) -> bool:
        """
        Check if the page matches the DT_DICT cerfa template.

        TODO : Verification is currently limited to Cerfa form 14434*03
        """

        check_fields = {}
        for field_name, field in self.template_cerfa_detection["fields"].items():
            area = self._crop_center(page, tuple(field["bbox"]))
            text = (area.extract_text() or "").strip()
            check_fields[field_name] = text

        return check_fields == {
            "GLOBAL.titre": "Déclaration de projet de Travaux\nDéclaration d’Intention de Commencement de Travaux",
            "GLOBAL.cerfa_numero": "N° 14434*03",
        }

    def _is_page_contain_geometry(self, page: pdfplumber_page) -> bool:
        text = page.extract_text()
        return bool(
            re.search(r"<gml:Polygon\b[^>]*>.*?</gml:Polygon>", text, flags=re.DOTALL)
        )

    def extract_cerfa_data(self, page: pdfplumber_page, results) -> dict:
        """
        Extract data from the DT_DICT cerfa page.

        Returns a dictionary with the extracted field values.
        """

        page = page.filter(
            lambda obj: (
                "casesaremplir" not in obj.get("fontname", "").lower()
                and not (
                    obj.get("text") == "_"
                    and "helvetica" not in obj["fontname"].lower()
                )
            )
        )

        for field_name, field in self.template_cerfa["fields"].items():
            category, name = field_name.split(".", 1)
            area = self._crop_center(page, tuple(field["bbox"]))
            text = (area.extract_text() or "").strip()

            if field["type"] == "checkbox":
                results[category][name] = bool(text)
            elif field["type"] == "date":
                results[category][name] = self._parse_date(text)
            else:
                results[category][name] = text or None

        return results

    def extract_geometry(self, page: pdfplumber_page, results) -> dict:
        """
        Extract the first GML polygon of the page, reproject it to TARGET_EPSG
        and store its WKT in results["global"]["geom"].

        TODO: Handle cases where the page does not contain a GML polygon.
        """

        text = page.extract_text() or ""
        match = re.search(
            r"<gml:Polygon\b[^>]*>.*?</gml:Polygon>", text, flags=re.DOTALL
        )
        if not match:
            return results

        gml = match.group(0).replace("\n", "").replace("gml:", "")
        root = ET.fromstring(gml)

        def read_ring(ring: ET.Element) -> list[tuple[float, float]]:
            values = [float(v) for v in ring.findtext(".//posList", "").split()]
            if len(values) % 2:
                raise ValueError("GML posList has an odd number of values")
            return list(zip(values[::2], values[1::2]))

        exterior = read_ring(root.find("./exterior/LinearRing"))
        interiors = [read_ring(r) for r in root.findall("./interior/LinearRing")]
        polygon = Polygon(exterior, interiors)

        source_epsg = root.get("srsName", "EPSG:4326")
        transformer = Transformer.from_crs(
            source_epsg, self.TARGET_EPSG, always_xy=True
        )
        results["global"]["geom"] = shapely_transform(
            transformer.transform, polygon
        ).wkt

        return results

    @staticmethod
    def _crop_center(page, bbox: tuple[float, float, float, float]):
        """Keep only the objects whose center lies inside the bbox."""
        x0, top, x1, bottom = bbox
        return page.filter(
            lambda obj: (
                x0 <= (obj["x0"] + obj["x1"]) / 2 <= x1
                and top <= (obj["top"] + obj["bottom"]) / 2 <= bottom
            )
        )

    @staticmethod
    def _parse_date(text: str) -> date | None:
        """Parse 'dd / mm / yyyy'; return None if empty or invalid."""
        try:
            return datetime.strptime("".join(text.split()), "%d/%m/%Y").date()
        except ValueError:
            return None


class XMLParser(ParserFactory):
    TARGET_EPSG = FlattenedPDFParser.TARGET_EPSG

    def __init__(self, xml_path: Path):
        super().__init__(xml_path)
        self.root = ET.parse(xml_path).getroot()

        # Drop namespaces so that tags match the dataclass field names.
        for element in self.root.iter():
            element.tag = element.tag.rsplit("}", 1)[-1]

    def read_content(self) -> list[DT | DICT]:
        """
        Returns:
            list[DT | DICT]: the declarations found in the XML (both when
            the file is a joint DT-DICT).
        """

        declarations: list[DT | DICT] = []

        dt = self.root.find("DT")
        if dt is None:
            dt = self.root.find("dtDictConjointes/partieDT")
        if dt is not None:
            conjointe = dt.findtext("declarationConjointeDTDICT", "").strip() == "true"
            declaration_type = (
                DeclarationType.CONJOINTE if conjointe else DeclarationType.DT
            )
            declarations.append(self._build(DT, dt, declaration_type=declaration_type))

        dict_part = self.root.find("dtDictConjointes/partieDICT")
        if dict_part is not None:
            declarations.append(
                self._build(DICT, dict_part, declaration_type=DeclarationType.DICT)
            )

        return declarations

    def _build(self, model: type, element: ET.Element, **overrides):
        """Instantiate a dataclass from the child elements named like its fields."""
        hints = get_type_hints(model)
        kwargs = {}
        for f in fields(model):
            if f.name in overrides:
                kwargs[f.name] = overrides[f.name]
                continue

            tp = FlattenedPDFParser._unwrap_optional(hints[f.name])
            child = element.find(f.name)

            if get_origin(tp) is list:
                (item_tp,) = get_args(tp)
                if is_dataclass(item_tp):
                    items = (
                        [self._build(item_tp, c) for c in child]
                        if child is not None
                        else []
                    )
                else:
                    items = [
                        self._convert(c.text, item_tp) for c in element.findall(f.name)
                    ]
                kwargs[f.name] = [i for i in items if i is not None]
            elif child is None:
                kwargs[f.name] = None
            elif f.name == "geometrie":
                kwargs[f.name] = self._read_geometry(child)
            elif is_dataclass(tp):
                kwargs[f.name] = self._build(tp, child)
            else:
                kwargs[f.name] = self._convert(child.text, tp)
        return model(**kwargs)

    @staticmethod
    def _convert(text: str | None, tp):
        """Coerce an element text to the dataclass field type."""
        text = (text or "").strip()
        if not text:
            return None
        try:
            if tp is bool:
                return text.lower() == "true"
            if tp is int:
                return int(text)
            if tp is float:
                return float(text)
            if tp is datetime:
                return datetime.fromisoformat(text)
            if tp is date:
                return date.fromisoformat(text[:10])  # drops the timezone suffix
            if isinstance(tp, type) and issubclass(tp, Enum):
                return tp(text.upper())
        except ValueError:
            return None
        return text

    def _read_geometry(self, element: ET.Element) -> str | None:
        """Read the first GML polygon and return its WKT in TARGET_EPSG."""
        polygon_el = element.find(".//Polygon")
        if polygon_el is None:
            return None

        def read_ring(ring: ET.Element) -> list[tuple[float, float]]:
            coordinates = ring.findtext("coordinates")
            if coordinates:
                return [
                    tuple(float(v) for v in pair.split(",")[:2])
                    for pair in coordinates.split()
                ]
            values = [float(v) for v in ring.findtext(".//posList", "").split()]
            return list(zip(values[::2], values[1::2]))

        exterior = read_ring(polygon_el.find("exterior/LinearRing"))
        interiors = [read_ring(r) for r in polygon_el.findall("interior/LinearRing")]
        polygon = Polygon(exterior, interiors)

        transformer = Transformer.from_crs(
            element.get("srsName", "EPSG:4326"), self.TARGET_EPSG, always_xy=True
        )
        return shapely_transform(transformer.transform, polygon).wkt


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝

"""
TODO
    - gestion des checkbo avec valeur true et false que l'on met dans une seule variable in-fine
"""

if __name__ == "__main__":
    # input_file_path = Path("/home/bn/Documents/maquette/Travaux-Prevelles-09-2026.pdf")
    input_file_path = Path(
        "/home/bn/Documents/maquette/2026100801380T_DICT-DT Conjointe_1.pdf"
    )
    # input_file_path = Path(
    #     "/home/bn/Documents/Perso/CadastralDataAnalyzer/src/DT_DICT/dev_tools/2026100800884T_DDC/2026100800884T_DDC_description/2026100800884T_DDC_description.xml"
    # )

    document_inspector = DocumentInspector(input_file_path)
    print(document_inspector.document_info)

    if document_inspector.document_info["file_type"] == "pdf":
        if document_inspector.document_info["content_type"] == "flattened_pdf":
            flattened_pdf = FlattenedPDFParser(input_file_path)
            content = flattened_pdf.read_content()
        elif document_inspector.document_info["content_type"] == "scanned_pdf":
            # scanned_pdf = ScannedPDFParser(input_file_path)
            # content = scanned_pdf.read_content()
            raise NotImplementedError("Scanned PDF parsing is not implemented yet.")
    elif document_inspector.document_info["file_type"] == "xml":
        xml_parser = XMLParser(input_file_path)
        content = xml_parser.read_content()

    breakpoint()
