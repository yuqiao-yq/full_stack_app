# full_stack_app

Vue + Flask + MySQL 的全栈练习项目。

## 项目结构

- `fe`：Vue 3 + Vite 前端
- `be`：Flask 后端
- `MySQL`：使用 Docker 启动

## 启动前准备

### 1. 启动 MySQL

建议先检查 Docker 是否可用：

```bash
docker --version
docker info
```

如果 `docker info` 报错 `Cannot connect to the Docker daemon`，说明 Docker 后台还没启动。

当前环境如果使用 OrbStack，可以先执行：

```bash
open -a OrbStack
```

如果 OrbStack 启动时提示权限错误，可先修复：

```bash
sudo chown -R $USER ~/Library/Group\ Containers/HUAQ24HBR6.dev.orbstack/data
```

然后再次检查：

```bash
docker info
```

再检查本机是否已经存在名为 `full-stack-mysql` 的容器：

```bash
docker ps -a
```

如果容器已经存在，不要重复执行 `docker run`，直接启动即可：

```bash
docker start full-stack-mysql
```

如果你还没有创建 MySQL 容器，建议使用带 volume 持久化的方式：

```bash
docker run --name full-stack-mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=full_stack_app \
  -p 3306:3306 \
  -v full_stack_mysql_data:/var/lib/mysql \
  -d mysql:8
```

如果容器已经创建过，直接启动：

```bash
docker start full-stack-mysql
```

启动成功后可再次确认：

```bash
docker ps
```

如果你想确认当前 MySQL 容器是否已经挂了 volume 持久化，可以执行：

```bash
docker inspect full-stack-mysql --format '{{json .Mounts}}'
```

输出中如果包含：

- `"Type":"volume"`
- `"Destination":"/var/lib/mysql"`

就说明 MySQL 数据已经持久化。

### 2. 后端环境变量

后端会自动读取 `be/.env`，当前默认配置如下：

```env
FLASK_DEBUG=true
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=full_stack_app
JWT_SECRET=dev-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN_HOURS=24
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
IGDB_AUTH_URL=https://id.twitch.tv/oauth2/token
IGDB_BASE_URL=https://api.igdb.com/v4
```

如果你要修改数据库账号或密码，更新 `be/.env` 即可。

如果你要启用“我的评价”中的游戏搜索功能，还需要在 `be/.env` 中填写 IGDB/Twitch 凭证：

- `IGDB_CLIENT_ID`
- `IGDB_CLIENT_SECRET`

申请方式：

1. 打开 [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. 创建一个新的应用
3. 拿到 `Client ID`
4. 在应用详情里生成或查看 `Client Secret`

后端会先通过 Twitch OAuth 获取 access token，再代理请求 IGDB 的游戏搜索接口。
如果凭证未配置，`/api/games/search` 会返回明确错误提示，而不会直接崩溃。

## 启动项目

建议按照下面顺序启动。

### 1. 启动后端

进入后端目录：

```bash
cd be
```

首次安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

后续启动：

```bash
cd be
source .venv/bin/activate
python3 app.py
```

后端默认地址：

```text
http://127.0.0.1:3000
```

### 2. 启动前端

新开一个终端：

```bash
cd fe
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

## 接口代理

前端开发环境已配置 Vite 代理：

- 前端请求 `/api/*`
- 自动转发到 `http://localhost:3000`

如果后端端口变了，可以通过 `fe` 启动前设置：

```bash
VITE_API_PROXY_TARGET=http://localhost:8080 npm run dev
```

## 登录与注册

- 注册用户数据保存在 MySQL 的 `users` 表中
- 密码使用哈希加密存储，不是明文
- JWT 默认有效期为 `24` 小时

## 游戏搜索与评价

- “我的评价”支持通过第三方游戏数据库搜索游戏信息
- 当前后端通过 Flask 代理 `IGDB API`
- 前端不会直接暴露第三方 API key
- 搜索结果会带回封面图、平台、类型、评分、发布日期、简介摘要等基础信息
- 当你提交评价时，会把这些游戏信息快照和你的本地评价一起写入 MySQL

启用前请确认：

```env
IGDB_CLIENT_ID=你的TWITCH_CLIENT_ID
IGDB_CLIENT_SECRET=你的TWITCH_CLIENT_SECRET
```

评价数据会保存在本地数据库的 `game_reviews` 表中。

## 当前目录结构

后端已按功能模块整理为：

```text
be/
  core/
  modules/
    auth/
    games/
      providers/
    reviews/
```

前端已按应用入口与功能模块整理为：

```text
fe/src/
  app/
  router/
  features/
    auth/
    games/
    home/
    profile/
    reviews/
    shared/
```

## 常见命令

查看 MySQL 容器状态：

```bash
docker ps
```

查看后端用户数据：

```bash
docker exec -it full-stack-mysql mysql -uroot -p123456
```

进入 MySQL 后执行：

```sql
USE full_stack_app;
SELECT id, username, display_name, password_hash, created_at FROM users;
SELECT id, user_id, game_name, status, user_score, created_at FROM game_reviews;
```