#!/usr/bin/env python3

'''
Fetches all LER XSD files, and dependencies, and saves them to `xsd` folder.

Uses `xmlschema` library's `export` function, which changes the `schemaLocation`
attributes to point to the local files, so that they can be used offline.

The `xsd` is committed to the repo, so no need to run this script unless
the XSD files are updated.
'''

import urllib.request
import xmlschema

opener = urllib.request.build_opener()
opener.addheaders = [("User-Agent", "Mozilla/5.0"),]
urllib.request.install_opener(opener)

schema = xmlschema.XMLSchema("https://ler.dk/files/2.2_ler.xsd")
schema.export(target="src/lerxml/xsd", save_remote=True)
