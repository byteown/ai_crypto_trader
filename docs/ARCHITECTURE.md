# Архитектура: AI Crypto Trader

## Идея

Бот по расписанию забирает свечи с биржи и свежие новости. Затем он считает технические индикаторы,
оценивает сентимент новостей через LLM и просит LLM принять решение BUY / SELL / HOLD с обоснованием.
Решение проходит через риск-менеджер на жёстких правилах и исполняется брокером: виртуальным (paper)
или реальным (ccxt). Весь процесс виден в React-дашборде в реальном времени.

Ключевой принцип: **LLM советует, код решает**. Риск-менеджер всегда имеет право вето.

## Компоненты

```
                ┌──────────────┐        ┌──────────────┐
                │ React (Vite) │◄─ WS ──┤   FastAPI    │◄──── REST ────┐
                │  dashboard   │── REST►│   (api)      │               │
                └──────────────┘        └──────┬───────┘               │
                                               │ SQLAlchemy            │
                       ┌───────────────────────┼───────────────┐       │
                       ▼                       ▼               ▼       │
                ┌────────────┐          ┌────────────┐   ┌──────────┐  │
                │ PostgreSQL │          │   Redis    │   │  Ollama  │  │
                │ (данные)   │          │ broker +   │   │ /OpenAI  │  │
                └────────────┘          │ cache +    │   └────▲─────┘  │
                       ▲                │ pub/sub    │        │        │
                       │                └─────▲──────┘        │        │
                       │                      │               │        │
                ┌──────┴──────────────────────┴───────────────┴──┐     │
                │ Celery worker + Celery beat (расписание)       │─────┘
                │ fetch_candles → fetch_news → analyze → execute │
                └────────────────────────┬───────────────────────┘
                                         │ ccxt
                                         ▼
                                  Биржа (Binance)
```

| Сервис (docker-compose) | Роль |
|---|---|
| `api` | FastAPI: REST + WebSocket, управление ботами, чтение данных |
| `worker` | Celery: выполняет задачи торгового цикла |
| `beat` | Celery beat: запускает цикл раз в N минут |
| `db` | PostgreSQL |
| `redis` | брокер Celery, кэш цен, pub/sub событий для WebSocket |
| `ollama` | локальная LLM (опционально, вместо OpenAI) |
| `frontend` | React-дашборд |

## Торговый цикл (один «тик» бота)

1. **Market data**: забрать последние OHLCV-свечи через ccxt, сохранить в `candles`, положить последнюю цену в Redis.
2. **News**: забрать новости по монете (RSS / CryptoPanic API), новые статьи прогнать через LLM, получить `sentiment` от -1 до 1 и сохранить. Каждая статья анализируется только один раз.
3. **Indicators**: посчитать RSI, EMA, MACD и т.д. Это чистые функции без I/O.
4. **AI decision**: собрать контекст (индикаторы, агрегированный сентимент, текущая позиция) и получить от LLM **структурированный** ответ `{action, confidence, reasoning}`, провалидированный Pydantic. Сохранить в `signals`.
5. **Risk check**: проверить лимиты (размер позиции, макс. просадка, stop-loss, минимальный confidence, kill switch). Результат: approved или rejected с причиной.
6. **Execution**: `Broker.place_order()`. Обновить `orders`, `positions`, `balance`.
7. **Events**: опубликовать событие в Redis pub/sub. FastAPI пересылает его во фронт по WebSocket.

## Структура репозитория

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # создание FastAPI-приложения
│   │   ├── core/                # config (pydantic-settings), logging
│   │   ├── db/                  # engine, session, Base
│   │   ├── models/              # SQLAlchemy-модели
│   │   ├── schemas/             # Pydantic-схемы (вход/выход API)
│   │   ├── repositories/        # доступ к БД (запросы)
│   │   ├── api/v1/              # роутеры
│   │   ├── services/
│   │   │   ├── market_data/     # MarketDataSource (ccxt)
│   │   │   ├── indicators/      # чистые функции
│   │   │   ├── news/            # NewsSource + sentiment
│   │   │   ├── llm/             # LLMProvider: Ollama / OpenAI
│   │   │   ├── strategy/        # Strategy: RuleBased / AI
│   │   │   ├── risk/            # RiskManager
│   │   │   └── execution/       # Broker: PaperBroker / CcxtBroker
│   │   └── workers/             # celery_app, tasks, beat schedule
│   ├── migrations/              # alembic
│   ├── tests/  (unit/ integration/)
│   ├── pyproject.toml / uv.lock
│   └── Dockerfile
├── frontend/                    # React + TypeScript + Vite
├── docs/
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

## Абстракции (что показываем работодателю)

Каждая внешняя зависимость спрятана за `typing.Protocol`. Благодаря этому реализацию можно подменить
одной настройкой, а в тестах использовать фейки вместо сети:

| Интерфейс | Реализации |
|---|---|
| `Broker` | `PaperBroker` (БД), `CcxtBroker` (реальная биржа / testnet) |
| `LLMProvider` | `OllamaProvider`, `OpenAIProvider`, `FakeLLM` (тесты) |
| `MarketDataSource` | `CcxtMarketData`, `FakeMarketData` |
| `NewsSource` | `RssNewsSource`, `CryptoPanicSource` |
| `Strategy` | `RuleBasedStrategy` (EMA/RSI), `AIStrategy` |

## Модель данных (черновик)

- `bots`: id, name, symbol (`BTC/USDT`), timeframe, mode (`paper`/`live`), strategy (`rules`/`ai`), llm_provider, risk-параметры, is_active
- `paper_accounts`: bot_id, quote_balance, base_balance
- `candles`: symbol, timeframe, ts, open, high, low, close, volume. Уникальный ключ `(symbol, timeframe, ts)`
- `news_articles`: source, url (unique), title, published_at, sentiment, sentiment_reason
- `signals`: bot_id, action, confidence, reasoning, indicators (JSONB), created_at
- `risk_decisions`: signal_id, approved, reason
- `orders`: bot_id, signal_id, side, type, amount, price, status, exchange_order_id
- `positions`: bot_id, symbol, amount, avg_entry_price
- `equity_snapshots`: bot_id, ts, equity. Используется для графика PnL.
- `users`: для JWT-авторизации фронта

Деньги хранятся только как `Numeric` / `Decimal`, **никогда не float**.

## Безопасность live-режима

- Live выключен по умолчанию (`LIVE_TRADING_ENABLED=false`), ключи биржи берутся только из env.
- Сначала Binance testnet, реальные деньги только сознательно.
- Kill switch: эндпоинт или флаг, который останавливает все боты.
- Лимиты риск-менеджера применяются в любом режиме.
