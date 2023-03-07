"""********************************************************************"""
"""                                                                    """
"""   [proxies] ProxyManager.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 14/08/2021 05:30:06                                     """
"""   Updated: 07/09/2021 06:19:24                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary
import glob
import random

from questionary import Choice

from core.singletons.ProxySingleton import ProxySingleton
from utilities import Logger, getTime, Colors, ReadFile, ProxySelectorTheme

class ProxyManager(metaclass=ProxySingleton):

    def proxyToString(self, proxy):
        if ("http" in proxy):
            proxy = proxy['http']
        
        proxy = proxy.replace("http://", "")
        
        try:
            proxySplitted = proxy.split("@")
            proxy = proxySplitted[1] + ":" + proxySplitted[0]
        except IndexError:
            pass

        return (proxy)

    def getProxiesSelector(self):
        files = glob.glob(f"proxies/{self.moduleName}/*")

        Choices = []
        for file in files:

            size, content = ReadFile(file)

            if (size > 0):
                Choices.append(Choice(
                    title=[
                        ("class:purple", '{message: <16}'.format(message=file.split("\\")[-1])),
                        ("class:text", " ["),
                        ("class:blue", '{message} proxies'.format(message=size)),
                        ("class:text", "]")
                    ],
                    value={
                        "name": file.split("\\")[-1],
                        "content": content,
                        "size": size
                    }
                ))

        return (Choices)
        
    def chooseProxiesFiles(self):
        
        if len(glob.glob(f"proxies/{self.moduleName}/*")) < 1:
            Logger.error("[Proxy] No proxies found in directory!")
            Logger.info(f"[Proxy] Insert proxies files in proxies/{self.moduleName}")

            try:
                input(f"[{Colors.PURPLE}{getTime()}{Colors.RESET}] Press Enter for retrying or exit CLI. {Colors.RESET}")
            except KeyboardInterrupt:
                return None
                
            return self.chooseProxiesFiles()
        
        files = self.getProxiesSelector()

        answers = questionary.checkbox(
            "Which proxies file you want to use?",
            choices=files,
            style=ProxySelectorTheme,
            validate=lambda text: True if len(text) > 0 else "You need to select at least one file for proxies!"
        ).ask()

        return (answers)
        
    def importProxiesFromFile(self, proxiesData):
        Logger.debug(f"[Proxy] Importing proxies from {proxiesData['name']}")

        fileName = proxiesData['name'].split(".")[0]
        formattedProxies = []
        badProxies: int = 0
        
        for proxy in proxiesData['content']:

            proxy = proxy.strip()
            proxy = proxy.split(":")

            if (len(proxy) == 2):
                formattedProxies.append(
                    "http://" + proxy[0] + ":" + proxy[1]
                )

            elif (len(proxy) == 4):
                formattedProxies.append(
                    "http://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + ":" + proxy[1]
                )
            else:
                badProxies += 1
        
        if (badProxies > 0):
            Logger.warning(f"[Proxy] Filtered {badProxies} bad proxies from {fileName}!")

        self.proxies.append({
            "name": fileName,
            "file": proxiesData['name'],
            "proxies": formattedProxies
        })

    def __init__(self, moduleName) -> None:
        self.moduleName = moduleName
        self.proxies = []
        self.length = 0
        
        proxiesFiles = self.chooseProxiesFiles()

        if (proxiesFiles is None):
            return (None)
            
        for proxiesFile in proxiesFiles:
            self.importProxiesFromFile(proxiesFile)

        for proxiesProfile in self.proxies:
            self.length += len(proxiesProfile['proxies'])

        Logger.success(f"[Proxy] Successfully loaded {self.length} proxies from {len(proxiesFiles)} files!")
        
    """
        @Getters
    """

    def getProxy(self, profile=None):
        if (profile is None):
            proxyProfile = random.choice(self.proxies)
        else:
            try:
                proxyProfile = [proxyFile for proxyFile in self.proxies if proxyFile['name'] == profile][0]
            except IndexError:
                proxyProfile = random.choice(self.proxies)
        
        try:
            proxy = random.choice(proxyProfile['proxies'])
        except IndexError:
            Logger.error("[ProxyManager] No more proxies available! Stop Tasks!")
            return None
            
        formatedProxy = {"https": proxy, "http": proxy}

        return {
            "profile": proxyProfile['name'],
            "proxyString": self.proxyToString(formatedProxy),
            "proxy": formatedProxy
        }

    def banProxy(self, proxy):

        try:
            proxyProfile = [proxyFile for proxyFile in self.proxies if proxyFile['name'] == proxy['profile']][0]
            
            proxyProfile['proxies'].remove(proxy['proxy']['http'])
            Logger.debug(f"[ProxyManager] Removed {proxy['proxyString']} from {proxy['profile']} list")
            
        except Exception:
            Logger.debug("[ProxyManager] Failed to ban Proxy...")

    def rotateProxy(self, session, proxy):

        self.banProxy(proxy)
        newProxy = self.getProxy()
        session.proxies.update(newProxy['proxy'])
        
        return (newProxy)

