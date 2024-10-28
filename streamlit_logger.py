import os
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
import traceback

class SafeJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable objects"""
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)
        except Exception:
            return '<not serializable>'

class StreamlitLogger:
    """Enhanced logging functionality for Streamlit applications"""
    
    def __init__(
        self,
        app_name: str = 'CodeWizard',
        log_dir: str = 'logs',
        max_bytes: int = 1024 * 1024,  # 1MB
        backup_count: int = 5,
        log_level: int = logging.INFO
    ):
        self.app_name = app_name
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation
        try:
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, f'{app_name.lower()}.log'),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(file_formatter)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"Error setting up logger: {str(e)}")
            # Fallback to basic console logging
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(file_formatter)
            self.logger.addHandler(console_handler)
    
    def _prepare_log_data(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> dict:
        """Prepare log data with consistent structure"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'content': content,
            'metadata': metadata or {}
        }
        
        if error:
            log_data['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
            
        return log_data
    
    def _safe_json_dump(self, data: dict) -> str:
        """Safely convert data to JSON string"""
        try:
            return json.dumps(data, cls=SafeJsonEncoder)
        except Exception as e:
            return json.dumps({
                'error': 'JSON serialization failed',
                'message': str(e)
            })
    
    def log_event(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        level: str = 'info'
    ) -> None:
        """Log an event with proper error handling"""
        try:
            log_data = self._prepare_log_data(event_type, content, metadata)
            log_message = self._safe_json_dump(log_data)
            
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(log_message)
            
        except Exception as e:
            # Fallback logging for when everything else fails
            self.logger.error(f"Logging failed: {str(e)}")
            print(f"Critical logging error: {str(e)}")

    def log_user_action(
        self,
        action_type: str,
        user_id: str,
        session_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user actions with session context"""
        try:
            metadata = {
                'user_id': user_id,
                'session_id': session_id,
                'details': details or {}
            }
            self.log_event(
                event_type='user_action',
                content=action_type,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Failed to log user action: {str(e)}")

    def log_error(
        self,
        error: Exception,
        context: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log errors with full context and stack trace"""
        try:
            log_data = self._prepare_log_data(
                event_type='error',
                content=context,
                metadata=metadata,
                error=error
            )
            self.logger.error(self._safe_json_dump(log_data))
        except Exception as e:
            # Last resort error logging
            print(f"Critical error logging failure: {str(e)}")
