from pythonpancakes import PancakeSwapAPI

ps = PancakeSwapAPI()
summary = ps.tokens("0xff14832d713ea76389362dd6ad47cf971b46c344dd386f5be524fce60526f708")
print(summary)