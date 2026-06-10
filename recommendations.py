import shelve
import statistics, random
import datetime
from typing import Any

class SectorEightRecommendations:
    def __init__(self):
        self.log_store = shelve.open(r"data\purchases")
        self.log: list[str] = self.log_store.get('log', list())
        
    def get_item_history(self) -> list[str]:
        history_list = list()
        for item in self.log:
            stripped_item = item.split(sep=" | ")
            history_list.append(stripped_item[1])
        return history_list
    
    def get_recommended_item(self) -> str:
        items_bought = self.get_item_history()
        
        # 1. Fast-path check: If list is empty, avoid exception overhead entirely!
        if not items_bought:
            return random.choice(['Laser Boost', 'XP Speedups', 'Powerups', 'Invisibility', 'Extra Life'])
            
        try:
            # 2. Return immediately on success to keep control flow dead simple
            return statistics.mode(items_bought)
        except statistics.StatisticsError:
            # 3. Fallback if a statistics error somehow still occurs
            return random.choice(['Laser Boost', 'XP Speedups', 'Powerups', 'Invisibility', 'Extra Life'])   
    
    def release_file(self):
        self.log_store.close()

class SectorEightHistory:
    def __init__(self):
        self.log_store = shelve.open(r"data\purchases")
        self.log: list[str] = self.log_store.get('log', list())
        self.datetime_list: list[Any]  = list()
    
    def get_general_history(self):
        full_history = list()
        for item in self.log:
            stripped_item = item.split(sep=" | ")
            item_history = list()
            for sub_item in stripped_item:
                item_history.append(sub_item)
            full_history.append(tuple(item_history))
        return full_history
    
    def get_date_time_history(self):
        
        for item in self.get_general_history():
            item_date_time: str = item[0]
            dt_obj = datetime.datetime.fromisoformat(item_date_time)
            item_date = dt_obj.strftime("%A, %b %d, %Y")
            item_time = dt_obj.strftime('%H : %M (24-hour format)')
            self.datetime_list.append({'date': item_date, 'time': item_time})
            
        return self.datetime_list
    def get_trans_id_history(self):
        trans_id_list = list()
        for item in self.get_general_history():
            item_trans_id = item[2]
            trans_id_list.append(int(item_trans_id))
        return trans_id_list