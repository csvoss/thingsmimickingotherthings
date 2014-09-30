import Image
import urllib, cStringIO
import json

# http://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
# http://stackoverflow.com/questions/8151282/make-a-thumbnail-with-pil-enhanced-way

filein = open("template.html", 'r')
fileout = open("index.html", 'w')
nodefile = open("nodes.txt", 'r')
linkfile = open("links.txt", 'r')

node_urls = {}
link_urls = {}
linkcounter = {}

node_species={}
link_species={}

##Read the input files
for line in nodefile:
    stuff = line.split(' ')
    if len(stuff) < 2:
        continue
    node_urls[stuff[0]] = stuff[1].strip()
    node_species[stuff[0]] = ' '.join(stuff[2:]).strip()

nodefile.close()

for line in linkfile:
    stuff = line.split(' ')
    if len(stuff) < 3:
        continue
    num = 0
    tup = (stuff[0], stuff[1])
    if tup in linkcounter:
        linkcounter[tup] += 1
        num = linkcounter[tup]
    else:
        linkcounter[tup] = 0
    link_urls[(stuff[0], stuff[1], num)] = stuff[2].strip()
    for s in tup:
        if not s in node_urls:
            print "Warning: not in nodes.txt: "+s
    link_species[(stuff[0], stuff[1], num)] = ' '.join(stuff[3:]).strip()

linkfile.close()

def thumbnailify(name, url):
    our_url = "http://csvoss.scripts.mit.edu/thingsmimickingotherthings/"
    # Read a URL, convert it to a thumbnail,
    # save the thumbnail at images/name.jpg,
    # return a modified URL with the thumbnail

    outfilename = 'images/%s.jpg' % name

    # Test if the result is already cached...
    try:
        with open(outfilename):
            return outfilename
    except IOError:
        pass

    debug = True
    WIDTH, HEIGHT = 50, 50

    if debug:
        print url
    infile = cStringIO.StringIO(urllib.urlopen(url).read())
    img = Image.open(infile)
    im = img.copy()
    if im.size[0] >= im.size[1]:
        im = im.resize((HEIGHT * im.size[0]/im.size[1], HEIGHT), Image.ANTIALIAS)
        im = im.crop(((im.size[0]-WIDTH)/2, 0, (im.size[0]+WIDTH)/2, HEIGHT))
    else:
        im = im.resize((WIDTH, WIDTH*im.size[1]/im.size[0]), Image.ANTIALIAS)
        im = im.crop((0, (im.size[1]-HEIGHT)/2, WIDTH, (im.size[1]+HEIGHT)/2))
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(outfilename)
    if debug:
        print outfilename
    return our_url + outfilename

def toenailify(name, url):
    "It's bigger than a thumbnail"
    our_url = "http://csvoss.scripts.mit.edu/thingsmimickingotherthings/"
    outfilename = 'big_images/%s.jpg' % name
    try:
        with open(outfilename):
            return outfilename
    except IOError:
        pass
    debug = True
    WIDTH = 300
    if debug:
        print url
    infile = cStringIO.StringIO(urllib.urlopen(url).read())
    img = Image.open(infile)
    im = img.copy()
    im = im.resize((WIDTH, WIDTH*im.size[1]/im.size[0]), Image.ANTIALIAS)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(outfilename)
    if debug:
        print outfilename
    return our_url + outfilename
 
def write(line):
    fileout.write(line)

def writeln(line):
    write(line + "\n")

def token(link):
    return link[0]+"_"+link[1]+"_"+str(link[2])

def text(link):
    return link[1]+"-mimicking "+link[0]

def descriptorify(name, species):
    species = species.strip()
    if len(species) == 0:
        return name
    else:
        return "<i>%s</i>, %s" % (species, name)

##Output
for line in filein:
    if line.strip() == "//ADDNODES":
        #graph.addNode('anvaka', {url:'https://secure.gravatar.com/avatar/91bad8ceeec43ae303790f8fe238164b', name:'whatever'});
        for node in node_urls:
            writeln("graph.addNode('"+node+"', {url:'"+thumbnailify(node, node_urls[node])+"', name: '"+node+"', source: '"+node_urls[node]+"', descriptor: '"+descriptorify(node, node_species[node])+"'});")
            #writeln("graph.addNode('"+node+"', {url:'"+thumbnailify(node, node_urls[node])+"'});")
        for link in link_urls:
            writeln("graph.addNode('"+token(link)+"', {url:'"+thumbnailify(token(link), link_urls[link])+"', name: '"+text(link)+"', source: '"+link_urls[link]+"', descriptor: '"+descriptorify(text(link), link_species[link])+"'});")
            #writeln("graph.addNode('"+token(link)+"', {url:'"+thumbnailify(token(link), link_urls[link])+"'});")

    elif line.strip() == "//ADDLINKS":
        #graph.addLink('indexzero', 'anvaka', false);
        for link in link_urls:
            writeln("graph.addLink('"+link[0]+"', '"+token(link)+"', false);")
            writeln("graph.addLink('"+token(link)+"', '"+link[1]+"', false);")

    ## OBSOLETE
    ##elif line.strip() == "//HIDEALLNODEIMAGES":
    ##    #$("#anvaka").hide();
    ##    for node in node_urls:
    ##        writeln("$('#"+node+"').hide();")
    ##    for link in link_urls:
    ##        writeln("$('#"+token(link)+"').hide();")

    ## For preloading images
    elif line.strip() == "//ADDIMAGES":
        #<span id="anvaka"><img src="URL.jpg"></img></span>
        for node in node_urls:
            writeln("<span id='"+node+"'><img class='invisible' src='"+node_urls[node]+"'></img></span>")
        for link in link_urls:
            writeln("<span id='"+token(link)+"'><img class='invisible' src='"+link_urls[link]+"'></img></span>")

    elif line.strip() == "//PICTIONARY":
        jsonout = dict([(node, toenailify(node, node_urls[node])) for node in node_urls])
        jsonout_2 = dict([(token(link), toenailify(token(link), link_urls[link])) for link in link_urls])
        jsonout.update(jsonout_2)

        writeln("pictionary = " + json.dumps(jsonout) + ";")

    elif line.strip() == "//PRELOADER":
        for node, url in node_urls:
            writeln("<img src=\""+toenailify(node, url)+"\" width=\"1\" height=\"1\" />")
        for link, url in link_urls:
            writeln("<img src=\""+toenailify(token(link), url)+"\" width=\"1\" height=\"1\" />")

    elif line.strip() == "//PRELOADER_JS":
        for node, url in node_urls.items():
            writeln("document.getElementById(\"preloader\").style.background = \"url("+toenailify(node, url)+") no-repeat -9999px -9999px\";")
        for link, url in link_urls.items():
            writeln("document.getElementById(\"preloader\").style.background = \"url("+toenailify(token(link), url)+") no-repeat -9999px -9999px\";")

    else:
        write(line)


filein.close()
fileout.close()
