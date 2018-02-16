#curl -i http://localhost:5000/starplus/api/v1.0/storecodes

#echo \##########TESTING GETMODULES#####################################
#curl -i http://localhost:5000/starplus/api/v1.0/getmodules/abcp01/24.244.1.123/10.10.1.1
#echo \##############################################################

echo
echo \##########TESTING GETKEY######################################
curl -i http://localhost:5000/starplus/api/v1.0/getkey/abcp01/7777/24.244.1.123/10.10.1.1
echo \##############################################################

#echo \##########TESTING ON NGINX######################################
#curl -i http://keys.auto-star.com/starplus/api/v1.0/getmodules/abcp01/24.244.1.123/10.10.1.1
#curl -i https://keys.auto-star.com/starplus/api/v1.0/getmodules/abcp01/24.244.1.123/10.10.1.1
