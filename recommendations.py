import shelve
import statistics

class SectorEightRecommendations:
    def __init__(self):
        self.log_store = shelve.open(r"data\purchases")
        self.log: list[str] = self.log_store.get('log', list())
        
    def get_item_history(self) -> list[str]:
        history_list = list()
        for item in self.log:
            stripped_item = item.split(sep=" ")
            history_list.append(stripped_item[2])
        return history_list
    
    def get_recommended_item(self) -> str:
        items_bought = self.get_item_history()
        try:
            recommended_item = statistics.mode(items_bought)
        except statistics.StatisticsError:
            return "Laser Boost"
        return recommended_item
        
        