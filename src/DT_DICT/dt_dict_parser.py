import json
from datetime import date, datetime
from enum import Enum
from functools import cached_property
from pathlib import Path

import pdfplumber
from pdfplumber.page import Page as pdfplumber_page
from pypdf import PdfReader

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


# TO DO : avoir une approche page par page : es-ce nécéssaire ?
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

        return FileType.UNKNOWN

    @property
    def content_type(self) -> ContentType:

        if self.file_type != FileType.PDF:
            return ContentType.UNKNOWN

        if self.has_form_fields:
            return ContentType.ACROFORM_PDF

        if self.has_extractable_text:
            return ContentType.FLATTENED_PDF

        return ContentType.SCANNED_PDF

    @property
    def document_info(self) -> dict:
        return {
            "file_type": self.file_type.value,
            "content_type": self.content_type.value,
            "has_form_fields": self.has_form_fields,
            "page_count": len(self.pdf_reader.pages),
        }

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

    def read_content(self) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")


class FlattenedPDFParser(ParserFactory):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.reader = PdfReader(file_path)

        with open("template_14434_03.json", encoding="utf-8") as f:
            self.template_cerfa = json.load(f)

        with open("template_cerfa_detection.json", encoding="utf-8") as f:
            self.template_cerfa_detection = json.load(f)

    def read_content(self) -> dict:
        """
        Read the content of the first page of the PDF.

        TO DO :
         - présence de plusieurs cerfa dans un document en entré
         - Aucun cerfa détecté

        Returns:
            dict: A dictionary containing the parsed content of the PDF.
        """

        results = {"DT": {}, "DICT": {}, "GLOBAL": {}}

        with pdfplumber.open(self.file_path) as pdf_file:
            for page in pdf_file.pages:
                if not (abs(page.width - 595) < 2 and abs(page.height - 842) < 2):
                    raise NotImplementedError(
                        "Page dimensions are not A4 / rezise need ?"
                    )

                if self._is_dt_dict_cerfa(page):
                    results = self.extract_cerfa_data(page, results)

        return results

    def _is_dt_dict_cerfa(self, page: pdfplumber_page) -> bool:
        """
        Check if the page matches the DT_DICT cerfa template.

        TO DO : Verification is currently limited to Cerfa form 14434*03
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

    def extract_cerfa_data(self, page: pdfplumber_page, results: dict) -> dict:
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


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝

if __name__ == "__main__":
    input_file_path = Path("/home/bn/Documents/maquette/Travaux-Prevelles-09-2026.pdf")
    document_inspector = DocumentInspector(input_file_path)
    print(document_inspector.document_info)

    toto = FlattenedPDFParser(input_file_path)
    content = toto.read_content()

    breakpoint()
