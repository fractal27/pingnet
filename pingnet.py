
from threading import Thread
import subprocess
from queue import Queue
import time
import sys
import logging
import argparse
import configparser
import os

parser=argparse.ArgumentParser()

#get the time_counter with the maximum precision
default_timer = time.time if sys.platform!='win32' else time.perf_counter

start_init=default_timer()


parser.add_argument("-l","--logfile",default=None,
                    help='adds an handler on the logger.')
parser.add_argument("-t","--threads-number",type=int,default=100,
                    help='il numero di thread usati nella queue.')
parser.add_argument("-c", "--configuration", type=str,
                    help='ping configuration.',default='DEFAULT')
parser.add_argument("-r","--repeat",action="store_true",
                    help='repeats the control infinitely many times')
parser.add_argument("-p", "--pause", type=float,default=5,
                    help="scan delay.")
parser.add_argument("-!t", "--no-topography", action="store_true",
                    help='removes scan topology.')
parser.add_argument("-w","--webmode",action="store_true",
                    help='produces an html file')
parser.add_argument("-v","--verbose",action="store_true",
                    help="verbose output.")
parser.add_argument("-s","--save-time-dataframe",action="store_true",
                    help="saves dataframe of execution times(csv,html e xmls).")
parser.add_argument("-n","--gethostnames",action="store_true",
                    help="gets the hostnames by their ip.")

args=parser.parse_args()


level = 10*(2-args.verbose)
logging.basicConfig(format='[ %(asctime)s ] %(levelname)s: %(message)s',
                    datefmt='%H:%M:%S',level=level)
logger=logging.getLogger(__name__)
if args.logfile:
  #add a file handler
  fh=logging.FileHandler(' '.join(args.logfile))
  fh.setLevel(level)
  formatter=logging.Formatter('[ %(asctime)s ] %(levelname)s: %(message)s')
  fh.setFormatter(formatter)
  logger.addHandler(fh)
repeat=args.repeat
show_topography=not args.no_topography
webmode=args.webmode
pause=args.pause
num_threads=args.threads_number
st=args.save_time_dataframe
gethostnames=args.gethostnames

#ping configuration

config=configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__name__),'config.ini'))

if not args.configuration=='DEFAULT':config_section=config[args.configuration]
else:config_section=config.defaults()
logger.debug("setting ping configuration %s"%'\n'.join(map(lambda x:f"{x[0]}: {x[1]}",config_section.items())))
webmode_timeformat=config_section.get("webmode.timeformat","%H:%M:%S %d/%m/%Y")
if webmode_timeformat == '':
  webmode_timeformat="%H:%M:%S %d/%m/%Y"
class control_type():
  _None = 0
  Always_active = 1
  to_switch_off = 2

def _getnum(items):
  item=items[0].split(".")[2]
  if item=='from':return 0
  elif item=='to':return 1
  elif item=='name':return 2
  elif item=='type':return 3
  else:return 4

def gnt(string):
  return int(string.split(".")[1])

def splitby(items:list[tuple[str,str]]):
  final={}
  for key,val in items:
    if key.split(".")[1] not in final:
      if final.get(int(key.split(".")[1])):
        final[int(key.split(".")[1])].append(val)
      else:
        final[int(key.split(".")[1])]=[val]
  final=list(map(lambda lst:[*map(int,(lst[0],lst[1])),lst[2],control_type().__getattribute__(lst[3])],list(final.values())))
  return final
p_reti=dict([x for x in config_section.items() if x[0].startswith('networks.')])
p_reti=dict(sorted(p_reti.items(),key=_getnum))

networks=splitby(list(p_reti.items())[:-1])

ipv4base=list(p_reti.values())[-1]
num_pcs=sum(list(map(lambda x:x[1],networks)))

addresses,desc_pc,scan_results,pc_type = [],[],[],[]

for idx in range(num_pcs):
  addresses.append(idx)
  desc_pc.append(idx)
  scan_results.append(idx)
  pc_type.append(idx)

num_pc = 0
results = {}

for network in networks:
  for index in range(network[1]):
    #a = "%s%d"% (string_base_ip, rete[0] + index)
    addresses[num_pc] = "{}{}".format(ipv4base, network[0] + index)
    if network[1] == 1:
      desc_pc[num_pc] = network[2]
    else:
      desc_pc[num_pc] = "{} {}".format(network[2], index+1)
    pc_type[num_pc] = network[3]
    num_pc+=1

queue = Queue()

#wraps system ping command
if sys.platform=='win32':
  def pinger(i, q):
    """Pings subnet"""
    while 1:
      idx = q.get()
      ip = addresses[idx]
      logger.debug(f"Thread {i}: Pinging {ip}")
      ret = subprocess.call(f"ping -n 1 -w 500 -l 1 {ip}",
        shell=True,
        stdout=open('NUL', 'w'),
        stderr=subprocess.STDOUT)
      if not ret:
        logger.debug(f"{ip}: is alive")
        scan_results[idx] = "on"
      else:
        logger.debug(f"{ip}: did not respond")
        scan_results[idx] = "off"
      q.task_done()
else:
  def pinger(i, q):
    """Pings subnet"""
    while 1:
      idx = q.get()
      ip = addresses[idx]
      logger.debug("Thread {}: Pinging {}".format(i, ip))
      ret = subprocess.call(f"ping -c 1 {ip}",
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.STDOUT)
      if ret == 0:
          logger.debug("{}: is alive".format(ip))
          scan_results[idx] = "on"
      else:
          logger.debug("{}: did not respond".format(ip))
          scan_results[idx] = "off"
      q.task_done()

end_init=default_timer()
logger.debug("inizializzation ended in %f second(s)"%(end_init-start_init))

logger.debug("creating thread")
for i in range(num_threads):
  worker = Thread(target=pinger, args=(i, queue))
  worker.daemon = True
  worker.start()
logger.debug("threads created")

while 1:

    logger.info("Start performing check")
    start_control=default_timer()

    for idx in range(num_pcs):
      queue.put(idx)
    queue.join()

    end_control=default_timer()
    logger.debug("check ended.")
    logger.debug("Starting visualization.")
    start_visualization=default_timer()

    if not webmode:
      logger.debug("Visualizing result..")
      accesi = scan_results.count("acceso")
      for addr,desc,res in zip(addresses,desc_pc,scan_results):
        if res == "on":
          logger.info(f" {addr} {desc} {res}")
      logger.info(f"Open PCs :{accesi}/{num_pcs}\n")

    if show_topography:
      logging.debug("Visualizing topology of pcs...")
      for network in networks:
        _str = "{}{}:{} =>".format(ipv4base, network[0], network[2])
        for index in range(network[1]):
          a = "".join(map(str,(ipv4base, network[0]+index)))
          idx = addresses.index(a)
          _str += ' X' if scan_results[idx] == "on" else ' .'
        logger.info(f"topography: {_str}")
      # controllo in base alla tipologia
      logger.info("Visualizing tipology of PCs..")
      for scan_res,typ,addr,pc_desc in zip(scan_results,pc_type,addresses,desc_pc):
        if scan_res != "on" and typ == control_type.Always_active:
          logging.info(' '.join(("*** WARNING:DEVICE IS OFF *** =>",addr, pc_desc, scan_res)))
      for scan_res,typ,addr,pc_desc in zip(scan_results,pc_type,addresses,desc_pc):
        if (scan_res == "on" and typ == control_type.to_switch_off):
          logging.info(' '.join(("--- TURN OFF BEFORE LEAVING --- =>",addr,pc_desc,scan_res)))
    if gethostnames:
      from socket import gethostbyaddr,herror
      logging.info("Showing hostnames...")
      addrs=[x for x,r in zip(addresses,scan_results) if r=='on']
      _q=Queue(len(addrs))
      def scan_hostnames(_addr,q):
        try:
          idx=q.get()
          logging.info(f"{_addr}: {gethostbyaddr(addrs[idx])[0]}")
        except herror:
          logging.debug(f"{addresses[idx]}: Unknown hostname")
        finally:
          logging.debug(f"{idx}th Thread terminated.")
          q.task_done()
      threads=[]
      for i,addr in enumerate(addrs):
        t=Thread(target=scan_hostnames,args=(addr,_q))

        t.start()
      for i,addr in enumerate(addrs):
        _q.put(i)
      _q.join()
    if webmode:
        logger.warning("webmode is on, visualization will be skipped.")
        logger.debug("building webfile.")
        refreshtime = pause if pause>0 else 2
        webpage = [f'<html><head><meta http-equiv="refresh" content="{refreshtime}"></head><body>',"Last update: {}".format(time.strftime(webmode_timeformat)),"<table border=1 width=100%>"]
        
        for network in networks:
          num_group_pcs = 1
          webstr ="<tr><td>{}{}</td><td>{}</td>".format(ipv4base, network[0], network[2])
          _str = "{}{}:{} =>".format(ipv4base, network[0], network[2])
          webstr2 = ""
          for index in range(network[1]):
            idx = addresses.index(f"{ipv4base}{network[0]+index}")
            colour = "black"
            # if (pc_type[idx] == tipo_controllo.Sempre_acceso):
            if pc_type[idx] == 1:
                if scan_results[idx] == "on":
                  backgroundcolour,colour = "blue","white"
                else:
                  backgroundcolour = "red"
                  _str += ' X'
            else:
                if scan_results[idx] == "on":backgroundcolour = "lightgreen"
                else:backgroundcolour = "yellow"
            _str += ' .'
            webstr2 = ('%s<td style="background: %s; color: %s; width: 25px;">%d</td>' % (webstr2, backgroundcolour, colour, num_group_pcs))
            num_group_pcs += 1
          webpage.extend([webstr,webstr2,"<tr>"])
        webpage.append("</table></body></html>")
        result=''.join(webpage)
        if int(config_section.get("webmode.prettify")):
          # using lxml instead of BeautifulSoup is .2s faster
          from lxml import etree, html
          document_root = html.fromstring(result)
          result=etree.tostring(document_root, pretty_print=True, method="html").decode()
        with open("netstatus.html","w") as out_file:
          out_file.write(result)
    end_visualizzazione = default_timer()
    if not repeat:break
    if not webmode:
      logging.info("Waiting %.2f secondi" % pause)
      time.sleep(pause)
end=default_timer()
# creating times dataframe
if st:
  import pandas as pd
  logger.debug("creating dataframe")
  times = pd.DataFrame({"total":[end-start_init],"initialization":[end_init-start_init],"control":[end_control-start_control],"visualizzazione":[end_visualizzazione-start_visualization]})
  logger.debug(f"{times=!r}")
  logger.debug("getting current directory")
  def getfilepath(filename):
    return os.path.abspath(os.path.join(config_section.get("times.path"),filename))
  logger.info("exporting dataframe...")
  logger.debug("saving dataframe to csv")
  try:
    csv_path=getfilepath("times.csv")
    if not os.path.exists(csv_path):
      times.to_csv(csv_path,index=False)
    else:
      df=pd.read_csv(csv_path)
      df=pd.concat([df,times])
      df.to_csv(csv_path,index=False)
    logger.debug("saving dataframe to html")
    html_path=getfilepath("times.html")
    if not os.path.exists(html_path):
      times.to_html(html_path,index=False)
    else:
      df=pd.read_html(html_path)
      df.append(times)
      df=pd.concat(df)
      df.to_html(html_path,index=False)
    logger.debug("saving dataframe to excel")
    excel_path=getfilepath("times.xlsx")
    if not os.path.exists(excel_path):
      times.to_excel(excel_path,index=False)
    else:
      df=pd.read_excel(excel_path)
      df=pd.concat([df,times])
      df.to_excel(excel_path,index=False)
  except Exception as e:
    logger.error("Error accurred while exporting dataframe: {}".format(e))
    logger.error(e)
  logger.info("times succesfully exported!")
logger.info("Finished.")

