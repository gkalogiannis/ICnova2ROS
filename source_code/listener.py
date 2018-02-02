import datetime #For use in the timestamps
#Regular Expresions module
import re
#For handling URL requests
import urllib2
#Our ROS API in Python
import rospy
#String module (diffrent than str() build-in function). Required for ROSpy messages type
from std_msgs.msg import String


#Init
print("\t Starting Listener...\n\n")

logFile = "LISTENER-Log.txt" #The desired name of the file to keep the logs for this module
lastStatusFile = "GPIO-Last-Status.txt"

icnova_IP = "192.168.2.11" #the IP of our ICnova
icnova_PORT = "" #not used for now
icnova_ScriptPath = "/cgi-bin/api.sh" #the relative path of our api-script in ICnova web server
topicName = "icnova" #the topic name we have used in bottle-api and using in ROS

#The function to handle logging to file
def log_to_file(text_to_write="given no text", timestamp="noTimestamp"):
    print(text_to_write)
    with open(logFile, "a") as myfile:
        myfile.write(str(text_to_write) + " @" + str(timestamp) + '\n')

#Save the last checked status from the GPIO in a file
def save_last_gpio_status(gpio="unknown", status="unknown"):
    with open(logFile, "a") as myfile:
        myfile.write(str(gpio) + ":" + str(status) + '\n')

#The function for handling URL Request Error messages and logging
def custom_URL_Error(prefixed_text="", error="", timestamp=""):
    message= str(prefixed_text + str(error))
    log_to_file(text_to_write=message, timestamp=timestamp)


#The function that prepares and sends the Command (that we listened to in ROS topic) to ICnova
def icnova_gpio_get_request(ip=icnova_IP, port=icnova_PORT, scriptPath=icnova_ScriptPath, gpio="buzzer", state="off"):
    port = port if port == "" else ":"+port#check if port is specified, else ignore it
    command = str( gpio + "=" + state )#preparing the command (just a pair of GET key=value)
    url = str('http://'+ip+port+icnova_ScriptPath+"?"+command)#preparing the final URL
    currentTimestamp = str(datetime.datetime.now())#getting current timestamp
    log_to_file(text_to_write= "   ... requesting: " + url, timestamp=currentTimestamp)
    
    #The following block is for error handling for any network/server issues (if any exists)
    try: 
        response = urllib2.urlopen(url, timeout = 9)#Requesting the final URL and waiting 9sec for any response (HTTP code)
        #the_page = response.read() #just for debugging
    except urllib2.HTTPError, e:
        custom_URL_Error(prefixed_text= 'HTTPError = ', error=e.code, timestamp=currentTimestamp)
        save_last_gpio_status(gpio="icnova", status="no_communication")
    except urllib2.URLError, e:
        custom_URL_Error(prefixed_text= 'URLError = ', error=e.reason, timestamp=currentTimestamp)
        save_last_gpio_status(gpio="icnova", status="no_communication")
    except httplib.HTTPException, e:
        custom_URL_Error(prefixed_text= 'HTTPException', timestamp=currentTimestamp)
        save_last_gpio_status(gpio="icnova", status="no_communication")
    except Exception:
        import traceback
        custom_URL_Error(prefixed_text= 'generic exception: ' + traceback.format_exc(), timestamp=currentTimestamp)
        save_last_gpio_status(gpio="icnova", status="no_communication")
    else:
        log_to_file(text_to_write= "SENT Command to ICnova: " + url, timestamp=currentTimestamp)
        save_last_gpio_status(gpio=gpio, status=state)


#A simple function just for timing purposes
def icnova_timing(ip=icnova_IP, port=icnova_PORT, scriptPath=icnova_ScriptPath, mstime=0):
    port = port if port == "" else ":"+port#check if port is specified, else ignore it
    command = str( "timing" + "=" + mstime )#preparing the command (just a pair of GET key=value)
    url = str('http://'+ip+port+icnova_ScriptPath+"?"+command)#preparing the final URL
    currentTimestamp = str(datetime.datetime.now())#getting current timestamp
    log_to_file(text_to_write= "   ... ... timing: " + url, timestamp=currentTimestamp)


#The main function that is called every time the ROS topic displays a message and parsing each message
def callback(data):
    data_text = data.data #getting the data from the Message in the ROS Topic
    if "[USER]/[GPIO]/[STATE]=" in data_text:
        '''example: [USER]/[GPIO]/[STATE]={buzzer:off} @timestamp'''
        command = re.findall(r"\{([^}]+)\}", data_text)#find all the key:value inside the curly brackets using RegEx
        gpio, state = command[0].split(":")#getting only the first instance of curly brackets and spliting it to: key,value
        icnova_gpio_get_request(gpio=gpio, state=state)#calling the function that prepares this command for sending to ICnova

    elif "[MESSAGE]/[TEXT]=" in data_text: #for debugging
        '''example: [MESSAGE]/[TEXT]={text} @timestamp'''
        pass
    elif "[FEEDBACK]/[STATUS]=" in data_text: #for debugging
        '''example: [FEEDBACK]/[STATUS]={status} @timestamp'''
        pass
    elif "[TIMESTAMP]/[MICROSECONDS_last8digits]=" in data_text:
        '''example: [FEEDBACK]/[STATUS]={status} @timestamp'''
        command = re.findall(r"\{([^}]+)\}", data_text)#find all the key:value inside the curly brackets using RegEx
        mstime = command[0]#getting only the first instance of curly brackets, that it is our time
        icnova_timing(mstime=mstime)#calling the function that prepares this command for sending to ICnova
    else: #for debugging
        return


#The main function for this script
def listener():
    rospy.init_node(topicName, anonymous=True)#Initilize the Node (corresponding ROS node) inside ROSpy
    rospy.Subscriber(topicName, String, callback)#Subscribe (Listen) to the ROS topic, reading the messages (message type: String), and for each message call the function: callback

    # spin() simply keeps Python from exiting until this node is stopped
    rospy.spin()



#Now execute function listener() if only we call this script directly (not importing it elsewhere)
if __name__ == '__main__':
    listener()
