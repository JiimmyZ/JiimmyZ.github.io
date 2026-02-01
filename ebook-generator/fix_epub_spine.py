"""Post-process EPUB to fix spine order - move cover page to first position."""

import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def fix_epub_spine(epub_path: Path, output_path: Path = None):
    """Fix EPUB spine order to put cover page first."""
    if output_path is None:
        output_path = epub_path

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract EPUB
        with zipfile.ZipFile(epub_path, "r") as zip_ref:
            zip_ref.extractall(temp_path)

        # Find and modify content.opf
        opf_path = temp_path / "EPUB" / "content.opf"
        if not opf_path.exists():
            print(f"Error: content.opf not found in {epub_path}")
            return False

        # Parse OPF
        tree = ET.parse(opf_path)
        root = tree.getroot()

        # Find spine element - handle both with and without namespace
        namespaces = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        # Try to find spine with namespace first
        spine = root.find(".//{http://www.idpf.org/2007/opf}spine")
        if spine is None:
            spine = root.find(".//opf:spine", namespaces)
        if spine is None:
            print("Error: spine element not found")
            return False

        # Find all itemref elements (they may not have namespace prefix)
        itemrefs = []
        # Try without namespace first (most common)
        for elem in spine:
            if elem.tag.endswith("itemref") or elem.tag == "itemref":
                itemrefs.append(elem)

        if not itemrefs:
            # Try with namespace
            itemrefs = list(spine.findall("{http://www.idpf.org/2007/opf}itemref"))

        ch001_ref = None
        nav_ref = None
        other_refs = []

        for itemref in itemrefs:
            idref = itemref.get("idref")
            if idref == "ch001_xhtml":
                ch001_ref = itemref
            elif idref == "nav":
                nav_ref = itemref
            else:
                other_refs.append(itemref)

        # Reorder: ch001 first, then nav, then others
        if ch001_ref is not None:
            # Clear existing itemrefs
            for itemref in itemrefs:
                spine.remove(itemref)

            # Add in new order: cover first, then nav, then others
            spine.append(ch001_ref)
            if nav_ref is not None:
                spine.append(nav_ref)
            for ref in other_refs:
                spine.append(ref)

            # Save modified OPF
            tree.write(opf_path, encoding="utf-8", xml_declaration=True)
            print("[OK] Fixed spine order: cover page is now first")
        else:
            print("Warning: ch001_xhtml not found in spine")
            print(f"Found itemrefs: {[item.get('idref') for item in itemrefs]}")

        # Recreate EPUB
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
            # Add mimetype first (required by EPUB spec)
            mimetype_path = temp_path / "mimetype"
            if mimetype_path.exists():
                zip_out.write(
                    mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED
                )

            # Add all other files
            for file_path in temp_path.rglob("*"):
                if file_path.is_file() and file_path.name != "mimetype":
                    arcname = file_path.relative_to(temp_path)
                    zip_out.write(file_path, arcname)

        print(f"[OK] EPUB saved to: {output_path}")
        return True


if __name__ == "__main__":
    epub_path = Path("output/camino_pilgrim.epub")
    if epub_path.exists():
        fix_epub_spine(epub_path)
    else:
        print(f"Error: {epub_path} not found")
