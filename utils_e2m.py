import tempfile

import nltk
from fastapi import HTTPException
from wisup_e2m import E2MParser
from wisup_e2m.configs.base import E2MParserConfig


# 文档处理效果还行，但引擎要预载
# 不手动处理，因为用这个框架后续方便叠加图片识别
class MultiE2MParser:
    def __init__(self):
        parser_config = {
            "doc_parser": {"engine": "pandoc"},
            "docx_parser": {"engine": "pandoc"},
            "ppt_parser": {"engine": "unstructured"},
            "pptx_parser": {"engine": "unstructured"},
        }
        nltk.download('punkt_tab')
        self.parser = E2MParser(E2MParserConfig(parsers=parser_config))

    def parse_file(self, file_path, dir_path):
        data = self.parser.parse(
            file_name=file_path,
            work_dir=dir_path,
            image_dir=dir_path
        )
        if data is None:
            raise HTTPException(status_code=500, detail=f"Empty file")
        return data.text


if __name__ == '__main__':
    multi_parser = MultiE2MParser()
    with tempfile.TemporaryDirectory() as temp_dir:
        result = multi_parser.parse_file('archive/ccc.pptx', temp_dir)
        print(result)
