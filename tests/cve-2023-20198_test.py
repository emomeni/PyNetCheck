"""
https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-iosxe-webui-privesc-j22SaA4z
"""
import os

import pytest
from ciscoconfparse import CiscoConfParse
from ipfabric import IPFClient

from .conftest import DIR

if DIR:
    CONFIGS = os.listdir(DIR)
    DEVICES = []
else:
    # Initiliaze IPF Client
    IPF = IPFClient()
    # Get all IOS-XE devices
    DEVICES = IPF.devices.by_family["ios-xe"]
    CONFIGS = []


def check_config(config, file=False):
    """
    Vulnerability is not exploitable if:
    ip http server command is present and the configuration also contains ip http active-session-modules none
    ip http secure-server command is present and the configuration also contains ip http secure-active-session-modules none
    """
    if file:
        cfg = CiscoConfParse(os.path.join(DIR, config), syntax="ios")
    else:
        cfg = CiscoConfParse(config.split("\n"), syntax="ios") if config else None

    http_svr = [l.strip() for l in cfg.find_lines("ip http")]
    if not http_svr or (
            "no ip http server" in http_svr and "no ip http secure-server" in http_svr
    ):
        assert True, "HTTP and HTTPS Servers Disabled"

    elif "ip http server" in http_svr and "ip http secure-server" in http_svr:
        assert (
                "ip http active-session-modules none" in http_svr
                and "ip http secure-active-session-modules none" in http_svr
        ), "HTTP and HTTPS Server Vulnerable"
    elif "ip http server" in http_svr:
        assert (
                "ip http active-session-modules none" in http_svr
        ), "HTTP Server Vulnerable, HTTPS Server Disabled"
    elif "ip http secure-server" in http_svr:
        assert (
                "ip http secure-active-session-modules none" in http_svr
        ), "HTTPS Server Vulnerable, HTTP Server Disabled"
    else:
        assert False, "Unknown HTTP(S) Server State"


# Test each device for HTTP(S) Server configuration in running and startup configs
@pytest.mark.parametrize("device", DEVICES, ids=[d.hostname for d in DEVICES])
class TestHTTPServerIPF:
    # If no devices then skip
    __test__ = True if DEVICES else False

    def test_running_config_http_server(self, device):
        # First get configurations using the `/management/saved-config-consistency` table.
        configs = device.get_config(IPF)
        # Check the startup configuration
        check_config(configs.current)
        if configs.status == "saved":
            check_config(configs.start)


# Test each device for HTTP(S) Server configuration in configuration directory
@pytest.mark.parametrize("config", CONFIGS, ids=[d.hostname for d in DEVICES])
class TestHTTPServerConfig:
    # If no devices then skip
    __test__ = True if CONFIGS else False

    def test_running_config_http_server(self, config):
        # Check the configuration
        check_config(config, file=True)
