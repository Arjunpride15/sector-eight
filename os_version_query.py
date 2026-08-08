import platform, subprocess
import sys, os


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

if __name__ == "__main__":
    print(get_detailed_os_name())