import asyncio
import os

from fastapi import HTTPException
from loguru import logger
from zerox import zerox


# 效果不错，但要手动合并分页
class PdfZeroxParser:
    def __init__(self):
        os.environ["OPENAI_API_BASE"] = "https://api.gptsapi.net/v1"
        os.environ["OPENAI_API_KEY"] = "sk-yOs320a80baaadba32e81a730eb845c40fac4023547dgl35"
        self.thread = 32

    async def parse_file(self, file_path):
        logger.info(f"Parsing file {file_path}")
        data = await zerox(file_path=file_path, concurrency=self.thread)
        if data is None:
            raise HTTPException(status_code=500, detail=f"Empty file")
        return ''.join(page.content for page in data.pages)


if __name__ == '__main__':
    pdf_parser = PdfZeroxParser()
    result = asyncio.run(pdf_parser.parse_file('archive/aabbcc.pdf'))
    print(result)
