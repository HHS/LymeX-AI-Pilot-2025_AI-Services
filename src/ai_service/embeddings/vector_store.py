"""
Minimal pgvector upsert wrapper (will need to adapt to out custom schema).
"""
import psycopg_pool

class PgVectorStore:
    def __init__(self, dsn: str):
        self.pool = psycopg_pool.ConnectionPool(dsn)

    def upsert(self, doc_id: str, page_no: int, vector: list[float]):
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO page_vectors (doc_id, page_no, embedding)
                VALUES (%s,%s,%s)
                ON CONFLICT (doc_id,page_no)
                DO UPDATE SET embedding = EXCLUDED.embedding;
                """,
                (doc_id, page_no, vector),
            )
