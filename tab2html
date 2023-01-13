#!/usr/bin/python3

import argparse, jinja2, logging, markdown, os, re, requests, shutil
import subprocess, sys
from os.path import exists

parser = argparse.ArgumentParser(
    description="convert discourse RAD parser document to HTML",
    epilog="--------")
parser.add_argument("-i", type=str, default="stdin",metavar="MD_FILENAME",
                   help="input markdown filename (default: stdin)")
parser.add_argument("-o", type=str, default="stdout", metavar="HTML_FILENAME",
                   help="output html filename (default: stdout)")
parser.add_argument("-t", type=str, metavar="TMPL_FILENAME",
                    help="output html template filename")
parser.add_argument("-l", action="count", help="increase log levels")
parser.add_argument("-L", type=str, default="/tmp/tab2html.log",
                    metavar="LOG_FILENAME",
                    help="log filename (default: /tmp/tab2html.log)")
parser.add_argument("-s", action='store_true',
                    help="do not process images")
parser.add_argument("version", type=str, 
                    help="version to include (must match tab value & case)")
parser.add_argument("view", type=str, 
                    help="view to include (must match tab value & case)")
parser.add_argument("title", type=str,
                    help="title of html document (quoted)")
args = parser.parse_args()

loglevel = logging.WARNING
if args.l == 1:
    loglevel = logging.INFO
elif args.l == 2:
    loglevel = logging.WARNING
elif args.l == 3:
    loglevel = logging.ERROR
elif args.l == 4:
    loglevel = logging.CRITICAL
elif args.l == 5:
    loglevel = logging.DEBUG

logging.basicConfig(filename=args.L,level=loglevel,format='%(asctime)s %(levelname)s %(message)s')

logging.info('\n-------------- new run started -----------------')
logging.info('input file: %s', args.i)
logging.info('output file: %s', args.o)

logging.info('attempting to read input file')
if args.i == "stdin":
    inbuf = sys.stdin.read()
else:
    try:
        mdfile = open(args.i, "r")
    except:
        logging.warning('could not open input file %s: aborting',
                        args.i)
        print('could not open input file',args.i,': aboring')
        sys.exit(-1)
    rawinbuf = mdfile.read()
    mdfile.close()

logging.info('successfully read input file')

logging.info('removing any sections marked as not for html processing')
inbuf = ""
liveblobs = re.split('<!-- nohtml',rawinbuf)
for x in liveblobs:
    logging.debug('processing live blob:\n' + x + "\n")
    if x.find("begin-nohtml") > 0:
        logging.debug('   live blob is not for html processing')
        continue
    elif x.find("end-nohtml") > 0:
        inbuf += x.split(">")[1]
    else:
        inbuf += x

logging.info('splitting file into blobs')
blobs = re.split('\[[/]*tab[s\] ]*',inbuf)

logging.info('removing irrelevant tab sections')
outbuf = ""
for x in blobs:
    logging.debug('processing blob:\n' + x + "\n")
    if x.startswith("version="):
        logging.debug('  blob starts with \"version=\"')
        if x.find(args.version) > 0:
            logging.debug('  blob matches version string ' + args.version)
            if x.find("view=") < 0:
                logging.debug('  blob has no view string')
                outbuf += x.split("]",1)[1]
            elif x.find("view=\"" + args.view + "\"") > 0:
                logging.debug('  blob view string matches ' + args.view)
                outbuf += x.split("]",1)[1]
            else:
                logging.debug('  blob view string does not match ' + args.view)
                ('  blob view string does not match ' + args.view)
                continue
    else:
        outbuf += x
md = outbuf

logging.info('attempting to create temp image storage dir /tmp/images')
if not os.path.isdir("/tmp/images"):
    try:
        os.mkdir("/tmp/images")
        logging.info('successfully created /tmp/images')
    except:
        logging.warn('could not create /tmp/images: aborting')
        print('could not create /tmp/images: aborting')
        sys.exit(-3)

match2 = re.findall(r'<a href="[^>]*><img src="[^ ]*">', md)
imagelines = match2

logging.info('processing images linked in the input file')
for x in imagelines:
    img_url = str(re.findall(r'<img src="([^ ]*)">',x)).split("'")[1]
    img_fnam = "/tmp/images/" + str(img_url).split("/")[-1].split(")")[0].split("'")[0]
    img_link = "../images/" + x.split("/")[-1].split(")")[0].split('"')[0]

    if args.s == False and not exists(img_fnam):
        print(img_fnam)
        logging.info('copying %s to /tmp/images', img_fnam)
        r = requests.get(img_url, stream=True)
        r.raw.decode_content = True
        with open(img_fnam, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        logging.info('conforming %s to doc image dimensions', img_fnam)
        img_props = str(subprocess.check_output(["file", img_fnam]))

        img_awidth = (
            re.search(",[ ]*[0-9]*[]*x[ ]*[0-9]*[ ]*,", img_props)
            .group()
            .split(",")[1]
            .split("x")[0]
        )
        img_aheight = (
            re.search(",[ ]*[0-9]*[]*x[ ]*[0-9]*[ ]*,", img_props)
            .group()
            .split(",")[1]
            .split("x")[1]
        )
        
        corr_width = 690
        corr_height = int(float(img_awidth) / 690.0 * float(img_aheight))
        
        logging.info('adjusting url for %s to local image directory', img_fnam)
        repl_img_line = '<a href="' + img_link
        repl_img_line += '" target = "_blank"><img alt="'
        repl_img_line += "unlabeled image" + '" '
        repl_img_line += 'width="690" '
        repl_img_line += 'src="' + img_link + '">'
            
        logging.info('replacing markdown URL for %s with HTML URL', img_fnam)
        md = md.replace(x, repl_img_line)
        
        logging.info('images downloaded and copied to /tmp/images')

logging.info('attempting to reroute interdocument links')
try:
    md = re.sub(r"https://discourse.maas.io/t", "/t", md)
    md = re.sub(r"/t/([a-z0-9-]*)/[0-9]*#", r"\1.html#", md)
    md = re.sub(r"/t/([a-z0-9-]*)/[0-9]*", r"\1.html", md)
    logging.info('interdocument links rerouted to local html targets')
except:
    logging.info('no interdocument links found')

logging.info('attempting to convert [note][/note] entries')
try:
    md = re.sub(r"\[note\]", r"**NOTE:** ", md)
    md = re.sub(r"\[/note\]", r" ", md)
    logging.info('[note][/note] entries converted')
except:
    logging.info('no note entries found')
    
logging.info('temporarily commenting out <detail> sections')
logging.info('  (do not process correctly on markdown conversion)')
md = (
    md.replace("<details>", "zorkD")
    .replace("<summary>", "zorkS")
    .replace("</details>", "zorkDC")
    .replace("</summary>", "zorkSC")
)

logging.info('convert the corrected markdown to html')
extensions = {"extra", "smarty"}
html = markdown.markdown(md, extensions=extensions, output_format="html5")
html = "<h1>" + args.title + "</h1>" + html

logging.info('restoring <detail> sections')
html = (
    html.replace("zorkDC", "</details>")
    .replace("zorkSC", "</summary>")
    .replace("zorkD", "<details>")
    .replace("zorkS", "<summary>")
    .replace("<ul>","<ul style=\"margin-left:4px; list-style-type:disc;\">")
)

logging.info('attempting to open template file')
try:
    template_file = open(args.t, "r")
    TEMPLATE = template_file.read()
except:
    TEMPLATE = """<!DOCTYPE html>
    <html>
    <body>
    <div class="container">
    {{content}}
    </div>
    </body>
    </html>
    """

logging.info('rendering jinja template')
doc = jinja2.Template(TEMPLATE).render(content=html)

logging.info('attempting to create output file')
if args.o == "stdout":
    sys.stdout.write(doc)
else:
    htmlf = open(args.o, "w")
    htmlf.write(doc)
    htmlf.close()
    

