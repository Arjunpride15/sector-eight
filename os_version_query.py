import platform, subprocess
import sys, os, psutil
from pyglet import gl
import pyglet


def get_detailed_os_name() -> str:
    system = platform.system()
    arch = platform.machine()

    if system == "Windows":
        release = platform.release()  # "10" or "11"
        display_version = ""
        build_number = ""

        # Fetch Windows Feature Update (e.g., '23H2', '24H2') and Build Number from Registry
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            )
            display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            build_number, _ = winreg.QueryValueEx(key, "CurrentBuild")
            winreg.CloseKey(key)
        except Exception:
            pass

        # Format output
        version_parts = [f"Windows {release}"]
        if display_version:
            version_parts.append(display_version)
        if build_number:
            version_parts.append(f"Build {build_number}")

        version_str = " ".join(version_parts)
        return f"{version_str} [{sys.platform} / {arch}]"

    elif system == "Darwin":
        mac_ver, _, mac_build = platform.mac_ver()
        return f"macOS {mac_ver} Build {mac_build} [Darwin / {arch}]"

    elif system == "Linux":
        try:
            info = platform.freedesktop_os_release()
            os_name = info.get("NAME", "Linux")
            version_id = info.get("VERSION_ID", platform.release())
            return f"{os_name} {version_id} [{sys.platform} / {arch}]"
        except (AttributeError, OSError):
            return f"Linux {platform.release()} [{sys.platform} / {arch}]"

    return f"{system} {platform.release()} [{arch}]"

def get_cpu_info() -> str:
    """Returns processor brand and logical thread count."""
    system = platform.system()
    threads = os.cpu_count() or "Unknown"
    cpu_name = ""

    if system == "Windows":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            )
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
        except Exception:
            cpu_name = platform.processor()

    elif system == "Darwin":
        try:
            cpu_name = (
                subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"]
                )
                .decode()
                .strip()
            )
        except Exception:
            cpu_name = platform.processor()

    elif system == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu_name = line.split(":")[1].strip()
                        break
        except Exception:
            cpu_name = platform.processor()

    # Clean up extra spacing in returned string
    cpu_name = " ".join(cpu_name.split())
    return f"{cpu_name} [{threads} Logical Cores / {platform.machine()}]"
class SystemCapabilityCheckerFor120FPS:
    def __init__(
        self,
        window=None,
        min_cores: int = 4,
        min_freq_mhz: float = 2500,
        min_ram_gb: float = 8.0,
    ):
        self.window = window
        self.min_cores = min_cores
        self.min_freq_mhz = min_freq_mhz
        self.min_ram_gb = min_ram_gb

    def get_max_refresh_rate(self) -> int:
        """Inspects all supported display modes to find the maximum refresh rate (Hz)."""
        try:
            # Method 1: Use window.display if window exists, otherwise pyglet.display.get_display()
            if self.window and hasattr(self.window, "display"):
                display = self.window.display
            else:
                display = pyglet.display.get_display()

            screen = display.get_default_screen()

            max_rate = 0
            # Query all modes supported by the screen
            for mode in screen.get_modes():
                if mode.rate and mode.rate > max_rate:
                    max_rate = mode.rate

            # Fallback to active display mode
            if max_rate == 0 and screen.get_mode():
                max_rate = screen.get_mode().rate or 60

            return max_rate
        except Exception as e:
            print(f"Warning: Could not query display modes ({e})")
            return 60

    def inspect_hardware(self) -> dict:
        """Inspects system CPU, RAM, and GPU specs."""
        logical_cores = psutil.cpu_count(logical=True) or 1
        cpu_freq_info = psutil.cpu_freq()
        max_freq = cpu_freq_info.max if cpu_freq_info else 0.0

        ram_gb = psutil.virtual_memory().total / (1024**3)

        gpu_renderer = "Unknown GPU"
        try:
            gpu_renderer = gl.glGetString(gl.GL_RENDERER).decode("utf-8")
        except Exception:
            gpu_renderer = "GL Context Not Initialized"

        cpu_passed = (
            logical_cores >= self.min_cores or max_freq >= self.min_freq_mhz
        )
        ram_passed = ram_gb >= self.min_ram_gb

        return {
            "cores": logical_cores,
            "freq_mhz": max_freq,
            "ram_gb": round(ram_gb, 1),
            "gpu": gpu_renderer,
            "hardware_pass": cpu_passed and ram_passed,
        }

    def evaluate_120fps_support(self) -> dict:
        """Combines display capabilities and hardware specs."""
        max_hz = self.get_max_refresh_rate()
        hw_info = self.inspect_hardware()

        monitor_supported = max_hz >= 120
        hardware_supported = hw_info["hardware_pass"]

        return {
            "can_enable_120fps": monitor_supported and hardware_supported,
            "max_refresh_rate_hz": max_hz,
            "monitor_supported": monitor_supported,
            "hardware_supported": hardware_supported,
            "hardware_details": hw_info,
        }
   

    
if __name__ == "__main__":
    print(get_detailed_os_name())