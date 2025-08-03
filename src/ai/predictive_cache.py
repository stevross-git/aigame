import hashlib
import time
import threading
import json
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# Import moved to avoid circular import - will use Any for type hints

@dataclass
class CacheEntry:
    """A cached AI response with metadata"""
    response: Any  # Will be AIResponse object
    context_hash: str
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    confidence: float = 1.0  # How confident we are this response is still valid

@dataclass
class PredictiveContext:
    """Context variations we might encounter soon"""
    base_context: Dict
    variations: List[Dict]  # Likely context changes
    probability: float  # How likely this context is

class PredictiveAICache:
    """
    Smart caching system that predicts future AI interactions and pre-computes responses.
    Reduces API calls and eliminates response delays.
    """
    
    def __init__(self, ai_client, max_cache_size: int = 1000, cache_ttl: int = 3600):
        self.ai_client = ai_client
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl  # Time to live in seconds
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        self.npc_context_history: Dict[str, List[Dict]] = defaultdict(list)
        self.prediction_queue: List[Tuple[str, Dict, Dict]] = []  # (npc_id, npc_data, context)
        
        # Threading for background processing
        self.background_thread = None
        self.should_stop = False
        self.cache_lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'predictions_made': 0,
            'invalidations': 0,
            'background_requests': 0
        }
        
        self.logger = logging.getLogger(__name__)
        self.start_background_processing()
    
    def start_background_processing(self):
        """Start background thread for predictive caching"""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.background_thread = threading.Thread(
                target=self._background_processor,
                daemon=True
            )
            self.background_thread.start()
    
    def _background_processor(self):
        """Background thread that processes prediction queue"""
        while not self.should_stop:
            try:
                # Process prediction queue
                if self.prediction_queue:
                    with self.cache_lock:
                        if self.prediction_queue:
                            npc_id, npc_data, context = self.prediction_queue.pop(0)
                    
                    # Generate predictions for this NPC
                    self._generate_predictions(npc_id, npc_data, context)
                
                # Clean expired cache entries
                self._cleanup_expired_cache()
                
                # Sleep before next iteration
                time.sleep(2.0)  # Process every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Background processing error: {e}")
                time.sleep(5.0)
    
    def get_cached_response(self, npc_data: Dict, context: Dict) -> Optional[Any]:
        """Get cached response if available and still valid"""
        cache_key = self._generate_cache_key(npc_data, context)
        
        with self.cache_lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Check if cache entry is still valid
                if self._is_cache_valid(entry, context):
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    self.stats['cache_hits'] += 1
                    
                    self.logger.debug(f"Cache hit for {npc_data.get('name', 'unknown')}")
                    return entry.response
                else:
                    # Remove invalid entry
                    del self.cache[cache_key]
                    self.stats['invalidations'] += 1
        
        self.stats['cache_misses'] += 1
        return None
    
    def cache_response(self, npc_data: Dict, context: Dict, response: Any):
        """Cache an AI response"""
        cache_key = self._generate_cache_key(npc_data, context)
        context_hash = self._generate_context_hash(context)
        
        entry = CacheEntry(
            response=response,
            context_hash=context_hash,
            timestamp=time.time(),
            last_accessed=time.time()
        )
        
        with self.cache_lock:
            self.cache[cache_key] = entry
            
            # Update context history for this NPC
            npc_id = npc_data.get('name', 'unknown')
            self.npc_context_history[npc_id].append(context.copy())
            
            # Keep only recent history
            if len(self.npc_context_history[npc_id]) > 10:
                self.npc_context_history[npc_id] = self.npc_context_history[npc_id][-10:]
            
            # Trigger predictive caching
            self._queue_prediction(npc_id, npc_data, context)
            
            # Cleanup if cache is too large
            if len(self.cache) > self.max_cache_size:
                self._cleanup_oldest_entries()
    
    def _queue_prediction(self, npc_id: str, npc_data: Dict, context: Dict):
        """Queue predictive caching for this NPC"""
        # Add to prediction queue if not already there
        prediction_item = (npc_id, npc_data.copy(), context.copy())
        if prediction_item not in self.prediction_queue:
            self.prediction_queue.append(prediction_item)
    
    def _generate_predictions(self, npc_id: str, npc_data: Dict, base_context: Dict):
        """Generate predicted contexts and pre-cache responses"""
        try:
            predicted_contexts = self._predict_future_contexts(npc_id, base_context)
            
            for predicted_context in predicted_contexts:
                # Check if we already have this cached
                cache_key = self._generate_cache_key(npc_data, predicted_context)
                
                with self.cache_lock:
                    if cache_key not in self.cache:
                        # Generate response in background
                        self._generate_background_response(npc_data, predicted_context)
                        
        except Exception as e:
            self.logger.error(f"Prediction generation error for {npc_id}: {e}")
    
    def _predict_future_contexts(self, npc_id: str, base_context: Dict) -> List[Dict]:
        """Predict likely future contexts for an NPC"""
        predictions = []
        
        # Get recent context history
        history = self.npc_context_history.get(npc_id, [])
        
        # Predict context variations based on common patterns
        
        # 1. Predict need changes (hunger, sleep, etc. will decrease)
        needs_context = base_context.copy()
        if 'npc_needs' in needs_context:
            predicted_needs = needs_context['npc_needs'].copy()
            for need, value in predicted_needs.items():
                # Predict needs will decrease over time
                predicted_needs[need] = max(0.0, value - 0.2)
            needs_context['npc_needs'] = predicted_needs
            predictions.append(needs_context)
        
        # 2. Predict time progression
        time_contexts = []
        current_hour = base_context.get('current_hour', 12)
        for hour_delta in [1, 2, 3]:  # Predict 1-3 hours ahead
            time_context = base_context.copy()
            time_context['current_hour'] = (current_hour + hour_delta) % 24
            time_context['situation'] = self._predict_situation_for_time(current_hour + hour_delta)
            time_contexts.append(time_context)
        predictions.extend(time_contexts)
        
        # 3. Predict social interactions
        if 'nearby_npcs' in base_context:
            # Predict with different nearby NPCs
            for i in range(3):  # Generate a few social scenarios
                social_context = base_context.copy()
                social_context['situation'] = 'talking with another NPC'
                social_context['social_interaction'] = True
                predictions.append(social_context)
        
        # 4. Predict player interaction scenarios
        player_contexts = []
        player_messages = [
            "Hello, how are you?",
            "What are you doing?", 
            "Can you help me?",
            "Nice weather today!",
            "How's your day going?"
        ]
        
        for message in player_messages:
            player_context = base_context.copy()
            player_context['situation'] = 'chatting with player'
            player_context['player_message'] = message
            player_context['chat_history'] = []
            player_contexts.append(player_context)
        predictions.extend(player_contexts)
        
        # 5. Predict based on historical patterns
        if len(history) >= 3:
            # Look for patterns in recent contexts
            pattern_context = self._extrapolate_from_history(history, base_context)
            if pattern_context:
                predictions.append(pattern_context)
        
        # Limit predictions to avoid overwhelming the system
        return predictions[:8]  # Maximum 8 predictions per NPC
    
    def _predict_situation_for_time(self, hour: int) -> str:
        """Predict what an NPC might be doing at a specific hour"""
        if 6 <= hour < 9:
            return "having breakfast"
        elif 9 <= hour < 12:
            return "working in the morning"
        elif 12 <= hour < 14:
            return "having lunch"
        elif 14 <= hour < 17:
            return "working in the afternoon"
        elif 17 <= hour < 19:
            return "having dinner"
        elif 19 <= hour < 22:
            return "relaxing in the evening"
        else:
            return "sleeping or resting"
    
    def _extrapolate_from_history(self, history: List[Dict], base_context: Dict) -> Optional[Dict]:
        """Extrapolate future context from historical patterns"""
        try:
            # Simple pattern: if emotion has been changing, predict next emotion
            emotions = [ctx.get('emotion', 'neutral') for ctx in history[-3:]]
            if len(set(emotions)) > 1:  # Emotion is changing
                # Predict continuation of emotional pattern
                pattern_context = base_context.copy()
                if emotions[-1] == 'happy' and emotions[-2] != 'happy':
                    pattern_context['emotion'] = 'excited'
                elif emotions[-1] == 'sad':
                    pattern_context['emotion'] = 'neutral'  # Recovery
                return pattern_context
        except:
            pass
        return None
    
    def _generate_background_response(self, npc_data: Dict, context: Dict):
        """Generate AI response in background and cache it"""
        def callback(response: Any):
            if response:
                self.cache_response(npc_data, context, response)
                self.stats['background_requests'] += 1
                self.stats['predictions_made'] += 1
        
        # Use async AI client to generate response
        if hasattr(self.ai_client, 'make_decision_async'):
            self.ai_client.make_decision_async(npc_data, context, callback)
        else:
            # Fallback: generate synchronously in thread
            try:
                response = self.ai_client.make_decision(npc_data, context)
                callback(response)
            except Exception as e:
                self.logger.error(f"Background response generation failed: {e}")
    
    def invalidate_npc_cache(self, npc_id: str, context_changes: Dict):
        """Invalidate cache entries for an NPC when context significantly changes"""
        with self.cache_lock:
            keys_to_remove = []
            
            for cache_key, entry in self.cache.items():
                if npc_id in cache_key:
                    # Check if this cache entry is affected by the context changes
                    if self._should_invalidate(entry, context_changes):
                        keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self.cache[key]
                self.stats['invalidations'] += 1
            
            if keys_to_remove:
                self.logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for {npc_id}")
    
    def _should_invalidate(self, entry: CacheEntry, context_changes: Dict) -> bool:
        """Determine if a cache entry should be invalidated based on context changes"""
        # Invalidate if major context elements have changed
        major_changes = [
            'emotion', 'needs', 'relationships', 'current_hour', 
            'situation', 'nearby_npcs', 'active_events'
        ]
        
        for change_key in context_changes.keys():
            if change_key in major_changes:
                return True
        
        # Check confidence level
        if entry.confidence < 0.5:
            return True
        
        return False
    
    def _is_cache_valid(self, entry: CacheEntry, current_context: Dict) -> bool:
        """Check if a cached entry is still valid for the current context"""
        # Check age
        if time.time() - entry.timestamp > self.cache_ttl:
            return False
        
        # Check context similarity
        current_hash = self._generate_context_hash(current_context)
        if entry.context_hash != current_hash:
            # Allow some flexibility for minor context changes
            similarity = self._calculate_context_similarity(entry, current_context)
            if similarity < 0.7:  # Less than 70% similar
                return False
        
        return True
    
    def _calculate_context_similarity(self, entry: CacheEntry, current_context: Dict) -> float:
        """Calculate similarity between cached context and current context"""
        # Simple similarity based on key overlap
        # This could be made more sophisticated
        try:
            cached_keys = set(str(entry.context_hash))  # Simplified
            current_keys = set(str(self._generate_context_hash(current_context)))
            
            if not cached_keys and not current_keys:
                return 1.0
            
            intersection = len(cached_keys & current_keys)
            union = len(cached_keys | current_keys)
            
            return intersection / union if union > 0 else 0.0
        except:
            return 0.5  # Default moderate similarity
    
    def _generate_cache_key(self, npc_data: Dict, context: Dict) -> str:
        """Generate a unique cache key for NPC data and context"""
        # Create a stable key based on important NPC and context elements
        key_data = {
            'npc_name': npc_data.get('name', ''),
            'personality': str(sorted(npc_data.get('personality', {}).items())),
            'situation': context.get('situation', ''),
            'emotion': context.get('emotion', ''),
            'player_message': context.get('player_message', ''),
            'current_hour': context.get('current_hour', 0),
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_context_hash(self, context: Dict) -> str:
        """Generate hash for context to detect changes"""
        # Hash relevant context elements
        context_string = json.dumps({
            k: v for k, v in context.items() 
            if k in ['situation', 'emotion', 'player_message', 'current_hour', 'nearby_npcs']
        }, sort_keys=True)
        return hashlib.md5(context_string.encode()).hexdigest()
    
    def _cleanup_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        
        with self.cache_lock:
            keys_to_remove = []
            
            for cache_key, entry in self.cache.items():
                if current_time - entry.timestamp > self.cache_ttl:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self.cache[key]
    
    def _cleanup_oldest_entries(self):
        """Remove oldest cache entries when cache is full"""
        with self.cache_lock:
            if len(self.cache) <= self.max_cache_size:
                return
            
            # Sort by last accessed time and remove oldest
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            entries_to_remove = len(self.cache) - self.max_cache_size + 10  # Remove extra to avoid frequent cleanup
            
            for i in range(entries_to_remove):
                if i < len(sorted_entries):
                    key_to_remove = sorted_entries[i][0]
                    del self.cache[key_to_remove]
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        with self.cache_lock:
            hit_rate = (
                self.stats['cache_hits'] / 
                (self.stats['cache_hits'] + self.stats['cache_misses'])
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 
                else 0.0
            )
            
            return {
                **self.stats,
                'cache_size': len(self.cache),
                'hit_rate': hit_rate,
                'prediction_queue_size': len(self.prediction_queue)
            }
    
    def shutdown(self):
        """Shutdown the cache system"""
        self.should_stop = True
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5.0)