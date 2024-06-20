import os
from lionagi.os.lib.sys_util import check_import


class DocumentParser:

    def __init__(self, filepath):
        check_import(package_name="unstructured", pip_name="unstructured[all-docs]")

        self.filepath = filepath
        self.file_extension = os.path.splitext(filepath)[1].lower()
        self.elements = []
        self.parsers = {
            ".pdf": self._partition_pdf,
            ".txt": self._partition_text,
            ".md": self._partition_text,
            ".rst": self._partition_text,
            ".docx": self._partition_docx,
            ".html": self._partition_html,
            ".eml": self._partition_email,
            ".jpeg": self._partition_image,
            ".jpg": self._partition_image,
            ".png": self._partition_image,
            ".tiff": self._partition_image,
            ".bmp": self._partition_image,
            ".heic": self._partition_image,
            ".csv": self._partition_csv,
        }

    def parse(self, **kwargs):
        parser_method = self.parsers.get(self.file_extension, self._partition_auto)
        parser_method(**kwargs)

    def _partition_pdf(self, **kwargs):
        from unstructured.partition.pdf import partition_pdf

        kwargs["infer_table_structure"] = kwargs.get("infer_table_structure", True)
        kwargs["strategy"] = kwargs.get("strategy", "hi_res")
        self.elements = partition_pdf(filename=self.filepath, **kwargs)

    def _partition_text(self, **kwargs):
        from unstructured.partition.text import partition_text

        self.elements = partition_text(filename=self.filepath, **kwargs)

    def _partition_docx(self, **kwargs):
        from unstructured.partition.docx import partition_docx

        self.elements = partition_docx(filename=self.filepath, **kwargs)

    def _partition_html(self, **kwargs):
        from unstructured.partition.html import partition_html

        self.elements = partition_html(filename=self.filepath, **kwargs)

    def _partition_email(self, **kwargs):
        from unstructured.partition.email import partition_email

        self.elements = partition_email(filename=self.filepath, **kwargs)

    def _partition_image(self, **kwargs):
        from unstructured.partition.image import partition_image

        self.elements = partition_image(filename=self.filepath, **kwargs)

    def _partition_csv(self, **kwargs):
        from unstructured.partition.csv import partition_csv

        self.elements = partition_csv(filename=self.filepath, **kwargs)

    def _partition_auto(self, **kwargs):
        from unstructured.partition.auto import partition

        self.elements = partition(filename=self.filepath, **kwargs)

    def convert_to_markdown(self):
        markdown_content = ""
        for el in self.elements:
            if el.category == "Table":
                markdown_content += el.metadata.text_as_html + "\n\n"
            else:
                markdown_content += el.text + "\n\n"
        return markdown_content

    def save_as_markdown(self, output_path):
        markdown_content = self.convert_to_markdown()
        with open(output_path, "w") as md_file:
            md_file.write(markdown_content)


# Example usage
if __name__ == "__main__":
    parser = DocumentParser("path/to/your/document.pdf")
    parser.parse()
    parser.save_as_markdown("output/path/document.md")
