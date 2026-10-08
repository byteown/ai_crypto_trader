# Роадмап

Как работаем: я даю шаг (цель, что изучить, критерии готовности). Ты реализуешь, коммитишь и пишешь «готово».
Я проверяю код и тесты, даю замечания, после этого переходим к следующему шагу.

После каждой фазы проект **рабочий** и его можно показать.

## Фаза 0. Фундамент
- [x] 0.1 git, uv, скелет FastAPI, `/health`, config через pydantic-settings, первый тест, ruff
- [x] 0.2 Docker: Dockerfile для backend, docker-compose (api + postgres + redis)
- [x] 0.3 GitHub-репозиторий + GitHub Actions CI (ruff + pytest)

## Фаза 1. База данных
- [x] 1.1 SQLAlchemy 2.0 (async) + сессия как FastAPI-зависимость
- [ ] 1.2 Alembic, первая миграция: модель `bots`
- [ ] 1.3 CRUD API для ботов (schemas → repository → router)
- [ ] 1.4 Интеграционные тесты с отдельной тестовой БД (фикстуры pytest)

## Фаза 2. Рыночные данные и фоновые задачи
- [ ] 2.1 ccxt: сервис `MarketDataSource`, модель `candles`, upsert свечей
- [ ] 2.2 Celery + Redis: worker, задача `fetch_candles`
- [ ] 2.3 Celery beat: периодический запуск, кэш последней цены в Redis
- [ ] 2.4 Эндпоинт `GET /bots/{id}/candles`, тесты с `FakeMarketData`

## Фаза 3. Paper trading без AI ← первый «живой» бот
- [ ] 3.1 Индикаторы (EMA, RSI, MACD) как чистые функции, TDD
- [ ] 3.2 `PaperBroker`: аккаунт, ордера, позиции, комиссия, Decimal
- [ ] 3.3 `RuleBasedStrategy` (пересечение EMA + фильтр RSI)
- [ ] 3.4 `RiskManager`: размер позиции, stop-loss, макс. просадка, kill switch
- [ ] 3.5 Задача `run_bot_tick`: свечи → стратегия → риск → брокер, `equity_snapshots`

## Фаза 4. AI
- [ ] 4.1 `LLMProvider` Protocol + `OllamaProvider` + `OpenAIProvider`, выбор через конфиг
- [ ] 4.2 Структурированный ответ (JSON → Pydantic), ретраи, таймауты, fallback на HOLD
- [ ] 4.3 `AIStrategy`: промпт с индикаторами и позицией, сохранение reasoning в `signals`
- [ ] 4.4 Новости: `NewsSource` (RSS / CryptoPanic), дедупликация по url
- [ ] 4.5 Сентимент новостей через LLM (отдельная задача, кэш), подмешивание в контекст AIStrategy
- [ ] 4.6 Тесты с `FakeLLM`, логирование стоимости и латентности LLM-вызовов

## Фаза 5. Realtime + авторизация
- [ ] 5.1 Redis pub/sub события из worker, WebSocket-эндпоинт в FastAPI
- [ ] 5.2 JWT-авторизация (регистрация / логин, защищённые роуты)

## Фаза 6. Фронтенд (React + TS + Vite)
- [ ] 6.1 Скелет: Vite, роутинг, TanStack Query, API-клиент, логин
- [ ] 6.2 Список ботов, создание / редактирование, старт / стоп
- [ ] 6.3 Страница бота: свечной график (lightweight-charts) + маркеры сделок
- [ ] 6.4 Лента сигналов с reasoning от AI, позиции, график equity
- [ ] 6.5 Live-обновления через WebSocket, фронт в docker-compose

## Фаза 7. Live-торговля
- [ ] 7.1 `CcxtBroker` против Binance testnet, тот же интерфейс `Broker`
- [ ] 7.2 Защиты: флаг `LIVE_TRADING_ENABLED`, синхронизация статусов ордеров, обработка ошибок биржи

## Фаза 8. Полировка для портфолио
- [ ] 8.1 Бэктест RuleBasedStrategy на исторических свечах (метрики: PnL, max drawdown, win rate)
- [ ] 8.2 README: диаграмма, скриншоты / GIF, «как запустить одной командой», решения и компромиссы
- [ ] 8.3 Покрытие тестами, structured logging, финальная чистка
