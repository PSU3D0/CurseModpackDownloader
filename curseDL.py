import tkinter
import os
import json
from tkinter import filedialog
from urllib.request import urlopen, Request


class ModpackDownloader():
    def __init__(self):
        root = tkinter.Tk()
        root.withdraw()

        self.cwd = os.getcwd()


    def manifestEvent(self):
        '''
        Event for the case of downloading a zip file from curseforge.
        Folder is extracted, manifest read, and mods downloaded to the contained /minecraft/mods/ folder.
        '''
        import zipfile #Default in versions of python >3.2. Used only within this function

        print("Please select zip file\n")
        zip_path = filedialog.askopenfilename(title="Select zip file",filetypes=[('Zip File','.zip')])

        working_dir = zip_path.split(".zip")[0]
        print("Extracting to parent directory...\n")

        with zipfile.ZipFile(zip_path,'r') as zip_ref:
            zip_ref.extractall(working_dir)#SHOULD always extract to parent directory

        #File is always named 'manifest.json' calling function is enough here
        manifest = self.parseManifest(os.path.join(working_dir,'manifest.json'))
        dl_dir = os.path.join(working_dir,'overrides/mods')
        print("Successfully parsed manifest\nDownloading mods to %s" % dl_dir)

        self.sequentialDownload(manifest,dl_dir)

        print("Forge version is %s" % manifest['forge_version']['id'])

    def callAPI(self,mod):
        #Returns formatted download URL
        #Api Docs : https://twitchappapi.docs.apiary.io
        return urlopen(Request('https://addons-ecs.forgesvc.net/api/v2/addon/%s/file/%s/download-url' % mod)).read().decode()
        

    def parseManifest(self,path):
        '''
        Reads manifest.json and returns dictionary with mod name, forge version, and list of tuples (projectID, fileID)
        '''

        try:
            with open(path,'r') as manifest_file:
                data = json.load(manifest_file)
        except:
            print("There was an error opening the manifest.")

        #Creates tuples
        modList = [(m['projectID'],m['fileID']) for m in data['files']]
        
        manifest = {
            'minecraft_version': data['minecraft']['version'],
            'forge_version': data['minecraft']['modLoaders'][0],
            'modpack_name': '{}_v{}'.format(data['name'],data['version']),
            'mods': modList
        }

        return manifest

    def jar_from_url(self,url):
        #Utility function
        return url.split('/')[-1]

    def sequentialDownload(self,manifest,download_output):

        total_mods = len(manifest['mods'])
        
        i = 1
        for mod in manifest['mods']:
            download_url = self.callAPI(mod).replace(" ", "%20")
            mod_name = self.jar_from_url(download_url)
            download = os.path.join(download_output,mod_name)

            if os.path.exists(download):
                print(f"{mod_name} exists. Skipping download ({i}/{total_mods}")
            else:
                dl = urlopen(download_url).read()
                open(download,'wb').write(dl)
                print(f"Downloaded {mod_name} ({i}/{total_mods})")
            i+=1
        print("\n\nDownload complete!\n")
        
if __name__ == '__main__':
    downloader = ModpackDownloader()
    downloader.manifestEvent()