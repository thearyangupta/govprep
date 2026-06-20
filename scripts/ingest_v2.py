import chromadb
from chromadb.utils import embedding_functions
from ingest_multi import load_pdf_with_pages, DOCUMENTS
from chunkers import recursive_chunk


from pathlib import Path


def ingest(
    chunk_size=1000,
    overlap=100,
    collection_name='govprep_v2',
    force=False,
):
    db_path = Path(__file__).resolve().parent.parent / 'db'
    client = chromadb.PersistentClient(path=str(db_path))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='all-MiniLM-L6-v2'
    )

    if force:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
    )

    if collection.count() == 0:
        ids, docs, metas = [], [], []

        for source, folder in DOCUMENTS.items():
            for pdf_path in sorted(folder.glob('*.pdf')):
                for page_num, page_text in load_pdf_with_pages(pdf_path):
                    for ci, chunk in enumerate(
                        recursive_chunk(
                            page_text,
                            chunk_size=chunk_size,
                            overlap=overlap,
                        )
                    ):
                        ids.append(f'{source}_{pdf_path.stem}_p{page_num}_c{ci}')
                        docs.append(chunk)
                        metas.append({'source': source, 'page': page_num, 'file': pdf_path.name})

        print(f'Adding {len(docs)} chunks from {len(DOCUMENTS)} sources...')
        collection.add(ids=ids, documents=docs, metadatas=metas)
        print(f'Stored {collection.count()} chunks')
    else:
        print(f'Already has {collection.count()} chunks')

    return collection.count()


if __name__ == '__main__':
    ingest(force=True)
