import asyncio, socket, logging, os, datetime, shlex
from time import strftime, localtime
from gbytes import format_size

logging.basicConfig(format='%(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# IMPORTANT: CHANGE THESE BEFORE RUNNING!!!!!!!!!!!!!
# I SWEAR TO FUCKING GOD IF YOU DON'T, I'M GOING TO KILL YOU IN YOUR FUCKING SLEEP
gophsrc = 'C:/gopher'
hostname = 'aim.gaysexonline.net'
host = '0.0.0.0'
port = 70

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

async def expy(script, query, reqhost, cwd, client, selector):
    loop = asyncio.get_event_loop()
    #print('executing script: %s, host: %s, query: %s, cwd: %s' % (script, host, query, cwd))
    proc = await asyncio.create_subprocess_exec(
        'python3', script,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
        env = os.environ.copy() | {'GOPHER_QUERY': query, 'GOPHER_REQUEST_HOST': reqhost},
        cwd = cwd
        )
    stdout, stderr = await proc.communicate()
    if stderr:
        print(stderr.decode())
        b = stdout + b'3 -- execution was halted due to an exception being raised --\r\ni' + b'\r\ni'.join(stderr.splitlines())
    else: b = stdout
    await loop.sock_sendall(client, b)
    do_log(selector, len(b), reqhost, query)
    client.close()

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
    do_log(selector, len(b), reqer, '')
    client.close()

# selector processing
async def process(client, selector):
    reqer = client.getpeername()[0]
    loop = asyncio.get_event_loop()
    s = selector[:-2].decode('latin1').rstrip('/')
    query = ''
    if '\t' in s:
        query = s.split('\t',1)[1]
        s = s.split('\t',1)[0]
    elif '?' in s:
        query = s.split('?',1)[1]
        s = s.split('?',1)[0]
    if '..' in s: client.close()
    else:
        f = gophsrc + s
        if os.path.isfile(f+'/menu.pol'):
            with open(f+'/menu.pol', 'rb') as f: await excscript(f.read(), client, s, reqer)
        elif os.path.isdir(f):
            fl = [fi for fi in os.listdir(f) if os.path.isfile(f + '/' +fi)]
            dr = [fi for fi in os.listdir(f) if os.path.isdir(f + '/' + fi)]
            snd = b'idirectory listing for %s\t\t\t\r\ni----------------------\t\t\t\r\n' % (s.encode('latin1') if s else b'/')
            #await loop.sock_sendall(client, b'i dir listing for %s\t\t\t\r\n\r\n' % (s.encode('latin1') if s else b'/'))
            for l in dr:
                t = '1'
                probe = os.stat(f + '/' + l)
                form = l[:32].ljust(32, ' ') + ' ' + '-'[:8].ljust(8, ' ') + strftime('%d-%b-%Y %I:%M', localtime(probe.st_mtime))
                r = (t, form, s, l, hostname, str(port))
                snd += ('%s%s\t%s/%s\t%s\t%s\r\n' % r).encode('latin1')
            for l in fl:
                t = find_type(pathlib.Path(l).suffix)
                probe = os.stat(f + '/' + l)
                # TODO: oh no
                form = l[:32].ljust(32, ' ') + ' ' + format_size(probe.st_size)[:8].ljust(8, ' ') + strftime('%d-%b-%Y %I:%M', localtime(probe.st_mtime))
                r = (t, form, s, l, hostname, str(port))
                snd += ('%s%s\t%s/%s\t%s\t%s\r\n' % r).encode('latin1')
            do_log(s, len(snd), reqer, query)
            await loop.sock_sendall(client, snd)
            client.close()
        elif os.path.isfile(f):
            if f.endswith('.pol'):
                with open(f, 'r') as f: await excscript(f.read(), client, s, reqer)
            elif f.endswith('.py'):
                await expy(f, query, reqer, f.rpartition('/')[0], client, s)
            else:
                with open(f, 'rb') as f:
                    snd = f.read()
                    await loop.sock_sendall(client, snd)
                    do_log(s, len(snd), reqer, query)
                    client.close()
        else:
            client.close()

def do_log(request, length, req, query):
    current_time = datetime.datetime.now()
    lg = (
        req, strftime('%d/%b/%Y:%H:%M:%S %z'), request if request else '/', length, query
        )
    logger.info('%s - - [%s] "%s" %s "%s"' % lg)

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