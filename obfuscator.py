import pathvalidate

class PseudoEncryptor:
    """
    Simple string obfuscator using character flip-flopping 
    and deterministic uncommon character injection.
    """
    def __init__(self):
        # Filename-safe characters in Windows
        self.uncommon_chars = ["~", "@", "#", "$", "%", "^"]

    def _get_key_char(self, text: str) -> str:
        """Deterministically picks a character based on the text."""
        idx = len(text) % len(self.uncommon_chars)
        return self.uncommon_chars[idx]

    def obfuscate_filename(self, username: str) -> str:
        """
        Flips adjacent characters and inserts a deterministic uncommon marker.
        """
        if not username:
            return "anon~data"
        
        clean_name = pathvalidate.sanitize_filename(username.strip().lower())
        key_char = self._get_key_char(clean_name)
        chars = list(clean_name)
        
        # 1. Flip-flop adjacent character pairs
        for i in range(0, len(chars) - 1, 2):
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
            
        flipped_str = "".join(chars)
        
        # 2. Insert uncommon character in the middle
        mid = len(flipped_str) // 2
        return f"{flipped_str[:mid]}{key_char}{flipped_str[mid:]}"

    def deobfuscate_filename(self, filename: str) -> str:
        """
        Reverses the uncommon character injection and flip-flopping.
        """
        # 1. Strip any of the valid uncommon characters
        flipped_str = filename
        for char in self.uncommon_chars:
            flipped_str = flipped_str.replace(char, "")
        
        # 2. Flip adjacent characters back
        chars = list(flipped_str)
        for i in range(0, len(chars) - 1, 2):
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
            
        return "".join(chars)