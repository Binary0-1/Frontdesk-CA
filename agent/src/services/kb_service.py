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
        pass # DB session will be passed per request or managed by a context manager

    def search(self, business_id: int, query: str, max_results: int = 3) -> KBResult:
        logger.info(f"KB search called for business '{business_id}' with query: '{query}'")
        
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()

            # Using a raw SQL query for simplicity, but can be replaced with SQLAlchemy ORM
            # This query fetches all KB articles for the given business_id
            cur.execute(
                "SELECT title, content FROM kb_article WHERE business_id = %s",
                (business_id,)
            )
            items = cur.fetchall()
            
            if not items:
                logger.warning(f"No KB entries found for business: {business_id}")
                return KBResult(hit=False, matches=[])
            
            # Convert content from JSONB to dict and extract question/answer for ranking
            processed_items = []
            for item in items:
                title = item['title']
                content = item['content'] # This is already a dict from RealDictCursor
                
                # Assuming 'question' and 'answer' keys exist within the JSONB content
                question_from_content = content.get('question', title if title else '')
                answer_from_content = content.get('answer', '')
                
                if question_from_content and answer_from_content:
                    processed_items.append({
                        "question": question_from_content,
                        "answer": answer_from_content,
                        "category": content.get('category'), # Assuming category might be in content
                        "original_title": title # Keep original title if needed
                    })
            
            matches = self._rank_results(query, processed_items)
            
            top_matches = matches[:max_results]
            
            result = KBResult(
                hit=len(top_matches) > 0,
                matches=top_matches
            )
            
            return result
            
        except Exception as e:
            logger.error(f"KB search error: {e}", exc_info=True)
            return KBResult(hit=False, matches=[], error=str(e))
        finally:
            if conn:
                conn.close()
    
    def _rank_results(self, query: str, items: List[Dict]) -> List[KBMatch]:

        logger.info(f"Ranking results........")
        
        query_lower = query.lower()
        query_words = set(self._tokenize(query_lower))
        
        matches = []
        
        for item in items:
            kb_question = item.get("question", "").lower()
            kb_answer = item.get("answer", "")
            category = item.get("category")
            
            score = self._calculate_score(query_lower, query_words, kb_question)
            
            if score > 0:
                matches.append(KBMatch(
                    question=item.get("question", ""),
                    answer=kb_answer,
                    score=score,
                    category=category
                ))
        
        matches.sort(key=lambda x: x.score, reverse=True)

        logger.info(f"matches :  {matches}")
        
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
        
        if len(common_words) < 2:
            return 0.0
        
        union_words = query_words | kb_words
        jaccard = len(common_words) / len(union_words)
        
        avg_common_word_length = sum(len(w) for w in common_words) / len(common_words)
        length_boost = min(avg_common_word_length / 10, 0.2)
        
        return min(jaccard + length_boost, 0.7)
    
    def _tokenize(self, text: str) -> List[str]:
        stop_words = {
            'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
            'what', 'when', 'where', 'who', 'how', 'do', 'does', 'can', 'could',
            'would', 'should', 'your', 'my', 'our', 'their'
        }
        
        words = text.split()
        return [w for w in words if w not in stop_words and len(w) > 2]
