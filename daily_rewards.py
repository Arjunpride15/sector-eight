import shelve, time, atexit, pyglet, obfuscator
from datetime import datetime, timedelta
from session_manager import SessionManager

class DailyRewards:
    def __init__(self):
        self.session_obj = SessionManager()
        self.active_user = self.session_obj.get_active_user()
        self.obfuscator_obj = obfuscator.PseudoEncryptor()
        if self.active_user:
            self.db = \
            shelve.open(f'data\\temp\\miscn\\{self.obfuscator_obj.obfuscate_filename(self.active_user)}')
        else:
            Popen(["auth_launch.cmd"])
        
        self.prev_time = self.db.get("last_opened", time.time())
        self.claimed_yet = self.db.get("claimed", False)
        
        atexit.register(self.exit)
        pyglet.clock.schedule_interval(self.update, interval=0.5)
    
    def is_daily_reward_pending(self):
        
        current_time = self.db.get("current", time.time())
        
        
        prev_obj = datetime.fromtimestamp(int(self.prev_time))
        current_obj = datetime.fromtimestamp(int(current_time))
        
        time_difference = current_obj - prev_obj
        one_day = timedelta(days=1)
        
        
        if time_difference > one_day:
            if self.claimed_yet:
                self.claimed_yet = False
                self.sync_data("claimed", False)
        
        return not self.claimed_yet
        
    def claim_reward(self):
        if not self.is_daily_reward_pending():
            return False
            
        self.claimed_yet = True
        self.sync_data("claimed", True)
        return True
        
    def sync_data(self, name, var):
        self.db[name] = var
        self.db.sync()
        
    def update(self, dt):
        self.sync_data("current", time.time())
        
    def exit(self):
        self.db.close()