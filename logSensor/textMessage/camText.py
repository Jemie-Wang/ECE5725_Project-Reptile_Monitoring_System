from twilio.rest import Client 
 
account_sid = 'ACba371d3b45df34689eb9b5a94c5715f7' 
auth_token = '52961bcffcdf946fa3550e4c43c61ce9' 
client = Client(account_sid, auth_token) 
 
message = client.messages.create(  
	messaging_service_sid='MG5b84d040c9b31bfa0a5b9300eb405ca8', 
    body='Warning! There may be something wrong with your pet.',      
    to='+16072624205' 
                          ) 
 
print(message.sid)
