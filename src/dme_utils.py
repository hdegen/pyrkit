import json
import os
import logging
import sys


class DMESession():
    """
    A utility class to perform Data Management Environment requests
    """

    def __init__(self, dme_url = '', dme_token = ''):
        """
        Constructor

        @param dme_token <str>
        The DME authentication token
        """
        self.dme_utils = 'HPC_DM_UTILS'
        self.dme_url = dme_url if dme_url != '' else self.get_dme_url()
        self.dme_token = dme_token if dme_token != '' else self.get_token_from_file()
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    def get_dme_url(self):
        try:
            hpc_utils = os.environ[self.dme_utils]
        except:
            print(f"ERROR: {self.dme_utils} not found in PATH envirronment. Exiting...")
            sys.exit(1)
        
        properties = f"{hpc_utils}/hpcdme.properties"
        f = open(properties,'r')
        url = ''
        for l in f.readlines():
            if (l[0] == '#'):
                continue
            if 'hpc.server.url' in l:
                url = l.split('=')[1]
                break
        return url

    def get_token_from_file(self):
        try:
            hpc_utils = os.environ[self.dme_utils]
        except:
            print(f"ERROR: {self.dme_utils} not found in PATH envirronment. Exiting...")
            sys.exit(1)
        
        token_path = f"{hpc_utils}/tokens/curl-conf"
        if (not os.path.exists(token_path)):
            print(f"WARNING: token file not found in {token_path}. Requesting a token...")
            print("dm_generate_token")
            os.system("dm_generate_token")
        try:
            token_file = open(token_path)
        except:
            print(f"ERROR: could not open token file. Exiting...")
            sys.exit(1)

        lines = [l for l in token_file]
        token = lines[1].split('Bearer ')[1][0:-2]
        token_file.close()
        del lines
        return token
    
    def list_files(self, dir_path, print_dataObjects = False):
        """
        Returns a list of files in in a given DME director 

        @param dir_path str
            The the path of the direcotry on DME 
        
        @return files list(<str>)
            List of the files in dir_path 
        """

        # data_object_path = encode_path(data_object_path)
        dme_token = self.dme_token
        headers = {}
        headers["Authorization"] = "Bearer {0}".format(dme_token)
        full_path = self.dme_url + "/collection/" + dir_path 
        params = {"list":"true"}
        
        import requests
        get_response = requests.get(full_path, headers=headers, verify=False, params=params)
        if get_response.status_code != 200:
            logging.error("Error getting DME directory", dir_path)
            raise Exception("Response code: {0}, Response message: {1}".format(get_response.status_code, get_response.text))
        
        metadata_dic = json.loads(get_response.text)
        dataObjects = metadata_dic['collections'][0]['collection']['dataObjects']
        if print_dataObjects:
            print(json.dumps(metadata_dic['collections'][0]['collection']['dataObjects'], indent=2, separators=(", ", " = ")))

        files = []
        for dataObject in dataObjects:
            files.append(dataObject['path'])
        return files

    def get_dataObject_dme_meta(self, data_object_path):
        """
            Return the self metadata values for a file (data_object)
            Parameters
            ----------
            data_object_path : string
                The path of the file on DME 
  
            Returns
            ----------
            dictionary
                Dictonary of all metadata for the file in DME 
        """
        # data_object_path = encode_path(data_object_path)
        dme_token = self.dme_token
        headers = {}
        headers["Authorization"] = "Bearer {0}".format(dme_token)
        import requests
        full_path = self.dme_url + "v2/dataObject/" + data_object_path
        get_response = requests.get(full_path, headers=headers, verify=False)
        if get_response.status_code != 200:
            logging.error("Error downloading from DME", data_object_path)
            raise Exception("Response code: {0}, Response message: {1}".format(get_response.status_code, get_response.text))
  
        metadata_dic = json.loads(get_response.text)
        #print(json.dumps(metadata_dic, indent=2, separators=(", ", " = ")))
        self_metadata = metadata_dic['metadataEntries']['selfMetadataEntries'][0]['systemMetadataEntries']
        self_dic = {}
        for pair in self_metadata:
            self_dic[pair['attribute']] = pair['value']
 
        return self_dic
