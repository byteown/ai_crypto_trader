import pytest
from app.models.bot import BotMode, BotStrategy
from app.schemas.bot import BotCreate, BotUpdate
from pydantic import ValidationError

VALID = {"name": "John", "symbol": "BTC/USDT", "timeframe": "1h"}


def test_valid_bot():
    bot = BotCreate(**VALID)
    assert bot.name == "John"


def test_bot_defaults():
    bot = BotCreate(**VALID)
    assert bot.mode == BotMode.PAPER
    assert bot.strategy == BotStrategy.RULES


@pytest.mark.parametrize("bad_symbol", ["BTCUSDT", "BTC", "btc/usdt", "BTC/", "/USDT"])
def test_bad_symbols(bad_symbol):
    with pytest.raises(ValidationError):
        BotCreate(**{**VALID, "symbol": bad_symbol})


@pytest.mark.parametrize("bad_timeframe", ["2h", "lol", ""])
def test_bad_timeframe(bad_timeframe):
    with pytest.raises(ValidationError):
        BotCreate(**{**VALID, "timeframe": bad_timeframe})


@pytest.mark.parametrize(
    "bad_name",
    ["jd", "lollollollollollollollollollollollollollollollollollollollollol"],
)
def test_bad_name(bad_name):
    with pytest.raises(ValidationError):
        BotCreate(**{**VALID, "name": bad_name})


def test_empty_update():
    bot = BotUpdate()
    assert bot.model_dump(exclude_unset=True) == {}


def test_update_timeframe():
    bot = BotUpdate(timeframe="1h")
    assert bot.model_dump(exclude_unset=True) == {"timeframe": "1h"}


def test_bad_symbol():
    with pytest.raises(ValidationError):
        BotUpdate(symbol="lol")


def test_empty_patch():
    bot = BotUpdate()
    assert bot.model_dump() == {
        "name": None,
        "symbol": None,
        "timeframe": None,
        "mode": None,
        "strategy": None,
    }
