from datetime import datetime, time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import datetime

#--------------creat firebae---------------
from scipy.linalg import bandwidth

cred = credentials.Certificate('afad-database-firebase-adminsdk-qag17-affdb07974.json')
firebase_admin.initialize_app(cred)

device_id = ""

class service_firebase:

    device_id = ""

    def __init__(self,user_id,request_id,location,device_id):
        self.user_id=user_id
        self.request_id = request_id
        self.location = location
        self.device_id=device_id
        #print('location :'+location)
        #print('id :'+device_id)


    def init_firebase(self):
        db = firestore.client()
        dt = datetime.datetime.now()
        data = {"personId": self.user_id, "id": self.request_id, "position" : self.location,"time":dt,"status":True}
        band_ref = db.collection(u'messages').document(self.device_id).set(data)



        #location_data_ref = db.collection(u'messages').document(self.device_id).collection('Location')


        #heart_rate_data_ref = db.collection(u'messages').document(self.device_id).collection('user_id')
       # Status_data_doc_ref = db.collection(u'messages').document(self.device_id).collection('message_id')
        # Set the capital field

        #lat = self.location.split('*')[0]
        #long = self.location.split('*')[1]
        #rate = self.location.split('*')[2]

        # print('lat :' +lat+':')
        # print('lat :' +long+':')
        # print('lat :' +rate+':')
        try:
            if(self.location is None):
                print("location error")
            else:
               data = {"message" : self.location}
        except:
            print("Converting Error")

#sf = service_firebase('46.508131*46.508131*32','test4')
#sf = service_firebase('deneme',"test4")
#sf.init_firebase()