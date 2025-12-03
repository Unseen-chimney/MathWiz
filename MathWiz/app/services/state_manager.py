"""
State Manager - Handles conversation state and persistence
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uuid
import os

from app.models.database import (
    Base, User, Conversation, Message, TaskLog, 
    SolutionRecord, ReflectionLog, LLMCall
)


class StateManager:
    """Manages conversation state and database persistence"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize state manager with database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "sqlite:///./mathwiz.db"
        )
        
        # Create engine and session
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # In-memory state cache for current session
        self.current_user_id = None
        self.current_convo_id = None
        self.conversation_context = []
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_or_get_user(self, user_id: str, name: str = None, email: str = None) -> User:
        """
        Create a new user or get existing one.
        
        Args:
            user_id: Unique user identifier
            name: User name (optional)
            email: User email (optional)
            
        Returns:
            User object
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                user = User(
                    user_id=user_id,
                    name=name or f"User {user_id[:8]}",
                    email=email,
                    created_at=datetime.utcnow()
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            
            self.current_user_id = user_id
            return user
        finally:
            session.close()
    
    def start_conversation(self, user_id: str, convo_id: str = None) -> Conversation:
        """
        Start a new conversation or get existing one.
        
        Args:
            user_id: User identifier
            convo_id: Optional conversation ID
            
        Returns:
            Conversation object
        """
        session = self.get_session()
        try:
            if convo_id:
                conversation = session.query(Conversation).filter(
                    Conversation.convo_id == convo_id
                ).first()
                
                if conversation:
                    self.current_convo_id = convo_id
                    return conversation
            
            # Create new conversation
            convo_id = convo_id or str(uuid.uuid4())
            conversation = Conversation(
                convo_id=convo_id,
                user_id=user_id,
                started_at=datetime.utcnow()
            )
            
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            
            self.current_convo_id = convo_id
            self.conversation_context = []
            
            return conversation
        finally:
            session.close()
    
    def end_conversation(self, convo_id: str = None):
        """
        End a conversation.
        
        Args:
            convo_id: Conversation ID (uses current if not provided)
        """
        convo_id = convo_id or self.current_convo_id
        if not convo_id:
            return
        
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.convo_id == convo_id
            ).first()
            
            if conversation:
                conversation.ended_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def save_message(self, convo_id: str, sender: str, content: str) -> Message:
        """
        Save a message to the conversation.
        
        Args:
            convo_id: Conversation ID
            sender: 'user' or 'agent'
            content: Message content
            
        Returns:
            Message object
        """
        session = self.get_session()
        try:
            message = Message(
                message_id=str(uuid.uuid4()),
                convo_id=convo_id,
                sender=sender,
                content=content,
                timestamp=datetime.utcnow()
            )
            
            session.add(message)
            session.commit()
            session.refresh(message)
            
            # Update in-memory context
            self.conversation_context.append({
                'sender': sender,
                'content': content,
                'timestamp': message.timestamp
            })
            
            return message
        finally:
            session.close()
    
    def save_task_result(self, result: Dict[str, Any]) -> Dict[str, str]:
        """
        Save complete task result including task log, solution, and reflection.
        
        Args:
            result: Result dictionary from orchestrator
            
        Returns:
            Dictionary with saved IDs
        """
        session = self.get_session()
        try:
            # Save task log
            task_log_data = result.get('task_log', {})
            task_log = TaskLog(
                task_id=task_log_data.get('task_id', str(uuid.uuid4())),
                convo_id=task_log_data.get('convo_id'),
                agent_name=task_log_data.get('agent_name'),
                tool_used=task_log_data.get('tool_used'),
                task_type=task_log_data.get('task_type'),
                status=task_log_data.get('status'),
                confidence=task_log_data.get('confidence'),
                created_at=task_log_data.get('created_at', datetime.utcnow())
            )
            session.add(task_log)
            
            # Save solution record
            solution_data = result.get('solution_record', {})
            solution = SolutionRecord(
                solution_id=solution_data.get('solution_id', str(uuid.uuid4())),
                task_id=task_log.task_id,
                question=solution_data.get('question'),
                answer=solution_data.get('answer'),
                method_source=solution_data.get('method_source'),
                created_at=solution_data.get('created_at', datetime.utcnow())
            )
            session.add(solution)
            
            # Save reflection log
            reflection_data = result.get('reflection', {})
            if reflection_data:
                reflection = ReflectionLog(
                    reflect_id=reflection_data.get('reflect_id', str(uuid.uuid4())),
                    task_id=task_log.task_id,
                    evaluation=str(reflection_data.get('evaluation', '')),
                    suggestion=str(reflection_data.get('suggestion', '')),
                    final_confidence=reflection_data.get('final_confidence', 0.5),
                    created_at=reflection_data.get('created_at', datetime.utcnow())
                )
                session.add(reflection)
            
            session.commit()
            
            return {
                'task_id': task_log.task_id,
                'solution_id': solution.solution_id,
                'status': 'saved'
            }
        except Exception as e:
            session.rollback()
            return {'status': 'error', 'error': str(e)}
        finally:
            session.close()
    
    def get_conversation_history(self, convo_id: str = None, limit: int = 10) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            convo_id: Conversation ID (uses current if not provided)
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        convo_id = convo_id or self.current_convo_id
        if not convo_id:
            return self.conversation_context
        
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.convo_id == convo_id
            ).order_by(Message.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    'sender': msg.sender,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in reversed(messages)
            ]
        finally:
            session.close()
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations
            
        Returns:
            List of conversation dictionaries
        """
        session = self.get_session()
        try:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.started_at.desc()).limit(limit).all()
            
            return [
                {
                    'convo_id': conv.convo_id,
                    'started_at': conv.started_at,
                    'ended_at': conv.ended_at,
                    'message_count': len(conv.messages)
                }
                for conv in conversations
            ]
        finally:
            session.close()
    
    def get_conversation_context(self, convo_id: str = None, last_n: int = 5) -> str:
        """
        Get formatted conversation context for LLM prompts.
        
        Args:
            convo_id: Conversation ID
            last_n: Number of recent messages to include
            
        Returns:
            Formatted context string
        """
        history = self.get_conversation_history(convo_id, limit=last_n)
        
        if not history:
            return "No previous conversation context."
        
        context_parts = ["Previous conversation context:"]
        for msg in history:
            sender_label = "User" if msg['sender'] == 'user' else "Assistant"
            context_parts.append(f"{sender_label}: {msg['content'][:200]}")
        
        return "\n".join(context_parts)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get current state summary.
        
        Returns:
            Dictionary with state information
        """
        return {
            'current_user_id': self.current_user_id,
            'current_convo_id': self.current_convo_id,
            'context_messages': len(self.conversation_context),
            'database_url': self.database_url
        }
    
    def reset_state(self):
        """Reset in-memory state"""
        self.current_user_id = None
        self.current_convo_id = None
        self.conversation_context = []
