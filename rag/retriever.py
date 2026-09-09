"""Knowledge retrieval with optional ChromaDB and a zero-service local fallback."""
from __future__ import annotations
import json
from pathlib import Path
DEFAULT_CORPUS=Path(__file__).resolve().parent.parent/"knowledge"/"icar_chunks.json"
class KnowledgeRetriever:
    def __init__(self,persist_directory="rag/chroma",corpus_path=None):
        self.persist_directory=persist_directory; self.corpus_path=Path(corpus_path) if corpus_path else DEFAULT_CORPUS; self.collection=None
        try:
            import chromadb; self.client=chromadb.PersistentClient(path=persist_directory); self.collection=self.client.get_or_create_collection("agrimind_knowledge")
        except ImportError: self.client=None
    def add_documents(self,documents,ids,metadatas=None):
        metadatas=metadatas or [{} for _ in documents]
        if self.collection is not None: self.collection.upsert(documents=documents,ids=ids,metadatas=metadatas); return
        existing=[]
        if self.corpus_path.exists():
            try: existing=json.loads(self.corpus_path.read_text(encoding="utf-8"))
            except Exception: existing=[]
        by_id={x["id"]:x for x in existing}
        for doc_id,doc,meta in zip(ids,documents,metadatas): by_id[doc_id]={"id":doc_id,"text":doc,"metadata":meta or {}}
        self.corpus_path.parent.mkdir(parents=True,exist_ok=True); self.corpus_path.write_text(json.dumps(list(by_id.values()),ensure_ascii=False),encoding="utf-8")
    def search(self,query,n_results=4,where=None):
        if self.collection is not None:
            kwargs={"query_texts":[query],"n_results":n_results};
            if where: kwargs["where"]=where
            result=self.collection.query(**kwargs); docs=result.get("documents",[[]])[0]; metas=result.get("metadatas",[[]])[0]; ids=result.get("ids",[[]])[0]
            return [{"id":i,"text":d,"metadata":m or {}} for i,d,m in zip(ids,docs,metas)]
        if not self.corpus_path.exists(): return []
        corpus=json.loads(self.corpus_path.read_text(encoding="utf-8"))
        if where: corpus=[x for x in corpus if all(x.get("metadata",{}).get(k)==v for k,v in where.items())]
        if not corpus: return []
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            texts=[x["text"] for x in corpus]; vec=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=30000); mat=vec.fit_transform(texts); q=vec.transform([query]); scores=(mat@q.T).toarray().ravel(); order=np.argsort(-scores)[:n_results]
            return [dict(corpus[i],score=float(scores[i])) for i in order if scores[i]>0]
        except Exception:
            terms=set(query.lower().split()); scored=[]
            for x in corpus: scored.append((len(terms&set(x["text"].lower().split())),x))
            scored.sort(key=lambda z:-z[0]); return [x for score,x in scored[:n_results] if score]
