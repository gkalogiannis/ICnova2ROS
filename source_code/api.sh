#!/bin/sh

cat <<"HEAD"
Content-Type: text/html

<html>
<head>
<title> The ICnova API GET </title>
</head>
<body>
<h2> The ICnova API with GET </h2>
<p> request: http://ip/cgi-bin/api.sh?GPIO=STATE </p>
<p> eg: http://ip/cgi-bin/api.sh?buzzer=on </p>
<p> eg: http://ip/cgi-bin/api.sh?buzzer=mode1 </p>
<p> eg: http://ip/cgi-bin/api.sh?buzzer=mode2 </p>


HEAD

if [ -d "/sys/devices/platform/atmel-pwm-hwmon.0" ]; then

    FilePWM=/sys/devices/platform/atmel-pwm-hwmon.0/pwm1
    FilePWMFREQ=/sys/devices/platform/atmel-pwm-hwmon.0/pwm1_freq

    FileNull=/dev/null
    
    FeedbackURL=http://192.168.2.13:8080/feedback/
    #wget -O FileNull -o FileNull example.com

    if (echo $QUERY_STRING | grep "buzzer=on" >> "$FileNull" ); then
  
        if (echo $QUERY_STRING | grep "mode1" >> "$FileNull" ); then
            echo 500 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  MODE1</p>"
        else if (echo $QUERY_STRING | grep "mode2" >> "$FileNull" ); then
            echo 800 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  MODE2</p>"
        else if (echo $QUERY_STRING | grep "mode3" >> "$FileNull" ); then
            echo 1050 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  MODE3</p>"
        else if (echo $QUERY_STRING | grep "mode4" >> "$FileNull" ); then
            echo 1200 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  MODE4</p>"
        else if (echo $QUERY_STRING | grep "mode5" >> "$FileNull" ); then
            echo 2000 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  MODE5</p>"
        else
            echo 1500 > "$FilePWMFREQ"
            echo 500 > "$FilePWM"
            echo "<p>BUZZER  ON</p>"
        fi
    else
        echo 0 > "$FilePWMFREQ"
        echo 0 > "$FilePWM"
    fi

    #Sending the Feedback
    #   eg:  http://192.168.2.13:8080/feedback/buzzer:(Frequency:1093,Pulse-Width:500)
    FeedbackURLbuzzer="$FeedbackURL""buzzer:"
    Freq="$(head -1 "$FilePWMFREQ")"
    Pwm="$(head -1 "$FilePWM")"
    FeedbackURLbuzzer="$FeedbackURLbuzzer""(Frequency:""$Freq"",Pulse-Width:""$Pwm"")"
    wget FeedbackURLbuzzer -O FileNull

else
    echo "<h1>BUZZER  IS  MISSING!</h1>"
fi
cat <<"FOOTER"

</body>
</html>
FOOTER
