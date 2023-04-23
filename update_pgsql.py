from dataclasses import dataclass, replace
from dotenv import load_dotenv, find_dotenv
import os
import psycopg2


@dataclass
class Tunnel:
    name: str = ''
    t: str = ''
    lvl: str = ''
    msg: str = ''
    obj: str = ''
    addr: str = ''
    url: str = ''


load_dotenv(find_dotenv())
SYSLOG = '/var/log/syslog'
#SYSLOG = 'host.syslog.log'


def update_tunnels(tunnels:dict):
    sql = '''INSERT INTO ngtunnel (name, t, url, addr) VALUES (%s, %s, %s, %s) 
             ON CONFLICT (name, t) DO NOTHING;
        '''
    conn = None
    try:
        conn = psycopg2.connect(
            user    =os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host    =os.getenv("DB_HOST"),
            port    =os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )
        cur = conn.cursor()
        # update to PSQL DB
        for tn_name, tn in tunnels.items():
            cur.execute(sql, (tn_name, tn.t, tn.url, tn.addr))
            # print(cur.statusmessage, tn)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return

def main():
    tunnels = {}
    with open(SYSLOG) as f:
        for line in f:
            if all([w in line for w in ['started tunnel', 'ngrok.io']]):
                tunnel_desc = line.strip().split(': ')[1]
                tn = Tunnel()
                for kv in tunnel_desc.split():
                    if '=' in kv:
                        k, v = kv.split('=')
                        tn = replace(tn, **{k: v})

                tunnels.update({tn.name: tn})

    update_tunnels(tunnels)

if __name__ == '__main__':
    main()