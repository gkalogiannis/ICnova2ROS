import datetime #For use in the timestamps

#Imporint the required methods for this bottle-server
from bottle import app, get, request, Bottle, run, template


#PyROS Init
#Importing everything need for communication with ROS via Python
topicName = "icnova" #the topic name we have used in Listener and using in ROS
import pyros_interfaces_ros
subproc = pyros_interfaces_ros.PyrosROS(topicName) #Creating the Topic
client_conn = subproc.start()
import pyros
import pyros.client
pyrosClient = pyros.client.PyrosClient(client_conn)
import rospy
from std_msgs.msg import String
rospy.init_node(topicName, anonymous=True)
pub = rospy.Publisher(topicName, String, queue_size=10)


 #The desired name of the file to keep the logs for this module
logFile = "API-Log.txt"
lastStatusFile = "GPIO-Last-Status.txt"

#Init Bottle
app = Bottle()
serverIP = "localhost"
serverPort = "8080"


#The function to handle logging to file
def log_to_file(text_to_write="given no text", timestamp="noTimestamp"):
    print(text_to_write)
    with open(logFile, "a") as myfile:
        myfile.write(str(text_to_write) + " @" + str(timestamp) + '\n')

#Function to read the last status of a GPIO for the file
def read_gpio_last_status():
    '''returns a list [gpio:status] '''
    try:
        with open(lastStatusFile, "r") as myfile:
            last_line = myfile.readlines()[-1]
            return last_line.split(":")
    except IOError:
        return ["file","not-exists"]


#Homepage: USER Controller
@app.route('/control', method='GET')
@app.route('/control/', method='GET')
@app.route('/control', method='POST')
@app.route('/control/', method='POST')
def homepage():
    #if no POST data then None
    api_type = request.POST.get('api_type')
    api_gpio = request.POST.get('api_gpio')
    api_state = request.POST.get('api_state')

    if api_type == 'user':
        if api_gpio is not None:
            if api_state is not None:
                user_input(gpio=api_gpio,state=api_state)

    print("api_state: ",api_state,", api_gpio: ",api_gpio,", api_state: ",api_state)

    _gpio , _state = read_gpio_last_status()

    return template(
        "control",
        gpioFromFile = _gpio,
        statusFromFile = _state
        )



# USER input
@app.route('/user/<gpio>/<state>')
@app.route('/user/<gpio>/<state>/')
def user_input(gpio='buzzer', state='off'):
    currentTimestamp = str(datetime.datetime.now())
    message = str("[USER]/[GPIO]/[STATE]={"+gpio+":"+state+"}")
    pub.publish(String(message + " @" + currentTimestamp))
    log_to_file(text_to_write=message, timestamp=currentTimestamp)
    return { "type": "USER", "GPIO" : gpio, "STATE" : state }#returning json (format) about the command

#  MESSAGE input
@app.route('/message/<text>')
@app.route('/message/<text>/')
def message_input(text='no_message'):
    currentTimestamp = str(datetime.datetime.now())
    message = str("[MESSAGE]/[TEXT]={"+text+"}")
    pub.publish(String(message + " @" + currentTimestamp))
    log_to_file(text_to_write=message, timestamp=currentTimestamp)
    return { "type": "MESSAGE", "TEXT" : text }#returning json (format) about the command


# FEEDBACK input
@app.route('/feedback/<status>')
@app.route('/feedback/<status>/')
def feedback_input(status='unknown'):
    currentTimestamp = str(datetime.datetime.now())
    message = str("[FEEDBACK]/[STATUS]={"+status+"}")
    pub.publish(String(message + " @" + currentTimestamp))
    log_to_file(text_to_write=message, timestamp=currentTimestamp)
    return { "type": "FEEDBACK", "STATUS" : status }#returning json (format) about the command


# Timing function to time the whole communication process (API->ROS->listener->ICnova->API) including network latency
@app.route('/timing/<previous_timestamp>')
@app.route('/timing/<previous_timestamp>/')
@app.route('/timing')
@app.route('/timing/')
def timing_whole_communication(previous_timestamp=0):
    '''FOR DEBUGGING: wget -qO- http://ip:8080/timing/$(date +%s%6N) &> /dev/null'''
    api_type = "TIMESTAMP"
    import time
    currentTime = int(round(time.time() * 1000*1000)) #time in microseconds from Epoch  eg: 1517068736834530 
    if previous_timestamp > 0 :
        api_type = "TIMINGS"
        if previous_timestamp.isdigit():
            previous_timestamp = int(str(previous_timestamp)[-8:]) #is in microseconds Keeping the last 8 digits
            current_timestamp = int(str(currentTime)[-8:]) #is in microseconds. Keeping the last 8 digits
            diff_timing = (current_timestamp - previous_timestamp)#the time difference in microseconds
            keysvalues = "start:" + str(previous_timestamp) + ", end:" + str(current_timestamp) + ", diff:" + str(diff_timing)
        else:
            keysvalues = "error:NaN previous_timestamp"
    else:#for debugging
        keysvalues = str(currentTime)[-8:]#is in microseconds. Keeping the last 8 digits
    message = str("["+api_type+"]/[MICROSECONDS_last8digits]={"+keysvalues+"}")
    pub.publish(String(message))
    log_to_file(text_to_write=message)
    return { "type": api_type, "MICROSECONDS_last8digits" : message }#returning json (format) about the command





#Now the bottle server if only we call this script directly (not importing it elsewhere)
if __name__ == '__main__':
    print("\t Starting Bottle...\n\n")

    #Run the server
    run(app, host=serverIP, port=serverPort)
