import sqlite3
import chromadb
import json
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class Memory:
    npc_name: str
    memory_type: str
    content: str
    timestamp: str
    participants: List[str]
    emotion: str
    location: Optional[tuple] = None
    importance: float = 0.5
    
    def to_dict(self):
        return asdict(self)

class MemoryManager:
    def __init__(self, db_path: str = "game_memories.db"):
        self.db_path = db_path
        self._init_sqlite()
        self._init_chromadb()
    
    def _init_sqlite(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc_name TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                participants TEXT NOT NULL,
                emotion TEXT,
                location TEXT,
                importance REAL DEFAULT 0.5,
                embedding_id TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc1 TEXT NOT NULL,
                npc2 TEXT NOT NULL,
                relationship_value REAL DEFAULT 0.5,
                last_interaction TEXT,
                interaction_count INTEGER DEFAULT 0,
                UNIQUE(npc1, npc2)
            )
        ''')
        
        self.conn.commit()
    
    def _init_chromadb(self):
        # ✅ Updated to new API
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Handle collection creation safely
        try:
            self.collection = self.chroma_client.get_collection("npc_memories")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name="npc_memories",
                metadata={"hnsw:space": "cosine"}
            )
    
    def store_memory(self, memory: Memory) -> int:
        participants_json = json.dumps(memory.participants)
        location_json = json.dumps(memory.location) if memory.location else None
        
        self.cursor.execute('''
            INSERT INTO memories 
            (npc_name, memory_type, content, timestamp, participants, emotion, location, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.npc_name,
            memory.memory_type,
            memory.content,
            memory.timestamp,
            participants_json,
            memory.emotion,
            location_json,
            memory.importance
        ))
        
        memory_id = self.cursor.lastrowid
        
        embedding_id = f"{memory.npc_name}_{memory_id}"
        self.collection.add(
            documents=[memory.content],
            metadatas=[{
                "npc_name": memory.npc_name,
                "memory_type": memory.memory_type,
                "timestamp": memory.timestamp,
                "emotion": memory.emotion,
                "importance": memory.importance
            }],
            ids=[embedding_id]
        )
        
        self.cursor.execute(
            "UPDATE memories SET embedding_id = ? WHERE id = ?",
            (embedding_id, memory_id)
        )
        
        self.conn.commit()
        return memory_id
    
    def get_recent_memories(self, npc_name: str, limit: int = 10) -> List[Dict]:
        self.cursor.execute('''
            SELECT * FROM memories
            WHERE npc_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (npc_name, limit))
        
        memories = []
        for row in self.cursor.fetchall():
            memory_dict = {
                "id": row[0],
                "npc_name": row[1],
                "memory_type": row[2],
                "content": row[3],
                "timestamp": row[4],
                "participants": json.loads(row[5]),
                "emotion": row[6],
                "location": json.loads(row[7]) if row[7] else None,
                "importance": row[8]
            }
            memories.append(memory_dict)
        
        return memories
    
    def search_memories(self, npc_name: str, query: str, limit: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"npc_name": npc_name}
        )
        
        if not results['ids'][0]:
            return []
        
        memory_ids = [int(id.split('_')[1]) for id in results['ids'][0]]
        
        placeholders = ','.join('?' * len(memory_ids))
        self.cursor.execute(f'''
            SELECT * FROM memories
            WHERE id IN ({placeholders})
        ''', memory_ids)
        
        memories = []
        for row in self.cursor.fetchall():
            memory_dict = {
                "id": row[0],
                "npc_name": row[1],
                "memory_type": row[2],
                "content": row[3],
                "timestamp": row[4],
                "participants": json.loads(row[5]),
                "emotion": row[6],
                "location": json.loads(row[7]) if row[7] else None,
                "importance": row[8]
            }
            memories.append(memory_dict)
        
        return memories
    
    def update_relationship(self, npc1: str, npc2: str, value_change: float):
        sorted_names = sorted([npc1, npc2])
        
        self.cursor.execute('''
            INSERT INTO relationships (npc1, npc2, relationship_value, last_interaction, interaction_count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(npc1, npc2) DO UPDATE SET
                relationship_value = MIN(1.0, MAX(0.0, relationship_value + ?)),
                last_interaction = ?,
                interaction_count = interaction_count + 1
        ''', (
            sorted_names[0],
            sorted_names[1],
            0.5 + value_change,
            datetime.datetime.now().isoformat(),
            value_change,
            datetime.datetime.now().isoformat()
        ))
        
        self.conn.commit()
    
    def get_relationship(self, npc1: str, npc2: str) -> float:
        sorted_names = sorted([npc1, npc2])
        
        self.cursor.execute('''
            SELECT relationship_value FROM relationships
            WHERE npc1 = ? AND npc2 = ?
        ''', (sorted_names[0], sorted_names[1]))
        
        result = self.cursor.fetchone()
        return result[0] if result else 0.5
    
    def get_all_relationships(self, npc_name: str) -> Dict[str, float]:
        self.cursor.execute('''
            SELECT npc1, npc2, relationship_value FROM relationships
            WHERE npc1 = ? OR npc2 = ?
        ''', (npc_name, npc_name))
        
        relationships = {}
        for row in self.cursor.fetchall():
            other_npc = row[1] if row[0] == npc_name else row[0]
            relationships[other_npc] = row[2]
        
        return relationships
    
    def summarize_memories(self, npc_name: str, time_window_hours: int = 24) -> str:
        cutoff_time = (datetime.datetime.now() - datetime.timedelta(hours=time_window_hours)).isoformat()
        
        self.cursor.execute('''
            SELECT memory_type, COUNT(*) as count FROM memories
            WHERE npc_name = ? AND timestamp > ?
            GROUP BY memory_type
        ''', (npc_name, cutoff_time))
        
        summary = []
        for row in self.cursor.fetchall():
            summary.append(f"{row[1]} {row[0]} memories")
        
        return ", ".join(summary) if summary else "No recent memories"
    
    def get_all_memories(self, limit: int = None) -> List[Dict]:
        """Get all memories from database, optionally limited"""
        query = 'SELECT * FROM memories ORDER BY timestamp DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        
        memories = []
        for row in self.cursor.fetchall():
            memory_data = {
                'id': row[0],
                'npc_name': row[1],
                'memory_type': row[2],
                'content': row[3],
                'timestamp': row[4],
                'participants': json.loads(row[5]) if row[5] else [],
                'emotion': row[6],
                'location': json.loads(row[7]) if row[7] else None,
                'importance': row[8]
            }
            memories.append(memory_data)
        
        return memories
    
    def close(self):
        self.conn.close()
