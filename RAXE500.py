from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager


AP_APPLY_CHANGES_TIMEOUT = 180
# Map channel selection list - element IDs
CHANNEL_PULLDOWNS = {
        "2G": "wireless_channel",
        "5G": "wireless_channel_an",
        "6G": "wireless_channel_an_2"
}
# Map mode pulldowns - element IDs
MODE_OPTIONS = {
    "2G": "opmode",
    "5G": "opmode_an",
    "6G": "opmode_an_2"
}
# SSID element IDs mapping
SSID_ELEMENTS = {
    "2G": "ssid",
    "5G": "ssid_an",
    "6G": "ssid_an_2"
}

#Map mode - width comnbinations -> element's text
MODE_MAPPING = {
    #(band, mode, width, ax_enabled?): mode_on_list
    # 2.4 GHz
    ("2G", "G", "20", False): "Up to 54 Mbps",
    ("2G", "N", "20", False): "Up to 433 Mbps",
    ("2G", "N", "40", False): "Up to 1000 Mbps",
    ("2G", "AX", "20", True): "Up to 600 Mbps",
    ("2G", "AX", "40", True): "Up to 1200 Mbps",

    # 5 GHz
    ("5G", "N", "20", False): "Up to 433 Mbps",
    ("5G", "N", "40", False): "Up to 1000 Mbps",
    ("5G", "AC", "20", False): "Up to 433 Mbps",
    ("5G", "AC", "40", False): "Up to 1000 Mbps",
    ("5G", "AC", "80", False): "Up to 2165 Mbps",
    ("5G", "AX", "20", True): "Up to 600 Mbps",
    ("5G", "AX", "40", True): "Up to 1200 Mbps",
    ("5G", "AX", "80", True): "Up to 2400 Mbps",
    ("5G", "AX", "160", True): "Up to 4800 Mbps",

    # 6 GHz
    ("6G", "AX", "20", True): "Up to 600 Mbps",
    ("6G", "AX", "40", True): "Up to 1200 Mbps",
    ("6G", "AX", "80", True): "Up to 2400 Mbps",
    ("6G", "AX", "160", True): "Up to 4800 Mbps"
}
# Security element IDs
SECURITY_MAPPING = {
    "2G": {
        "OPEN": "security_disable",
        "WPA2": "security_wpa2",
        "WPA2/WPA3": "security_auto",
        "WPA3": "security_wpa3"
    },
    "5G": {
        "OPEN": "security_an_disable",
        "WPA2": "security_an_wpa2",
        "WPA2/WPA3": "security_an_auto",
        "WPA3": "security_an_wpa3"
    },
    "6G": {
        "OWE": "security_an_2_owe",
        "WPA3": "security_an_2_wpa3"
    }
}
# Password field element IDs mapping
PASSWORD_FIELDS = {
    "2G": "passphrase",
    "5G": "passphrase_an",
    "6G": "passphrase_an_2"
}

class ApController:
    def __init__(self, ap_ip, username, password, headless=False):
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
        self.headless = headless

        chrome_options = Options()
        print(self.headless)
        if self.headless:
            # run chrome in background
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        # Launch driver with options
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    # def connect(self):
    # http://admin:PCVtest123$@192.168.1.9/

    def connect_and_login(self):
        LOGIN_RETRIES = 5
        i = 0
        while i < LOGIN_RETRIES:
            print(f"[INFO] Attempt to login to AP {i+1}/{LOGIN_RETRIES}")
            self.driver.get("http://" + self.username +":" + self.password + "@" + self.ap_ip + "/")
            sleep(2)
            title = self.driver.title
            if title == "":
                print("[ERROR] Failed to login to AP...")
                i = i + 1
            elif title == "NETGEAR Router RAXE500":
                print(f"[OK] AP login successful")
                break
            else:
                print(f"[OK] Login successfull, but wrong title! Expected title: NETGEAR Router RAXE500, Detected title: {title}"
                      f"Make sure the AP model and FW version is coreect!")

    def apply_and_wait(self, timeoout=300):
        try:
            # Switch to iframe
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "formframe"))
            )
            self.driver.switch_to.frame(iframe)
            apply_button = self.driver.find_element(By.ID, "apply")
            apply_button.click()
            print(f"[INFO] Waiting for changes to be apllied...")

            try:
                # Check if secuirty alert appeared
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                print(f"[INFO] Alert from AP detected: {alert.text}")
                alert.accept()
                print(f"[INFO] Alert accepted")
            except Exception:
                # If alert not detected just continue
                pass
            WebDriverWait(self.driver, timeoout).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.subhead2.page_title"), "Wireless Setup")
            )
            print(f"[OK] Changes applied")
        except UnexpectedAlertPresentException:
            try:
                alert = self.driver.switch_to.alert
                print(f"[INFO] Alert from AP detected: {alert.text}")
                alert.accept()
                print("[INFO] Alert accepted")
                WebDriverWait(self.driver, timeoout).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.subhead2.page_title"), "Wireless Setup")
                )
                print(f"[OK] Changes applied")
            except NoAlertPresentException:
                print("[ERROR] Alert disappeared before it could be handled.")

        # switch back to default context
        self.driver.switch_to.default_content()

    def apply_and_wait_advanced(self, timeoout=300):
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)
        try:
            apply_button = self.driver.find_element(By.ID, "apply")
            apply_button.click()
            print(f"[INFO] Waiting for changes to be apllied...")

            try:
                # Check if secuirty alert appeared
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                print(f"[INFO] Alert from AP detected: {alert.text}")
                alert.accept()
                print(f"[INFO] Alert accepted")
            except Exception:
                # If alert not detected just continue
                pass
            WebDriverWait(self.driver, timeoout).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#target > div.subhead2"), "Wireless Settings")
            )
            print(f"[OK] Changes applied")
        except UnexpectedAlertPresentException:
            try:
                alert = self.driver.switch_to.alert
                print(f"[INFO] Alert from AP detected: {alert.text}")
                alert.accept()
                print("[INFO] Alert accepted")
                WebDriverWait(self.driver, timeoout).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.subhead2.page_title"), "Wireless Setup")
                )
                print(f"[OK] Changes applied")
            except NoAlertPresentException:
                print("[ERROR] Alert disappeared before it could be handled.")

        # switch back to default context
        self.driver.switch_to.default_content()

    def open_wireless_settings(self):
        wireless_menu_button = self.driver.find_element(By.ID,"basic_wireless")
        wireless_menu_button.click()

        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)

        # Wait for "Wireless Setup" text on page loaded
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.subhead2"), "Wireless Setup")
        )
        print("[OK] Wireless settings page loaded")
        # switch back to default content
        self.driver.switch_to.default_content()

    def open_advanced_wireless_settings(self):
        self.driver.switch_to.default_content()
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "topframe"))
        )
        self.driver.switch_to.frame(iframe)

        advanced_wireless_tab = self.driver.find_element(By.ID, "advanced_label")
        advanced_wireless_tab.click()
        # switch back to default context
        self.driver.switch_to.default_content()
        advanced_wireless_button = self.driver.find_element(By.ID, "advanced_wireless")
        # Check if "Wireless settings" button is visible, if not unfold "Advanced Setup" menu
        try:
            advanced_wireless_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "advanced_wireless")))
            advanced_wireless_button.click()
        except Exception as e:
            print(f"[INFO] \"Wireless settings\" seems to be hidden, expanding \"Advanced setup\" menu")
            advanced_setup = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "advanced_bt"))
            )
            advanced_setup.click()
            advanced_wireless_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "advanced_wireless")))
            advanced_wireless_button.click()
            print(f"[DEBUG] Wireless settings button clicked")

        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)
        # Wait for "Wireless Setup" text on page loaded DZIAŁA
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "5g_wifi_settings")))

        # Wait for "Wireless Setup" text on page loaded  DZIAŁA
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#target > table > tbody > tr:nth-child(2) > td > div > table > tbody > tr:nth-child(1) > td > a > b"), "Wireless Advanced Settings (2.4GHz b/g/n/ax)")
        )
        # NIE DZIALA - czekanie na fragemnt zaczynający sie od "Wireless..." dalej w zaleznosci od basic/advanced settings mamy ...Settings/Setup
        # WebDriverWait(self.driver, 10).until(
        #     EC.text_to_be_present_in_element((By.TAG_NAME, "subhead2"), "Wireless"))

        radio_checkbox = self.driver.find_element(By.ID, "enable_ap_an_2")
        print(f"[DEBUG] Radio checkbox found")
        print("[OK] Advanced wireless settings page loaded")
        # switch back to default context
        self.driver.switch_to.default_content()

    def switch_radio(self, band, enabled):
        radio_checkbox_mapping = {
            "2G": "enable_ap",
            "5G": "enable_ap_an",
            "6G": "enable_ap_an_2"
        }
        band = band.upper()
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)
        radio_checkbox_id = radio_checkbox_mapping[band]
        radio_checkbox = self.driver.find_element(By.ID, radio_checkbox_id)
        enabled = eval(enabled)
        if enabled:
            if radio_checkbox.is_selected():
                print(f"[DEBUG] Radio for {band} interface already enabled")
            else:
                print(f"[DEBUG] Radio for {band} interface disabled. Attempting to enable...")
                radio_checkbox.click()
                print(f"[DEBUG] {band} radio enabled")
        else:
            if radio_checkbox.is_selected():
                print(f"[DEBUG] Radio for {band} interface enabled. Attempting to disable...")
                radio_checkbox.click()
                print(f"[DEBUG] {band} radio disabled")
            else:
                print(f"[DEBUG] Radio for {band} interface already disabled")

        # switch back to default context
        self.driver.switch_to.default_content()

    def set_channel(self, band, channel):
        channels = {
            "1": "01",
            "2": "02",
            "3": "03",
            "4": "04",
            "5": "05",
            "6": "06",
            "7": "07",
            "8": "08",
            "9": "09",
            "10": "10",
            "11": "11",
            "12": "12",
            "13": "13"
        }
        psc_channels = {
            "37", "53", "69", "85", "101"}
        if band.upper() == "2G":
            channel = channels[channel]
        if band.upper() == "6G" and channel in psc_channels:
            channel = channel + "(PSC)"
            print(channel)
        band = band.upper()
        if band not in CHANNEL_PULLDOWNS:
            raise ValueError(f"[ERROR] Unrecognized band value: {band}")
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)

        pulldown_list = self.driver.find_element(By.ID, str(CHANNEL_PULLDOWNS[band]))
        select = Select(pulldown_list)
        try:
            select.select_by_visible_text(str(channel))
            print(f"[OK] Channel selected: {channel}")
        except Exception as e:
            print(f"[ERROR] Unable to select {channel} for band {band}")
            raise
        # switch back to default context
        self.driver.switch_to.default_content()

    def set_mode(self, band, mode, width):
        band = band.upper()
        mode = mode.upper()
        width = width
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)

        # check if desired combination is possible to set
        possible_combinations = []
        for key in MODE_MAPPING.keys():
            if key[0] == band and key[1] == mode and key[2] == width:
                possible_combinations.append(key)
        if not possible_combinations:
            print(f"[ERROR] Combination of parameters is not supported for band {band}: {mode, width}. Please check the parameters once again")
            raise ValueError(f"[ERROR] Unsupported combination: {(band, mode, width)}")
        ax_enabled = False
        target_mode = None
        for key, value in MODE_MAPPING.items():
            if key[0] == band and key[1] == mode and key[2] == width:
                print(f"[DEBUG] Combination found [band: {band}, mode: {mode}, channelWidth: {width}, AX_mode: {key[3]}]")
                target_mode = value
                ax_enabled = key[3]
                print(f"[DEBUG] ax_enabled: {ax_enabled}, type{type(ax_enabled)}")
                break
        try:
            ax_checkbox = self.driver.find_element(By.ID, "enable_ax_chec")
            print(f"[DEBUG] ax_checkbox state: {ax_checkbox.is_selected()}")
            if ax_enabled and not ax_checkbox.is_selected():
                print(f"[INFO] AX mode required. Attempting to select \"AX checkbox\"")
                ax_checkbox.click()
                if ax_checkbox.is_selected():
                    print("[OK] AX mode enabled")
            elif not ax_enabled and ax_checkbox.is_selected():
                print(f"[INFO] AX mode not required. Attempting to uncheck \"AX checkbox\"")
                ax_checkbox.click()
                if not ax_checkbox.is_selected():
                    print("[OK] AX mode disabled")
        except Exception as e:
            print(f"[ERROR] Unable to find AX checkbox")
            raise


        mode_list = self.driver.find_element(By.ID, MODE_OPTIONS[band])
        if not mode_list:
            print(f"[ERROR] Expected mode cannot be set, not found on the list")
            print(mode_list)
            return

        select = Select(mode_list)
        try:
            select.select_by_visible_text(target_mode)
            print(f"[OK] \"{target_mode}\" mode selected")
        except Exception as e:
            print(f"[ERROR] Error when trying to select mode: {e}")

        # switch back to default context
        self.driver.switch_to.default_content()

    def set_security(self, band, security_type, password=None):
        band = band.upper()
        security_type = security_type.upper()
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)

        if band not in SECURITY_MAPPING:
            raise ValueError(f"[ERROR] Unrecognized band: {band}")
        band_mapping = SECURITY_MAPPING[band]
        if security_type not in band_mapping:
            raise ValueError(f"[ERROR] Security type {security_type} is not selectable for band {band}")
        # Assign element ID and select
        target_security_id = band_mapping[security_type]
        try:
            security_button = self.driver.find_element(By.ID, target_security_id)
            security_button.click()
        except Exception as e:
            print(f"[ERROR] Unable to select expected security type: {e}")
        if security_type != "OPEN" or security_type != "OWE":
            if not password or len(password) < 8:
                raise ValueError(f"[ERROR] Invalid password: must be at least 8 ASCII characters.")
            print(f"[INFO] Password provided for security type {security_type}, setting a new password...")
            self.set_password(band, password)
        # switch back to default context
        self.driver.switch_to.default_content()

    def set_password(self, band, password):
        band = band.upper()

        # # Switch to iframe
        # iframe = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "formframe"))
        # )
        # self.driver.switch_to.frame(iframe)
        if band not in PASSWORD_FIELDS:
            raise ValueError(f"[ERROR] Unrecognized band: {band}")
        password_field_id = PASSWORD_FIELDS[band]

        try:
            # Wait for password field to be visible
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, password_field_id))
            )
            password_field = self.driver.find_element(By.ID, password_field_id)
            if not password_field.is_displayed():
                print(f"[ERROR] Password field for band {band} not found or not active")
                return
            # Clear the field and input new password
            password_field.clear()
            password_field.send_keys(password)
        except Exception as e:
            print(f"[ERROR] Unable to set password: {e}")

        # switch back to default context
        self.driver.switch_to.default_content()

    def set_ssid(self, band, ssid):
        band = band.upper()
        if band not in SSID_ELEMENTS:
            raise ValueError(f"[ERROR] Unrecognized band: {band}")
        if not ssid or len(ssid) > 32:
            raise ValueError(f"[ERROR] Invalid SSID: must be 1–32 characters long.")
        ssid_field_id = SSID_ELEMENTS[band]
        # Switch to iframe
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "formframe"))
        )
        self.driver.switch_to.frame(iframe)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, ssid_field_id))
            )
            ssid_field = self.driver.find_element(By.ID, ssid_field_id)
            ssid_field.clear()
            ssid_field.send_keys(ssid)
            print(f"[OK] SSID for interface {band} set to: {ssid}")
        except Exception as e:
            print(f"[ERROR] Unable to set SSID: {e}")
        # switch back to default context
        self.driver.switch_to.default_content()

    def close(self):
        self.driver.quit()
        print("[INFO] Selenium driver closed")

# Simple main for testing purpose
# if __name__ == '__main__':
#     object = ApController("192.168.1.9", "admin", "PCVtest123$", False )
#     object.connect_and_login()
#     object.open_wireless_settings()
#     object.set_ssid("2G", "testSSID")
#     object.set_channel("2G", "6")
#     object.set_security("2G", "WPA2", "123456789")
#     object.set_security("6G", "WPA3", "testing123")
#     object.set_channel("5G", "36")
#     # object.open_advanced_wireless_settings()
#     # object.apply_and_wait_advanced()
#     # object.switch_radio("6G", False)
#     # object.apply_and_wait()
#     object.close()
