import tomli

class Config:
    """
    The class for reading Sector Eight's TOML config files! :-)
    It uses the tomli module (https://github.com/hukkin/tomli) to
    parse the config files.
    """
    def __init__(self):
        self.toml_dict = None
        
        # Open default config file
        with open("config/config.toml", "rb") as f:
            self.toml_dict = tomli.load(f)
    def main_music_path(self):
        return self.toml_dict['music']['def_file']
    
                
    
        