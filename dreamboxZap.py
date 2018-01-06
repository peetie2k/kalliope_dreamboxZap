import json
import logging

import requests
import xmltodict

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException


logging.basicConfig()
logger = logging.getLogger("kalliope")


class DreamboxZap(NeuronModule):

    def __init__(self, **kwargs):
        super(DreamboxZap, self).__init__(**kwargs)

        # input variables
        self.hostname = kwargs.get('hostname', None)
        self.port = kwargs.get('port', None)
        self.user = kwargs.get('user', None)
        self.password = kwargs.get('password', None)
        self.useSSL = kwargs.get('useSSL', False )
        self.bouquetName = kwargs.get('bouquetId', None )
        
        # channel (dynamically from the input)
        self.channel = kwargs.get('channel', False )


        # processing parameters
        self.request_parameters = None
        self.baseUrl = None
        self.channelMap = {}
        
        
        
        #some constants
        self.endpointBouquet = 'web/getservices?sRef='
        self.endpointZapService = 'web/zap?sRef='
        self.endpointAllServices = 'web/getallservices'
        
        # output variable
        self.status_code = None
        self.content = None
        self.text = None
        self.response_header = None

       

        # check parameters
        if self._is_parameters_ok():
                  
            retDict = dict()

            # we get parameters that will be passed to the neuron
            self.request_parameters = self.get_parameters()
            
            #iinitiate the basic connection stuff
            self.buildDreamBaseUrl()
            self.buildRequestParameters()
            
            #extract the existing channels
            self.extractChannels()
            
            #now check whether the requested channel excists
            if self.checkChannelExists(self.channel) == True:
                self.status = self.zapToService(self.channelMap[self.channel])
            else:
                self.status = 'unknown'
            
            retDict["status"] = self.status
            self.say(retDict)
    
    def buildDreamBaseUrl(self):
        prefix = 'http://'
        if (self.useSSL == True):
            prefix = 'https://'
        
        self.baseUrl = prefix + self.hostname + ':' + self.port + '/' ;
    
    def extractChannels(self):
        url = self.baseUrl
        if self.bouquetName == None:
            url = url + self.endpointAllServices 
        else:
            url = url + self.endpointBouquet + self.bouquetName 
        r = requests.get(url=url, **self.request_parameters)
        xmlContent = r.content
        doc = xmltodict.parse(xmlContent)
    
        if self.bouquetName == None:
            for bouquet in doc['e2servicelistrecursive']['e2bouquet']:
                for service in bouquet['e2servicelist']['e2service']:
                    self.channelMap[service['e2servicename']] = service['e2servicereference']
        else:
            for service in doc['e2servicelist']['e2service']:
                self.channelMap[service['e2servicename']] = service['e2servicereference']
    
    
    def buildRequestParameters(self):
        self.request_parameters = dict()
        self.request_parameters["timeout"] = 10 
        if self.user != None:
            self.request_parameters["auth"] = self.user, self.password
  
    def zapToService(self, channelService):
        url = self.baseUrl + self.endpointZapService + channelService 
        r = requests.get(url=url, **self.request_parameters)
        if r.status_code == 200:
            outMessage = 'ok'
        else:
            outMessage = 'fail'
        return outMessage
    
    def checkChannelExists(self,channelName):
        if channelName in self.channelMap:
            return True
        else:
            return False
    
  
    def _is_parameters_ok(self):
        """
        Check that all provided parameters in the neurons are valid
        :return: True if all check passed
        """       
        self.hostname = kwargs.get('hostname', None)
        self.port = kwargs.get('port', None)
        self.user = kwargs.get('user', None)
        self.password = kwargs.get('password', None)
        self.useSSL = kwargs.get('useSSL', False )
        
        # Hostname is mandatory
        if self.hostname is None:
            raise InvalidParameterException("Hostname is missing")
        
        # Port is mandatory
        if self.port is None:
            raise InvalidParameterException("Port is missing")
        
        # User is mandatory
        if (self.user is not None and self.password is None) or
        (self.user is None and self.password is not None):
            raise InvalidParameterException("If you enabled authentication, please always spacify user and password")
        return True