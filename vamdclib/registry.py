#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

routines for querying the registry

"""
import sys
import os

if sys.version_info[0] == 3:
    from .settings import *
else:
    from settings import *

REL_REG = 'http://registry.vamdc.eu/vamdc_registry/services/RegistryQueryv1_0'
DEV_REG = 'http://casx019-zone1.ast.cam.ac.uk/registry/services/RegistryQueryv1_0'
REL_REG = 'http://registry.vamdc.eu/registry-12.07/services/RegistryQueryv1_0'
# use registry defined in settings if defined
try:
  WSDL = REGURL + '?wsdl'
except:
  REGURL = REL_REG
  WSDL = REGURL + '?wsdl'

from suds.client import Client
from suds.xsd.doctor import Doctor
class RegistryDoctor(Doctor):
    TNS = 'http://www.ivoa.net/wsdl/RegistrySearch/v1.0'
    def examine(self, node):
        tns = node.get('targetNamespace')
        # find a specific schema
        if tns != self.TNS:
            return
        for e in node.getChildren('element'):
            # find our response element
            if e.get('name') != 'XQuerySearchResponse':
                continue
            # fix the <xs:any/> by adding maxOccurs
            any = e.childAtPath('complexType/sequence/any')
            any.set('maxOccurs', 'unbounded')
            break


def getNodeList():

    d = RegistryDoctor()
    client = Client(WSDL) #,doctor=d)

    qr="""declare namespace ri='http://www.ivoa.net/xml/RegistryInterface/v1.0';
<nodes>
{
   for $x in //ri:Resource
   where $x/capability[@standardID='ivo://vamdc/std/VAMDC-TAP']
   and $x/@status='active'
   and $x/capability[@standardID='ivo://vamdc/std/VAMDC-TAP']/versionOfStandards='12.07'
   return
   <node><title>{$x/title/text()}</title>
   <url>{$x/capability[@standardID='ivo://vamdc/std/VAMDC-TAP']/interface/accessURL/text()}</url>
   <referenceURL>{$x/content/referenceURL/text()}</referenceURL>
   <identifier>{$x/identifier/text()}</identifier>
   <maintainer>{$x/curation/contact/email/text()}</maintainer>
   <returnables>{$x/capability/returnable}</returnables>
   </node>
}
</nodes>"""


    v=client.service.XQuerySearch(qr)
    nameurls=[]
    for node in v.node:
        # take only the first url
        try:
            url = node.url.split(" ")[0]
        except:
            url = None

        nameurls.append({
            'name': node.title,
            'url': url,
            'referenceUrl': node.referenceUrl if "referenceUrl" in dir(node) else None,
            'identifier': node.identifier,
            'maintainer': node.maintainer,
            'returnables': node.returnables['returnable']})
    return nameurls



if __name__ == '__main__':
    print(getNodeList())
