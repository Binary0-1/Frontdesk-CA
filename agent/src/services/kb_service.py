import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from .db import get_db

logger = logging.getLogger("kb_service")


@dataclass
class KBMatch:
    question: str
    answer: str
    score: float
    category: Optional[str] = None


@dataclass
class KBResult:
    hit: bool
    matches: List[KBMatch]
    error: Optional[str] = None


class KnowledgeBaseService:
    
    def __init__(self):
        pass

    def search(self, business_id: int, query: str, max_results: int = 3) -> KBResult:
        logger.info(f"KB search called for business '{business_id}' with query: '{query}'")

        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()

            ## get the json data stored in KB table 
            cur.execute(
                """
                SELECT title, content 
                FROM kb_article 
                WHERE business_id = %s
                """,
                (business_id,)
            )
            rows = cur.fetchall()

            
            if not rows:
                logger.warning(f"No KB entries found for business: {business_id}")
                return KBResult(hit=False, matches=[])

            # Normalize structure for ranking
            ## Approach for dev env as data size is limited just for proof of concept 
            processed_items = []
            for row in rows:
                title = row["title"]
                content = row["content"]

                # Extract question answer from JSON content
                question_from_content = content.get("question", title or "")
                answer_from_content = content.get("answer", "")
                category = content.get("category")

                if answer_from_content: 
                    processed_items.append({
                        "question": question_from_content,
                        "answer": answer_from_content,
                        "category": category,
                    })
            # basic ranking 
            matches = self._rank_results(query, processed_items)

            return KBResult(
                hit=len(matches) > 0,
                matches=matches[:max_results]
            )

        except Exception as e:
            logger.error(f"KB search error: {e}", exc_info=True)
            return KBResult(hit=False, matches=[], error=str(e))

        finally:
            if conn:
                conn.close()

    # ----------------- Ranking Logic -----------------

    def _rank_results(self, query: str, items: List[Dict]) -> List[KBMatch]:
        logger.info("Ranking results...")

        query_lower = query.lower()
        query_words = set(self._tokenize(query_lower))

        matches = []

        for item in items:
            kb_question = item["question"].lower()
            kb_answer = item["answer"]
            category = item.get("category")

            score = self._calculate_score(query_lower, query_words, kb_question)

            if score > 0:
                matches.append(KBMatch(
                    question=item["question"],
                    answer=kb_answer,
                    score=score,
                    category=category
                ))

        matches.sort(key=lambda x: x.score, reverse=True)
        logger.info(f"matches: {matches}")
        return matches

    def _calculate_score(self, query: str, query_words: set, kb_question: str) -> float:
        if query == kb_question:
            return 1.0

        if kb_question in query or query in kb_question:
            return 0.8

        kb_words = set(self._tokenize(kb_question))
        if not kb_words:
            return 0.0

        common_words = query_words & kb_words
        if len(common_words) < 1:
            return 0.0

        jaccard = len(common_words) / len(query_words | kb_words)
        return min(jaccard, 0.7)

    def _tokenize(self, text: str) -> List[str]:
        stop_words = {
            'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
            'what', 'when', 'where', 'who', 'how', 'do', 'does', 'can',
            'could', 'would', 'should', 'your', 'my', 'our', 'their'
        }

        return [w for w in text.split() if w not in stop_words and len(w) > 2]
