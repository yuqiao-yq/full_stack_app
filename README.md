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
```

如果你要修改数据库账号或密码，更新 `be/.env` 即可。

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
```