import shelve, time, atexit, pyglet
from datetime import datetime, timedelta

class DailyRewards:
    def __init__(self):
        self.db = shelve.open("data\\miscn")
        self.prev_time = self.db.get("last_opened", time.time())
        self.current_time = self.db.get("current", time.time())
        self.prev_obj = datetime.fromtimestamp(int(self.prev_time))
        self.current_obj = datetime.fromtimestamp(int(self.current_time))
        atexit.register(self.exit)
        pyglet.clock.schedule_interval(self.update, interval=0.5)
    
    def is_daily_reward_pending(self):
        time_difference = self.current_obj - self.prev_obj
        one_day = timedelta(days=1)
        if time_difference < one_day:
            return True
        else:
            return False
    def sync_data(self, name, var):
        self.db[name] = var
        self.db.sync()
    def update(self, dt):
        self.sync_data("current", time.time())
    def exit(self):
        self.db.close()
        