import os
import glob
import langchain_text_splitters
import langchain_huggingface
import langchain_chroma
import pathlib

class Representation:

    '''
    scenario:
        1: RecursiveCharacterTextSplitter
        2: MarkdownHeaderTextSplitter (## 層級)
        3: Sub-section-based (## 和 ### 層級)
    '''
    def __init__(self, scenario: int) -> None:
        self.scenario = scenario
        return

    def createEngine(self, parameter: dict) -> bool:
        self.engine = langchain_text_splitters.RecursiveCharacterTextSplitter(
            chunk_size=parameter['chunk'],
            chunk_overlap=parameter['overlap'],
        )
        self.parameter = parameter
        if self.scenario == 1:
            return (True)
        header = [("##", "section")]
        if self.scenario == 3:
            header.append(("###", "subsection"))
            pass
        self.markdown = langchain_text_splitters.MarkdownHeaderTextSplitter(
            headers_to_split_on=header,
            strip_headers=False,
        )
        return (True)

    def getSource(self, path: str) -> dict:
        name = os.path.basename(path)
        with open(path, encoding='utf-8') as paper:
            content = paper.read()
            pass
        item = {"source": name}
        if(self.scenario == 1):
            text = []
            meta = []
            book = self.engine.split_text(content)
            for piece in book:
                text.append(f"{name}: {piece}")
                meta.append(item)
                continue
            source = {"text": text, "meta": meta}
            return(source)
        condition = (self.scenario == 2 or self.scenario == 3)
        assert condition 
        text = []
        meta = []
        # block = self.markdown.split_text(content)
        scope = self.markdown.split_text(content)
        for block in scope:
            # pieces = self.engine.split_text(book.page_content)
            mark = {}
            mark.update(item)
            mark.update(block.metadata)
            book = self.engine.split_text(block.page_content)
            for piece in book:
                text.append(f"{name}: {piece}")
                meta.append(mark)
                continue
            _ = book
            continue
        _ = scope
        source = {"text": text, "meta": meta}
        return(source)

    def createData(self) -> bool:
        data = {
            'text': [],
            'meta': []
        }
        iteration = glob.glob('.data/source/device/md/*.md')
        for path in iteration:
            source = self.getSource(path)
            data['text'] += source['text']
            data['meta'] += source['meta']
            continue
        embedding = langchain_huggingface.HuggingFaceEmbeddings(
            model_name='BAAI/bge-m3'
        )
        folder = pathlib.Path(self.target[self.scenario])
        # if(self.scenario==1): 
        chunk = self.parameter.get("chunk")
        overlap = self.parameter.get("overlap")
        path = folder / f"chunk={chunk}-overlap={overlap}"
        langchain_chroma.Chroma.from_texts(
            texts=data['text'],
            embedding=embedding,
            metadatas=data['meta'],
            persist_directory=path,
        )
        return (True)

    target = {
        1: '.data/source/device/db1/',
        2: '.data/source/device/db2/',
        3: '.data/source/device/db3/',
    }
    pass