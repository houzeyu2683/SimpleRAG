import json
import yaml
import dotenv
import gradio
import utility

# dotenv.load_dotenv()

with open("template/application.css") as file:
    CSS = file.read()


class Application:
    def __init__(self, scenario: str = "configuration/news.yaml"):
        with open(scenario) as file:
            self.configuration = yaml.safe_load(file)

        self.retriever = utility.getRetriever(self.configuration)
        if self.configuration.get("reranking", False):
            self.retriever = utility.getReranker(self.retriever, self.configuration)
        self.chain = utility.getChain(self.retriever, self.configuration)
        self.examples = self._loadExamples()
        self.demo = self._buildUI()

    def _loadExamples(self) -> list:
        test_path = self.configuration.get("qa_test_path", "")
        if not test_path:
            return []
        with open(test_path, encoding="utf-8") as file:
            return [[pair["question"], pair["ground_truth"]] for pair in json.load(file)]

    def _getAnswer(self, question: str) -> tuple[str, str]:
        if not question.strip():
            return ("", "")
        response = self.chain.invoke(question)
        documents = self.retriever.invoke(question)
        sources = "\n".join(
            f"- [{document.metadata.get('title', '?')}]({document.metadata.get('url', '')})"
            for document in documents
        )
        return (response, sources)

    def _buildUI(self) -> gradio.Blocks:
        with gradio.Blocks(title="SPfRAG", css=CSS, theme=gradio.themes.Soft()) as demo:
            gradio.HTML(f"""
                <div class="header">
                    <h1>SPfRAG</h1>
                    <p>{self.configuration['domain'].capitalize()} 知識問答系統</p>
                </div>
            """)

            with gradio.Row():
                inquiry = gradio.Textbox(
                    label="問題",
                    placeholder="輸入你的問題，或從下方測試題目選擇...",
                    lines=2,
                    scale=5,
                )
                button = gradio.Button("送出", variant="primary", scale=1, elem_classes="send-btn")

            with gradio.Row():
                output = gradio.Textbox(label="RAG 回答", lines=6, scale=1, elem_classes="answer-box")
                truth = gradio.Textbox(label="標準答案", lines=6, scale=1, interactive=False, elem_classes="truth-box")

            panel = gradio.Markdown(label="來源")

            if self.examples:
                gradio.Examples(
                    examples=self.examples,
                    inputs=[inquiry, truth],
                    label="測試題目",
                )

            button.click(fn=self._getAnswer, inputs=inquiry, outputs=[output, panel])
            inquiry.submit(fn=self._getAnswer, inputs=inquiry, outputs=[output, panel])

        return demo

    def launch(self):
        self.demo.launch()


if __name__ == "__main__":
    Application('./configuration/news.yaml').launch()
