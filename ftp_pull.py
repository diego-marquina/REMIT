#%%
import os
import pysftp
import stat

#%%
myHostname = "sftp-transparency.entsoe.eu"
myUsername = "diego.marquina@shell.com"
myPassword = "entsoeDiego20210907!!"
remote_path = "/TP_export/UnavailabilityOfGenerationUnits_15.1.A_B"
local_path = "/home/azureuser/cloudfiles/code/Users/Diego.Marquina/REMIT/entsoe/UnavailabilityOfGenerationUnits_15.1.A_B"


# #%% get a remote directory for the first time   
# with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword) as sftp:
#     sftp.get_r(remote_path,local_path)

#%% synch directory
result = None
while result is None:
    try:
        # connect
        with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword) as sftp:
            print("Connection succesfully established ... ")
            sftp.cwd(remote_path)
            for f in sftp.listdir_attr():
                if not stat.S_ISDIR(f.st_mode):
                    # print("Checking %s..." % f.filename)
                    local_file_path = os.path.join(local_path, f.filename)
                    if ((not os.path.isfile(local_file_path)) or
                        (f.st_mtime > os.path.getmtime(local_file_path))):
                        print("Downloading %s..." % f.filename)
                        sftp.get(f.filename, local_file_path)
        result = 'done'
        print(result)
    except:
         pass

    # # Switch to a remote directory
    # sftp.cwd('/TP_export/UnavailabilityOfGenerationUnits_15.1.A_B')

    # # Obtain structure of the remote directory '/var/www/vhosts'
    # directory_structure = sftp.listdir_attr()

    # # Print data
    # for attr in directory_structure:
    #     print(attr.filename, attr)

    #Get files    
    
# connection closed automatically at the end of the with-block
# %%
