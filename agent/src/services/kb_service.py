"""
Knowledge Base Service
Handles all KB lookups and data retrieval logic.
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import boto3
import os

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
    
    def __init__(self, table_name: str, region: str):
        self.dynamo = boto3.resource(
            "dynamodb",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table = self.dynamo.Table(table_name)
        
    def search(self, business_id: str, query: str, max_results: int = 3) -> KBResult:
        """
        Search the knowledge base for relevant information.
        """
        try:
            # Query DynamoDB
            resp = self.table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": f"BUSINESS#{business_id}",
                    ":sk": "ENTRY#"
                }
            )
            
            items = resp.get("Items", [])
            if not items:
                logger.warning(f"No KB entries found for business: {business_id}")
                return KBResult(hit=False, matches=[])
            
            matches = self._rank_results(query, items)
            
            top_matches = matches[:max_results]
            
            result = KBResult(
                hit=len(top_matches) > 0,
                matches=top_matches
            )
            
            return result
            
        except Exception as e:
            logger.error(f"KB search error: {e}", exc_info=True)
            return KBResult(hit=False, matches=[], error=str(e))
    
    def _rank_results(self, query: str, items: List[Dict]) -> List[KBMatch]:
        
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
    