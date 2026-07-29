import shelve
import time
from datetime import datetime, timedelta
import atexit, pyglet


class SessionManager:
    def __init__(self, auto_clean=True):    
        self.db = shelve.open("data\\sessions")
        
        self.current_session = self.db.get("current_session", None)
        self.max_session_time = timedelta(hours=16)
        
        if self.current_session:
            self.last_session = datetime.fromtimestamp(self.current_session.get("login_time", time.time()))
        else:
            self.last_session = datetime.now()
            
        if auto_clean:
            pyglet.clock.schedule_interval(self.automatic_session_cleanup, 1)
        atexit.register(self.cleanup)
            
    def sync_data(self, name, var):
        self.db[name] = var
        self.db.sync()
    def save_session(self, username: str):
        """Saves the current active user session to disk."""
        now_ts = time.time()
        self.current_session = {
            "username": username,
            "login_time": now_ts
        }
        self.last_session = datetime.fromtimestamp(now_ts)
        self.sync_data("current_session", self.current_session)
        
    def get_active_user(self) -> str | None:
        """Retrieves the currently logged-in username, or None if no active session exists."""
        if self.current_session and isinstance(self.current_session, dict):
                return self.current_session.get("username")
        return None


    def clear_session(self):
        """Logs out the active user by deleting the session record."""
        
        if self.current_session:
            self.current_session = None
            self.sync_data("current_session", self.current_session)
    
    def automatic_session_cleanup(self, dt):
        if self.current_session:
            current_time = datetime.now()
            self.last_session = datetime.fromtimestamp(self.current_session.get("login_time", time.time()))
            if current_time - self.last_session > self.max_session_time:
                self.clear_session()
            
    def cleanup(self):
        self.db.close()