import asyncio, socket, logging, os, datetime
from time import strftime, localtime

logging.basicConfig(format='%(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# IMPORTANT: CHANGE THESE BEFORE RUNNING!!!!!!!!!!!!!
# I SWEAR TO FUCKING GOD IF YOU DON'T, I'M GOING TO KILL YOU IN YOUR FUCKING SLEEP
gophsrc = 'C:/gopher'
hostname = 'example.com'
host = '127.0.0.1'
port = 7000

import asyncio, socket, pathlib
from gtype import find_type

# execute process without general code execution being halted
async def ex(*exc):
    proc = await asyncio.create_subprocess_shell(
        *exc,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if stderr: return stderr
    else: return stdout

async def expy(script, query, host, cwd):
    proc = await asyncio.create_subprocess_shell(
        'python3', script,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
        env = {'GOPHER_QUERY': query, 'GOPHER_REQUEST_HOST': host},
        cwd = cwd
        )
    stdout, stderr = await proc.communicate()
    if stderr: return stderr
    else: return stdout

# execute custom POLscript
async def excscript(script, client, selector, reqer):
    loop = asyncio.get_event_loop()
    if type(script) == bytes: script = script.decode('latin1')
    s = script.splitlines()
    b = ''
    for i in s:
        if i.startswith('\\EXC'):
            c = i.split('\t',2)
            a = await asyncio.gather(ex(c[1]))
            for i2 in a[0].splitlines():
                if len(c) >= 3: b += '%s%s\t%s\r\n' % (i.removeprefix('\\EXC')[0], i2.decode('latin1'), c[2])
                else: b += '%s%s\t\t\t\r\n' % (i.removeprefix('\\EXC')[0], i2.decode('latin1'))
        else:
            b += i + '\r\n'
    await loop.sock_sendall(client, b.encode('latin1'))
    do_log(selector, len(b), reqer)
    client.close()

# selector processing
async def process(client, selector):
    reqer = client.getpeername()
    loop = asyncio.get_event_loop()
    s = selector[:-2].decode('latin1').rstrip('/')
    query = ''
    if '\t' in s:
        query = s.split('\t',1)[1]
        s = s.split('\t',1)[0]
        print(query, s)
    f = gophsrc + s
    print(f)
    if os.path.isfile(f+'/menu.pol'):
        with open(f+'/menu.pol', 'rb') as f: await excscript(f.read(), client, s, reqer)
    elif os.path.isdir(f):
        fl = [fi for fi in os.listdir(f) if os.path.isfile(f + '/' +fi)]
        dr = [fi for fi in os.listdir(f) if os.path.isdir(f + '/' + fi)]
        snd = b'i dir listing for %s\t\t\t\r\n\r\n' % (s.encode('latin1') if s else b'/')
        #await loop.sock_sendall(client, b'i dir listing for %s\t\t\t\r\n\r\n' % (s.encode('latin1') if s else b'/'))
        for l in dr:
            t = '1'
            r = (t, l, s, l, hostname, str(port))
            snd += ('%s%s\t%s/%s\t%s\t%s\r\n' % r).encode('latin1')
        for l in fl:
            t = find_type(pathlib.Path(l).suffix)
            r = (t, l, s, l, hostname, str(port))
            snd += ('%s%s\t%s/%s\t%s\t%s\r\n' % r).encode('latin1')
        do_log(s, len(snd))
        await loop.sock_sendall(client, snd)
        client.close()
    elif os.path.isfile(f):
        if f.endswith('.pol'):
            await excscript(f.read(), client, s, reqer)
        elif f.endswith('.py'):
            await expy(f, query, reqer, f.rpartition('/')[0])
        else:
            with open(f, 'rb') as f:
                snd = f.read()
                await loop.sock_sendall(client, snd)
                do_log(s, len(snd), reqer)
                client.close()
    else:
        client.close()
    pass

def do_log(request, length, req):
    current_time = datetime.datetime.now()
    lg = (
        req, strftime('%d/%b/%Y:%H:%M:%S %z'), request if request else '/', length
        )
    logger.info('%s - - [%s] "%s" %s' % lg)

# client bootstrap
async def handle_client(client):
    loop = asyncio.get_event_loop()
    request = b''
    while not request.endswith(b'\r\n'):
        request += await loop.sock_recv(client, 1)
    await asyncio.gather(process(client, request))


# init server
async def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    logger.info('Polly server listening on %s:%s' % (host, str(port)))
    server.listen(0)
    server.setblocking(False)

    loop = asyncio.get_event_loop()

    while True:
        client, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(client))

# run the bastard
asyncio.run(run_server())