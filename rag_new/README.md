# RAG Tutorial - Dunder Mifflin Edition

A hands-on tutorial for building a Retrieval-Augmented Generation (RAG) pipeline using OpenAI and LangChain.

## What's inside

| File | Description |
|------|-------------|
| `rag_tutorial_exercise.ipynb` | The exercise notebook with 8 TODO tasks to complete |
| `rag_tutorial_solutions.ipynb` | The complete solution notebook |
| `data/dunder_mifflin_docs.json` | Synthetic internal documents for the knowledge base |

## How to use

1. Open `rag_tutorial_exercise.ipynb` in Google Colab
2. Set your OpenAI API key (via Colab Secrets or directly in the notebook)
3. Run the cells from top to bottom
4. Complete the 8 TODO tasks
5. Compare your work with `rag_tutorial_solutions.ipynb`

## Requirements

- OpenAI API key
- Libraries (installed automatically in the notebook):
  - `langchain`, `langchain-openai`, `langchain-community`
  - `chromadb`
  - `openai`, `tiktoken`

All libraries are installed via `pip` in the first code cell.

## What you'll learn

- How documents are chunked into smaller pieces
- How embeddings turn text into searchable vectors
- How ChromaDB stores and retrieves similar documents
- How a RAG prompt is constructed for an LLM
- Why RAG beats a model without access to documents
