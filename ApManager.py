from pkgutil import walk_packages

from ApController import ApController

class ApManager:
    def __init__(self, ap_ip, username, password, headless=False):
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
        self.ap_controller = None
        self.headless = headless

    def setup_ap(self, ap_params):
        try:
            band = ap_params.get("BAND")
            ssid = ap_params.get("SSID")
            channel = ap_params.get("CHANNEL")
            mode = ap_params.get("MODE")
            width = ap_params.get("WIDTH")
            security = ap_params.get("SECURITY")
            if security.upper() != "NONE":
                password = ap_params.get("PWD")
            else:
                password = None
            # password = ap_params.get("PWD", None)
            print(ap_params)
        except KeyError as e:
            print(f"[ERROR] Unable to find element in AP configuration: {e}")
            return

        self.ap_controller = ApController(self.ap_ip, self.username, self.password)
        self.ap_controller.connect_and_login()
        self.ap_controller.open_wireless_settings()

        self.ap_controller.set_ssid(band, ssid)
        self.ap_controller.set_channel(band, channel)
        self.ap_controller.set_mode(band, mode, width)
        if security.upper() == "NONE":
            self.ap_controller.set_security(band, "NONE")
        else:
            self.ap_controller.set_security(band, security, password)
        self.ap_controller.apply_and_wait()
        self.ap_controller.close()



