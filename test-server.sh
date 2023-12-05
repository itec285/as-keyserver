echo
echo \##########TESTING STORECODES#####################################
curl -i http://localhost:5000/starplus/api/v1.0/storecodes

echo
echo \##########TESTING GETMODULES#####################################
curl -i http://localhost:5000/starplus/api/v1.0/getmodules/test99/24.244.1.123/10.10.1.1
#echo \##############################################################

echo
echo \##########TESTING GETMODULES2####################################
curl -i http://localhost:5000/starplus/api/v2.0/getmodules/test99/24.244.1.123/10.10.1.1
#echo \##############################################################

echo
echo \##########TESTING GETMODULES3####################################
curl -i http://localhost:5000/starplus/api/v3.0/getmodules/test99/24.244.1.123/10.10.1.1
#echo \##############################################################

echo
echo \##########TESTING GETKEY######################################
curl -i http://localhost:5000/starplus/api/v1.0/getkey/test99/7777/24.244.1.123/10.10.1.1
echo \##############################################################

echo \##########TESTING GETVAR######################################
curl -i http://localhost:5000/starplus/api/v1.0/getvar/test99
echo \##############################################################

echo \##########TESTING SENDMODULES#################################
curl -H "Content-type: text/plain" -X POST http://localhost:5000/starplus/api/v1.0/sendmodules -d "test99,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,8,AAA1,8.2.7,Ivans Store,123 Main Street Medicine Hat AB,403-555-1234"


#Uncomment the below to test the live server
#curl -H "Content-type: text/plain" -X POST https://keys.auto-star.com/starplus/api/v1.0/sendmodules -d "test01,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,8,AAA1,8.2.7,Ivans Store,123 Main Street Medicine Hat AB,403-555-1234"
echo \##############################################################

#echo \##########TESTING ON NGINX######################################
#curl -i http://keys.auto-star.com/starplus/api/v1.0/getmodules/abcp01/24.244.1.123/10.10.1.1
#curl -i https://keys.auto-star.com/starplus/api/v1.0/getmodules/abcp01/24.244.1.123/10.10.1.1
