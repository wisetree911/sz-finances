import aiohttp
from loguru import logger

class MoexClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def get_all_prices(self) -> dict:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities.json?marketdata.columns=SECID,LAST"
        try:
            async with self.session.get(url, timeout=30) as resp:
                data = await resp.json()
        except Exception as e:
            logger.error(f"!!!!!! Ошибка сети: {e} !!!!!")
            raise
        prices = {}
        for row in data["marketdata"]["data"]:
            prices[row[0]] = row[1]
        try:
            return prices
        except Exception:
            logger.error(f" !!!!!!! Ошибка парсинга ответа: {data} !!!!!!!")
            raise


    async def get_security_info(self, ticker: str) -> dict:
        pass

