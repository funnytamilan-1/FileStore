# Telegram FileStore + URL Shortener

A modular Telegram file distribution bot using Python 3.11+, Pyrogram 2.x, MongoDB/Motor and aiohttp.

## Features

- HMAC-signed URL-safe deep links with optional expiration
- Single, batch and custom-batch links
- Multiple private storage channels and primary storage
- Force Subscription and join-request tracking
- Persistent admins, bans and premium users
- Async URL shortener with failure handling and click statistics
- Broadcast with bounded concurrency and FloodWait handling
- Auto-delete, protected content and rate limiting
- MongoDB indexes and pagination-ready queries
- aiohttp health endpoints
- Docker, Procfile and Python 3.11 runtime files

## Install

Copy .env.example to .env, fill the required values, then run:

    python -m pip install -r requirements.txt
    python main.py

Required environment variables:

    API_ID
    API_HASH
    BOT_TOKEN
    OWNER_ID
    DATABASE_URL
    DATABASE_NAME

Optional primary storage:

    CHANNEL_ID

## Storage

Add the bot as an administrator of your private storage channel and set CHANNEL_ID.

    /addstorage <channel_id>
    /removestorage <channel_id>
    /storages

## Links

Reply to a stored message:

    /genlink

Batch:

    /batch <channel_id> <start_id> <end_id>

Custom:

    /custom_batch <channel_id> <id|start-end> ...

Generated payloads are HMAC authenticated and checked against enabled storage channels before delivery.

## Force Subscription

    /addchnl <channel_id> [invite_link] [request_join]
    /delchnl <channel_id>
    /listchnl
    /fsub_mode
    /delreq

## Shortener

Configure SHORTLINK_ENABLED, SHORTLINK_URL and SHORTLINK_API. The async provider adapter accepts shortenedUrl, shorturl, shortened_url or url in a JSON response.

    /setshortener <url> <api_key>
    /removeshortener
    /shortener
    /count

Provider failures are logged and do not expose stack traces to users.

## Premium and moderation

    /addpremium <user_id> [days]
    /remove_premium <user_id>
    /premium_users
    /myplan
    /ban <user_id>
    /unban <user_id>
    /banlist
    /add_admin <user_id>
    /deladmin <user_id>
    /admins

## Broadcast and administration

    /broadcast
    /dbroadcast
    /pbroadcast
    /dlt_time <seconds>
    /check_dlt_time
    /users
    /stats
    /settings
    /search <filename or caption>

## Health

    GET /
    GET /health
    GET /ping

The aiohttp server binds to 0.0.0.0:$PORT.

## Security

Secrets belong in environment variables. Do not commit .env. Deep-link payloads use HMAC verification and optional TTL. Admin commands and callbacks verify Telegram user IDs. MongoDB operations are asynchronous. User-facing errors are generic while internal failures are logged.

## Deployment

Docker:

    docker build -t filestore .
    docker run --env-file .env filestore

Render, Railway and VPS deployments can run Python 3.11 with python main.py and platform-managed environment variables.

## Testing

    PYTHONPATH=. pytest -q
    python -m compileall -q .

Live Telegram, MongoDB and shortener integration requires real credentials and is not part of the local unit-test suite.
