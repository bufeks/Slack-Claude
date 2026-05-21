# Slack-Claude

Slack未返信メンション検出ツール - 自分宛のメンションで返信していないものを洗い出します。

## 機能

- **未返信メンション検出**: 過去N日間の自分宛メンションをスキャンし、返信していないものをリストアップ
- **定期通知Bot**: 設定した間隔で未返信メンションをチェックし、Slackに通知

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Slack Appの作成

1. [Slack API](https://api.slack.com/apps) でAppを作成
2. OAuth & Permissions で以下のスコープを追加:

**Bot Token Scopes:**
- `channels:history` - パブリックチャンネルのメッセージ読み取り
- `channels:read` - チャンネル一覧の取得
- `chat:write` - メッセージの送信
- `groups:history` - プライベートチャンネルのメッセージ読み取り
- `groups:read` - プライベートチャンネル一覧の取得
- `im:history` - DMのメッセージ読み取り
- `im:read` - DM一覧の取得
- `mpim:history` - グループDMのメッセージ読み取り
- `mpim:read` - グループDM一覧の取得
- `users:read` - ユーザー情報の取得

**User Token Scopes (推奨):**
User Tokenを使用すると、より広範囲のメッセージにアクセスできます。

3. Appをワークスペースにインストール
4. Bot TokenまたはUser Tokenをコピー

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_TOKEN=xoxp-your-user-token
SLACK_USER_ID=U0123456789
NOTIFICATION_CHANNEL_ID=C0123456789
CHECK_INTERVAL_MINUTES=60
```

**User IDの確認方法:**
- Slackで自分のプロフィールを開く → 「...」→「メンバーIDをコピー」

## 使い方

### 単発で未返信メンションを確認

```bash
python unreplied_mentions.py
```

### Botとして定期実行

```bash
python bot.py
```

## サーバーで常駐させる (Docker)

### 1. サーバーにクローン

```bash
git clone https://github.com/bufeks/Slack-Claude.git
cd Slack-Claude
```

### 2. 環境変数を設定

```bash
cp .env.example .env
nano .env  # トークン等を入力
```

### 3. 起動

```bash
# バックグラウンドで起動
docker compose up -d

# ログ確認
docker compose logs -f

# 停止
docker compose stop

# 再起動
docker compose restart
```

サーバー再起動後も自動で立ち上がります。

## ライセンス

MIT
